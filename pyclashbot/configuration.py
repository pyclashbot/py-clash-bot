import json
import sys
from os import makedirs
from os.path import exists, expandvars, isdir, join
from typing import Any

top_level = join(expandvars('%appdata%'), "py-ClashBot")
config_file = join(top_level, 'config.json')

default_config = {
}


def validate_keys(user_config: dict[str, Any]) -> dict[str, Any]:
    # check keys in user_config
    default_keys = set(default_config)
    user_keys = set(user_config)

    if default_keys == user_keys:
        return user_config

    print("WARNING: Invalid keys in user config. Overwriting invalid keys with defaults")
    invalid_keys = user_keys - default_keys
    for key in invalid_keys:  # delete invalid keys
        del user_config[key]

    missing_keys = default_keys - user_keys
    for key in missing_keys:  # overwrite missing keys
        user_config[key] = default_config[key]

    write_config_file(user_config)
    return user_config


def validate_types(user_config: dict[str, Any]) -> dict[str, Any]:
    # check value types in user_config
    user_keys = set(user_config)
    for key in user_keys:
        # overwrite with defualt if types are not the same
        if not isinstance(user_config[key], type(default_config[key])):
            print(
                "WARNING: Invalid values in user config. Overwriting invalid values with defaults")
            user_config[key] = default_config[key]

    write_config_file(user_config)
    return user_config


def validate_user_config(user_config: dict[str, Any]) -> dict[str, Any]:
    return validate_types(validate_keys(user_config))


def load_user_config() -> dict[str, Any]:
    try:
        return validate_user_config(json.load(open(config_file, 'r')))
    except json.JSONDecodeError:
        print("User config file could not be loaded, is it misconfigured?")
        sys.exit()
    except OSError:
        print("Could not find config file, creating one now")
        create_config_file()
        return load_user_config()


def create_config_file() -> None:
    if not isdir(top_level):
        makedirs(top_level)
    if not exists(config_file):
        write_config_file(default_config)
        print("Created config file for the bot @ appdata/py-ClashBot/")
        print("Since this is the first time you are running the bot, please edit the config file then restart the bot.")


def write_config_file(config) -> None:
    with open(config_file, "w") as f:
        f.write(json.dumps(config, indent=4))


create_config_file()


if __name__ == "__main__":
    print(load_user_config())
