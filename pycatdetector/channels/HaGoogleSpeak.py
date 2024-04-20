import logging
from requests import post, get


class HaGoogleSpeak:
    """
    A class that provides functionality to speak a text message
    using Google Translate TTS and Google Cast.

     HomeAssitant - API:
     - https://developers.home-assistant.io/docs/api/rest/
    
     Google Translate: Text to MP3 served by Google Translate
     - https://www.home-assistant.io/integrations/google_translate/
    
     Text to Speech (TTS): Play Audio File into Google Castable Device
     - https://www.home-assistant.io/integrations/tts/#service-speak
    
     FAQ:
     - https://community.home-assistant.io/t/rest-api-service-calls-specify-target/537269  # noqa

    Args:
        config (dict): A dictionary containing the configuration parameters.

    Attributes:
        config (dict): A dictionary containing the configuration parameters.
        logger (logging.Logger): The logger object for logging messages.

    """

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.headers = {
            "Authorization": "Bearer " + self.config["token"],
            "Content-Type": "application/json",
        }
        self.entity_id = self.config["entity_id"]
        self.media_player_entity_id = self.config["media_player_entity_id"]
        self.volume_level = self.config["volume_level"]
        self.message = self.config["message"]

    def get_name(self):
        """
        Get the name of the class.

        Returns:
            str: The name of the class.

        """
        return self.__class__.__name__

    def call_api(self, url, method, headers={}, data={}):

        if method == "post":
            self.logger.info("POST: %s" % url)
            self.logger.debug("DATA: %s" % repr(data))
            response = post(url, headers=headers, json=data)
        elif method == "get":
            self.logger.info("GET: %s" % url)
            response = get(url, headers=headers)
        else:
            raise ValueError("Invalid HTTP method '%s'" % method)

        self.logger.debug("Response: " + response.text)

        return response

    def get_volume(self) -> float:
        url = self.config["url"] + "/api/states/" + self.media_player_entity_id
        response = self.call_api(url, "get", headers=self.headers)
        if not response.ok:
            self.logger.error("Failed to get volume level: " + response.text)
            return None
        else:
            return response.json()["attributes"]["volume_level"]

    def set_volume(self, volume_level) -> bool:
        url = self.config["url"] + "/api/services/media_player/volume_set"
        data = {
            "entity_id": self.media_player_entity_id,
            "volume_level": volume_level,
        }
        response = self.call_api(url, "post", headers=self.headers, data=data)
        if not response.ok:
            self.logger.error("Failed to set volume level: " + response.text)
            return False
        else:
            self.logger.info("Response: " + response.text)
            return True

    def speak(self, message) -> bool:
        url = self.config["url"] + "/api/services/tts/speak"
        data = {
            # HomeAssitant => Settings => Devices & Services
            # => Integrations => Google Translate TTS
            "entity_id": self.entity_id,
            # => Integrations => Google Cast
            "media_player_entity_id": self.media_player_entity_id,
            # Text message to be spoken
            "message": message
        }
        response = self.call_api(url, "post", headers=self.headers, data=data)
        if not response.ok:
            self.logger.error("Failed to speak: %s" % response.text)
            return False
        else:
            self.logger.info("Spoken '%s' sucessfully." % message)
            return True

    def notify(self, custom_message=None):
        """
        Send a notification by setting the volume and speaking a text message.
        """
        current_volume = self.get_volume()  # Save the current volume
        self.set_volume(self.volume_level)  # Set the volume to desired level

        notified = False
        if custom_message is not None:
            notified = self.speak(custom_message)  # Speak the custom message
        else:
            notified = self.speak(self.message)  # Speak the default message

        if current_volume is not None:
            self.set_volume(current_volume)  # Restore the volume

        return notified
