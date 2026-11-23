"""Tkinter-free job-dictionary construction."""

from __future__ import annotations

from typing import Any

from pyclashbot.emulators import EmulatorType
from pyclashbot.interface.enums import UIField
from pyclashbot.utils.platform import is_macos


def migrate_clan_job_settings(values: dict[str, Any]) -> None:
    clan_actions = (
        UIField.CLAN_DONATE_USER_TOGGLE,
        UIField.CLAN_CLAIM_GIFTS_USER_TOGGLE,
        UIField.CLAN_REQUEST_CARDS_USER_TOGGLE,
    )
    if values.get(UIField.CLAN_CHAT_USER_TOGGLE.value) and not any(values.get(field.value) for field in clan_actions):
        for field in clan_actions:
            values[field.value] = True


_CLAN_ACTION_TOGGLES = (
    UIField.CLAN_DONATE_USER_TOGGLE,
    UIField.CLAN_CLAIM_GIFTS_USER_TOGGLE,
    UIField.CLAN_REQUEST_CARDS_USER_TOGGLE,
)


def make_job_dictionary(values: dict[str, Any]) -> dict[str, Any]:
    migrate_clan_job_settings(values)

    def as_bool(field: UIField) -> bool:
        return bool(values.get(field.value, False))

    def as_int(field: UIField, default: int) -> int:
        try:
            return int(values.get(field.value, default))
        except (TypeError, ValueError):
            return default

    def as_str(field: UIField, default: str = "") -> str:
        return str(values.get(field.value, default) or default)

    job_dictionary: dict[str, Any] = {
        UIField.CARD_MASTERY_USER_TOGGLE.value: as_bool(UIField.CARD_MASTERY_USER_TOGGLE),
        UIField.SHOP_DAILY_OFFER_USER_TOGGLE.value: as_bool(UIField.SHOP_DAILY_OFFER_USER_TOGGLE),
        UIField.CLASSIC_1V1_USER_TOGGLE.value: as_bool(UIField.CLASSIC_1V1_USER_TOGGLE),
        UIField.CLASSIC_2V2_USER_TOGGLE.value: as_bool(UIField.CLASSIC_2V2_USER_TOGGLE),
        UIField.TROPHY_ROAD_USER_TOGGLE.value: as_bool(UIField.TROPHY_ROAD_USER_TOGGLE),
        UIField.RANDOM_DECKS_USER_TOGGLE.value: as_bool(UIField.RANDOM_DECKS_USER_TOGGLE),
        UIField.DECK_NUMBER_SELECTION.value: as_int(UIField.DECK_NUMBER_SELECTION, 2),
        UIField.CYCLE_DECKS_USER_TOGGLE.value: as_bool(UIField.CYCLE_DECKS_USER_TOGGLE),
        UIField.MAX_DECK_SELECTION.value: as_int(UIField.MAX_DECK_SELECTION, 2),
        UIField.SWITCH_ACCOUNTS_USER_TOGGLE.value: as_bool(UIField.SWITCH_ACCOUNTS_USER_TOGGLE),
        UIField.MAX_ACCOUNT_SELECTION.value: as_int(UIField.MAX_ACCOUNT_SELECTION, 2),
        UIField.CLAN_DONATE_USER_TOGGLE.value: as_bool(UIField.CLAN_DONATE_USER_TOGGLE),
        UIField.CLAN_CLAIM_GIFTS_USER_TOGGLE.value: as_bool(UIField.CLAN_CLAIM_GIFTS_USER_TOGGLE),
        UIField.CLAN_REQUEST_CARDS_USER_TOGGLE.value: as_bool(UIField.CLAN_REQUEST_CARDS_USER_TOGGLE),
        UIField.CLAN_CHAT_USER_TOGGLE.value: any(as_bool(field) for field in _CLAN_ACTION_TOGGLES),
        UIField.WAR_USER_TOGGLE.value: as_bool(UIField.WAR_USER_TOGGLE),
        UIField.RANDOM_PLAYS_USER_TOGGLE.value: as_bool(UIField.RANDOM_PLAYS_USER_TOGGLE),
        UIField.DISABLE_WIN_TRACK_TOGGLE.value: as_bool(UIField.DISABLE_WIN_TRACK_TOGGLE),
        UIField.RECORD_FIGHTS_TOGGLE.value: as_bool(UIField.RECORD_FIGHTS_TOGGLE),
        UIField.RECORDING_FOLDER_PATH.value: as_str(UIField.RECORDING_FOLDER_PATH),
    }

    job_dictionary["upgrade_user_toggle"] = as_bool(UIField.CARD_UPGRADE_USER_TOGGLE)
    job_dictionary[UIField.UPGRADE_PRINCESS_USER_TOGGLE.value] = as_bool(
        UIField.UPGRADE_PRINCESS_USER_TOGGLE,
    )

    if values.get(UIField.DIRECTX_TOGGLE.value):
        job_dictionary["memu_render_mode"] = "directx"
    else:
        job_dictionary["memu_render_mode"] = "opengl"

    if values.get(UIField.BS_RENDERER_DX.value):
        job_dictionary["bluestacks_render_mode"] = "dx"
    elif values.get(UIField.BS_RENDERER_VK.value):
        job_dictionary["bluestacks_render_mode"] = "vlcn"
    elif values.get(UIField.BS_RENDERER_GL.value):
        job_dictionary["bluestacks_render_mode"] = "gl"
    else:
        job_dictionary["bluestacks_render_mode"] = "vlcn" if is_macos() else "gl"

    if values.get(UIField.GOOGLE_PLAY_EMULATOR_TOGGLE.value):
        job_dictionary["emulator"] = EmulatorType.GOOGLE_PLAY
    elif values.get(UIField.BLUESTACKS_EMULATOR_TOGGLE.value):
        job_dictionary["emulator"] = EmulatorType.BLUESTACKS
    elif values.get(UIField.ADB_TOGGLE.value):
        job_dictionary["emulator"] = EmulatorType.ADB
    else:
        job_dictionary["emulator"] = EmulatorType.MEMU

    adb_serial = values.get(UIField.ADB_SERIAL.value)
    job_dictionary[UIField.ADB_SERIAL.value] = adb_serial.strip() if adb_serial else None

    gp_serial = values.get(UIField.GP_DEVICE_SERIAL.value)
    job_dictionary[UIField.GP_DEVICE_SERIAL.value] = gp_serial.strip() if gp_serial else None

    bs_serial = values.get(UIField.BS_DEVICE_SERIAL.value)
    job_dictionary[UIField.BS_DEVICE_SERIAL.value] = bs_serial.strip() if bs_serial else None

    return job_dictionary
