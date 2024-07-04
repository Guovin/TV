from os import path
from sys import _MEIPASS, executable
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
            base_path = _MEIPASS
            return path.join(base_path, relative_path)
        except Exception:
            return total_path


def load_external_config(name):
    """
    Load the external config file
    """
    config = None
    config_path = name
    config_filename = path.join(path.dirname(executable), config_path)

    if path.exists(config_filename):
        spec = util.spec_from_file_location(name, config_filename)
        config = util.module_from_spec(spec)
        spec.loader.exec_module(config)
    else:
        import config

    return config


def get_config():
    """
    Get the config
    """
    config_path = resource_path("user_config.py")
    config = (
        load_external_config("user_config.py")
        if path.exists(config_path)
        else load_external_config("config.py")
    )
    return config
