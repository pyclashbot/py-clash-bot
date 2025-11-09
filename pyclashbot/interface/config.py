"""Configuration for PyClashBot interface elements."""

from __future__ import annotations

from dataclasses import dataclass

from pyclashbot.interface.enums import (
    BATTLE_STAT_FIELDS,
    BATTLE_STAT_LABELS,
    BOT_STAT_LABELS,
    COLLECTION_STAT_FIELDS,
    COLLECTION_STAT_LABELS,
    BotStatField,
    StatField,
    UIField,
)

try:
    from pyclashbot.utils.graphics_detection import GraphicsDetector

    graphics_detection_available = True
except ImportError:
    graphics_detection_available = False


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


def get_available_memu_settings() -> list[RadioConfig]:
    """Get MEmu settings based on available graphics APIs."""
    if not graphics_detection_available:
        # Fallback to static config if detection not available
        return [
            RadioConfig("opengl_toggle", "OpenGL", "render_mode_radio"),
            RadioConfig("directx_toggle", "DirectX", "render_mode_radio", default=True),
        ]

    available_apis = GraphicsDetector.get_available_apis_for_emulator("memu")
    best_api = GraphicsDetector.get_best_default_api("memu")

    settings = []
    if "opengl" in available_apis:
        settings.append(RadioConfig("opengl_toggle", "OpenGL", "render_mode_radio", default=(best_api == "opengl")))
    if "directx" in available_apis:
        settings.append(RadioConfig("directx_toggle", "DirectX", "render_mode_radio", default=(best_api == "directx")))

    return settings if settings else [RadioConfig("opengl_toggle", "OpenGL", "render_mode_radio", default=True)]


def get_available_bluestacks_settings() -> list[RadioConfig]:
    """Get BlueStacks settings based on available graphics APIs."""
    if not graphics_detection_available:
        # Fallback to static config if detection not available
        return [
            RadioConfig("bs_renderer_gl", "OpenGL", "bs_render_mode_radio"),
            RadioConfig("bs_renderer_dx", "DirectX", "bs_render_mode_radio", default=True),
            RadioConfig("bs_renderer_vk", "Vulkan", "bs_render_mode_radio"),
        ]

    available_apis = GraphicsDetector.get_available_apis_for_emulator("bluestacks")
    best_api = GraphicsDetector.get_best_default_api("bluestacks")

    settings = []
    if "opengl" in available_apis:
        settings.append(RadioConfig("bs_renderer_gl", "OpenGL", "bs_render_mode_radio", default=(best_api == "opengl")))
    if "directx" in available_apis:
        settings.append(
            RadioConfig("bs_renderer_dx", "DirectX", "bs_render_mode_radio", default=(best_api == "directx"))
        )
    if "vulkan" in available_apis:
        settings.append(RadioConfig("bs_renderer_vk", "Vulkan", "bs_render_mode_radio", default=(best_api == "vulkan")))

    return settings if settings else [RadioConfig("bs_renderer_gl", "OpenGL", "bs_render_mode_radio", default=True)]


# Statistics Configuration
BATTLE_STATS = [StatConfig(field, BATTLE_STAT_LABELS[field]) for field in BATTLE_STAT_FIELDS]

COLLECTION_STATS = [StatConfig(field, COLLECTION_STAT_LABELS[field]) for field in COLLECTION_STAT_FIELDS]

BOT_STATS = [
    StatConfig(BotStatField.RESTARTS_AFTER_FAILURE, BOT_STAT_LABELS[BotStatField.RESTARTS_AFTER_FAILURE]),
    StatConfig(BotStatField.TIME_SINCE_START, BOT_STAT_LABELS[BotStatField.TIME_SINCE_START], size=(8, 1)),
]

# Job Configuration
JOBS = [
    JobConfig(UIField.CLASSIC_1V1_USER_TOGGLE, "Classic 1v1 battles", default=False),
    JobConfig(UIField.CLASSIC_2V2_USER_TOGGLE, "Classic 2v2 battles", default=False),
    JobConfig(UIField.TROPHY_ROAD_USER_TOGGLE, "Trophy Road battles", default=True),
    JobConfig(
        UIField.RANDOM_DECKS_USER_TOGGLE,
        "Random decks",
        default=False,
        extras={
            UIField.DECK_NUMBER_SELECTION: ComboConfig(
                key=UIField.DECK_NUMBER_SELECTION,
                label="Deck #",
                values=[1, 2, 3, 4, 5],
                default=2,
                label_size=(10, 1),
            )
        },
    ),
    JobConfig(
        UIField.CYCLE_DECKS_USER_TOGGLE,
        "Cycle decks",
        default=False,
        extras={
            UIField.MAX_DECK_SELECTION: ComboConfig(
                key=UIField.MAX_DECK_SELECTION,
                label="Decks to Cycle:",
                values=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                default=2,
                label_size=(15, 1),
            )
        },
    ),
    JobConfig(UIField.RANDOM_PLAYS_USER_TOGGLE, "Random plays", default=False),
    JobConfig(UIField.DISABLE_WIN_TRACK_TOGGLE, "Skip win/loss check", default=False),
    JobConfig(UIField.CARD_MASTERY_USER_TOGGLE, "Card Masteries", default=False),
    JobConfig(UIField.CARD_UPGRADE_USER_TOGGLE, "Upgrade Cards", default=False),
]

# Emulator Settings Configuration (dynamically generated)
MEMU_SETTINGS = get_available_memu_settings()

# BlueStacks specific renderer settings (dynamically generated)
BLUESTACKS_SETTINGS = get_available_bluestacks_settings()

EMULATOR_CHOICE = [
    RadioConfig(UIField.MEMU_EMULATOR_TOGGLE, "Memu", "emulator_type_radio", default=True),
    RadioConfig(UIField.GOOGLE_PLAY_EMULATOR_TOGGLE, "Google Play", "emulator_type_radio"),
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
    ]
)

# Keys to disable when bot is running
DISABLE_KEYS = [*USER_CONFIG_KEYS, "Start"]
