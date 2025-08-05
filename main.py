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

recorder: Recorder
detector: Detector
notifier: Notifier
screener: Screener
logger: logging.Logger


def main():
    global recorder, detector, notifier, screener, logger

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

    recorder = Recorder(config.get_str("rtsp_url"))

    screener_enabled = not config.get_bool("headless")
    net_model_name = config.get_str("net_model_name")
    net = NeuralNetPyTorch(net_model_name)
    notify_min_score = config.get_float("notify_min_score")

    videos_folder = config.get_str("videos_folder")

    detector = Detector(
        images=recorder.get_images(),
        screener_enabled=screener_enabled,
        net=net,
        notify_min_score=notify_min_score,
        encoder_folder=videos_folder,
    )

    notifier = Notifier(detector.get_detections())
    load_channels(config, notifier)

    detector.set_labels(notifier.get_labels())

    logger.info("Threads starting...")
    recorder.start()
    detector.start()
    notifier.start()

    if screener_enabled:
        screener = Screener(detector.get_images())
        screener.show()
        detector.disable_screener()

    logger.info("Threads joining...")
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
    NeuralNetPyTorch("FasterRCNN_MobileNet_V3_Large_FPN")
    NeuralNetPyTorch("FasterRCNN_MobileNet_V3_Large_320_FPN")
    logger.info("Preloading: Done.")


def load_channels(config: Config, notifier: Notifier):

    for channel_name, settings in config.get_dict("notifiers").items():

        # Check if channel is enabled
        enabled = "enabled" in settings and settings.get("enabled")
        logger.debug("Channel: " + channel_name + ", enabled: " + str(enabled))
        if not enabled:
            continue

        # Load channel class and add it to notifier
        class_name = Config.snake_to_camel(channel_name)  # e.g. MyChannel
        channel_config = config.get_dict("notifiers." + channel_name)
        channel = eval("pycatdetector.channels." + class_name)(channel_config)
        notifier.add_channel(
            channel, config.get_list("notifiers." + channel_name + ".objects")
        )

        # Get channel notification window names
        windows = config.get_dict("notifiers." + channel_name + ".notify_window")
        for window, schedule in windows.items():
            notifier.add_notify_window(channel, window, schedule)
            logger.info(
                "Added notify window '"
                + window
                + "' for channel '"
                + channel_name
                + "' for schedule: "
                + json.dumps(schedule)
            )


def enable_logging(config: Config):

    tz = time.strftime("%z")

    # https://docs.python.org/3/howto/logging.html#changing-the-format-of-displayed-messages
    if config.get_str("log_level").upper() == "DEBUG":
        logFormat = "[%(asctime)s " + tz + "] p%(process)s %(threadName)s"
        logFormat += " {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
    else:
        logFormat = "[%(asctime)s " + tz + "] %(levelname)s %(name)s - %(message)s"

    # https://docs.python.org/3/library/logging.html#logging.basicConfig
    logging.basicConfig(
        format=logFormat,
        encoding="utf-8",
        filename=os.path.join(config.get_str("log_dir"), "detector.log"),
        level=eval("logging." + config.get_str("log_level").upper()),
        force=True,
    )
    logging.Formatter.default_msec_format = "%s.%03d"

    # https://pypi.org/project/colorlog/
    if config.get_bool("log_tty"):
        colorHandler = colorlog.StreamHandler()
        colorHandler.setFormatter(
            colorlog.ColoredFormatter("%(log_color)s" + logFormat)
        )
        logging.getLogger().addHandler(colorHandler)
    else:
        logging.StreamHandler(stream=None)


if __name__ == "__main__":
    main()
