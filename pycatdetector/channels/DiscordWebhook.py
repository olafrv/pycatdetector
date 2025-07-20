import logging
from datetime import datetime
from typing import Optional
from discord_webhook import DiscordWebhook as discord_webhook
from .AbstractChannel import AbstractChannel  # Import the abstract base class


class DiscordWebhook(AbstractChannel):
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
        self.logger = logging.getLogger(__name__)
        self.url = config.get("url")
        self.message = config.get("message")

    def get_name(self):
        """
        Returns the name of the class.

        Returns:
            str: The name of the class.
        """
        return self.__class__.__name__

    def notify(self, custom_content: Optional[dict] = None) -> bool:
        """
        Sends a notification to the Discord webhook with optional image.
        """
        if custom_content and "message" in custom_content:
            content = custom_content["message"]
        else:
            content = self.message  # Fallback to default message
        
        content = str(datetime.now()) + ' - ' + content

        webhook = discord_webhook(url=self.url, content=content)

        if custom_content \
            and "image_data" in custom_content \
            and "image_name" in custom_content:
            
            image_data = custom_content["image_data"]
            image_name = custom_content["image_name"]
            
            webhook.add_file(file=image_data, filename=image_name)
            
            self.logger.info(
                "Request: URL:"  + self.url + ", Message: " + content
                    + ", Image: " + image_name)
        else:
            self.logger.info(
                "Request: URL:"  + self.url + ", Message: " + content
                    + ", Image: None")   
        
        response = webhook.execute()
        self.logger.info("Response: " + repr(response))     

        return response.ok
