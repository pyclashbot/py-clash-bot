"""This module defines the layout of the PyClashBot interface using FreeSimpleGUI."""

from os import path

import FreeSimpleGUI as sg  # noqa: N813
from FreeSimpleGUI import Window

from pyclashbot.interface.theme import THEME
from pyclashbot.utils.versioning import __version__

sg.theme(THEME)


def stat_box(stat_name: str, size=(5, 1)) -> sg.Text:
    """Returns a FreeSimpleGUI text box object for stats layout"""
    return sg.Text(
        "0", key=stat_name, relief=sg.RELIEF_SUNKEN, text_color="blue", size=size, pad=0
    )


def make_stat_titles(titles: list[str]) -> list[list[sg.Text]]:
    list = [[sg.Text(title, pad=0)] for title in titles]
    return list


# collection stats
collection_title_texts = [
    "Masteries",
    "Upgrades",
    "War Chests",
]


collection_stats_titles: list[list[sg.Text]] = make_stat_titles(collection_title_texts)

collection_stats_values: list[list[sg.Text]] = [
    [
        stat_box("card_mastery_reward_collections"),
    ],
    [
        stat_box("upgrades"),
    ],
    [
        stat_box("war_chest_collects"),
    ],
]

collection_stats = [
    [
        sg.Column(collection_stats_titles, element_justification="right"),
        sg.Column(collection_stats_values, element_justification="left"),
    ],
]


# fight stats
titles = [
    "Win",
    "Loss",
    "Win %",
    "Moves",
    "1v1s",
    "Decks",
]

battle_stats_titles: list[list[sg.Text]] = make_stat_titles(titles)


battle_stats_values = [
    [
        stat_box("wins"),
    ],
    [
        stat_box("losses"),
    ],
    [
        stat_box("winrate"),
    ],
    [
        stat_box("cards_played"),
    ],
    [
        stat_box("trophy_road_1v1_fights"),
    ],
    [
        stat_box("card_randomizations"),
    ],
]

battle_stats = [
    [
        sg.Column(battle_stats_titles, element_justification="right", pad=0),
        sg.Column(battle_stats_values, element_justification="left", pad=0),
    ],
]


# bot stats

bot_stat_title_texts = [
    "Bot Failures",
    "Runtime",
]

bot_stats_titles: list[list[sg.Text]] = make_stat_titles(bot_stat_title_texts)

bot_stats_values = [
    [
        stat_box("restarts_after_failure"),
    ],
    [
        stat_box("time_since_start", size=(7, 1)),
    ],
]

bot_stats = [
    [
        sg.Column(bot_stats_titles, element_justification="right"),
        sg.Column(bot_stats_values, element_justification="left"),
    ],
]


def no_jobs_popup() -> None:
    """FreeSimpleGUI to popup when no jobs are selected."""
    # Define the layout of the GUI
    layout = [
        [
            sg.Text(
                "You must select at least one job!",
                size=(25, 2),
                justification="center",
            ),
        ],
        [sg.Button("Exit", size=(10, 1), pad=((150, 0), 3))],
    ]

    # Create the window
    window = sg.Window("Critical Error!", layout)

    # Event loop to process events and get user input
    while True:
        event, *_ = window.read()  # type: ignore  # noqa: PGH003

        # Exit the program if the "Exit" button is clicked or window is closed
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break

    # Close the window
    window.close()


def job_check_box(text: str, element_key: str, default_value=True) -> sg.Checkbox:
    """Returns a checkbox element for the joblist window"""
    return sg.Checkbox(
        text,
        default=default_value,
        key=element_key,
        enable_events=True,
    )


