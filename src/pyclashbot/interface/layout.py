"""
This module defines the layout of the PyClashBot interface using PySimpleGUI.
"""

import os
import random
from os import path

import PySimpleGUI as sg

from pyclashbot.interface.controls import controls
from pyclashbot.interface.joblist import jobs_checklist
from pyclashbot.interface.stats import (
    battle_stats,
    bot_stats,
    collection_stats,
    stat_box,
)
from pyclashbot.interface.theme import THEME
from pyclashbot.utils.versioning import __version__

sg.theme(THEME)


# region DONATE BUTTON STUFF


DONATE_BUTTON_KEY = "donate_button_key"


def filter_donate_image_sources(path_list):
    """
    Filters a list of file paths to only include paths
    to PNG images with 'donate' in the file name.

    Args:
        path_list (list): A list of file paths.

    Returns:
        list: A filtered list of file paths.
    """
    good_paths = []

    for this_path in path_list:
        if ".png" not in this_path or "donate" not in this_path:
            continue
        good_paths.append(this_path)

    return good_paths


def get_random_donate_image_path():
    """
    Returns a random path to a donate image file.
    """
    # grab all the donate images
    donate_image_sources = os.listdir()

    # if 'github exists in the list, then we're in a source code version
    # of the bot, so source the images from the assets folder
    if ".github" in donate_image_sources:
        donate_image_sources = []

        files = os.listdir("src/pyclashbot/interface/assets")
        for file in files:
            this_path = os.path.join("src/pyclashbot/interface/assets", file)
            donate_image_sources.append(this_path)

    donate_image_sources = filter_donate_image_sources(donate_image_sources)

    random_image_index = random.randint(0, len(donate_image_sources) - 1)

    random_image_path = donate_image_sources[random_image_index]

    return random_image_path


DONATE_BUTTON_LAYOUTS = [
    [
        [
            sg.Button(
                image_source=get_random_donate_image_path(),
                size=(70, 7),
                key=DONATE_BUTTON_KEY,
            )
        ]
    ],
]

# endregion

main_layout = [
    # controls + jobs list
    [
        sg.Frame(layout=controls, title="Controls", expand_x=True, expand_y=True),
        sg.Frame(layout=jobs_checklist, title="Jobs", expand_x=True, expand_y=True),
    ],
    # stats
    [
        sg.Column(
            [[sg.Frame(layout=battle_stats, title="Battle Stats", expand_x=True)]],
            expand_x=True,
            expand_y=True,
        ),
        sg.Column(
            [
                [
                    sg.Frame(
                        layout=collection_stats,
                        title="Collection Stats",
                        expand_x=True,
                    )
                ],
                [sg.Frame(layout=bot_stats, title="Bot Stats", expand_x=True)],
            ],
            expand_x=True,
            expand_y=True,
            justification="right",
        ),
    ],
    [
        sg.Frame(
            layout=random.choice(DONATE_BUTTON_LAYOUTS),
            title="",
            relief=sg.RELIEF_SUNKEN,
            expand_x=True,
        ),
    ],
    # time+status bar
    [
        sg.Column(
            [
                [

                    sg.Input(
                        "Idle",
                        key="current_status",
                        use_readonly_for_disable=True,
                        disabled=True,
                        text_color="blue",
                        expand_x=True,
                        tooltip=r"Logs available in %appdata%/py-clash-bot/log.txt",
                    ),
                ]
            ],
            expand_x=True,
        )
    ],
]


# a list of all the keys that contain user configuration
user_config_keys = [
    # job list controls keys
    "open_chests_user_toggle",
    "request_user_toggle",
    "card_mastery_user_toggle",
    "free_offer_user_toggle",
    "1v1_user_toggle",
    "2v2_user_toggle",
    "card_upgrade_user_toggle",
    "war_user_toggle",
    "random_decks_user_toggle",
    # job increment controls keys
    "request_increment_user_input",
    "free_offer_collection_increment_user_input",
    "card_upgrade_increment_user_input",
    "card_mastery_collect_increment_user_input",
    "open_chests_increment_user_input",
    "deck_randomization_increment_user_input",
    'war_attack_increment_user_input',
]

# list of button and checkbox keys to disable when the bot is running
disable_keys = user_config_keys + ["Start"]


def create_window():
    """method for creating the main gui window"""
    icon_path = "pixel-pycb.ico"
    if not path.isfile(path=icon_path):
        icon_path = path.join("..\\..\\..\\assets\\", icon_path)
    return sg.Window(
        title=f"py-clash-bot | {__version__}", layout=main_layout, icon=icon_path
    )
