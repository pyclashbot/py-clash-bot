import logging
import os
import re
import subprocess
import time
from abc import ABC

import cv2
import numpy as np

from pyclashbot.emulators.base import (
    BaseEmulatorController,
    EmulatorNotReadyError,
)
from pyclashbot.utils.platform import is_linux

logger = logging.getLogger(__name__)

# Valid device serial patterns to prevent command injection
_DEVICE_SERIAL_PATTERNS = [
    re.compile(r"^[a-zA-Z0-9._-]+:\d{1,5}$"),  # host:port (localhost, IP, hostname)
    re.compile(r"^emulator-\d+$"),  # emulator-5554
    re.compile(r"^[A-Za-z0-9]{6,}$"),  # USB serial
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
        parts = [f'"{adb_path}"']
        if cls.adb_server_port:
            parts.append(f"-P {cls.adb_server_port}")
        parts.append("devices")
        full_command = " ".join(parts)
        try:
            result = subprocess.run(
                full_command,
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
        if re.match(r"-s\s+\S+", c):
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

    def is_app_installed(self, package: str) -> bool:
        return self._check_app_installed(package)

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

        Args:
            package_name (str): The package name to start.

        Returns:
            True if the app was launched.

        Raises:
            EmulatorNotReadyError: If the app is not installed.
        """
        if not self._check_app_installed(package_name):
            raise EmulatorNotReadyError(f"{package_name} is not installed on the emulator")

        logger.info("Launching app: %s", package_name)
        self.adb(f"shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
        return True
