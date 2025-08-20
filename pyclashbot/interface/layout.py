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


# Build interface components from configuration
jobs_checklist = build_jobs_section()
emulator_choice_frame = build_emulator_choice()
emulator_settings_tabs = build_emulator_settings_tabs()
data_settings_frame = build_data_settings()


# Jobs tab layout
jobs_tab_layout = [
    [
        sg.Frame(
            layout=jobs_checklist,
            title="Jobs",
            expand_x=True,
            expand_y=True,
            border_width=1,
            pad=5,
        )
    ],
]

# Emulator tab layout
emulator_tab_layout = [
    [emulator_choice_frame],
    [emulator_settings_tabs],
    [data_settings_frame],
]

# Stats tab layout
stats_tab_layout = [
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

# Create main tab group
controls_layout = [
    [
        sg.TabGroup(
            [
                [
                    sg.Tab("Jobs", jobs_tab_layout, key="-JOBS_TAB-"),
                    sg.Tab("Emulator", emulator_tab_layout, key="-EMULATOR_TAB-"),
                    sg.Tab("Stats", stats_tab_layout, key="-STATS_TAB-"),
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
                        layout=controls_layout, title="", border_width=0, pad=0
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


def handle_emulator_selection(window: Window, values: dict) -> None:
    """Handle emulator radio selection to switch tabs."""
    if values.get("memu_emulator_toggle"):
        # Switch to Memu tab
        window["-EMULATOR_TABS-"].Widget.select(0)
    elif values.get("google_play_emulator_toggle"):
        # Switch to Google Play tab
        window["-EMULATOR_TABS-"].Widget.select(1)


def test_window():
    """Method for testing the window layout"""
    window = create_window()
    while True:
        window_state = window.read(timeout=100)
        if window_state is None:
            continue

        event, values = window_state
        print(event)
        
        # Handle emulator radio button changes
        if event in ("memu_emulator_toggle", "google_play_emulator_toggle"):
            handle_emulator_selection(window, values)
            
        if event == sg.WIN_CLOSED:
            break
    window.close()


if __name__ == "__main__":
    test_window()
