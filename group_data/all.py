import yaml

from config import ConfigFile

with open("config.yml", "r") as fd:
    config_obj = yaml.safe_load(fd)

# Validate
config = ConfigFile(**config_obj)

# Assign
media_device = config.media_device
transmission = config.transmission
