import logging
from requests import post

class HAGoogleSay:
    config = {}

    def __init__(self, config):
        self.config = config

    def get_name(self):
        return "HAGoogleSay"

    def notify(self):
        # https://developers.home-assistant.io/docs/api/rest/
        headers = {
            "Authorization": "Bearer " + self.config["HOMEASSISTANT_TOKEN"],
            "content-type": "application/json",
        }
        url = self.config["HOMEASSISTANT_URL"] + '/services/tts/google_translate_say'
        data = {
            "entity_id": self.config["HOMEASSISTANT_ENTITY"],
            "message": self.config["HOMEASSISTANT_MESSAGE"],
            "language": self.config["HOMEASSISTANT_LANGUAGE"]
        }
        logging.info(data)
        response = post(url, headers=headers, json=data)
        logging.info(response.text)