from os import path

import PySimpleGUI as sg

from pyclashbot.interface.controls import controls
from pyclashbot.interface.joblist import jobs_checklist
from pyclashbot.interface.stats import (
    battle_stats,
    collection_stats,
    bot_stats,
    stat_box,
)
from pyclashbot.interface.theme import THEME
from pyclashbot.utils.versioning import __version__

sg.theme(THEME)

main_layout = [
    [
        sg.Frame(layout=controls, title="Controls", expand_x=True, expand_y=True),
        sg.Frame(layout=jobs_checklist, title="Jobs", expand_x=True, expand_y=True),
    ],
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
        sg.Column(
            [
                [
                    stat_box("time_since_start", size=(7, 1)),
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

    # job increment controls keys
    "request_increment_user_input",
    "free_offer_collection_increment_user_input",
    "card_upgrade_increment_user_input",
    "card_mastery_collect_increment_user_input",
    "open_chests_increment_user_input",
    "deck_randomization_increment_user_input",
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
