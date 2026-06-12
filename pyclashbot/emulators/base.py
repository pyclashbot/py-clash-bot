import numpy as np

from pyclashbot.utils.platform import CURRENT_PLATFORM, Platform

CLASH_ROYALE_PACKAGE = "com.supercell.clashroyale"


class EmulatorNotReadyError(RuntimeError):
    """The emulator can't be made ready (app missing, signed out, no main menu) —
    raised by `restart()` instead of waiting forever. Callers either stop the bot
    (first boot) or fold it into the bounded mid-run restart net."""


class BaseEmulatorController:
    """
    Base class for emulator controllers.
    This class is used to define the interface for all emulator controllers.
    """

    supported_platforms: list[Platform] = []

    @classmethod
    def is_supported_on_current_platform(cls) -> bool:
        """Check if this emulator is supported on the current platform."""
        return CURRENT_PLATFORM in cls.supported_platforms

    def __init__(self):
        raise NotImplementedError

    def __del__(self):
        # Avoid raising in destructor, subclasses may optionally implement cleanup.
        # Allow controllers to opt out by setting "_auto_stop_on_del = False".
        try:
            if getattr(self, "_auto_stop_on_del", True):  # type: ignore[attr-defined]
                self.stop()  # type: ignore[attr-defined]
        except Exception:
            pass

    def create(self):
        """
        This method is used to create the emulator.
        """
        raise NotImplementedError

    def configure(self):
        """
        This method is used to configure the emulator.
        """
        raise NotImplementedError

    def restart(self) -> bool:
        """
        Full boot -> configure -> launch Clash -> reach main menu.

        The single boot primitive, called explicitly after construction (and again
        for mid-run recovery). One attempt: it returns True once Clash Royale is
        left on a main menu detectable by check_if_on_clash_main_menu(self), and
        raises EmulatorNotReadyError on any not-ready failure — it never returns
        False.
        """
        raise NotImplementedError

    def is_reachable(self) -> tuple[bool, str]:
        """Return (ok, reason). Default: a screenshot decodes to a non-empty array."""
        try:
            screenshot = self.screenshot()
        except Exception as e:
            return (False, f"screenshot raised {type(e).__name__}: {e}")
        if screenshot is None or getattr(screenshot, "size", 0) == 0:
            return (False, "screenshot returned empty")
        return (True, "")

    def is_app_installed(self, package: str) -> bool:
        """Return whether the given package is installed on the emulator."""
        raise NotImplementedError

    def start(self):
        """
        This method is used to start the emulator.
        """
        raise NotImplementedError

    def stop(self):
        """
        This method is used to stop the emulator.
        """
        raise NotImplementedError

    def click(self, x_coord: int, y_coord: int, clicks: int, interval: float):
        """
        This method is used to click on the emulator screen.
        """
        raise NotImplementedError

    def swipe(
        self,
        x_coord1: int,
        y_coord1: int,
        x_coord2: int,
        y_coord2: int,
    ):
        """
        This method is used to swipe on the emulator screen.
        """
        raise NotImplementedError

    def screenshot(self) -> np.ndarray:
        """
        This method is used to take a screenshot of the emulator screen.
        """
        raise NotImplementedError

    def install_apk(self, apk_path: str):
        """
        This method is used to install an APK on the emulator.
        """
        raise NotImplementedError

    def start_app(self, package_name: str):
        """
        This method is used to start an app on the emulator.
        """
        raise NotImplementedError
