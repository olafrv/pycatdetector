import logging
from datetime import datetime
from requests import post

class DiscordWebhook:
    config = {}

    def __init__(self, config):
        self.config = config

    def get_name(self):
        return self.__class__.__name__

    # https://support.discord.com/hc/en-us/articles/228383668
    # https://discord.com/developers/docs/resources/webhook
    def notify(self):
        headers = {
            "content-type": "application/json",
        }
        data = {
            "wait": "true",
            "content": str(datetime.now()) + ' - ' + self.config["content"],
        }
        logging.debug(data)
        response = post(self.config["url"], headers=headers, json=data)
        logging.debug(response.text)