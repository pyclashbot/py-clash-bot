import PySimpleGUI as sg

from pyclashbot.interface.controls import controls
from pyclashbot.interface.joblist import jobs_checklist
from pyclashbot.interface.stats import battle_stats, collections_stats, progress_stats
from pyclashbot.interface.theme import THEME

sg.theme(THEME)

description = [
    [
        sg.Text("Matthew Miglio\nMartin Miglio\nOctober 2022\n", size=(13, None)),
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
        sg.Frame(layout=controls, title="Controls"),
    ],
    [
        sg.Frame(
            layout=battle_stats,
            title="Battle Stats",
        ),
        sg.Frame(
            layout=progress_stats,
            title="Progress Stats",
        ),
    ],
    [
        sg.Frame(
            layout=collections_stats,
            title="Collection Stats",
        ),
        sg.Frame(
            layout=description,
            title="Info",
        ),
    ],
    [
        sg.InputText(
            "Idle",
            key="current_status",
            use_readonly_for_disable=True,
            disabled=True,
            text_color="blue",
            size=(60, 1),
        ),
    ],
]

# a list of all the keys that contain user configuration
user_config_keys = [
    "-SSID_IN-",
    "-Open-Chests-in-",
    "-Fight-in-",
    "-Requesting-in-",
    "-Upgrade_cards-in-",
    "-War-Participation-in-",
    "-Random-Decks-in-",
    "-Card-Mastery-Collection-in-",
    "-Level-Up-Reward-Collection-in-",
    "-Battlepass-Reward-Collection-in-",
]

# list of button and checkbox keys to disable when the bot is running
disable_keys = user_config_keys + ["Start"]
