"""A module to cache and load program data to and from the disk"""

import json
import pickle
import threading
from io import UnsupportedOperation
from os import makedirs, remove
from os.path import exists, join
from typing import Any

from pyclashbot.utils.platform import get_app_data_dir

MODULE_NAME = "py-clash-bot"

top_level = get_app_data_dir(MODULE_NAME)


class FileCache:
    """a class to cache and load program data to and from the disk"""

    def __init__(self, file_name: str) -> None:
        self.file_name = file_name
        self.mutex = threading.Lock()

    def cache_data(self, data):
        """A method to cache data to the disk using json, merging with existing data"""
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
        """A method to load data from the disk using json"""
        file_path = join(top_level, self.file_name)
        if not exists(file_path):
            return {}
        with self.mutex:
            with open(file_path, encoding="utf-8") as this_file:
                try:
                    return json.load(this_file)
                except (json.JSONDecodeError, UnsupportedOperation):
                    return {}

    def exists(self) -> bool:
        """A method to check if the data file exists"""
        return exists(join(top_level, self.file_name))

    def get(self, key: str, default: Any = None) -> Any:
        """A method to get a value from the data file"""
        return self.load_data().get(key, default)


USER_SETTINGS_CACHE = FileCache("user_settings.json")

# Create a thread-local storage object for the deck cycle cache.
_thread_local = threading.local()


def _get_deck_cache():
    """
    Returns a deck cache dictionary that is local to the current thread.
    If a cache doesn't exist for the thread, it is initialized.
    """
    if not hasattr(_thread_local, "deck_cache"):
        # Initialize the cache for the current thread if it's the first time.
        _thread_local.deck_cache = {}
    return _thread_local.deck_cache


def get_deck_number_for_battle_mode(battle_mode: str) -> int:
    """Get the deck number for a specific battle mode from the thread-local cache."""
    cache = _get_deck_cache()
    return cache.get(battle_mode, 1)


def set_deck_number_for_battle_mode(battle_mode: str, deck_number: int):
    """Set the deck number for a specific battle mode in the thread-local cache."""
    cache = _get_deck_cache()
    cache[battle_mode] = deck_number


### The following section is for supporting the old pickle format for user settings ###


def _load_data_from_pickle(file_name) -> Any | None:
    """A method to load data from the disk using pickle"""
    file_path = join(top_level, file_name)
    if not exists(file_path):
        return None
    with open(file_path, "rb") as this_file:
        try:
            return pickle.load(this_file)
        except pickle.UnpicklingError:
            return None


def check_old_user_settings() -> bool:
    """A method to check if the user settings file exists"""
    return exists(join(top_level, "user_settings.dat"))


def migrate_user_settings() -> None:
    """A method to migrate user settings from the old pickle format to the new json format"""
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
