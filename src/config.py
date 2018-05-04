import configparser
import os


def get_config():
    script_path = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join('..', script_path)

    config_file = os.path.join(base_path, 'config.ini')
    config = configparser.ConfigParser().read(config_file)

    config['common']['script_path'] %= {'base_path': base_path}
    config['common']['util_path'] %= {'base_path': base_path}
    config['common']['word2vec_bin'] %= {'base_path': base_path}
    config['common']['convertvec_bin'] %= {'base_path': base_path}

    return config
