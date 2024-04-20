import logging
from requests import post


class HaGoogleSay:
    """
    A class that represents the Home Assistant Google Say channel (deprecated).

    HomeAssitant - Text To Speech (TTS):
    - https://www.home-assistant.io/integrations/tts
    HomeAssitant - API:
     - https://developers.home-assistant.io/docs/api/rest/
    HomeAssitant - TTS Integration Configuration (configuration.yaml):
        (...)
        tts:
        - platform: google_translate
        cache: true
        cache_dir: /tmp/tts
        time_memory: 300
        service_name: google_translate_say
        (...)

    Attributes:
        config (dict): A dictionary containing the configuration parameters.
        logger (logging.Logger): The logger object for logging messages.

    Methods:
        get_name(): Returns the name of the class.
        notify(): Sends a TTS notification using the Google Translate service.
    """

    def __init__(self, config):
        """
        Initializes a new instance of the HaGoogleSay class.

        Args:
            config (dict): A dictionary containing the configuration params.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.logger.warn(
            "HaGoogleSay is deprecated, use HaGoogleSpeak instead."
        )

    def get_name(self):
        """
        Returns the name of the class.

        Returns:
            str: The name of the class.
        """
        return self.__class__.__name__

    def notify(self):
        """
        Sends a TTS notification using the Google Translate service.
        """
        url = self.config["url"]
        url = url + "/services/tts/google_translate_say"
        token = self.config["token"]
        entity = self.config["entity"]
        message = self.config["message"]
        language = self.config["language"]
        headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
        }
        data = {
            "entity_id": entity,
            "message": message,
            "language": language
        }
        self.logger.info("Request: " + str(data))
        response = post(url, headers=headers, json=data)
        self.logger.info("Response: " + response.text)
