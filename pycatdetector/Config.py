import re
import yaml
import json
from typing import Optional


class Config:
    """
    The Config class represents a configuration object that loads
    and provides access to configuration settings.

    Attributes:
        _CONFIG (dict): Loaded configuration settings (i.e. key1.key2).
        _CONFIG_FLAT (dict): Flattened configuration settings (i.e. key1_key2).

    """
    _CONFIG = {}
    _CONFIG_FLAT = {}

    def __init__(self, config_file='config.yaml'):
        """
        Initializes a new instance of the Config class.

        Args:
            config_file (str): The path to the configuration file.
                               Default is 'config.yaml'.

        """
        with open(config_file, 'r') as stream:
            self._CONFIG = yaml.safe_load(stream)

        self._CONFIG_FLAT = self._flatten(self._CONFIG)

    def _flatten(self, config={}, separator="_"):
        """
        Flattens a nested dictionary into a flat dictionary.

        Args:
            config (dict): The nested dictionary to be flattened.
                           Default is an empty dictionary.
            separator (str): The separator to be used for the flattened keys.
                             Default is '_'.

        Returns:
            dict: The flattened dictionary.

        """
        flattened_config = {}
        for key in config:
            value = config[key]
            if isinstance(value, dict):
                recursive_config = self._flatten(value)
                for rkey in recursive_config:
                    rvalue = recursive_config[rkey]
                    flattened_config[key + separator + str(rkey)] = rvalue
            else:
                flattened_config[key] = value
        return flattened_config

    def get(self, name: str) -> str:
        """
        Retrieves a specific configuration setting by its key.

        Args:
            name (str): The key of the configuration setting to retrieve.

        Returns:
            str: The configuration setting value.

        """
        return self._CONFIG_FLAT[name]

    def get_all(self) -> dict:
        """
        Retrieves all configuration settings.

        Returns:
            dict: A dictionary containing all configuration settings.

        """
        return self._CONFIG_FLAT

    def get_regex(self, regex: str) -> dict:
        """
        Retrieves configuration settings that match a given regular expression.

        Args:
            regex (str): Regexp pattern to match against configuration keys.

        Returns:
            dict: A dictionary containing the matching configuration settings.

        """
        config = {}
        for key in self._CONFIG_FLAT:
            if re.match(regex, key):
                config[key] = self._CONFIG_FLAT[key]
        return config

    def get_prefix(self, prefix="", ltrim=True):
        """
        Retrieves configuration settings that have a given prefix.

        Args:
            prefix (str): The prefix to match against the configuration keys.
                          Default is an empty string, which matches all keys.
            ltrim (bool): Specifies whether to remove the prefix from the
                          returned keys. Default is True.

        Returns:
            dict: A dictionary containing the matching configuration settings.

        """
        filtered_config = {}
        for key in self._CONFIG_FLAT:
            if re.match("^"+prefix+"_", key):
                if ltrim:
                    ltrim_key = str(key).replace(prefix+"_", '', 1)
                    filtered_config[ltrim_key] = self._CONFIG_FLAT[key]
                else:
                    filtered_config[key] = self._CONFIG_FLAT[key]
        return filtered_config

    @classmethod
    def camel_to_snake(cls, s: str) -> str:
        """
        Converts a camel case string to snake case.

        Args:
            s (str): The camel case string to convert.

        Returns:
            str: The snake case string.

        """
        return ''.join([
                        '_' +
                        c.lower() if c.isupper() else c for c in s
                      ]).lstrip('_')

    @classmethod
    def snake_to_camel(cls, s: str) -> str:
        """
        Converts a snake_case string to CamelCase.

        Args:
            s (str): The snake_case string to convert.

        Returns:
            str: The CamelCase string.
        """
        return ''.join(word.capitalize() for word in s.split('_'))

    def to_json(self) -> str:
        """
        Converts the configuration settings to a JSON string.

        Returns:
            str: The JSON string representation of the configuration settings.

        """
        return json.dumps(self._CONFIG, indent=2)

    def __str__(self) -> str:
        """
        Returns a string representation of the Config instance.

        Returns:
            str: The string representation of the Config instance.

        """
        return yaml.dump(self._CONFIG)
