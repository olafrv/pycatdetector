import logging
from datetime import datetime
from requests import post


class DiscordWebhook:
    """
    A class representing a Discord webhook:
    - https://support.discord.com/hc/en-us/articles/228383668
    - https://discord.com/developers/docs/resources/webhook

    Attributes:
        config (dict): A dictionary containing the webhook configuration.
        logger (logging.Logger): A logger object for logging messages.
    """

    def __init__(self, config):
        """
        Initializes a DiscordWebhook object.

        Args:
            config (dict): A dictionary containing the webhook configuration.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

    def get_name(self):
        """
        Returns the name of the class.

        Returns:
            str: The name of the class.
        """
        return self.__class__.__name__

    def notify(self):
        """
        Sends a notification to the Discord webhook.
        """
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
