import os
import sys
import configparser
import shutil


def resource_path(relative_path, persistent=False):
    """
    Get the resource path
    """
    base_path = os.path.abspath(".")
    total_path = os.path.join(base_path, relative_path)
    if persistent or os.path.exists(total_path):
        return total_path
    else:
        try:
            base_path = sys._MEIPASS
            return os.path.join(base_path, relative_path)
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
        if os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                config_parser.read_file(f)
            break

    return config_parser


config = get_config()


def save_config():
    """
    Save config with write
    """
    user_config_file = "config/" + (
        "user_config.ini"
        if os.path.exists(resource_path("user_config.ini"))
        else "config.ini"
    )
    user_config_path = resource_path(user_config_file, persistent=True)
    if not os.path.exists(user_config_path):
        os.makedirs(os.path.dirname(user_config_path), exist_ok=True)
    with open(user_config_path, "w", encoding="utf-8") as configfile:
        config.write(configfile)


def copy_config():
    user_source_file = resource_path(config.get("Settings", "source_file"))
    user_config_path = resource_path("config/user_config.ini")
    default_config_path = resource_path("config/config.ini")
    user_config_file = (
        user_config_path if os.path.exists(user_config_path) else default_config_path
    )
    dest_folder = os.path.join(os.getcwd(), "config")
    files_to_copy = [user_source_file, user_config_file]
    try:
        for src_file in files_to_copy:
            dest_path = os.path.join(dest_folder, os.path.basename(src_file))
            if os.path.abspath(src_file) == os.path.abspath(dest_path):
                continue
            shutil.copy(src_file, dest_folder)
    except Exception as e:
        print(f"Failed to copy files: {str(e)}")
