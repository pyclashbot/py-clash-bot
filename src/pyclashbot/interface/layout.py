from os import path

import PySimpleGUI as sg

from pyclashbot.interface.controls import controls
from pyclashbot.interface.joblist import jobs_checklist
from pyclashbot.interface.stats import (
    battle_stats,
    collections_stats,
    progress_stats,
    stat_box,
)
from pyclashbot.interface.theme import THEME
from pyclashbot.utils.versioning import __version__

sg.theme(THEME)


main_layout = [
    [
        sg.Frame(layout=jobs_checklist, title="Jobs"),
        sg.Frame(layout=controls, title="Controls", expand_x=True, expand_y=True),
    ],
    [
        sg.Frame(
            layout=battle_stats,
            title="Battle Stats",
        ),
        sg.Frame(
            layout=progress_stats,
            title="Progress Stats",
            expand_x=True,
        ),
    ],
    [
        sg.Frame(
            layout=collections_stats,
            title="Collection Stats",
            expand_x=True,
        )
    ],
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
    ],
]

# a list of all the keys that contain user configuration
user_config_keys = [
    "-SSID_IN-",
    "-Open-Chests-in-",
    "-Requesting-in-",
    "-Card-Mastery-Collection-in-",
    "-Free-Offer-Collection-in-",
    "1v1_battle_in",
    "2v2_battle_in",
    "card_upgrading_in",
    "war_checkbox_in",
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
