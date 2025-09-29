import re
import subprocess
import time

import cv2
import numpy as np

# Assuming these are in the correct path
from pyclashbot.bot.nav import check_if_on_clash_main_menu
from pyclashbot.emulators.base import BaseEmulatorController

# Set to True for verbose ADB command logging
DEBUG = False


class AdbController(BaseEmulatorController):
    """
    Controller for a Android device/emulator using ADB.
    This class implements the BaseEmulatorController interface to interact with a
    physical/emulator Android device connected via USB or Wi-Fi.
    """

    def __init__(self, logger, device_serial: str | None = None):
        """
        Initializes the controller and connects to the adb device.
        Args:
            logger: The logger instance for status updates.
            device_serial (str, optional): The specific serial number of the device
                                           to connect to. If None, it will try to
                                           find a single connected device.
        """
        self.logger = logger
        self.device_serial = device_serial
        self._auto_stop_on_del = False  # No process to stop

        # For storing original screen settings
        self.original_size = None
        self.original_density = None

        self.logger.change_status("Connecting to ADB device...")

        if self.device_serial is None:
            self._discover_device()

        self.logger.log(f"Targeting device with serial: {self.device_serial}")

        # Verify connection
        if not self._is_connected():
            raise ConnectionError(
                f"Failed to connect to device {self.device_serial}. "
                "Ensure USB debugging is enabled and the device is authorized."
            )

        self.logger.log(f"Successfully connected to {self.device_serial}.")

        # automatically handle screen size and density
        self.handle_screen_size_and_density()

        # In the context of a real device, the initial 'restart' is just to get the app running
        if not self.restart():
            raise RuntimeError("Initial restart of Clash Royale failed on the physical device.")

    def get_screen_props(self):
        """Gets the current screen size and density of the device."""
        size_result = self.adb("shell wm size")
        density_result = self.adb("shell wm density")

        size = None
        density = None

        if size_result.returncode == 0:
            output = size_result.stdout.strip()
            # Physical size: 1080x2340
            match = re.search(r"Physical size: (\d+x\d+)", output)
            if match:
                size = match.group(1)

        if density_result.returncode == 0:
            output = density_result.stdout.strip()
            # Physical density: 420
            match = re.search(r"Physical density: (\d+)", output)
            if match:
                density = int(match.group(1))

        return size, density

    def handle_screen_size_and_density(self):
        """
        Checks the current screen size and density, sets them to the required values if they are not already set,
        and stores the original values for later restoration.
        """
        self.logger.log("Checking screen size and density...")
        current_size, current_density = self.get_screen_props()

        required_size = "419x633"
        required_density = 160

        # Store original values if they haven't been stored yet
        if self.original_size is None and current_size is not None:
            self.original_size = current_size
            self.logger.log(f"Stored original screen size: {self.original_size}")
        if self.original_density is None and current_density is not None:
            self.original_density = current_density
            self.logger.log(f"Stored original screen density: {self.original_density}")

        # Check and set size
        if current_size != required_size:
            self.logger.log(f"Current size {current_size} is not the required {required_size}. Setting it now.")
            self.set_screen_size(419, 633)
        else:
            self.logger.log("Screen size is already correct.")

        # Check and set density
        if current_density != required_density:
            self.logger.log(
                f"Current density {current_density} is not the required {required_density}. Setting it now."
            )
            self.set_screen_density(required_density)
        else:
            self.logger.log("Screen density is already correct.")

    def restore_original_screen_props(self):
        """Restores the original screen size and density."""
        if self.original_size:
            self.logger.log(f"Restoring original screen size: {self.original_size}")
            self.adb(f"shell wm size {self.original_size}")
        if self.original_density:
            self.logger.log(f"Restoring original screen density: {self.original_density}")
            self.adb(f"shell wm density {self.original_density}")

    @staticmethod
    def list_devices():
        """Lists all connected ADB devices."""
        result = subprocess.run(
            "adb devices",
            shell=True,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return []

        lines = result.stdout.strip().splitlines()
        devices = []
        for line in lines[1:]:  # Skip the "List of devices attached" header
            if "\tdevice" in line:
                serial = line.split("\t")[0]
                devices.append(serial)
        return devices

    @staticmethod
    def connect_device(logger, device_address: str) -> bool:
        """Connects to a device via ADB over network or confirms a USB connection."""
        if not device_address:
            logger.change_status("Device address cannot be empty.")
            return False

        # If device is already in the list (e.g., USB connected), no need to connect.
        if device_address in AdbController.list_devices():
            logger.change_status(f"Device {device_address} is already connected.")
            return True

        command = f"adb connect {device_address}"
        try:
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=False,
            )
            output = process.stdout.strip()
            logger.change_status(output)
            if "connected" in output or "already connected" in output:
                return True
            logger.change_status(f"Failed to connect: {process.stderr.strip()}")
            return False
        except FileNotFoundError:
            logger.change_status("ADB command not found. Make sure ADB is installed and in your PATH.")
            return False
        except subprocess.CalledProcessError as e:
            logger.change_status(f"Error connecting to {device_address}: {e.stderr.strip()}")
            return False

    def _discover_device(self):
        """Discovers a single connected device if no serial is provided."""
        self.logger.log("No device serial provided, attempting to auto-discover...")
        devices = self.list_devices()

        if not devices:
            raise ConnectionError("No ADB devices found. Check your connection and USB debugging settings.")

        if len(devices) > 1:
            raise ConnectionError(
                f"Multiple devices found: {devices}. Please specify the device serial during initialization."
            )

        self.device_serial = devices[0]
        self.logger.log(f"Auto-discovered device: {self.device_serial}")

    def _is_connected(self) -> bool:
        """Checks if the target device is connected and in 'device' state."""
        state = self.adb("get-state").stdout.strip()
        return state == "device"

    def adb(self, command: str, binary_output: bool = False, use_serial: bool = True) -> subprocess.CompletedProcess:
        """
        Runs an ADB command targeting the specified device.
        Args:
            command (str): The ADB command to execute (e.g., "shell input tap 100 200").
            binary_output (bool): If True, captures stdout as bytes. Defaults to False.
            use_serial (bool): If True, prepends the command with '-s <serial>'. Defaults to True.
        Returns:
            subprocess.CompletedProcess: The result of the command execution.
        """
        if use_serial and self.device_serial:
            full_command = f"adb -s {self.device_serial} {command}"
        else:
            full_command = f"adb {command}"

        if DEBUG:
            print(f"[Android/ADB] {full_command}")

        return subprocess.run(
            full_command,
            shell=True,
            capture_output=True,
            text=not binary_output,
            check=False,
        )

    def set_screen_size(self, width: int, height: int):
        """Sets the screen size of the device."""
        self.logger.log(f"Setting screen size to {width}x{height}")
        result = self.adb(f"shell wm size {width}x{height}")
        if result.returncode == 0:
            self.logger.log("Screen size set successfully.")
        else:
            self.logger.log(f"Failed to set screen size: {result.stderr}")

    def set_screen_density(self, density: int):
        """Sets the screen density of the device."""
        self.logger.log(f"Setting screen density to {density}")
        result = self.adb(f"shell wm density {density}")
        if result.returncode == 0:
            self.logger.log("Screen density set successfully.")
        else:
            self.logger.log(f"Failed to set screen density: {result.stderr}")

    def reset_screen_size(self):
        """Resets the screen size of the device to its default."""
        self.logger.log("Resetting screen size.")
        result = self.adb("shell wm size reset")
        if result.returncode == 0:
            self.logger.log("Screen size reset successfully.")
        else:
            self.logger.log(f"Failed to reset screen size: {result.stderr}")

    def reset_screen_density(self):
        """Resets the screen density of the device to its default."""
        self.logger.log("Resetting screen density.")
        result = self.adb("shell wm density reset")
        if result.returncode == 0:
            self.logger.log("Screen density reset successfully.")
        else:
            self.logger.log(f"Failed to reset screen density: {result.stderr}")

    ## No-Op Methods (Not applicable to physical devices) ##

    def create(self):
        """Not applicable for a real device. Does nothing."""
        self.logger.log("Create method is not applicable for a physical device.")
        pass

    def configure(self):
        """Not applicable for a real device. Does nothing."""
        self.logger.log("Configure method is not applicable for a physical device.")
        pass

    def start(self):
        """Not applicable for a real device. Assumes the device is already on."""
        self.logger.log("Start method is not applicable for a physical device.")
        pass

    def stop(self):
        """
        Restores the original screen properties when the bot stops.
        """
        self.logger.log("Stop method called. Restoring original screen properties.")
        self.restore_original_screen_props()
        pass

    ## Implemented Methods ##

    def restart(self) -> bool:
        """
        Restarts the Clash Royale app to ensure a clean state.
        This method will:
        1. Force-stop the app.
        2. Start the app.
        3. Wait for the main menu to appear.
        Returns:
            bool: True if the app was successfully restarted and the main menu is found, False otherwise.
        """
        start_ts = time.time()
        self.logger.change_status("Restarting Clash Royale on device...")

        clash_pkg = "com.supercell.clashroyale"

        # 1. Force stop the app
        self.logger.change_status(f"Force-stopping {clash_pkg}...")
        self.adb(f"shell am force-stop {clash_pkg}")
        time.sleep(3)

        # 2. Start the app
        self.logger.change_status("Launching Clash Royale...")
        self.start_app(clash_pkg)
        time.sleep(5)  # Give the app some time to load initially

        # 3. Wait for main menu
        self.logger.change_status("Waiting for Clash Royale main menu...")
        deadline = time.time() + 240  # 4-minute timeout
        while time.time() < deadline:
            if check_if_on_clash_main_menu(self):
                self.logger.change_status("Clash Royale main menu detected.")
                dur = f"{time.time() - start_ts:.1f}s"
                self.logger.log(f"App restart completed in {dur}")
                return True

            # Click in a safe area to dismiss potential pop-ups
            self.click(5, 350)
            time.sleep(2)

        self.logger.change_status("Timeout waiting for Clash Royale main menu. Please check the device.")
        return False

    def click(self, x_coord: int, y_coord: int, clicks: int = 1, interval: float = 0.1):
        """Clicks on the device screen at the given coordinates."""
        for _ in range(max(1, clicks)):
            self.adb(f"shell input tap {x_coord} {y_coord}")
            if clicks > 1:
                time.sleep(max(0.0, interval))

    def swipe(self, x_coord1: int, y_coord1: int, x_coord2: int, y_coord2: int):
        """
        Swipes on the device screen from one coordinate to another.
        """
        self.adb(f"shell input swipe {x_coord1} {y_coord1} {x_coord2} {y_coord2}")

    def screenshot(self) -> np.ndarray:
        """Takes a screenshot of the device screen."""
        if not self._is_connected():
            raise ConnectionError(f"Device {self.device_serial} is not connected.")

        result = self.adb("exec-out screencap -p", binary_output=True)

        if result.returncode != 0 or not result.stdout:
            err = result.stderr if result.stderr else b"Unknown ADB error"
            raise RuntimeError(f"ADB screencap failed: {err.decode('utf-8', 'ignore')}")

        # Convert raw PNG data to an OpenCV image
        img_array = np.frombuffer(result.stdout, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Failed to decode screenshot. The image data might be corrupt.")

        return img

    def start_app(self, package_name: str):
        """Starts an application on the device."""
        res = self.adb("shell pm list packages")
        if res.stdout and package_name not in res.stdout:
            self.logger.log(f"Package '{package_name}' not found on device.")
            # This triggers the UI prompt for the user to install the app manually
            return self._wait_for_clash_installation(package_name)

        self.adb(f"shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
        return True

    def _retry_installation_check(self):
        """Callback method triggered by the user clicking 'Retry' in the UI."""
        self.logger.change_status("Re-checking for Clash Royale installation...")
        package_name = getattr(self, "current_package_name", "com.supercell.clashroyale")
        result = self.adb("shell pm list packages")

        if result.stdout and package_name in result.stdout:
            self.installation_waiting = False  # Ends the waiting loop in _wait_for_clash_installation
            self.logger.change_status("Installation confirmed. Continuing...")
        else:
            # Re-show the prompt if the app is still not found
            self.logger.show_temporary_action(
                message="Still not found. Please install Clash Royale and complete the tutorial.",
                action_text="Retry",
                callback=self._retry_installation_check,
            )
            self.logger.log(f"[!] {package_name} is still not installed.")
