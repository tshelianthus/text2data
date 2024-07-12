import yaml
import logging

def parse_config(config_file):
    # Read the configuration file
    with open(config_file, "r") as config_file:
        try:
            config = yaml.safe_load(config_file)
            return config
        except yaml.YAMLError as e:
            logging.error(f"YAMLError. Error: {e}")
            raise


class Config:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = parse_config(config_file)

    def __getitem__(self, key):
        return self.config.get(key)