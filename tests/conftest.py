import pytest
import yaml

from config import ConfigFile


@pytest.fixture(scope="session")
def config():
    with open("config.yml", "r") as fd:
        config_obj = yaml.safe_load(fd)

    return ConfigFile(**config_obj)
