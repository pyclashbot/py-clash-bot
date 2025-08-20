"""Configuration for PyClashBot interface elements."""

from dataclasses import dataclass
from typing import Any


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


# Statistics Configuration
BATTLE_STATS = [
    StatConfig("wins", "Win"),
    StatConfig("losses", "Loss"),
    StatConfig("winrate", "Win %"),
    StatConfig("cards_played", "Moves"),
    StatConfig("trophy_road_1v1_fights", "1v1s"),
    StatConfig("card_randomizations", "Decks"),
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
    JobConfig(
        "trophy_road_1v1_user_toggle",
        "Trophy road battles",
        default=True
    ),
    JobConfig(
        "random_decks_user_toggle",
        "Random decks",
        default=False,
        extras={
            "deck_selector": ComboConfig(
                "deck_number_selection",
                "Deck #:",
                values=[1, 2, 3, 4, 5],
                default=2
            )
        }
    ),
    JobConfig("random_plays_user_toggle", "Random plays", default=False),
    JobConfig("disable_win_track_toggle", "Skip win/loss check", default=False),
    JobConfig("card_mastery_user_toggle", "Card Masteries", default=False),
    JobConfig("card_upgrade_user_toggle", "Upgrade Cards", default=False),
    JobConfig("season_shop_buys_user_toggle", "Season Shop Offers", default=False),
]

# Emulator Settings Configuration
MEMU_SETTINGS = [
    RadioConfig("opengl_toggle", "OpenGL", "render_mode_radio", default=True),
    RadioConfig("directx_toggle", "DirectX", "render_mode_radio"),
]

EMULATOR_CHOICE = [
    RadioConfig("memu_emulator_toggle", "Memu", "emulator_type_radio", default=True),
    RadioConfig("google_play_emulator_toggle", "Google Play", "emulator_type_radio"),
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
    [job.key for job in JOBS] +
    [radio.key for radio in MEMU_SETTINGS + EMULATOR_CHOICE] +
    [combo.key for combo in GOOGLE_PLAY_SETTINGS] +
    ["record_fights_toggle"]  # Data settings
)

# Keys to disable when bot is running
DISABLE_KEYS = [*USER_CONFIG_KEYS, "Start"]