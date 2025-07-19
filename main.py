import os
import sys
import signal
import logging
import time
import colorlog
import pycatdetector.channels
from pycatdetector.Config import Config
from pycatdetector.Recorder import Recorder
from pycatdetector.NeuralNetPyTorch import NeuralNetPyTorch
from pycatdetector.Detector import Detector
from pycatdetector.Notifier import Notifier
from pycatdetector.Screener import Screener

images = recorder = detector = notifier = screener = config = None


def main():
    global images, recorder, detector, notifier, screener, config

    config = Config()

    if len(sys.argv) > 1:
        if "--check-config" in sys.argv:
            print(config.CONFIG_FLAT)
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
    for class_name in pycatdetector.channels.__all__:
        if class_name == "Channels":
            continue
        channel_s = Config.camel_to_snake(class_name)
        if config.get("notifiers_" + channel_s + "_enabled"):
            filtered_config = config.get_prefix("notifiers_" + channel_s)
            channel = \
                eval('pycatdetector.channels.' + class_name)(filtered_config)
            labels = config.get("notifiers_" + channel_s + "_objects")
            notifier.add_channel(channel, labels)


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
