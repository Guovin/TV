from os import path
import sys
from importlib import util


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


def load_external_config(config_path):
    """
    Load the external config file
    """
    config = None
    if path.exists(config_path):
        spec = util.spec_from_file_location("config", config_path)
        config = util.module_from_spec(spec)
        spec.loader.exec_module(config)
    else:
        import config
    return config


def get_config():
    """
    Get the config
    """
    user_config_path = resource_path("user_config.py")
    default_config_path = resource_path("config.py")
    config = (
        load_external_config(user_config_path)
        if path.exists(user_config_path)
        else load_external_config(default_config_path)
    )
    return config
