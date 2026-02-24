"""Emulator controllers for different platforms."""

from collections.abc import Callable
from enum import StrEnum
from typing import TYPE_CHECKING, Protocol

from pyclashbot.utils.platform import is_windows

if TYPE_CHECKING:
    from pyclashbot.emulators.base import BaseEmulatorController


class ActionCallback(Protocol):
    """Protocol for UI action prompts (e.g., 'Install app and click Retry')."""

    def __call__(
        self,
        message: str,
        action_text: str = "Retry",
        callback: Callable[[], None] | None = None,
    ) -> None:
        """Display a temporary action button to the user.

        Args:
            message: The message to display to the user
            action_text: Text for the action button (default: "Retry")
            callback: Function to call when user clicks the button
        """
        ...


class EmulatorType(StrEnum):
    """Available emulator types with display names."""

    MEMU = "MEmu"
    GOOGLE_PLAY = "Google Play"
    BLUESTACKS = "BlueStacks 5"
    ADB = "ADB Device"


def get_emulator_registry() -> dict[EmulatorType, type["BaseEmulatorController"]]:
    """Return mapping of emulator types to controller classes.

    Only imports modules that are supported on the current platform.
    """
    registry: dict[EmulatorType, type[BaseEmulatorController]] = {}

    # Always available - pure ADB, no platform-specific deps
    from pyclashbot.emulators.adb import AdbController

    registry[EmulatorType.ADB] = AdbController

    # BlueStacks - supports both Windows and macOS
    from pyclashbot.emulators.bluestacks import BlueStacksEmulatorController

    registry[EmulatorType.BLUESTACKS] = BlueStacksEmulatorController

    # Windows-only emulators
    if is_windows():
        from pyclashbot.emulators.google_play import GooglePlayEmulatorController
        from pyclashbot.emulators.memu import MemuEmulatorController

        registry[EmulatorType.GOOGLE_PLAY] = GooglePlayEmulatorController
        registry[EmulatorType.MEMU] = MemuEmulatorController

    return registry


def get_available_emulators() -> list[EmulatorType]:
    """Return list of emulator types supported on current platform."""
    return [emu_type for emu_type, cls in get_emulator_registry().items() if cls.is_supported_on_current_platform()]
