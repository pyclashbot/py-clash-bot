"""This module defines the layout of the PyClashBot interface using FreeSimpleGUI."""

from os import path

import FreeSimpleGUI as sg
from FreeSimpleGUI import Window

from pyclashbot.interface.joblist import jobs_checklist
from pyclashbot.interface.stats import (
    battle_stats,
    bot_stats,
    collection_stats,
)
from pyclashbot.interface.theme import THEME
from pyclashbot.utils.versioning import __version__

sg.theme(THEME)

jobs_frame = sg.Frame(
    layout=jobs_checklist,
    title="Jobs",
    expand_x=False,
    expand_y=True,
    border_width=None,
    pad=0,
)
account_switching_switching_frame = sg.Frame(
    layout=[
        [
            sg.Checkbox(
                "Enabled",
                key="account_switching_toggle",
                default=False,
            ),
        ],
        [
            sg.Slider(
                range=(1, 3),
                orientation="h",
                key="account_switching_slider",
                size=(10, 20),
            ),
        ],
    ],
    title="Account Switching",
    expand_x=True,
    pad=0,
)
memu_settings_frame = sg.Frame(
    layout=[
        [
            sg.Radio(
                enable_events=True,
                text="OpenGL",
                group_id="render_mode_radio",
                default=True,
                key="opengl_toggle",
                pad=1,
            ),
        ],
        [
            sg.Radio(
                enable_events=True,
                text="DirectX",
                group_id="render_mode_radio",
                key="directx_toggle",
                pad=1,
            ),
        ],
    ],
    title="Memu Settings",
    expand_y=True,
    expand_x=True,
    pad=0,
)


controls_layout = [
    [
        sg.Frame(layout=[[jobs_frame]], title="", expand_y=True, border_width=0, pad=0),
        sg.Frame(
            layout=[[account_switching_switching_frame]],
            title="",
            border_width=0,
            pad=0,
            expand_x=True,
            expand_y=True,
        ),
    ]
]

stats_tab_layout = [
    [
        sg.Column(
            [
                [
                    sg.Frame(
                        layout=battle_stats,
                        title="Battle Stats",
                        expand_y=False,
                        expand_x=True,
                        pad=0,
                    ),
                ],
                [
                    sg.Frame(
                        layout=bot_stats,
                        title="Bot Stats",
                        expand_x=False,
                        expand_y=True,
                        pad=0,
                    ),
                ],
            ],
            expand_y=True,
            pad=0,
        ),
        sg.Column(
            [
                [
                    sg.Frame(
                        layout=collection_stats,
                        title="Collection Stats",
                        expand_y=True,
                        pad=0,
                    ),
                ],
            ],
            justification="right",
            expand_y=True,
            pad=0,
        ),
    ],
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
            ],
        ],
        expand_x=True,
    ),
]


main_layout = [
    [
        sg.pin(
            sg.Column(
                [
                    [
                        sg.TabGroup(
                            layout=[
                                [sg.Tab("Controls", controls_layout)],
                                [sg.Tab("Stats", stats_tab_layout)],
                            ],
                            border_width=0,
                            pad=0,
                        ),
                    ],
                ],
                key="-tab-group-",
            ),
        ),
    ],
    [
        sg.Button(
            "Start",
            button_color="Lime Green",
            border_width=3,
            size=(10, 1),
        ),
        sg.Button(
            "Stop",
            disabled=True,
            button_color="Red",
            border_width=2,
            size=(10, 1),
        ),
        sg.Button(
            "Collapse",
            key="-Collapse-Button-",
            border_width=2,
            size=(10, 1),
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
    "disable_win_track_toggle",
    "free_offer_user_toggle",
    "gold_offer_user_toggle",
    "trophy_road_1v1_user_toggle",
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
    "magic_items_user_toggle",
    # account switching stuff
    "account_switching_toggle",
    "account_switching_slider",
    # MEmu settings
    "opengl_toggle",
    "directx_toggle",
]

# list of button and checkbox keys to disable when the bot is running
disable_keys = [*user_config_keys, "Start"]


def create_window() -> Window:
    """Method for creating the main gui window"""
    icon_path = "pixel-pycb.ico"
    if not path.isfile(path=icon_path):
        icon_path = path.join("..\\..\\..\\assets\\", icon_path)
    return sg.Window(
        title=f"py-clash-bot | {__version__}",
        layout=main_layout,
        icon=icon_path,
    )


def test_window():
    """Method for testing the window layout"""
    window = create_window()
    while True:
        event, values = window.read()
        print(event)
        if event == sg.WIN_CLOSED:
            break
    window.close()


if __name__ == "__main__":
    test_window()
