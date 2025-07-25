import yaml
import json
from typing import Any, Optional

class Config:
    """
    The Config class represents a configuration object that loads
    and provides access to configuration settings.

    Attributes:
        _CONFIG (dict): Loaded configuration settings from a YAML file.
    """
    _CONFIG = {}


    def __init__(self, config_file='config.yaml'):
        """
        Initializes a new instance of the Config class.

        Args:
            config_file (str): The path to the configuration file.
                               Default is 'config.yaml'.

        """
        with open(config_file, 'r') as stream:
            self._CONFIG = yaml.safe_load(stream)


    def _get_nested_value(self, keys: list[str]) -> dict:
        """
        Helper method to traverse nested dictionary structure.
        
        Args:
            keys: List of keys representing the path to the value
            
        Returns:
            The value at the specified path
            
        Raises:
            KeyError: If any key in the path is not found
        """
        current = self._CONFIG
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                raise KeyError(f"Key path '{'.'.join(keys)}' not found in configuration.")
            current = current[key]
        return current
    

    def _get(self, name: str) -> Any:
        """
        Retrieves a configuration value by its key.
        Supports dot-separated strings for nested keys.

        Args:
            name: The key of the configuration setting to retrieve
            default: Default value to return if key is not found

        Returns:
            The configuration value or default if not found
        """
        if "." not in name:
            return self._CONFIG[name]
        else:
            keys = name.split('.')
            return self._get_nested_value(keys)


    def get_str(self, name: str) -> str:
        """Get a string configuration value."""
        value = self._get(name)
        if not isinstance(value, str):
            raise TypeError(f"Configuration value '{name}' is not a string")
        return value


    def get_int(self, name: str) -> int:
        """Get an integer configuration value."""
        value = self._get(name)
        if not isinstance(value, int):
            raise TypeError(f"Configuration value '{name}' is not an integer")
        return value


    def get_float(self, name: str) -> float:
        """Get a float configuration value."""
        value = self._get(name)
        if not isinstance(value, (int, float)):
            raise TypeError(f"Configuration value '{name}' is not a number")
        return float(value)


    def get_bool(self, name: str) -> bool:
        """Get a boolean configuration value."""
        value = self._get(name)
        if not isinstance(value, bool):
            raise TypeError(f"Configuration value '{name}' is not a boolean")
        return value


    def get_dict(self, name: Optional[str] = None) -> dict:
        """Get a dictionary configuration value."""
        if name is None:
            return self._CONFIG
        value = self._get(name)
        if not isinstance(value, dict):
            raise TypeError(f"Configuration value '{name}' is not a dictionary")
        return value


    def get_list(self, name: str) -> list:
        """Get a list configuration value."""
        value = self._get(name)
        if not isinstance(value, list):
            raise TypeError(f"Configuration value '{name}' is not a list")
        return value
    

    def has_key(self, name: str) -> bool:
        """Check if a configuration key exists."""
        try:
            self._get(name)
            return True
        except KeyError:
            return False


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
