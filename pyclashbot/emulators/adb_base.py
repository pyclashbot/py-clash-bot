import logging
import os
import re
import subprocess
from abc import ABC

import cv2
import numpy as np

from pyclashbot.emulators.base import BaseEmulatorController
from pyclashbot.utils.cancellation import interruptible_sleep
from pyclashbot.utils.platform import is_linux

logger = logging.getLogger(__name__)

# Valid device serial patterns to prevent command injection
_DEVICE_SERIAL_PATTERNS = [
    re.compile(r"^localhost:\d{1,5}$"),  # localhost:6520
    re.compile(r"^127\.0\.0\.1:\d{1,5}$"),  # 127.0.0.1:5567
    re.compile(r"^(\d{1,3}\.){3}\d{1,3}:\d{1,5}$"),  # Any IP:port
    re.compile(r"^[a-zA-Z0-9._-]+:\d{1,5}$"),  # hostname:port
    re.compile(r"^emulator-\d+$"),  # emulator-5554
    re.compile(r"^[A-Za-z0-9]{6,}$"),  # USB serial (hex/alphanum)
]


def validate_device_serial(serial: str | None) -> bool:
    """Validate device serial format to prevent command injection.

    Returns True if serial is None (will use auto-discovery) or matches
    a known safe pattern.
    """
    if serial is None:
        return True
    serial = serial.strip()
    if not serial:
        return True  # Empty treated as None
    return any(pattern.match(serial) for pattern in _DEVICE_SERIAL_PATTERNS)


