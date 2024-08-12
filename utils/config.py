from os import path
import sys

# from importlib import util
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


# def load_external_config(config_path):
#     """
#     Load the external config file
#     """
#     config = None
#     if path.exists(config_path):
#         spec = util.spec_from_file_location("config", config_path)
#         config = util.module_from_spec(spec)
#         spec.loader.exec_module(config)
#     else:
#         import config.config as config
#     return config


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
