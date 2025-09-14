import numpy as np


class BaseEmulatorController:
    """
    Base class for emulator controllers.
    This class is used to define the interface for all emulator controllers.
    """

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

    def restart(self):
        """
        This method is used to restart the emulator.
        """
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