class AdbBasedController(BaseEmulatorController, ABC):
    """
    Abstract base class for emulator controllers that use ADB.

    This class provides concrete implementations for common ADB operations
    (click, swipe, screenshot, start_app, installation waiting, device listing)
    with configurable ADB path, server port, and environment.

    Subclasses must set before using ADB methods:
    - device_serial: str | None (the ADB device serial to target)

    Subclasses may override these properties for custom ADB configuration:
    - adb_path: str (default: "adb" for system ADB)
    - adb_server_port: int | None (default: None, no custom port)
    - adb_env: dict | None (default: None, inherit environment)
    """

    device_serial: str | None = None

    adb_path: str = "adb"
    adb_server_port: int | None = None
    adb_env: dict | None = None

    @classmethod
    def find_adb(cls) -> str | None:
        """Find ADB executable. Override in subclasses for bundled ADB."""
        return None  # Default: use system adb

    @classmethod
    def discover_devices(cls) -> list[str]:
        """List connected ADB device serials using this controller's ADB."""
        adb_path = cls.find_adb() or "adb"
        try:
            result = subprocess.run(
                f'"{adb_path}" devices',
                shell=True,
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError:
            return []  # ADB not available
        if result.returncode != 0:
            return []
        devices = []
        for line in result.stdout.strip().splitlines()[1:]:
            if "\tdevice" in line:
                devices.append(line.split("\t")[0])
        return devices

    @classmethod
    def is_device_connected(cls, device_serial: str | None) -> bool:
        """Check if a device serial is in the connected devices list."""
        if not device_serial:
            return False
        return device_serial in cls.discover_devices()

    def _is_server_command(self, command: str) -> bool:
        """Check if command targets ADB server rather than a specific device.

        Server commands should not have -s device_serial added.
        """
        c = command.strip()
        if re.search(r"-s\s+\S+", c):
            return True  # Already device-scoped
        first = c.split()[0] if c else ""
        return first in {
            "connect",
            "disconnect",
            "devices",
            "start-server",
            "kill-server",
            "version",
            "help",
            "keys",
        }

    def adb(self, command: str, binary_output: bool = False) -> subprocess.CompletedProcess:
        """
        Execute an ADB command with automatic device scoping.

        Builds the command with the configured ADB path, optional server port,
        and device serial (unless it's a server-level command).

        Args:
            command (str): The ADB command to execute (e.g., "shell input tap 1 2").
            binary_output (bool): Whether to capture stdout as bytes (True) or
                                  decode as text (False).

        Returns:
            subprocess.CompletedProcess: The result of the ADB command.

        Raises:
            ValueError: If device_serial contains invalid characters.
        """
        if self.device_serial and not validate_device_serial(self.device_serial):
            raise ValueError(f"Invalid device serial format: {self.device_serial}")

        parts = [f'"{self.adb_path}"']

        if self.adb_server_port:
            parts.append(f"-P {self.adb_server_port}")

        if not self._is_server_command(command) and self.device_serial:
            parts.append(f"-s {self.device_serial}")

        parts.append(command)
        full_command = " ".join(parts)

        logger.debug("Executing ADB: %s", full_command)

        kwargs: dict = {
            "shell": True,
            "capture_output": True,
            "text": not binary_output,
        }

        if self.adb_env:
            kwargs["env"] = self.adb_env

        if is_linux():
            kwargs["preexec_fn"] = os.setsid

        result = subprocess.run(full_command, check=False, **kwargs)

        if binary_output:
            logger.debug("ADB result: rc=%d, stdout=%d bytes", result.returncode, len(result.stdout or b""))
        else:
            stdout_preview = (result.stdout or "")[:200]
            logger.debug("ADB result: rc=%d, stdout=%r", result.returncode, stdout_preview)

        if result.returncode != 0 and result.stderr:
            stderr_msg = (
                result.stderr.strip()
                if isinstance(result.stderr, str)
                else result.stderr.decode("utf-8", "ignore").strip()
            )
            if stderr_msg:
                logger.warning("ADB command failed (rc=%d): %s", result.returncode, stderr_msg)

        return result

    def _check_app_installed(self, package_name: str) -> bool:
        """Check if an app is installed via ADB.

        Args:
            package_name (str): The package name to check (e.g., "com.supercell.clashroyale").

        Returns:
            bool: True if the app is installed, False otherwise.
        """
        logger.debug("Checking if app is installed: %s", package_name)
        result = self.adb("shell pm list packages")
        installed = result.stdout is not None and package_name in result.stdout
        if installed:
            logger.info("App %s is installed", package_name)
        else:
            logger.info("App %s is NOT installed", package_name)
        return installed

    def list_devices(self) -> list[tuple[str, str]]:
        """List all ADB devices with their status.

        Returns:
            list of (serial, status) tuples, e.g., [("localhost:6520", "device"), ("emulator-5554", "offline")]
        """
        result = self.adb("devices")
        devices = []
        if result.stdout:
            for line in result.stdout.strip().splitlines()[1:]:
                parts = line.split()
                if len(parts) >= 2:
                    devices.append((parts[0], parts[1]))

        logger.info("Found %d ADB device(s): %s", len(devices), devices)

        for serial, status in devices:
            if status == "offline":
                logger.warning("Device %s is offline - may need reconnection", serial)
            elif status == "unauthorized":
                logger.warning("Device %s is unauthorized - check USB debugging authorization on device", serial)

        return devices

    def list_online_devices(self) -> list[str]:
        """List serials of online (status='device') devices only."""
        return [serial for serial, status in self.list_devices() if status == "device"]

    def click(self, x_coord: int, y_coord: int, clicks: int = 1, interval: float = 0.0):
        """Click on the screen using ADB input tap."""
        for _ in range(max(1, clicks)):
            self.adb(f"shell input tap {x_coord} {y_coord}")
            if clicks > 1:
                interruptible_sleep(max(0.0, interval))

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
            error_msg = err.decode("utf-8", "ignore")
            logger.error("Screenshot capture failed: %s", error_msg)
            raise RuntimeError(f"ADB screencap failed: {error_msg}")

        img_array = np.frombuffer(result.stdout, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img is None:
            logger.error("Failed to decode screenshot data (%d bytes)", len(result.stdout))
            raise ValueError("Failed to decode screenshot. Image data may be corrupt or empty.")

        logger.debug("Screenshot captured: %dx%d", img.shape[1], img.shape[0])
        return img

    def start_app(self, package_name: str):
        """
        Start an app using ADB monkey command.

        If the app is not installed, it will trigger the
        installation waiting mechanism.

        Args:
            package_name (str): The package name to start.

        Returns:
            True if the app was started or if the installation
            wait was successfully initiated and completed.
        """
        if not self._check_app_installed(package_name):
            return self._wait_for_clash_installation(package_name)

        logger.info("Launching app: %s", package_name)
        self.adb(f"shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
        return True

    def _wait_for_clash_installation(self, package_name: str):
        """
        Show a UI prompt and wait for the user to install the specified app.
        """
        self.current_package_name = package_name
        logger.warning("App %s not installed - waiting for user to install", package_name)

        if hasattr(self, "logger") and hasattr(self.logger, "show_temporary_action"):
            self.logger.show_temporary_action(
                message=f"{package_name} not installed - please install it and complete tutorial",
                action_text="Retry",
                callback=self._retry_installation_check,
            )

        self.installation_waiting = True

        while self.installation_waiting:
            interruptible_sleep(0.5)

        logger.info("App %s installation confirmed", package_name)
        return True

    def _retry_installation_check(self):
        """
        Callback method for the 'Retry' button. Checks if the app has been installed.
        """
        logger.debug("Retry clicked - checking for app installation")

        package_name = getattr(self, "current_package_name", "com.supercell.clashroyale")

        if self._check_app_installed(package_name):
            self.installation_waiting = False
            logger.info("App %s now installed", package_name)
        else:
            logger.warning("App %s still not installed", package_name)
            if hasattr(self, "logger") and hasattr(self.logger, "show_temporary_action"):
                self.logger.show_temporary_action(
                    message=f"{package_name} still not found - please install it and complete tutorial",
                    action_text="Retry",
                    callback=self._retry_installation_check,
                )
