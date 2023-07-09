import pickle
from os import makedirs
from os.path import exists, expandvars, join
from typing import Any

# a module to cache and load program data to and from the disk

MODULE_NAME = "py-clash-bot"

top_level = join(expandvars("%appdata%"), MODULE_NAME)


def _cache_data(data, file_name) -> None:
    # a method to cache data to the disk using pickle
    file_path = join(top_level, file_name)
    if not exists(top_level):
        makedirs(top_level)
    with open(file_path, "wb") as this_file:
        pickle.dump(data, this_file)


def _load_data(file_name) -> Any | None:
    # a method to load data from the disk using pickle
    file_path = join(top_level, file_name)
    if not exists(file_path):
        return None
    with open(file_path, "rb") as this_file:
        try:
            return pickle.load(this_file)
        except pickle.UnpicklingError:
            return None


def cache_user_settings(data: dict[str, Any] | None) -> None:
    # a method to cache user settings to the disk
    _cache_data(data, "user_settings.dat")


def read_user_settings() -> dict[str, Any] | None:
    # a method to read user settings from the disk
    return _load_data("user_settings.dat")


def check_user_settings() -> bool:
    # a method to check if the user settings file exists
    return exists(join(top_level, "user_settings.dat"))
