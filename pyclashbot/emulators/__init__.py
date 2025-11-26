"""Emulator controllers for different platforms."""

from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyclashbot.emulators.base import BaseEmulatorController


class EmulatorType(StrEnum):
    """Available emulator types with display names."""

    MEMU = "MEmu"
    GOOGLE_PLAY = "Google Play"
    BLUESTACKS = "BlueStacks 5"
    ADB = "ADB Device"


def get_emulator_registry() -> dict[EmulatorType, type["BaseEmulatorController"]]:
    """Return mapping of emulator types to controller classes.

    Uses lazy import to avoid circular dependencies.
    """
    from pyclashbot.emulators.adb import AdbController
    from pyclashbot.emulators.bluestacks import BlueStacksEmulatorController
    from pyclashbot.emulators.google_play import GooglePlayEmulatorController
    from pyclashbot.emulators.memu import MemuEmulatorController

    return {
        EmulatorType.MEMU: MemuEmulatorController,
        EmulatorType.GOOGLE_PLAY: GooglePlayEmulatorController,
        EmulatorType.BLUESTACKS: BlueStacksEmulatorController,
        EmulatorType.ADB: AdbController,
    }


def get_available_emulators() -> list[EmulatorType]:
    """Return list of emulator types supported on current platform."""
    return [emu_type for emu_type, cls in get_emulator_registry().items() if cls.is_supported_on_current_platform()]
