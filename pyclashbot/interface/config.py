"""Configuration for PyClashBot interface elements."""

from dataclasses import dataclass
from typing import Any

try:
    from pyclashbot.utils.graphics_detection import GraphicsDetector

    graphics_detection_available = True
except ImportError:
    graphics_detection_available = False


@dataclass
class StatConfig:
    """Configuration for a stat display element."""

    key: str
    title: str
    size: tuple[int, int] = (6, 1)


@dataclass
class JobConfig:
    """Configuration for a job checkbox element."""

    key: str
    title: str
    default: bool = False
    extras: dict[str, Any] | None = None


@dataclass
class RadioConfig:
    """Configuration for a radio button element."""

    key: str
    title: str
    group_id: str
    default: bool = False


@dataclass
class ComboConfig:
    """Configuration for a combo box element."""

    key: str
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
BATTLE_STATS = [
    StatConfig("wins", "Win"),
    StatConfig("losses", "Loss"),
    StatConfig("winrate", "Win %"),
    StatConfig("cards_played", "Moves"),
    StatConfig("classic_1v1_fights", "Classic 1v1s"),
    StatConfig("classic_2v2_fights", "Classic 2v2s"),
    StatConfig("trophy_road_1v1_fights", "Trophy Road 1v1s"),
    StatConfig("card_randomizations", "Decks Randomized"),
    StatConfig("card_cycles", "Decks Cycled"),
]

COLLECTION_STATS = [
    StatConfig("card_mastery_reward_collections", "Masteries"),
    StatConfig("upgrades", "Upgrades"),
    StatConfig("war_chest_collects", "War Chests"),
]

BOT_STATS = [
    StatConfig("restarts_after_failure", "Bot Failures"),
    StatConfig("time_since_start", "Runtime", size=(8, 1)),
]

# Job Configuration
JOBS = [
    JobConfig("classic_1v1_user_toggle", "Classic 1v1 battles", default=False),
    JobConfig("classic_2v2_user_toggle", "Classic 2v2 battles", default=False),
    JobConfig("trophy_road_user_toggle", "Trophy Road battles", default=True),
    JobConfig(
        "random_decks_user_toggle",
        "Random decks",
        default=False,
        extras={
            "deck_number_selection": ComboConfig(
                key="deck_number_selection",
                label="Deck #",
                values=[1, 2, 3, 4, 5],
                default=2,
                label_size=(10, 1),
            )
        },
    ),
    JobConfig(
        "cycle_decks_user_toggle",
        "Cycle decks",
        default=False,
        extras={
            "max_deck_selection": ComboConfig(
                key="max_deck_selection",
                label="Decks to Cycle:",
                values=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                default=2,
                label_size=(15, 1),
            )
        },
    ),
    JobConfig("random_plays_user_toggle", "Random plays", default=False),
    JobConfig("disable_win_track_toggle", "Skip win/loss check", default=False),
    JobConfig("card_mastery_user_toggle", "Card Masteries", default=False),
    JobConfig("card_upgrade_user_toggle", "Upgrade Cards", default=False),
]

# Emulator Settings Configuration (dynamically generated)
MEMU_SETTINGS = get_available_memu_settings()

# BlueStacks specific renderer settings (dynamically generated)
BLUESTACKS_SETTINGS = get_available_bluestacks_settings()

EMULATOR_CHOICE = [
    RadioConfig("memu_emulator_toggle", "Memu", "emulator_type_radio", default=True),
    RadioConfig("google_play_emulator_toggle", "Google Play", "emulator_type_radio"),
    RadioConfig("bluestacks_emulator_toggle", "BlueStacks 5", "emulator_type_radio"),
]

# Google Play Settings Configuration
GOOGLE_PLAY_SETTINGS = [
    ComboConfig("gp_angle", "angle", ["true", "false"]),
    ComboConfig("gp_vulkan", "vulkan", ["true", "false"]),
    ComboConfig("gp_gles", "gles", ["true", "false"]),
    ComboConfig("gp_surfaceless", "surfaceless", ["true", "false"]),
    ComboConfig("gp_egl", "egl", ["true", "false"]),
    ComboConfig("gp_backend", "backend", ["gfxstream", "angle", "swiftshader"]),
    ComboConfig("gp_wsi", "wsi", ["vk", "glx"]),
]

# All user configuration keys (auto-generated from configs)
USER_CONFIG_KEYS = (
    [job.key for job in JOBS]
    + [radio.key for radio in MEMU_SETTINGS + BLUESTACKS_SETTINGS + EMULATOR_CHOICE]
    + [combo.key for combo in GOOGLE_PLAY_SETTINGS]
    + ["record_fights_toggle"]  # Data settings
    + [
        "deck_number_selection",
        "max_deck_selection",
        "cycle_decks_user_toggle",
    ]
)

# Keys to disable when bot is running
DISABLE_KEYS = [*USER_CONFIG_KEYS, "Start"]
