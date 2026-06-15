import os
import time
import xml.etree.ElementTree as ET
from contextlib import suppress
from os.path import normpath

import psutil

from pyclashbot.bot.state_detect import check_if_on_clash_main_menu
from pyclashbot.emulators.adb_base import AdbBasedController
from pyclashbot.emulators.base import CLASH_ROYALE_PACKAGE, EmulatorNotReadyError
from pyclashbot.utils.cancellation import interruptible_sleep
from pyclashbot.utils.platform import Platform
from pyclashbot.utils.subprocess import run as run_command

DEBUG = False


class GooglePlayEmulatorController(AdbBasedController):
    supported_platforms = [Platform.WINDOWS]

    # Default device serial for Google Play Games emulator
    DEFAULT_DEVICE_SERIAL = "localhost:6520"

    @classmethod
    def find_adb(cls) -> str | None:
        """Find bundled adb.exe path, or None if not found."""
        try:
            install = cls._find_install_location()
            adb = os.path.join(install, "current", "emulator", "adb.exe")
            return adb if os.path.isfile(adb) else None
        except Exception:
            return None

    def __init__(self, logger, render_settings: dict | None = None, device_serial: str | None = None):
        self.logger = logger
        # Discovery/config only — no boot. restart() owns the boot sequence.
        self.render_settings = render_settings or {}

        # search for base installation folder
        self.base_folder = self._find_install_location()
        if not self.base_folder:
            raise FileNotFoundError("Google Play Games Developer Emulator not found.")

        # locate the executable
        self.emulator_executable_path = os.path.join(self.base_folder, "Bootstrapper.exe")

        # locate the config file
        # C:\Program Files\Google\Play Games Developer Emulator\current\service\Service.exe.config
        self.service_config_path = os.path.join(self.base_folder, "current", "service", "Service.exe.config")

        # locate the adb executable
        self.adb_path = self._find_adb_path()
        if DEBUG:
            print(f"[INIT DEBUG] ADB path found: {self.adb_path}")

        # verify all those paths exist
        for path in [
            self.base_folder,
            self.emulator_executable_path,
            self.service_config_path,
            self.adb_path,
        ]:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Required file or directory not found: {path}")
            elif DEBUG:
                print(f"[INIT DEBUG] Path verified: {path}")

        # Set device serial - use provided value or default
        self.device_serial: str = device_serial if device_serial else self.DEFAULT_DEVICE_SERIAL
        if DEBUG:
            print(f"[INIT DEBUG] Device serial set to: {self.device_serial}")

        # emulator config
        self.google_play_emulator_process_name = "Google Play Games on PC Emulator"
        self.expected_dims = (419, 633)

    def _get_settings_configuration(self):
        """
        Parses and returns the current EmulatorGpuGuestAngle settings as a dictionary.

        Returns:
            dict: e.g. {
                "angle": "true",
                "vulkan": "false",
                "gles": "false",
                "backend": "gfxstream",
                ...
            }
        """
        # Load and parse XML
        tree = ET.parse(self.service_config_path)
        root = tree.getroot()

        # Find EmulatorGpuGuestAngle setting
        xpath = ".//setting[@name='EmulatorGpuGuestAngle']/value"
        setting_node = root.find(xpath)

        if setting_node is None or not setting_node.text:
            raise ValueError("Could not find EmulatorGpuGuestAngle setting in XML.")

        # Parse the comma-separated key=value string into a dictionary
        config_dict = {}
        for pair in setting_node.text.strip().split(","):
            if "=" in pair:
                k, v = pair.strip().split("=")
                config_dict[k.strip()] = v.strip()

        return config_dict

    def _configure_settings(self, settings: dict):
        """
        Updates EmulatorGpuGuestAngle settings in the XML config using a user-provided dictionary.
        Only keys present in the dictionary will be modified.

        Parameters:
            settings (dict): e.g. {
                "angle": True,
                "vulkan": False,
                "gles": True,
                "backend": "gfxstream",
                ...
            }
        """
        while self._is_emulator_running():
            print("Clearing residual emulator process before overwriting settings...")
            self.stop()

        valid_keys = {"angle", "vulkan", "gles", "surfaceless", "egl", "backend", "wsi"}

        # Filter to valid keys only
        updates = {k: v for k, v in settings.items() if k in valid_keys and v is not None}

        if not updates:
            return

        # Load and parse XML
        tree = ET.parse(self.service_config_path)
        root = tree.getroot()

        # Find EmulatorGpuGuestAngle setting
        xpath = ".//setting[@name='EmulatorGpuGuestAngle']/value"
        setting_node = root.find(xpath)

        if setting_node is None or not setting_node.text:
            raise ValueError("Could not find EmulatorGpuGuestAngle setting in XML.")

        # Parse existing settings
        config_dict = {}
        for pair in setting_node.text.strip().split(","):
            if "=" in pair:
                k, v = pair.strip().split("=")
                config_dict[k.strip()] = v.strip()

        # Apply updates
        for k, v in updates.items():
            config_dict[k] = str(v).lower()

        # Serialize and save
        new_value = ",".join(f"{k}={v}" for k, v in config_dict.items())
        setting_node.text = new_value
        tree.write(self.service_config_path, encoding="utf-8", xml_declaration=True)

        if DEBUG:
            print(f"[OK] Updated EmulatorGpuGuestAngle settings:\n{new_value}")

    def __del__(self):
        print("Cleaning up google emulator controller object...")
        print("Can't call self here; cleanup is handled elsewhere.")
        print("Someone 10x try to clear google play processes here")

    def _connect(self):
        if DEBUG:
            print("[CONNECT DEBUG] Starting connection process...")

        if DEBUG:
            print("[CONNECT DEBUG] Disconnecting any existing connections...")
        disconnect_result = self.adb(f"disconnect {self.device_serial}")
        if DEBUG:
            print(f"[CONNECT DEBUG] Disconnect result: {disconnect_result.stdout}")

        if DEBUG:
            print(f"[CONNECT DEBUG] Attempting to connect to {self.device_serial}...")
        connect_result = self.adb(f"connect {self.device_serial}")
        if DEBUG:
            print(f"[CONNECT DEBUG] Connect result: {connect_result.stdout}")
            print(f"[CONNECT DEBUG] Connect return code: {connect_result.returncode}")

        interruptible_sleep(1)

        if DEBUG:
            print("[CONNECT DEBUG] Checking device list...")
        result = self.adb("devices")
        if DEBUG:
            print(f"[CONNECT DEBUG] Devices output: {result.stdout}")
            print(f"[CONNECT DEBUG] Devices return code: {result.returncode}")

        if result.stdout is None:
            if DEBUG:
                print("[CONNECT DEBUG] Devices command returned None stdout")
            return False

        # Check if our specific device is online
        devices = self.list_devices()
        for serial, status in devices:
            if serial == self.device_serial:
                if status == "device":
                    self.logger.log(f"Connected to emulator at {self.device_serial}")
                    return True
                elif status == "offline":
                    self.logger.log(f"[!] Device {self.device_serial} is offline. Please check the connection.")
                    return False

        if DEBUG:
            print("[CONNECT DEBUG] Connection failed - device not found or not ready")
        return False

    @staticmethod
    def _find_install_location() -> str:
        """
        Locate the installation path of Google Play Games Developer Emulator using the Windows Registry.

        :return: The normalized installation path
        :raises FileNotFoundError: If the emulator is not found
        """
        import winreg

        # C:\Program Files\Google\Play Games Developer Emulator\Bootstrapper.exe
        registry_keys = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\GooglePlayGamesDeveloperEmulator",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\GooglePlayGames",
        ]

        for key in registry_keys:
            with suppress(FileNotFoundError):
                with winreg.OpenKey(  # ty: ignore[unresolved-attribute]
                    winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE),  # ty: ignore[unresolved-attribute]
                    key,
                ) as reg_key:
                    value = winreg.QueryValueEx(reg_key, "InstallLocation")  # ty: ignore[unresolved-attribute]
                    install_path = value[0]
                    folder_path = normpath(install_path)
                    if os.path.exists(folder_path) and os.path.isdir(folder_path):
                        return folder_path

        raise FileNotFoundError("Google Play Games Emulator not found in registry.")

    def _find_adb_path(self):
        """
        Locate the adb.exe path using the same logic as _find_install_location.

        :return: The normalized path to adb.exe
        :raises FileNotFoundError: If adb.exe is not found
        """
        base_path = self._find_install_location()
        adb_path = os.path.join(base_path, "current", "emulator", "adb.exe")
        adb_path = normpath(adb_path)

        if os.path.exists(adb_path) and os.path.isfile(adb_path):
            return adb_path

        raise FileNotFoundError(f"adb.exe not found at expected location: {adb_path}")

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

    def _list_process_pids(self, names: set[str]) -> list[int]:
        """Return PIDs for any processes whose image name matches the provided set."""
        targets = {name.lower() for name in names}
        pids: list[int] = []
        for proc in psutil.process_iter(attrs=["pid", "name"]):
            try:
                name = (proc.info.get("name") or "").lower()
                if name in targets:
                    pids.append(proc.info["pid"])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return pids

    def _is_emulator_running(self):
        # Consider emulator running once the core VM process is present.
        process_names = {"crosvm.exe"}
        return bool(self._list_process_pids(process_names))

    def _wait_for_adb_ready(self, timeout: float = 120.0) -> bool:
        """Wait for the emulator to accept ADB connections, retrying until timeout."""
        start = time.time()
        while time.time() - start < timeout:
            # Query adb devices directly to avoid relying on intermediate state.
            result = self.adb("devices")
            if result.stdout:
                for line in result.stdout.strip().splitlines():
                    if self.device_serial in line and "device" in line:
                        return True
            self._connect()
            interruptible_sleep(3)
        return False

    def _is_connected(self):
        """Returns True if emulator is connected and not offline."""
        result = self.adb("devices")
        for line in result.stdout.strip().splitlines():
            if DEBUG:
                print(line)
            if self.device_serial in line and "device" in line:
                return True
        return False

    def _valid_screen_size(self, expected_dims: tuple):
        # reverse expected_dims just because that's how cv2 works
        if DEBUG:
            print("Validating screen size...")
        expected_dims = (expected_dims[1], expected_dims[0])
        image = self.screenshot()
        dims = image.shape[:2]
        if DEBUG:
            print(f"Image of size {dims} received, expected {expected_dims}")
        if dims != expected_dims:
            return False

        return True

    def _set_screen_size(self, width, height):
        self.adb(f"shell wm size {width}x{height}")

    def restart(self):
        restart_start_time = time.time()

        self.logger.change_status("Starting Google Play emulator restart process...")

        # close emulator
        self.logger.change_status("Shutting down Google Play emulator processes...")
        print("Restarting emulator...")
        print("Closing emulator...")
        while self._is_emulator_running():
            self.stop()

        # write render settings to the XML config while the emulator is stopped
        self._configure_settings(self.render_settings)

        # boot emulator
        self.logger.change_status("Starting Google Play emulator...")
        print("Starting emulator...")
        boot_deadline = time.time() + 120
        while not self._is_emulator_running():
            if time.time() > boot_deadline:
                self.logger.change_status("Timed out waiting for the Google Play emulator process to start.")
                raise EmulatorNotReadyError("Google Play restart() timed out waiting for the emulator to start")
            self.start()
            print("Waiting for google play emulator to start...")
            interruptible_sleep(0.3)

        # wait for adb readiness (locale-agnostic) once the VM process is up
        self.logger.change_status("Waiting for Google Play emulator to finish starting...")
        if not self._wait_for_adb_ready(timeout=120):
            self.logger.change_status("Timed out waiting for Google Play emulator ADB to become ready.")
            raise EmulatorNotReadyError("Google Play restart() timed out waiting for ADB to become ready")

        # Allow emulator services/UI to settle before manipulating display or launching the app.
        interruptible_sleep(5)

        self.logger.change_status(f"Setting emulator screen size to {self.expected_dims}...")
        for i in range(3):
            print(f"Setting adb screen size to {self.expected_dims}")
            self._set_screen_size(*self.expected_dims)
            interruptible_sleep(1)

        # validate image size
        self.logger.change_status("Validating Google Play emulator screen dimensions...")
        if not self._valid_screen_size(self.expected_dims):
            self.logger.change_status(f"Invalid screen size - expected {self.expected_dims}")
            print(
                f"[!] Fatal error: Emulator screen size is not {self.expected_dims}. "
                "Please check the emulator settings."
            )
            raise EmulatorNotReadyError(f"Google Play restart() could not set screen size to {self.expected_dims}")

        # boot clash
        self.logger.change_status("Launching Clash Royale application...")
        interruptible_sleep(10)
        clash_royale_name = CLASH_ROYALE_PACKAGE
        start_app_count = 3
        for i in range(start_app_count):
            self.logger.change_status(f"Starting Clash Royale (attempt {i + 1}/{start_app_count})...")
            print(f"Starting clash app (attempt {i + 1}/{start_app_count})...")
            # start_app raises EmulatorNotReadyError if Clash Royale isn't installed
            self.start_app(clash_royale_name)
            interruptible_sleep(1)

        # wait for clash main to appear
        self.logger.change_status("Waiting for Clash Royale main menu to load...")
        print("Waiting for CR main menu")
        clash_main_wait_start_time = time.time()
        clash_main_wait_timeout = 240  # s
        interruptible_sleep(12)
        while 1:
            if time.time() - clash_main_wait_start_time > clash_main_wait_timeout:
                self.logger.change_status("Timeout waiting for Clash Royale main menu")
                self.logger.log("[!] Fatal error: Timeout reached while waiting for clash main menu to appear.")
                raise EmulatorNotReadyError("Google Play restart() timed out waiting for the Clash Royale main menu")

            # if found main in time, break
            if check_if_on_clash_main_menu(self) is True:
                self.logger.change_status("Clash Royale main menu detected successfully!")
                self.logger.log("Clash Royale main menu detected")
                break

            # click deadspace
            self.click(35, 405)

        restart_duration = str(time.time() - restart_start_time)[:5]
        self.logger.change_status(f"Google Play emulator restart completed successfully in {restart_duration}s")
        self.logger.log("Emulator restarted and configured successfully.")
        return True

    def start(self):
        """
        Starts the emulator using the Windows shell to open the shortcut.
        """
        os.startfile(self.emulator_executable_path)  # ty: ignore[unresolved-attribute]
        interruptible_sleep(5)

    def stop(self):
        """
        Closes the Google Play Games Developer Emulator by force-killing related processes.
        Includes: crosvm.exe, Service.exe, client.exe, and others.
        """
        process_names = [
            "crosvm.exe",
            "Service.exe",
            "client.exe",
            "gpu_check.exe",
            "adbproxy.exe",
            "adb.exe",
        ]

        for proc in process_names:
            result = run_command(["taskkill", "/f", "/im", proc], timeout=10)

            if result.returncode == 0:
                print(f"[OK] {proc} terminated.")
            elif "not found" not in (result.stderr or "").lower():
                print(f"[!] Failed to terminate {proc}")

    def install_apk(self, apk_path: str):
        """
        This method is used to install an APK on the emulator.
        """
        raise NotImplementedError

    def debug_adb_connectivity(self):
        """
        Comprehensive ADB debugging method to test connectivity and commands.
        """
        print("\n" + "=" * 50)
        print("ADB CONNECTIVITY DEBUG REPORT")
        print("=" * 50)

        # Test 1: ADB executable
        print(f"1. ADB Path: {self.adb_path}")
        print(f"   Exists: {os.path.exists(self.adb_path)}")

        # Test 2: ADB version
        print("\n2. ADB Version Test:")
        version_result = self.adb("version")
        print(f"   Return code: {version_result.returncode}")
        print(f"   Output: {version_result.stdout}")

        # Test 3: ADB devices
        print("\n3. ADB Devices Test:")
        devices_result = self.adb("devices")
        print(f"   Return code: {devices_result.returncode}")
        print(f"   Output: {devices_result.stdout}")

        # Test 4: Check if emulator process is running
        print("\n4. Emulator Process Check:")
        print(f"   Is emulator running: {self._is_emulator_running()}")

        # Test 5: Try to connect
        print("\n5. Connection Attempt:")
        connect_success = self._connect()
        print(f"   Connection successful: {connect_success}")

        # Test 6: If connected, test screencap
        if connect_success:
            print("\n6. Screenshot Test:")
            try:
                print("   Attempting screenshot...")
                # Call inherited screenshot method
                img = self.screenshot()
                print(f"   Screenshot successful. Image shape: {img.shape}")

            except Exception as e:
                print(f"   Screenshot test failed: {e}")
        else:
            print("\n6. Screenshot Test: Skipped (not connected)")

        print("\n" + "=" * 50)
        print("END DEBUG REPORT")
        print("=" * 50)


if __name__ == "__main__":
    pass
