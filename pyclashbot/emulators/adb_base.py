import logging
import subprocess
import time
from abc import ABC, abstractmethod

import cv2
import numpy as np

from pyclashbot.emulators.base import AppNotInstalledError, BaseEmulatorController


class AdbBasedController(BaseEmulatorController, ABC):
    """
    Abstract base class for emulator controllers that use ADB.

    This class provides concrete implementations for common ADB operations
    (click, swipe, screenshot, start_app, installation waiting)
    by leveraging an abstract `adb` method that subclasses must implement.

    Subclasses must implement:
    - adb(command, binary_output) -> subprocess.CompletedProcess
    - _check_app_installed(package_name) -> bool
    """

    # === Abstract methods (must be implemented by subclasses) ===

    @abstractmethod
    def adb(self, command: str, binary_output: bool = False) -> subprocess.CompletedProcess:
        """
        Execute an ADB command.

        Implementation varies by emulator (e.g., system ADB, bundled ADB,
        private server) and must be provided by the subclass.

        Args:
            command (str): The ADB command to execute (e.g., "shell input tap 1 2").
            binary_output (bool): Whether to capture stdout as bytes (True) or
                                  decode as text (False).

        Returns:
            subprocess.CompletedProcess: The result of the ADB command.
        """
        raise NotImplementedError

    @abstractmethod
    def _check_app_installed(self, package_name: str) -> bool:
        """
        Check if an app is installed using the emulator's specific ADB mechanism.

        Args:
            package_name (str): The package name to check (e.g., "com.supercell.clashroyale").

        Returns:
            bool: True if the app is installed, False otherwise.
        """
        raise NotImplementedError

    # === Concrete shared methods (inherited by all subclasses) ===

    def click(self, x_coord: int, y_coord: int, clicks: int = 1, interval: float = 0.0):
        """Click on the screen using ADB input tap."""
        for _ in range(max(1, clicks)):
            self.adb(f"shell input tap {x_coord} {y_coord}")
            if clicks > 1:
                time.sleep(max(0.0, interval))

    def swipe(self, x_coord1: int, y_coord1: int, x_coord2: int, y_coord2: int):
        """Swipe on the screen using ADB input swipe."""
        self.adb(f"shell input swipe {x_coord1} {y_coord1} {x_coord2} {y_coord2}")

    def screenshot(self) -> np.ndarray:
        """
        Capture a screenshot using ADB 'exec-out screencap -p'.

        Returns:
            np.ndarray: The screenshot as a CV2 (BGR) image.

        Raises:
            RuntimeError: If the ADB screencap command fails.
            ValueError: If the captured image data cannot be decoded.
        """
        result = self.adb("exec-out screencap -p", binary_output=True)

        if result.returncode != 0 or not result.stdout:
            err = result.stderr if result.stderr else b"Unknown ADB error"
            raise RuntimeError(f"ADB screencap failed: {err.decode('utf-8', 'ignore')}")

        img_array = np.frombuffer(result.stdout, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Failed to decode screenshot. Image data may be corrupt or empty.")

        return img

    def start_app(self, package_name: str):
        """
        Start an app using ADB monkey command.

        If the app is not installed, raises AppNotInstalledError.

        Args:
            package_name (str): The package name to start.

        Raises:
            AppNotInstalledError: If the app is not installed.

        Returns:
            True if the app was started successfully.
        """
        if not self._check_app_installed(package_name):
            # App not found, raise exception for caller to handle
            logging.info(f"App {package_name} is not installed")
            raise AppNotInstalledError(package_name)

        # App is installed, launch it
        logging.info(f"Launching app: {package_name}")
        self.adb(f"shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
        return True
