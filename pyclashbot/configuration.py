from os.path import dirname, join, exists
import json
import sys

top_level = dirname(__file__)
config_file = join(top_level, 'config.json')


def __init__():
    create_config_file()


def load_user_settings():
    return json.load(open(config_file))


def create_config_file():
    if not exists(config_file):
        with open(config_file) as f:
            default_config = {
                "card_to_request": "giant",
                "selected_accounts": [0],
                "enable_donate": "True",
                "enable_card_mastery_collection": "True",
                "enable_battlepass_collection": "True",
                "enable_request": "True",
                "enable_card_upgrade": "True",
                "enable_program_auto_update": "True"
            }
            f.write(json.dumps(default_config))
    try:
        json.load(open(config_file))
    finally:
        print("User config file could not be loaded, is it misconfigured?")
        sys.exit()
