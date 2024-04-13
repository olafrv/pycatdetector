import logging
from requests import post

# HomeAssitant
# * Text To Speech (TTS):
#   https://www.home-assistant.io/integrations/tts
# * API:
#   https://developers.home-assistant.io/docs/api/rest/
# * TTS Integration Configuration (configuration.yaml)
# <<<
# tts:
#   - platform: google_translate
#     cache: true
#     cache_dir: /tmp/tts
#     time_memory: 300
#     service_name: google_translate_say
# >>>


class HaGoogleSay:
    config = {}

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def get_name(self):
        return self.__class__.__name__

    def notify(self):
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
