from os import path
import sys
import configparser


def resource_path(relative_path, persistent=False):
    """
    Get the resource path
    """
    base_path = path.abspath(".")
    total_path = path.join(base_path, relative_path)
    if persistent or path.exists(total_path):
        return total_path
    else:
        try:
            base_path = sys._MEIPASS
            return path.join(base_path, relative_path)
        except Exception:
            return total_path


def get_config():
    """
    Get the config
    """
    config_parser = configparser.ConfigParser()
    user_config_path = resource_path("config/user_config.ini")
    default_config_path = resource_path("config/config.ini")

    config_files = [user_config_path, default_config_path]
    for config_file in config_files:
        if path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                config_parser.read_file(f)
            break

    return config_parser


config = get_config()
