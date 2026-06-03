"""Configuration for PyClashBot interface elements."""

from __future__ import annotations

from dataclasses import dataclass

from pyclashbot.interface.enums import (
    BATTLE_STAT_FIELDS,
    BATTLE_STAT_LABELS,
    BOT_STAT_LABELS,
    COLLECTION_STAT_FIELDS,
    COLLECTION_STAT_LABELS,
    WIN_RATE_STAT_FIELDS,
    WIN_RATE_STAT_LABELS,
    BotStatField,
    StatField,
    UIField,
)
from pyclashbot.utils.platform import is_macos


@dataclass
class StatConfig:
    """Configuration for a stat display element."""

    key: StatField | BotStatField
    title: str
    size: tuple[int, int] = (6, 1)


@dataclass
class JobConfig:
    """Configuration for a job checkbox element."""

    key: UIField
    title: str
    default: bool = False
    extras: dict[UIField, ComboConfig] | None = None
    primary: bool = False


@dataclass
class RadioConfig:
    """Configuration for a radio button element."""

    key: UIField
    title: str
    group_id: str
    default: bool = False


@dataclass
class ComboConfig:
    """Configuration for a combo box element."""

    key: UIField
    label: str
    values: list[str | int]
    default: str | int = ""
    size: tuple[int, int] = (5, 1)
    label_size: tuple[int, int] = (6, 1)
    tooltip: str = ""


# Statistics Configuration
WIN_RATE_STATS = [StatConfig(field, WIN_RATE_STAT_LABELS[field]) for field in WIN_RATE_STAT_FIELDS]

BATTLE_STATS = [StatConfig(field, BATTLE_STAT_LABELS[field]) for field in BATTLE_STAT_FIELDS]

COLLECTION_STATS = [StatConfig(field, COLLECTION_STAT_LABELS[field]) for field in COLLECTION_STAT_FIELDS]

BOT_STATS = [
    StatConfig(BotStatField.RESTARTS_AFTER_FAILURE, BOT_STAT_LABELS[BotStatField.RESTARTS_AFTER_FAILURE]),
    StatConfig(BotStatField.TIME_SINCE_START, BOT_STAT_LABELS[BotStatField.TIME_SINCE_START], size=(8, 1)),
]

# Job Configuration
JOBS = [
    JobConfig(UIField.CLASSIC_1V1_USER_TOGGLE, "⚔️ Classic 1v1", default=False, primary=True),
    JobConfig(UIField.CLASSIC_2V2_USER_TOGGLE, "👥 Classic 2v2", default=False, primary=True),
    JobConfig(UIField.TROPHY_ROAD_USER_TOGGLE, "🏆 Trophy Road", default=True, primary=True),
    JobConfig(
        UIField.RANDOM_DECKS_USER_TOGGLE,
        "🎲 Randomize deck",
        default=False,
        extras={
            UIField.DECK_NUMBER_SELECTION: ComboConfig(
                key=UIField.DECK_NUMBER_SELECTION,
                label="Deck slot",
                values=[1, 2, 3, 4, 5],
                default=2,
                label_size=(10, 1),
                tooltip="Deck slot (1-5) to use when randomizing",
            )
        },
    ),
    JobConfig(
        UIField.CYCLE_DECKS_USER_TOGGLE,
        "♻️ Cycle decks",
        default=False,
        extras={
            UIField.MAX_DECK_SELECTION: ComboConfig(
                key=UIField.MAX_DECK_SELECTION,
                label="Decks to cycle",
                values=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                default=2,
                label_size=(15, 1),
                tooltip="Number of deck slots to rotate through",
            )
        },
    ),
    JobConfig(
        UIField.SWITCH_ACCOUNTS_USER_TOGGLE,
        "🔀 Switch accounts",
        default=False,
        extras={
            UIField.MAX_ACCOUNT_SELECTION: ComboConfig(
                key=UIField.MAX_ACCOUNT_SELECTION,
                label="Accounts to cycle",
                values=[2, 3],
                default=2,
                label_size=(15, 1),
                tooltip=(
                    "How many linked Supercell accounts to swap between each bot loop (2-3). "
                    "Accounts are picked in the order you signed into them on this device."
                ),
            )
        },
    ),
    JobConfig(UIField.RANDOM_PLAYS_USER_TOGGLE, "❔ Random card plays", default=False),
    JobConfig(UIField.DISABLE_WIN_TRACK_TOGGLE, "⏭️ Skip win/loss tracking", default=False),
    JobConfig(UIField.CARD_MASTERY_USER_TOGGLE, "🎯 Card Mastery", default=False),
    JobConfig(UIField.CARD_UPGRADE_USER_TOGGLE, "⬆️ Upgrade cards", default=False),
]

