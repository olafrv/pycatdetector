import os
import sys
import signal
import logging
import colorlog
from pycatdetector import *
from pycatdetector.channels import *

images = recorder = detector = notifier = screener = None

def main():
    global images, recorder, detector, notifier, screener
    
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
    detector = Detector(recorder, NeuralNet())

    notifier = Notifier(detector)
    if config.get("notifiers_ha_google_say_enabled"): 
        notifier.add_channel(
            HAGoogleSay(config.get_prefix("notifiers_ha_google_say")),
            config.get("notifiers_ha_google_say_objects")
        )
    if config.get("notifiers_discord_webhook_enabled"): 
        notifier.add_channel(
            DiscordWebhook(config.get_prefix("notifiers_discord_webhook")),
            config.get("notifiers_discord_webhook_objects")
        )

    recorder.start()
    detector.start()
    notifier.start()

    if not config.get("headless"):
        screener = Screener(detector)
        screener.show()

    notifier.join()
    recorder.join()
    detector.join()

def handler(signum, frame):
    global recorder, detector, notifier, screener
    if not screener is None:
        screener.close()
    notifier.stop()
    recorder.stop()
    detector.stop()

def enable_logging(config):
    # https://docs.python.org/3/howto/logging.html
    if config.get("log_level").upper() == "DEBUG":
        logFormat = "[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'"
    else:
        logFormat = '[%(asctime)s] %(levelname)s %(name)s - %(message)s'
    
    logging.basicConfig(format=logFormat, encoding='utf-8', 
        filename = os.path.join(config.get("log_dir"), 'detector.log'), 
            level=eval('logging.' + config.get("log_level").upper()))
    
    # https://pypi.org/project/colorlog/
    if config.get("log_tty"):
        colorHandler = colorlog.StreamHandler()
        colorHandler.setFormatter(colorlog.ColoredFormatter('%(log_color)s' + logFormat))
        logging.getLogger().addHandler(colorHandler)
    
    # logging.debug("Logging Test");
    # logging.info("Logging Test");
    # logging.warning("Logging Test");
    # logging.error("Logging Test");
    # logging.critical("Logging Test");

if __name__ == '__main__':
    main()