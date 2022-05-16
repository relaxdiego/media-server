import yaml

from config import ConfigFile

with open("config.yml", "r") as fd:
    config_obj = yaml.safe_load(fd)

# Parse and validate the config file
config = ConfigFile(**config_obj)

# Assign
media_servers = [config.host]
