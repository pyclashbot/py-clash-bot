"""
A module to cache and load program data to and from the disk
"""
import json
import pickle
from os import makedirs, remove
from os.path import exists, expandvars, join
from typing import Any

# a module to cache and load program data to and from the disk

MODULE_NAME = "py-clash-bot"

top_level = join(expandvars("%appdata%"), MODULE_NAME)


def _cache_data(data, file_name) -> None:
    """a method to cache data to the disk using json"""
    file_path = join(top_level, file_name)
    if not exists(top_level):
        makedirs(top_level)
    with open(file_path, "w", encoding="utf-8") as this_file:
        json.dump(data, this_file)


def _load_data(file_name) -> dict[str, Any]:
    """a method to load data from the disk using json"""
    file_path = join(top_level, file_name)
    if not exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as this_file:
        try:
            return json.load(this_file)
        except json.JSONDecodeError:
            return {}


def cache_user_settings(data: dict[str, Any] | None) -> None:
    """a method to cache user settings to the disk"""
    _cache_data(data, "user_settings.json")


def read_user_settings() -> dict[str, Any]:
    """a method to read user settings from the disk"""
    return _load_data("user_settings.json")


def check_user_settings() -> bool:
    """a method to check if the user settings file exists"""
    return exists(join(top_level, "user_settings.json"))


### The following section is for supporting the old pickle format for user settings ###


def _load_data_from_pickle(file_name) -> Any | None:
    """a method to load data from the disk using pickle"""
    file_path = join(top_level, file_name)
    if not exists(file_path):
        return None
    with open(file_path, "rb") as this_file:
        try:
            return pickle.load(this_file)
        except pickle.UnpicklingError:
            return None


def check_old_user_settings() -> bool:
    """a method to check if the user settings file exists"""
    return exists(join(top_level, "user_settings.dat"))


def migrate_user_settings() -> None:
    """a method to migrate user settings from the old pickle format to the new json format"""
    user_settings = _load_data_from_pickle("user_settings.dat")
    if user_settings is not None:
        cache_user_settings(user_settings)
        # remove the old pickle file
        file_path = join(top_level, "user_settings.dat")
        if exists(file_path):
            remove(file_path)


# when module is imported, if the user settings file exists, migrate it
if check_old_user_settings():
    migrate_user_settings()
