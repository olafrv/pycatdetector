import re
import yaml


class Config:
    config = None
    config_flat = None

    def __init__(self, config_file='config.yaml'):
        with open(config_file, 'r') as stream:
            self.config = yaml.safe_load(stream)
        self.config_flat = self.flatten(self.config)

    def flatten(cls, config={}, separator="_"):
        flattened_config = {}
        for key in config:
            value = config[key]
            if isinstance(value, dict):
                recursive_config = cls.flatten(value)
                for rkey in recursive_config:
                    rvalue = recursive_config[rkey]
                    flattened_config[key + separator + str(rkey)] = rvalue
            else:
                flattened_config[key] = value
        return flattened_config

    def get_regex(self, regex):
        config = {}
        for key in self.config_flat:
            if re.match(regex, key):
                config[key] = self.config_flat[key]
        return config

    def get_prefix(self, prefix="", ltrim=True):
        config = {}
        for key in self.config_flat:
            if re.match("^"+prefix+"_", key):
                if ltrim:
                    ltrim_key = str(key).replace(prefix+"_", '', 1)
                    config[ltrim_key] = self.config_flat[key]
                else:
                    config[key] = self.config[key]
        return config

    def get(self, name) -> dict:
        return self.config_flat[name]

    def get_assoc(self, key) -> dict:
        return self.config[key]

    def camel_to_snake(s):
        return ''.join([
                        '_' +
                        c.lower() if c.isupper() else c for c in s
                      ]).lstrip('_')

    def __str__(self) -> str:
        return yaml.dump(self.config)
