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
    try:
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
    except Exception:
        print("Error getting random donate image")
        return None


RANDOM_DONATE_IMAGE = get_random_donate_image_path()

DONATE_BUTTON_LAYOUTS = [
    [
        [
            sg.Button(
                image_source=RANDOM_DONATE_IMAGE,
                size=(70, 7),
                key=DONATE_BUTTON_KEY,
            )
            if RANDOM_DONATE_IMAGE is not None
            else sg.Button(
                "Donate",
                size=(70, 7),
                key=DONATE_BUTTON_KEY,
            ),
        ]
    ],
]

# endregion


controls_layout = [
    [
        sg.Frame(layout=controls, title="Controls", expand_x=True, expand_y=True),
        sg.Frame(layout=jobs_checklist, title="Jobs", expand_x=True, expand_y=True),
    ]
]


account_switching_layout = [
    [
        sg.Frame(
            layout=[
                [
                    sg.Checkbox(
                        "Enabled",
                        key="account_switching_toggle",
                        default=False,
                    ),
                    sg.Slider(
                        range=(1, 8),
                        orientation="h",
                        key="account_switching_slider",
                    ),
                    sg.Text("Current Account #"),
                    sg.Text(
                        "-",
                        key="current_account",
                        relief=sg.RELIEF_SUNKEN,
                        text_color="blue",
                        size=(5, 1),
                    ),
                ],
            ],
            title="Account Switching",
            expand_x=True,
        ),sg.Frame(
        layout=[
            [
                sg.Checkbox(
                    "Enabled",
                    key="memu_attach_mode_toggle",
                    default=False,
                ),
            ],
        ],
        title="Memu Docking",
        expand_x=True,
        expand_y=True,
    ),
    ]
]


stats_tab_layout = [
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
    ]
]


donate_button_layout_tab = [
    sg.Frame(
        layout=random.choice(DONATE_BUTTON_LAYOUTS),
        title="",
        relief=sg.RELIEF_SUNKEN,
        expand_x=True,
    ),
]


time_status_bar_layout = [
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
]


main_layout = [
    [
        # layout:List[List[Tab]]
        sg.TabGroup(
            layout=[
                [sg.Tab("Controls", controls_layout)],
                [sg.Tab("Stats", stats_tab_layout)],
            ]
        ),
    ],
    [account_switching_layout],
    [
        sg.Button("Start", expand_x=True, button_color="Lime Green", border_width=3),
        sg.Button("Stop", disabled=True, expand_x=True, border_width=2),
        sg.Button(
            "Pause",
            disabled=True,
            key="-Pause-Resume-Button-",
            expand_x=True,
            border_width=2,
        ),
    ],
    [
        sg.Button(
            "Discord",
            key="discord",
            expand_x=True,
            button_color="#7289da",
            border_width=2,
        ),
        sg.Button("Upload Log", key="upload-log", expand_x=True, border_width=2),
        sg.Button(
            "Report Bug",
            key="bug-report",
            expand_x=True,
            button_color="#FF0000",
            border_width=2,
        ),
    ],
    [donate_button_layout_tab],
    [time_status_bar_layout],
]


# a list of all the keys that contain user configuration
user_config_keys = [
    # job list controls keys
    "open_chests_user_toggle",
    "open_battlepass_user_toggle",
    "request_user_toggle",
    "donate_toggle",
    "card_mastery_user_toggle",
    "memu_attach_mode_toggle",
    "disable_win_track_toggle",
    "free_offer_user_toggle",
    "gold_offer_user_toggle",
    "1v1_user_toggle",
    "2v2_user_toggle",
    "card_upgrade_user_toggle",
    "war_user_toggle",
    "random_decks_user_toggle",
    "open_bannerbox_user_toggle",
    "daily_rewards_user_toggle",
    "random_plays_user_toggle",
    "skip_fight_if_full_chests_user_toggle",
    # job increment controls keys
    "request_increment_user_input",
    "donate_increment_user_input",
    "daily_reward_increment_user_input",
    "shop_buy_increment_user_input",
    "card_upgrade_increment_user_input",
    "card_mastery_collect_increment_user_input",
    "open_chests_increment_user_input",
    "deck_randomization_increment_user_input",
    "war_attack_increment_user_input",
    "battlepass_collect_increment_user_input",
    "account_switching_increment_user_input",
    # account switching stuff
    "account_switching_toggle",
    "account_switching_slider",
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
