import PySimpleGUI as sg

from interface.controls import controls
from interface.joblist import jobs_checklist
from interface.stats import (
    battle_stats,
    collections_stats,
    progress_stats,
    stat_box,
)
from interface.theme import THEME

sg.theme(THEME)

description = [
    [
        sg.Text("Matthew Miglio\nMartin Miglio\nNovember 2022\n", size=(13, None)),
    ],
    [
        sg.Text(
            "Issues?",
            key="issues-link",
            enable_events=True,
            tooltip="https://github.com/matthewmiglio/py-clash-bot/issues/new/choose",
            text_color="blue",
        ),
    ],
]

main_layout = [
    [
        sg.Frame(layout=jobs_checklist, title="Jobs"),
        sg.Frame(layout=controls, title="Controls", expand_x=True),
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
            expand_y=True,
        ),
        sg.Frame(layout=description, title="Info", expand_x=True),
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
    "-Daily-Challenge-Reward-Collection-",
    "1v1_battle_in",
]

# list of button and checkbox keys to disable when the bot is running
disable_keys = user_config_keys + ["Start"]
