from __future__ import annotations

from enum import StrEnum


class StatField(StrEnum):
    WINS = "wins"
    LOSSES = "losses"
    CARDS_PLAYED = "cards_played"
    CLASSIC_1V1_FIGHTS = "classic_1v1_fights"
    CLASSIC_2V2_FIGHTS = "classic_2v2_fights"
    TROPHY_ROAD_1V1_FIGHTS = "trophy_road_1v1_fights"
    CARD_RANDOMIZATIONS = "card_randomizations"
    CARD_CYCLES = "card_cycles"
    CARD_MASTERY_REWARD_COLLECTIONS = "card_mastery_reward_collections"
    UPGRADES = "upgrades"
    WAR_CHEST_COLLECTS = "war_chest_collects"


class DerivedStatField(StrEnum):
    WINRATE = "winrate"
    CURRENT_WIN_STREAK = "current_win_streak"
    BEST_WIN_STREAK = "best_win_streak"


class BotStatField(StrEnum):
    RESTARTS_AFTER_FAILURE = "restarts_after_failure"
    TIME_SINCE_START = "time_since_start"


class UIField(StrEnum):
    CARD_MASTERY_USER_TOGGLE = "card_mastery_user_toggle"
    CLASSIC_1V1_USER_TOGGLE = "classic_1v1_user_toggle"
    CLASSIC_2V2_USER_TOGGLE = "classic_2v2_user_toggle"
    TROPHY_ROAD_USER_TOGGLE = "trophy_road_user_toggle"
    CARD_UPGRADE_USER_TOGGLE = "card_upgrade_user_toggle"
    RANDOM_DECKS_USER_TOGGLE = "random_decks_user_toggle"
    DECK_NUMBER_SELECTION = "deck_number_selection"
    CYCLE_DECKS_USER_TOGGLE = "cycle_decks_user_toggle"
    MAX_DECK_SELECTION = "max_deck_selection"
    RANDOM_PLAYS_USER_TOGGLE = "random_plays_user_toggle"
    DISABLE_WIN_TRACK_TOGGLE = "disable_win_track_toggle"
    RECORD_FIGHTS_TOGGLE = "record_fights_toggle"
    OPENGL_TOGGLE = "opengl_toggle"
    DIRECTX_TOGGLE = "directx_toggle"
    BS_RENDERER_GL = "bs_renderer_gl"
    BS_RENDERER_DX = "bs_renderer_dx"
    BS_RENDERER_VK = "bs_renderer_vk"
    MEMU_EMULATOR_TOGGLE = "memu_emulator_toggle"
    GOOGLE_PLAY_EMULATOR_TOGGLE = "google_play_emulator_toggle"
    BLUESTACKS_EMULATOR_TOGGLE = "bluestacks_emulator_toggle"
    THEME_NAME = "theme_name"
    DISCORD_RPC_TOGGLE = "discord_rpc_toggle"
    GP_ANGLE = "gp_angle"
    GP_VULKAN = "gp_vulkan"
    GP_GLES = "gp_gles"
    GP_SURFACELESS = "gp_surfaceless"
    GP_EGL = "gp_egl"
    GP_BACKEND = "gp_backend"
    GP_WSI = "gp_wsi"
    ADB_TOGGLE = "adb_toggle"
    ADB_SERIAL = "adb_serial"


BATTLE_STAT_LABELS: dict[StatField, str] = {
    StatField.WINS: "Win",
    StatField.LOSSES: "Loss",
    StatField.CARDS_PLAYED: "Moves",
    StatField.CLASSIC_1V1_FIGHTS: "Classic 1v1s",
    StatField.CLASSIC_2V2_FIGHTS: "Classic 2v2s",
    StatField.TROPHY_ROAD_1V1_FIGHTS: "Trophy Road 1v1s",
    StatField.CARD_RANDOMIZATIONS: "Decks Randomized",
    StatField.CARD_CYCLES: "Decks Cycled",
}

BATTLE_STAT_FIELDS: tuple[StatField, ...] = tuple(BATTLE_STAT_LABELS.keys())

COLLECTION_STAT_LABELS: dict[StatField, str] = {
    StatField.CARD_MASTERY_REWARD_COLLECTIONS: "Masteries",
    StatField.UPGRADES: "Upgrades",
    StatField.WAR_CHEST_COLLECTS: "War Chests",
}

COLLECTION_STAT_FIELDS: tuple[StatField, ...] = tuple(COLLECTION_STAT_LABELS.keys())

BOT_STAT_LABELS: dict[BotStatField, str] = {
    BotStatField.RESTARTS_AFTER_FAILURE: "Bot Failures",
    BotStatField.TIME_SINCE_START: "Runtime",
}

BOT_STAT_FIELDS: tuple[BotStatField, ...] = tuple(BOT_STAT_LABELS.keys())

PRIMARY_JOB_TOGGLES: tuple[UIField, ...] = (
    UIField.CARD_MASTERY_USER_TOGGLE,
    UIField.CLASSIC_1V1_USER_TOGGLE,
    UIField.CLASSIC_2V2_USER_TOGGLE,
    UIField.TROPHY_ROAD_USER_TOGGLE,
    UIField.CARD_UPGRADE_USER_TOGGLE,
)
