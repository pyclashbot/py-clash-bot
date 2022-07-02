import json
import sys
from os import makedirs
from os.path import exists, expandvars, isdir, join

top_level = join(expandvars(f'%appdata%'), "py-clash-bot")
config_file = join(top_level, 'config.json')


def load_user_settings():
    try:
        return json.load(open(config_file, 'r'))
    except json.JSONDecodeError:
        print("User config file could not be loaded, is it misconfigured?")
        sys.exit()
    except OSError:
        print("Could not find config file, creating one now")
        create_config_file()
        return load_user_settings()


def create_config_file():
    if not isdir(top_level):
        makedirs(top_level)
    if not exists(config_file):
        with open(config_file, "w") as f:
            default_config = {
                "card_to_request": "giant",
                "selected_accounts": [0],
                "enable_donate": True,
                "enable_card_mastery_collection": True,
                "enable_battlepass_collection": True,
                "enable_request": True,
                "enable_card_upgrade": True,
                "enable_program_auto_update": True
            }
            f.write(json.dumps(default_config, indent=4))


create_config_file()