jobs_checklist = [
    [
        job_check_box(
            "Trophy road battles",
            "trophy_road_1v1_user_toggle",
            default_value=False,
        ),
    ],
    [
        job_check_box(
            "Random decks",
            "random_decks_user_toggle",
            default_value=False,
        ),
        sg.Text("Deck #:", size=(5, 1)),
        sg.Combo(
            values=[1, 2, 3, 4, 5],
            default_value=2,
            key="deck_number_selection",
            size=(5, 1),
            readonly=True,
            enable_events=True,
        ),
    ],
    [
        job_check_box(
            "Random plays",
            "random_plays_user_toggle",
            default_value=False,
        ),
    ],
    [
        job_check_box(
            "Skip win/loss check",
            "disable_win_track_toggle",
            default_value=False,
        ),
    ],
    [
        job_check_box(
            "Card Masteries",
            "card_mastery_user_toggle",
            default_value=False,
        ),
    ],
    [
        job_check_box(
            "Upgrade Cards",
            "card_upgrade_user_toggle",
            default_value=False,
        ),
    ],
    [
        job_check_box(
            "Season Shop Offers",
            "season_shop_buys_user_toggle",
            default_value=False,
        ),
    ],
]


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

emulator_choice_frame = sg.Frame(
    layout=[
        [
            sg.Radio(
                enable_events=True,
                text="Memu",
                group_id="emulator_type_radio",
                default=True,
                key="memu_emulator_toggle",
                pad=1,
            ),
        ],
        [
            sg.Radio(
                enable_events=True,
                text="Google Play",
                group_id="emulator_type_radio",
                key="google_play_emulator_toggle",
                pad=1,
            ),
        ],
    ],
    title="Emulator Type",
    expand_y=True,
    expand_x=True,
    pad=0,
)


google_play_settings_frame = sg.Frame(
    title="Google Play Settings",
    layout=[
        [
            sg.Text("angle", size=(10, 1)),
            sg.Combo(
                ["true", "false"], key="gp_angle", readonly=True, default_value=""
            ),
        ],
        [
            sg.Text("vulkan", size=(10, 1)),
            sg.Combo(
                ["true", "false"], key="gp_vulkan", readonly=True, default_value=""
            ),
        ],
        [
            sg.Text("gles", size=(10, 1)),
            sg.Combo(["true", "false"], key="gp_gles", readonly=True, default_value=""),
        ],
        [
            sg.Text("surfaceless", size=(10, 1)),
            sg.Combo(
                ["true", "false"], key="gp_surfaceless", readonly=True, default_value=""
            ),
        ],
        [
            sg.Text("egl", size=(10, 1)),
            sg.Combo(["true", "false"], key="gp_egl", readonly=True, default_value=""),
        ],
        [
            sg.Text("backend", size=(10, 1)),
            sg.Combo(
                ["gfxstream", "angle", "swiftshader"],
                key="gp_backend",
                readonly=True,
                default_value="",
            ),
        ],
        [
            sg.Text("wsi", size=(10, 1)),
            sg.Combo(["vk", "glx"], key="gp_wsi", readonly=True, default_value=""),
        ],
    ],
    expand_x=True,
    pad=(0, 5),
)

data_settings_frame = sg.Frame(
    title="Data Settings",
    layout=[
        [
            sg.Checkbox("Record fights", key="record_fights_toggle", default=True),
        ],
    ],
    expand_x=True,
    pad=(0, 5),
)


controls_layout = [
    [
        sg.Frame(
            layout=[
                [
                    sg.Frame(
                        layout=jobs_checklist,
                        title="Jobs",
                        expand_x=False,
                        expand_y=True,
                        border_width=None,
                        pad=0,
                    )
                ],
                [memu_settings_frame, emulator_choice_frame],
                [google_play_settings_frame, data_settings_frame],
            ],
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
        sg.Column(
            [
                [
                    sg.Frame(
                        layout=controls_layout, title="Controls", border_width=0, pad=0
                    )
                ],
                [
                    sg.Frame(
                        layout=stats_tab_layout, title="Stats", border_width=0, pad=0
                    )
                ],
            ],
            key="-stacked-section-",
            expand_x=True,
            expand_y=True,
            pad=0,
        )
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
        window_state = window.read(timeout=100)
        if window_state is None:
            continue

        event, values = window_state
        print(event)
        if event == sg.WIN_CLOSED:
            break
    window.close()


if __name__ == "__main__":
    test_window()
