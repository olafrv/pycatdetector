import os
import sys
import signal
import logging
import time
import colorlog
import pycatdetector.channels
from pycatdetector.Config import Config
from pycatdetector.Recorder import Recorder
from pycatdetector.NeuralNet import NeuralNet
from pycatdetector.Detector import Detector
from pycatdetector.Notifier import Notifier
from pycatdetector.Screener import Screener

images = recorder = detector = notifier = screener = config = None


def main():
    global images, recorder, detector, notifier, screener, config

    config = Config()

    if len(sys.argv) > 1:
        if "--check-config" in sys.argv:
            print(config.config_flat)
            exit(0)

    enable_logging(config)
    logger = logging.getLogger(__name__)
    logger.info("PATH: " + os.environ["PATH"])
    logger.info("Python Sys Prefix: " + sys.prefix)

    signal.signal(signal.SIGINT, handler)

    recorder = Recorder(config.get("rtsp_url"))

    screener_enabled = not config.get("headless")
    net_model_name = config.get("net_model_name")
    net = NeuralNet(model_name=net_model_name)

    net_min_score = config.get("net_min_score")
    detector = Detector(recorder, screener_enabled, net, net_min_score)

    notifier = Notifier(detector)
    attach_channels(notifier)

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
        notifier.stop()
        recorder.stop()
        detector.stop()


def attach_channels(notifier):
    global config
    for channel_class_name in pycatdetector.channels.__all__:
        channel_s = Config.camel_to_snake(channel_class_name)
        if config.get("notifiers_" + channel_s + "_enabled"):
            notifier.add_channel(
                eval(
                    'pycatdetector.channels.' +
                    channel_class_name)(config.get_prefix(
                            "notifiers_" + channel_s
                    )
                ),
                config.get("notifiers_" + channel_s + "_objects"))


def enable_logging(config):
    tz = time.strftime('%z')
    # https://docs.python.org/3/howto/logging.html
    if config.get("log_level").upper() == "DEBUG":
        logFormat = '[%(asctime)s ' + tz + '] p%(process)s %(threadName)s'
        logFormat += ' {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
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
