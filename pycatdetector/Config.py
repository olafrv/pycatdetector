import os
import re
import json
import logging
import colorlog

class Config:
    config = None
    
    def __init__(self, config_file = 'config.json'):
        config_file = open(config_file)
        self.config = json.load(config_file)
        self.enable_logging()

    def get_regex(self, regex):
        config = {}
        for key in self.config:
            if re.match(regex, key):
                config[key] = self.config[key]    
        return config

    def enable_logging(self):
        # https://docs.python.org/3/howto/logging.html
        if self.config.get("LOG_LEVEL").upper() == "DEBUG":
            logFormat = "[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'"
        else:
            logFormat = '[%(asctime)s] %(levelname)s %(name)s - %(message)s'
        logging.basicConfig(format=logFormat, encoding='utf-8', 
            filename = os.path.join(self.get("LOG_DIR"), 'detector.log'), 
                level=eval('logging.' + self.config.get("LOG_LEVEL").upper()))
        # https://pypi.org/project/colorlog/
        if self.config.get("LOG_TTY").lower() == "yes":
            colorHandler = colorlog.StreamHandler()
            colorHandler.setFormatter(colorlog.ColoredFormatter('%(log_color)s' + logFormat))
            logging.getLogger().addHandler(colorHandler)
        
        # Uncomment to test logging handlers an levels
        # logging.debug("Logging Test");
        # logging.info("Logging Test");
        # logging.warning("Logging Test");
        # logging.error("Logging Test");
        # logging.critical("Logging Test");

    def get(self, name) -> dict:
        return self.config[name]

    def __str__(self) -> str:
        return json.dumps(self.config)