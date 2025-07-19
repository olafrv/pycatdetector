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

images = recorder = detector = notifier = screener = config = None
logger = None

def main():
    global images, recorder, detector, notifier, screener, config, logger

    config = Config()

    if len(sys.argv) > 1:
        if "--check-config" in sys.argv:
            print(json.dumps(config.get_all(), indent=2))
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
    notifier.set_notify_window(config.get_assoc("notify_window"))
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


def load_channels(config, notifier):
    global logger
    settings = config.get_regex("^notifiers_.*_enabled$")
    for setting, enabled in settings.items():
        setting_name = setting.lstrip("notifiers_").rstrip("_enabled")
        class_name = Config.snake_to_camel(setting_name)
        logger.debug("Channel: " + class_name + ", enabled: " + str(enabled))
        if not enabled:
            continue
        else:
            channel_settings = config.get_prefix("notifiers_" + setting_name, ltrim=True)
            channel_labels = config.get("notifiers_" + setting_name + "_objects")
            channel = eval('pycatdetector.channels.' + class_name)(channel_settings)
            notifier.add_channel(channel, channel_labels)


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
