import logging
from datetime import datetime
from requests import post


class DiscordWebhook:

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def get_name(self):
        return self.__class__.__name__

    # https://support.discord.com/hc/en-us/articles/228383668
    # https://discord.com/developers/docs/resources/webhook
    def notify(self):
        url = self.config["url"]
        content = self.config["content"]
        headers = {
            "content-type": "application/json",
        }
        data = {
            "wait": "true",
            "content": str(datetime.now()) + ' - ' + content,
        }
        self.logger.info("Request: " + str(data))
        response = post(url, headers=headers, json=data)
        self.logger.info("Response: " + response.text)
