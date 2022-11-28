import logging
from requests import post

class HaGoogleSay:
    config = {}

    def __init__(self, config):
        self.config = config

    def get_name(self):
        return self.__class__.__name__

    # https://developers.home-assistant.io/docs/api/rest/
    def notify(self, url, token, entity, message, language):
        headers = {
            "Authorization": "Bearer " + token,
            "content-type": "application/json",
        }
        data = {
            "entity_id": entity,
            "message": message,
            "language": language
        }
        logging.debug(data)
        response = post(url, headers=headers, json=data)
        logging.debug(response.text)