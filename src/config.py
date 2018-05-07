import configparser
import os


def get_config():
    script_path = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(script_path, '..')

    config_file = os.path.join(base_path, 'config.ini')
    config = configparser.ConfigParser()
    config.read(config_file)

    return config
