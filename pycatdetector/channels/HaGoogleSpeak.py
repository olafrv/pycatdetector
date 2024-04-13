import logging
from requests import post

###
# HomeAssitant - API:
# - https://developers.home-assistant.io/docs/api/rest/
#
# Google Translate: Text to MP3 served by Google Translate
# - https://www.home-assistant.io/integrations/google_translate/
#
# Text to Speech (TTS): Play Audio File into Google Castable Device
# - https://www.home-assistant.io/integrations/tts/#service-speak
#
# FAQ:
# - https://community.home-assistant.io/t/rest-api-service-calls-specify-target/537269  # noqa
##


class HaGoogleSpeak:
    config = {}

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def get_name(self):
        return self.__class__.__name__

    def notify(self):
        token = self.config["token"]
        entity_id = self.config["entity_id"]
        media_player_entity_id = self.config["media_player_entity_id"]
        volume_level = self.config["volume_level"]
        message = self.config["message"]

        headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
        }

        # Set Volume
        url = self.config["url"] + "/api/services/media_player/volume_set"
        data = {
            "entity_id": media_player_entity_id,
            "volume_level": volume_level,
        }
        self.logger.info("Request: " + str(data))
        response = post(url, headers=headers, json=data)
        self.logger.info("Response: " + response.text)

        # Speak
        url = self.config["url"] + "/api/services/tts/speak"
        data = {
            # HomeAssitant => Settings => Devices & Services
            # => Integrations => Google Translate TTS
            "entity_id": entity_id,
            # => Integrations => Google Cast
            "media_player_entity_id": media_player_entity_id,
            # Text message to be spoken
            "message": message
        }
        self.logger.info("Request: " + str(data))
        response = post(url, headers=headers, json=data)
        self.logger.info("Response: " + response.text)
