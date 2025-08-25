"""Builder functions for creating FreeSimpleGUI elements from configuration."""

import FreeSimpleGUI as sg

from .config import (
    BATTLE_STATS,
    BOT_STATS,
    COLLECTION_STATS,
    EMULATOR_CHOICE,
    GOOGLE_PLAY_SETTINGS,
    JOBS,
    MEMU_SETTINGS,
    ComboConfig,
    JobConfig,
    RadioConfig,
    StatConfig,
)
from .theme import COLORS


def build_stat_box(stat: StatConfig) -> sg.Text:
    """Build a stat display text box with clean styling."""
    return sg.Text(
        "0",
        key=stat.key,
        relief=sg.RELIEF_SUNKEN,
        text_color=COLORS["white"],
        background_color=COLORS["navy"],
        size=stat.size,
        pad=(2, 1),
        font=("Arial", 9, "bold"),
        justification="center",
    )


def build_stat_title(stat: StatConfig) -> sg.Text:
    """Build a stat title text."""
    return sg.Text(stat.title, pad=(2, 1), font=("Arial", 9), justification="right", size=(10, 1))


def build_stats_section(stats: list[StatConfig], title: str) -> sg.Frame:
    """Build a clean stats section."""
    titles = [[build_stat_title(stat)] for stat in stats]
    values = [[build_stat_box(stat)] for stat in stats]

    layout = [
        [
            sg.Column(titles, element_justification="right", pad=(2, 2)),
            sg.Column(values, element_justification="left", pad=(2, 2)),
        ]
    ]

    return sg.Frame(layout=layout, title=title, expand_x=True, pad=(5, 3), font=("Arial", 9, "bold"))


def build_job_checkbox(job: JobConfig) -> list[sg.Element]:
    """Build a compact job checkbox."""
    elements = [
        sg.Checkbox(job.title, default=job.default, key=job.key, enable_events=True, font=("Arial", 9), pad=(3, 2))
    ]

    if job.extras:
        for extra_key, extra_config in job.extras.items():
            if isinstance(extra_config, ComboConfig):
                elements.extend(
                    [
                        sg.Text(f"{extra_config.label}", size=(6, 1), font=("Arial", 9)),
                        sg.Combo(
                            values=extra_config.values,
                            default_value=extra_config.default,
                            key=extra_config.key,
                            size=extra_config.size,
                            readonly=True,
                            enable_events=True,
                            font=("Arial", 9),
                        ),
                    ]
                )

    return elements


def build_jobs_section() -> list[list[sg.Element]]:
    """Build the jobs checklist section."""
    return [[*build_job_checkbox(job)] for job in JOBS]


def build_radio_section(radios: list[RadioConfig], title: str) -> sg.Frame:
    """Build a clean radio button section."""
    layout = [
        [
            sg.Radio(
                enable_events=True,
                text=radio.title,
                group_id=radio.group_id,
                default=radio.default,
                key=radio.key,
                pad=(5, 2),
                font=("Arial", 9),
            )
        ]
        for radio in radios
    ]

    return sg.Frame(layout=layout, title=title, expand_x=True, pad=(5, 3), font=("Arial", 9, "bold"))


def build_combo_section(combos: list[ComboConfig], title: str) -> sg.Frame:
    """Build a clean combo box section."""
    # For Google Play Settings, create a clean 3x2 grid layout like original
    if title == "Google Play Options":
        layout = []
        for i in range(0, len(combos), 3):  # Group by 3 items per row
            row = []
            for j in range(3):
                if i + j < len(combos):
                    combo = combos[i + j]
                    row.extend(
                        [
                            sg.Text(combo.label, size=(6, 1), font=("Arial", 9)),
                            sg.Combo(
                                combo.values,
                                key=combo.key,
                                readonly=True,
                                default_value=combo.default,
                                size=(4, 1),
                                font=("Arial", 9),
                            ),
                        ]
                    )
                else:
                    row.extend([sg.Text("", size=(10, 1))])
            layout.append(row)
    else:
        layout = [
            [
                sg.Text(combo.label, size=(10, 1), font=("Arial", 9)),
                sg.Combo(combo.values, key=combo.key, readonly=True, default_value=combo.default, font=("Arial", 9)),
            ]
            for combo in combos
        ]

    return sg.Frame(title=title, layout=layout, expand_x=True, pad=(5, 3), font=("Arial", 9, "bold"))


def build_memu_settings() -> sg.Frame:
    """Build the Memu settings frame."""
    return build_radio_section(MEMU_SETTINGS, "Memu Settings")


def build_emulator_choice() -> sg.Frame:
    """Build the emulator choice frame."""
    return build_radio_section(EMULATOR_CHOICE, "Emulator Type")


def build_google_play_settings() -> sg.Frame:
    """Build the Google Play settings frame."""
    return build_combo_section(GOOGLE_PLAY_SETTINGS, "Google Play Settings")


def build_emulator_settings_tabs() -> sg.TabGroup:
    """Build clean tabbed emulator settings."""
    google_play_tab = sg.Tab(
        "Google Play Settings",
        [[build_combo_section(GOOGLE_PLAY_SETTINGS, "Google Play Options")]],
        key="-GOOGLE_PLAY_TAB-",
        pad=(3, 3),
    )

    memu_tab = sg.Tab(
        "Memu Settings", [[build_radio_section(MEMU_SETTINGS, "Render Mode")]], key="-MEMU_TAB-", pad=(3, 3)
    )

    return sg.TabGroup(
        [[google_play_tab, memu_tab]],
        key="-EMULATOR_TABS-",
        enable_events=True,
        expand_x=True,
        pad=(3, 3),
        font=("Arial", 9, "bold"),
        selected_title_color=COLORS["white"],
        selected_background_color=COLORS["navy"],
        title_color=COLORS["dark_text"],
    )


def build_data_settings() -> sg.Frame:
    """Build the data settings frame."""
    layout = [
        [
            sg.Checkbox("Record fights", key="record_fights_toggle", default=False, font=("Arial", 9), pad=(5, 2)),
        ],
    ]

    return sg.Frame(title="Data Settings", layout=layout, expand_x=True, pad=(5, 3), font=("Arial", 9, "bold"))


def build_battle_stats() -> sg.Frame:
    """Build the battle stats section."""
    return build_stats_section(BATTLE_STATS, "Battle Stats")


def build_collection_stats() -> sg.Frame:
    """Build the collection stats section."""
    return build_stats_section(COLLECTION_STATS, "Collection Stats")


def build_bot_stats() -> sg.Frame:
    """Build the bot stats section."""
    return build_stats_section(BOT_STATS, "Bot Stats")
