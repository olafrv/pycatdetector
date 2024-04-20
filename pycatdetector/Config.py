import re
import yaml


class Config:
    """
    The Config class represents a configuration object that loads
    and provides access to configuration settings.

    Attributes:
        CONFIG (dict): Loaded configuration settings (i.e. key1.key2).
        CONFIG_FLAT (dict): Flattened configuration settings (i.e. key1_key2).

    """

    def __init__(self, config_file='config.yaml'):
        """
        Initializes a new instance of the Config class.

        Args:
            config_file (str): The path to the configuration file.
                               Default is 'config.yaml'.

        """
        with open(config_file, 'r') as stream:
            self.CONFIG = yaml.safe_load(stream)

        self.CONFIG_FLAT = self.flatten(self.CONFIG)

    def flatten(self, config={}, separator="_"):
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
                recursive_config = self.flatten(value)
                for rkey in recursive_config:
                    rvalue = recursive_config[rkey]
                    flattened_config[key + separator + str(rkey)] = rvalue
            else:
                flattened_config[key] = value
        return flattened_config

    def get_regex(self, regex):
        """
        Retrieves configuration settings that match a given regular expression.

        Args:
            regex (str): Regexp pattern to match against configuration keys.

        Returns:
            dict: A dictionary containing the matching configuration settings.

        """
        config = {}
        for key in self.CONFIG_FLAT:
            if re.match(regex, key):
                config[key] = self.CONFIG_FLAT[key]
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
        for key in self.CONFIG_FLAT:
            if re.match("^"+prefix+"_", key):
                if ltrim:
                    ltrim_key = str(key).replace(prefix+"_", '', 1)
                    filtered_config[ltrim_key] = self.CONFIG_FLAT[key]
                else:
                    filtered_config[key] = self.CONFIG[key]
        return filtered_config

    def get(self, name) -> dict:
        """
        Retrieves a specific configuration setting by its key.

        Args:
            name (str): The key of the configuration setting to retrieve.

        Returns:
            dict: The configuration setting.

        """
        return self.CONFIG_FLAT[name]

    def get_assoc(self, key) -> dict:
        """
        Retrieves a nested configuration setting by its key.

        Args:
            key (str): The key of the nested configuration setting to retrieve.

        Returns:
            dict: The nested configuration setting.

        """
        return self.CONFIG[key]

    def camel_to_snake(s):
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

    def __str__(self) -> str:
        """
        Returns a string representation of the Config instance.

        Returns:
            str: The string representation of the Config instance.

        """
        return yaml.dump(self.CONFIG)
