import logging
import re
import subprocess
import time

from pyclashbot.bot.nav import check_if_on_clash_main_menu
from pyclashbot.emulators import ActionCallback
from pyclashbot.emulators.adb_base import AdbBasedController, validate_device_serial
from pyclashbot.utils.cancellation import interruptible_sleep
from pyclashbot.utils.platform import Platform

logger = logging.getLogger(__name__)


class AdbController(AdbBasedController):
    """
    Controller for a Android device/emulator using ADB.
    This class implements the BaseEmulatorController interface to interact with a
    physical/emulator Android device connected via USB or Wi-Fi.

    It now inherits shared ADB logic from AdbBasedController.
    """

    supported_platforms = [Platform.WINDOWS, Platform.MACOS, Platform.LINUX]

    def __init__(
        self,
        device_serial: str | None = None,
        action_callback: ActionCallback | None = None,
    ):
        """
        Initializes the controller and connects to the adb device.
        Args:
            device_serial (str, optional): The specific serial number of the device
                                           to connect to. If None, it will try to
                                           find a single connected device.
            action_callback: Optional callback for UI action prompts.
        """
        self.device_serial: str | None = device_serial
        self._action_callback = action_callback
        self._auto_stop_on_del = False  # No process to stop

        # For storing original screen settings
        self.original_size = None
        self.original_density = None

        logger.info("Connecting to ADB device...")

        if self.device_serial is None:
            self._discover_device()

        logger.info("Targeting device with serial: %s", self.device_serial)

        # Verify connection
        if not self._is_connected():
            raise ConnectionError(
                f"Failed to connect to device {self.device_serial}. "
                "Ensure USB debugging is enabled and the device is authorized."
            )

        logger.info("Successfully connected to %s.", self.device_serial)

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
        logger.info("Checking screen size and density...")
        current_size, current_density = self.get_screen_props()

        required_size = "419x633"
        required_density = 160

        # Store original values if they haven't been stored yet
        if self.original_size is None and current_size is not None:
            self.original_size = current_size
            logger.info("Stored original screen size: %s", self.original_size)
        if self.original_density is None and current_density is not None:
            self.original_density = current_density
            logger.info("Stored original screen density: %s", self.original_density)

        # Check and set size
        if current_size != required_size:
            logger.info("Current size %s is not the required %s. Setting it now.", current_size, required_size)
            self.set_screen_size(419, 633)
        else:
            logger.info("Screen size is already correct.")

        # Check and set density
        if current_density != required_density:
            logger.info("Current density %s is not the required %s. Setting it now.", current_density, required_density)
            self.set_screen_density(required_density)
        else:
            logger.info("Screen density is already correct.")

    def restore_original_screen_props(self):
        """Restores the original screen size and density."""
        if self.original_size:
            logger.info("Restoring original screen size: %s", self.original_size)
            self.adb(f"shell wm size {self.original_size}")
        if self.original_density:
            logger.info("Restoring original screen density: %s", self.original_density)
            self.adb(f"shell wm density {self.original_density}")

    @staticmethod
    def discover_system_devices():
        """Lists all connected ADB devices (static, for pre-instantiation discovery).

        Use this for device discovery before creating a controller instance.
        For runtime device listing, use the inherited list_devices() method instead.
        """
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
    def connect_device(device_address: str) -> bool:
        """Connects to a device via ADB over network or confirms a USB connection."""
        if not device_address:
            logger.warning("Device address cannot be empty.")
            return False

        if not validate_device_serial(device_address):
            logger.warning("Invalid device address format: %s", device_address)
            return False

        # If device is already in the list (e.g., USB connected), no need to connect.
        if device_address in AdbController.discover_system_devices():
            logger.info("Device %s is already connected.", device_address)
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
            logger.info("%s", output)
            if "connected" in output or "already connected" in output:
                return True
            logger.warning("Failed to connect: %s", process.stderr.strip())
            return False
        except FileNotFoundError:
            logger.error("ADB command not found. Make sure ADB is installed and in your PATH.")
            return False
        except subprocess.CalledProcessError as e:
            logger.error("Error connecting to %s: %s", device_address, e.stderr.strip())
            return False

    def _discover_device(self):
        """Discovers a single connected device if no serial is provided."""
        logger.info("No device serial provided, attempting to auto-discover...")
        devices = self.discover_system_devices()

        if not devices:
            raise ConnectionError("No ADB devices found. Check your connection and USB debugging settings.")

        if len(devices) > 1:
            raise ConnectionError(
                f"Multiple devices found: {devices}. Please specify the device serial during initialization."
            )

        self.device_serial = devices[0]
        logger.info("Auto-discovered device: %s", self.device_serial)

    def _is_connected(self) -> bool:
        """Checks if the target device is connected and in 'device' state."""
        state = self.adb("get-state").stdout.strip()
        return state == "device"

    @staticmethod
    def restart_adb():
        """Restarts the ADB server."""
        logger.info("Restarting ADB server...")
        try:
            # Kill the server
            kill_result = subprocess.run(
                "adb kill-server",
                shell=True,
                capture_output=True,
                text=True,
                check=False,
            )
            if kill_result.returncode == 0:
                logger.info("ADB server killed successfully.")
            else:
                logger.warning("Failed to kill ADB server: %s", kill_result.stderr.strip())

            interruptible_sleep(1)

            # Start the server
            start_result = subprocess.run(
                "adb start-server",
                shell=True,
                capture_output=True,
                text=True,
                check=False,
            )
            if start_result.returncode == 0:
                logger.info("ADB server started successfully.")
                return True
            logger.warning("Failed to start ADB server: %s", start_result.stderr.strip())
            return False
        except FileNotFoundError:
            logger.error("ADB command not found. Make sure ADB is installed and in your PATH.")
            return False
        except subprocess.CalledProcessError as e:
            logger.error("Error restarting ADB server: %s", e.stderr.strip())
            return False

    def set_screen_size(self, width: int, height: int):
        """Sets the screen size of the device."""
        logger.info("Setting screen size to %dx%d", width, height)
        result = self.adb(f"shell wm size {width}x{height}")
        if result.returncode == 0:
            logger.info("Screen size set successfully.")
        else:
            logger.warning("Failed to set screen size: %s", result.stderr)

    def set_screen_density(self, density: int):
        """Sets the screen density of the device."""
        logger.info("Setting screen density to %d", density)
        result = self.adb(f"shell wm density {density}")
        if result.returncode == 0:
            logger.info("Screen density set successfully.")
        else:
            logger.warning("Failed to set screen density: %s", result.stderr)

    def reset_screen_size(self):
        """Resets the screen size of the device to its default."""
        logger.info("Resetting screen size.")
        result = self.adb("shell wm size reset")
        if result.returncode == 0:
            logger.info("Screen size reset successfully.")
        else:
            logger.warning("Failed to reset screen size: %s", result.stderr)

    def reset_screen_density(self):
        """Resets the screen density of the device to its default."""
        logger.info("Resetting screen density.")
        result = self.adb("shell wm density reset")
        if result.returncode == 0:
            logger.info("Screen density reset successfully.")
        else:
            logger.warning("Failed to reset screen density: %s", result.stderr)

    ## No-Op Methods (Not applicable to physical devices) ##

    def create(self):
        """Not applicable for a real device. Does nothing."""
        logger.debug("Create method is not applicable for a physical device.")

    def configure(self):
        """Not applicable for a real device. Does nothing."""
        logger.debug("Configure method is not applicable for a physical device.")

    def start(self):
        """Not applicable for a real device. Assumes the device is already on."""
        logger.debug("Start method is not applicable for a physical device.")

    def stop(self):
        """
        Restores the original screen properties when the bot stops.
        """
        logger.info("Stop method called. Restoring original screen properties.")
        self.restore_original_screen_props()

    ## Implemented Methods ##

    def restart(self) -> bool:
        """
        Restarts the Clash Royale app to ensure a clean state.
        This method will:
        1. Force-stop the app.
        2. Start the app (using the base class method).
        3. Wait for the main menu to appear.
        Returns:
            bool: True if the app was successfully restarted and the main menu is found, False otherwise.
        """
        start_ts = time.time()
        logger.info("Restarting Clash Royale on device...")

        clash_pkg = "com.supercell.clashroyale"

        # 1. Force stop the app
        logger.info("Force-stopping %s...", clash_pkg)
        self.adb(f"shell am force-stop {clash_pkg}")
        interruptible_sleep(3)

        # 2. Start the app using the inherited method
        logger.info("Launching Clash Royale...")
        if not self.start_app(clash_pkg):
            # This means the app isn't installed and the user is being prompted.
            # We can't proceed with the restart.
            logger.warning("App not installed. Restart cannot complete.")
            return False

        interruptible_sleep(5)  # Give the app some time to load initially

        # 3. Wait for main menu
        logger.info("Waiting for Clash Royale main menu...")
        deadline = time.time() + 240  # 4-minute timeout
        while time.time() < deadline:
            if check_if_on_clash_main_menu(self):
                logger.info("Clash Royale main menu detected.")
                dur = f"{time.time() - start_ts:.1f}s"
                logger.info("App restart completed in %s", dur)
                return True

            # Click in a safe area to dismiss potential pop-ups
            self.click(35, 405)
            interruptible_sleep(2)

        logger.warning("Timeout waiting for Clash Royale main menu. Please check the device.")
        return False

    # click() is now inherited from AdbBasedController
    # swipe() is now inherited from AdbBasedController
    # screenshot() is now inherited from AdbBasedController
    # start_app() is now inherited from AdbBasedController
    # _wait_for_clash_installation() is now inherited from AdbBasedController
    # _retry_installation_check() is now inherited from AdbBasedController
