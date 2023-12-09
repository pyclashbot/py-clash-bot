"""
A module to cache and load program data to and from the disk
"""
from io import UnsupportedOperation
import json
import pickle
from os import makedirs, remove
from os.path import exists, expandvars, join
from typing import Any
import threading


# a module to cache and load program data to and from the disk

MODULE_NAME = "py-clash-bot"

top_level = join(expandvars("%appdata%"), MODULE_NAME)


class FileCache:
    """a class to cache and load program data to and from the disk"""

    def __init__(self, file_name: str) -> None:
        self.file_name = file_name
        self.mutex = threading.Lock()

    def cache_data(self, data):
        """a method to cache data to the disk using json, merging with existing data"""
        file_path = join(top_level, self.file_name)
        if not exists(top_level):
            makedirs(top_level)
        with self.mutex:
            with open(file_path, "w", encoding="utf-8") as this_file:
                try:
                    file_data = json.load(this_file)
                except (json.JSONDecodeError, UnsupportedOperation):
                    file_data = {}
                file_data |= data
                json.dump(file_data, this_file, indent=4)
                return file_data

    def load_data(self):
        """a method to load data from the disk using json"""
        file_path = join(top_level, self.file_name)
        if not exists(file_path):
            return {}
        with self.mutex:
            with open(file_path, "r", encoding="utf-8") as this_file:
                try:
                    return json.load(this_file)
                except (json.JSONDecodeError, UnsupportedOperation):
                    return {}

    def exists(self) -> bool:
        """a method to check if the data file exists"""
        return exists(join(top_level, self.file_name))

    def get(self, key: str, default: Any = None) -> Any:
        """a method to get a value from the data file"""
        return self.load_data().get(key, default)


USER_SETTINGS_CACHE = FileCache("user_settings.json")


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
        USER_SETTINGS_CACHE.cache_data(user_settings)
        # remove the old pickle file
        file_path = join(top_level, "user_settings.dat")
        if exists(file_path):
            remove(file_path)


# when module is imported, if the user settings file exists, migrate it
if check_old_user_settings():
    migrate_user_settings()
