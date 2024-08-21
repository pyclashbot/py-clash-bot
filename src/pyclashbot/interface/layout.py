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
from PySimpleGUI import Window

sg.theme(THEME)


controls_layout = [
    [
        sg.Frame(layout=controls, title="Controls", expand_x=True, expand_y=True),
        sg.Frame(layout=jobs_checklist, title="Jobs", expand_x=True, expand_y=True),
    ],
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
                        size=(10, 20),
                    ),
                ],
                [
                    sg.Text("Current Account #"),
                    sg.Text(
                        "-",
                        key="current_account",
                        relief=sg.RELIEF_SUNKEN,
                        text_color="blue",
                        size=(5, 1),
                    ),
                ],
                [
                    sg.Text("Account Order"),
                    sg.Text(
                        "-",
                        key="account_order",
                        relief=sg.RELIEF_SUNKEN,
                        text_color="blue",
                        size=(10, 1),
                    ),
                ],
            ],
            title="Account Switching",
            expand_x=True,
        ),
        sg.Frame(
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
            expand_y=True,
            expand_x=True,
        ),
    ],
]


stats_tab_layout = [
    [
        sg.Column(
            [
                [
                    sg.Frame(
                        layout=battle_stats,
                        title="Battle Stats",
                        expand_x=True,
                        expand_y=True,
                    )
                ],
                [
                    sg.Frame(
                        layout=bot_stats,
                        title="Bot Stats",
                        expand_x=True,
                    ),
                ],
            ],
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
                        expand_y=True,
                    ),
                ],
            ],
            expand_x=True,
            justification="right",
            expand_y=True,
        ),
    ]
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
        sg.pin(
            sg.Column(
                [
                    [
                        sg.TabGroup(
                            layout=[
                                [sg.Tab("Controls", controls_layout)],
                                [sg.Tab("Stats", stats_tab_layout)],
                            ],
                        ),
                    ],
                ],
                key="-tab-group-",
            )
        )
    ],
    [
        sg.Button(
            "Start",
            expand_x=True,
            button_color="Lime Green",
            border_width=3,
            # size=(23, 1),
        ),
        sg.Button(
            "Stop",
            disabled=True,
            button_color="Red",
            expand_x=True,
            border_width=2,
            # size=(23, 1),
        ),
        sg.Button(
            "Collapse",
            key="-Collapse-Button-",
            expand_x=True,
            border_width=2,
            # size=(23, 1),
        ),
    ],
    [time_status_bar_layout],
]


# a list of all the keys that contain user configuration
user_config_keys = [
    # job list controls keys
    "open_chests_user_toggle",
    "open_battlepass_user_toggle",
    "request_user_toggle",
    "donate_toggle",
    "free_donate_toggle",
    "card_mastery_user_toggle",
    "memu_attach_mode_toggle",
    "disable_win_track_toggle",
    "free_offer_user_toggle",
    "gold_offer_user_toggle",
    "trophy_road_1v1_user_toggle",
    "goblin_queens_journey_1v1_battle_user_toggle",
    "path_of_legends_1v1_user_toggle",
    "2v2_user_toggle",
    "card_upgrade_user_toggle",
    "war_user_toggle",
    "random_decks_user_toggle",
    "open_bannerbox_user_toggle",
    "daily_rewards_user_toggle",
    "random_plays_user_toggle",
    "skip_fight_if_full_chests_user_toggle",
    "trophy_road_rewards_user_toggle",
    "upgrade_all_cards_user_toggle",
    "season_shop_buys_user_toggle",
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
    "level_up_chest_increment_user_input",
    "level_up_chest_user_toggle",
    "trophy_road_reward_increment_user_input",
    "season_shop_buys_increment_user_input",
    # account switching stuff
    "account_switching_toggle",
    "account_switching_slider",
]

# list of button and checkbox keys to disable when the bot is running
disable_keys = user_config_keys + ["Start"]


def create_window() -> Window:
    """method for creating the main gui window"""
    icon_path = "pixel-pycb.ico"
    if not path.isfile(path=icon_path):
        icon_path = path.join("..\\..\\..\\assets\\", icon_path)
    return sg.Window(
        title=f"py-clash-bot | {__version__}", layout=main_layout, icon=icon_path
    )
