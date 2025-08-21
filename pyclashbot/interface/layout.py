"""This module defines the layout of the PyClashBot interface using FreeSimpleGUI."""

from os import path

import FreeSimpleGUI as sg  # noqa: N813
from FreeSimpleGUI import Window

from pyclashbot.interface.builder import (
    build_battle_stats,
    build_bot_stats,
    build_collection_stats,
    build_data_settings,
    build_emulator_choice,
    build_emulator_settings_tabs,
    build_google_play_settings,
    build_jobs_section,
    build_memu_settings,
)
from pyclashbot.interface.config import DISABLE_KEYS, USER_CONFIG_KEYS
from pyclashbot.interface.theme import THEME
from pyclashbot.utils.versioning import __version__

sg.theme(THEME)


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


def create_jobs_tab():
    """Create the jobs tab layout."""
    return [
        [
            sg.Frame(
                layout=build_jobs_section(),
                title="Jobs",
                expand_x=True,
                expand_y=True,
                border_width=1,
                pad=5,
            )
        ],
    ]


def create_emulator_tab():
    """Create the emulator tab layout."""
    return [
        [build_emulator_choice()],
        [build_emulator_settings_tabs()],
        [build_data_settings()],
    ]


def create_stats_tab():
    """Create the stats tab layout."""
    return [
        [
            sg.Column(
                [[build_battle_stats()]],
                expand_y=True,
                pad=5,
            ),
            sg.Column(
                [
                    [build_collection_stats()],
                    [build_bot_stats()],
                ],
                justification="right",
                expand_y=True,
                pad=5,
            ),
        ],
    ]


def create_main_tabs():
    """Create the main tab group."""
    return [
        [
            sg.TabGroup(
                [
                    [
                        sg.Tab("Jobs", create_jobs_tab(), key="-JOBS_TAB-"),
                        sg.Tab("Emulator", create_emulator_tab(), key="-EMULATOR_TAB-"),
                        sg.Tab("Stats", create_stats_tab(), key="-STATS_TAB-"),
                    ]
                ],
                key="-MAIN_TABS-",
                enable_events=True,
                expand_x=True,
                expand_y=True,
                pad=0,
            )
        ]
    ]


def create_status_bar():
    """Create the status bar layout."""
    return [
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


def create_control_buttons():
    """Create the start/stop control buttons."""
    return [
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
    ]


main_layout = [
    [
        sg.Column(
            [
                [
                    sg.Frame(
                        layout=create_main_tabs(), 
                        title="", 
                        border_width=0, 
                        pad=0
                    )
                ],
            ],
            key="-stacked-section-",
            expand_x=True,
            expand_y=True,
            pad=0,
        )
    ],
    [*create_control_buttons()],
    [*create_status_bar()],
]


# Configuration keys imported from config module
user_config_keys = USER_CONFIG_KEYS
disable_keys = DISABLE_KEYS


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


if __name__ == "__main__":
    window = create_window()
    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED:
            break
    window.close()
