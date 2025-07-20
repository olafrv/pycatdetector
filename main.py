from asyncio.log import logger
import os
import sys
import signal
import logging
import time
import colorlog
import json
import pycatdetector.channels
from pycatdetector.Config import Config
from pycatdetector.Recorder import Recorder
from pycatdetector.NeuralNetPyTorch import NeuralNetPyTorch
from pycatdetector.Detector import Detector
from pycatdetector.Notifier import Notifier
from pycatdetector.Screener import Screener

recorder : Recorder
detector : Detector
notifier : Notifier
screener : Screener 
config : Config
logger : logging.Logger

def main():
    global recorder, detector, notifier, screener, config, logger

    config = Config()

    if len(sys.argv) > 1:
        if "--check-config" in sys.argv:
            print(config.to_json())
            exit(0)

    enable_logging(config)
    logger = logging.getLogger(__name__)
    logger.info("PATH: " + os.environ["PATH"])
    logger.info("Python Sys Prefix: " + sys.prefix)

    signal.signal(signal.SIGINT, handler)

    recorder = Recorder(config.get("rtsp_url"))

    screener_enabled = not config.get("headless")
    net_model_name = config.get("net_model_name")
    notify_min_score = float(config.get("notify_min_score"))

    if config.get("net_version") == 'v2':
        net = NeuralNetPyTorch(net_model_name)
    else:
        raise ValueError("Invalid net_version: " + config.get("net_version"))

    videos_folder = config.get("videos_folder")

    detector = Detector(images=recorder.get_images(), 
                        screener_enabled=screener_enabled, 
                        net=net,
                        notify_min_score=notify_min_score, 
                        encoder_folder=videos_folder)

    notifier = Notifier(detector.get_detections())
    load_channels(config, notifier)

    detector.set_labels(notifier.get_labels())

    recorder.start()
    detector.start()
    notifier.start()

    if screener_enabled:
        screener = Screener(detector)
        screener.show()

    notifier.join()
    recorder.join()
    detector.join()


def handler(signum, frame):
    global recorder, detector, notifier, screener
    if signum == signal.SIGINT:  # CTRL + C
        if screener is not None:
            screener.close()
        if notifier is not None:
            notifier.stop()
        if recorder is not None:
            recorder.stop()
        if detector is not None:
            detector.stop()

def models_preload():
    global logger
    logger.info("Preloading PyTorch models...")
    NeuralNetPyTorch('FasterRCNN_MobileNet_V3_Large_FPN')
    NeuralNetPyTorch('FasterRCNN_MobileNet_V3_Large_320_FPN')
    logger.info("Preloading: Done.")


def load_channels(config, notifier):
    global logger

    # Find all notification channels enabled
    settings = config.get_regex("^notifiers_.*_enabled$")
    for setting, enabled in settings.items():
        # Set channel name variants
        c_name_snaked = setting.lstrip("notifiers_").rstrip("_enabled")
        c_name_camel = Config.snake_to_camel(c_name_snaked)
        logger.debug("Channel: " + c_name_camel + ", enabled: " + str(enabled))
        if not enabled:
            logger.info("Channel " + c_name_camel + " is disabled, skipping.")
            continue

        # Load channel class and its configuration (snake cased)
        c_config = \
            config.get_prefix("notifiers_" + c_name_snaked, ltrim=True)
        channel = eval('pycatdetector.channels.' + c_name_camel)(c_config)
        
        # Get channel notify object labels and it to the notifier
        # c_labels = ["cat", "dog", "person"]
        c_labels = config.get("notifiers_" + c_name_snaked + "_objects")
        notifier.add_channel(channel, c_labels)

        # Get channel notification window names
        for c_notify_window_name in ["weekdays", "weekends"]:
            
            # Get channel notify windows config
            c_notify_window_schedule = config.get_prefix(
                "notifiers_" + c_name_snaked + "_notify_window_" + c_notify_window_name)

            # Add channel's notify window and its schedule to the notifier
            c_name = channel.get_name()
            notifier.add_notify_window(
                channel, c_notify_window_name, c_notify_window_schedule)
            logger.info(
                "Added notify window '" + c_notify_window_name 
                + "' for channel '" + c_name + "' for schedule: " 
                + json.dumps(c_notify_window_schedule)
            )

def enable_logging(config):
    tz = time.strftime('%z')
    # https://docs.python.org/3/howto/logging.html
    if config.get("log_level").upper() == "DEBUG":
        logFormat = '[%(asctime)s ' + tz + '] p%(process)s %(threadName)s'
        logFormat += ' {%(filename)s:%(lineno)d} %(levelname)s - %(message)s'
    else:
        logFormat = '[%(asctime)s ' \
            + tz + '] %(levelname)s %(name)s - %(message)s'

    # https://docs.python.org/3/library/logging.html#logging.basicConfig
    logging.basicConfig(
        format=logFormat,
        encoding='utf-8',
        filename=os.path.join(
            config.get("log_dir"), 'detector.log'
        ),
        level=eval(
            'logging.' +
            config.get("log_level").upper()
        ),
        force=True
    )
    logging.Formatter.default_msec_format = '%s.%03d'

    # https://pypi.org/project/colorlog/
    if config.get("log_tty"):
        colorHandler = colorlog.StreamHandler()
        colorHandler.setFormatter(
            colorlog.ColoredFormatter('%(log_color)s' + logFormat)
        )
        logging.getLogger().addHandler(colorHandler)
    else:
        logging.StreamHandler(stream=None)


if __name__ == '__main__':
    main()