# Emulator Settings Configuration
MEMU_SETTINGS = [
    RadioConfig(UIField.OPENGL_TOGGLE, "OpenGL", "render_mode_radio"),
    RadioConfig(UIField.DIRECTX_TOGGLE, "DirectX", "render_mode_radio", default=True),
]

# BlueStacks specific renderer settings
# DirectX is default on Windows, Vulkan on macOS (DirectX not available on macOS)
BLUESTACKS_SETTINGS = [
    RadioConfig(UIField.BS_RENDERER_GL, "OpenGL", "bs_render_mode_radio"),
    RadioConfig(UIField.BS_RENDERER_DX, "DirectX", "bs_render_mode_radio", default=not is_macos()),
    RadioConfig(UIField.BS_RENDERER_VK, "Vulkan", "bs_render_mode_radio", default=is_macos()),
]

EMULATOR_CHOICE = [
    RadioConfig(UIField.MEMU_EMULATOR_TOGGLE, "MEmu", "emulator_type_radio", default=True),
    RadioConfig(UIField.GOOGLE_PLAY_EMULATOR_TOGGLE, "Google Play Games", "emulator_type_radio"),
    RadioConfig(UIField.BLUESTACKS_EMULATOR_TOGGLE, "BlueStacks 5", "emulator_type_radio"),
]

# Google Play Settings Configuration
GOOGLE_PLAY_SETTINGS = [
    ComboConfig(UIField.GP_ANGLE, "angle", ["true", "false"]),
    ComboConfig(UIField.GP_VULKAN, "vulkan", ["true", "false"]),
    ComboConfig(UIField.GP_GLES, "gles", ["true", "false"]),
    ComboConfig(UIField.GP_SURFACELESS, "surfaceless", ["true", "false"]),
    ComboConfig(UIField.GP_EGL, "egl", ["true", "false"]),
    ComboConfig(UIField.GP_BACKEND, "backend", ["gfxstream", "angle", "swiftshader"]),
    ComboConfig(UIField.GP_WSI, "wsi", ["vk", "glx"]),
]

# All user configuration keys (auto-generated from configs)
USER_CONFIG_KEYS = (
    [job.key.value for job in JOBS]
    + [radio.key.value for radio in MEMU_SETTINGS + BLUESTACKS_SETTINGS + EMULATOR_CHOICE]
    + [combo.key.value for combo in GOOGLE_PLAY_SETTINGS]
    + [UIField.THEME_NAME.value, UIField.RECORD_FIGHTS_TOGGLE.value]  # Data settings
    + [
        UIField.DECK_NUMBER_SELECTION.value,
        UIField.MAX_DECK_SELECTION.value,
        UIField.CYCLE_DECKS_USER_TOGGLE.value,
        UIField.MAX_ACCOUNT_SELECTION.value,
        UIField.SWITCH_ACCOUNTS_USER_TOGGLE.value,
    ]
)

# Keys to disable when bot is running
DISABLE_KEYS = [*USER_CONFIG_KEYS, "Start"]
