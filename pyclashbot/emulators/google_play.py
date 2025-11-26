import os
import subprocess
import time
import xml.etree.ElementTree as ET
from contextlib import suppress
from os.path import normpath
import sys

if sys.platform == "win32":
    from winreg import (
        HKEY_LOCAL_MACHINE,
        OpenKey,
        QueryValueEx,
        ConnectRegistry,
    )
else:
    HKEY_LOCAL_MACHINE = None

    def OpenKey(*args, **kwargs):
        raise RuntimeError("BlueStacks emulator is only supported on Windows (winreg not available).")

    def QueryValueEx(*args, **kwargs):
        raise RuntimeError("BlueStacks emulator is only supported on Windows (winreg not available).")

    def ConnectRegistry(*args, **kwargs):
        raise RuntimeError("BlueStacks emulator is only supported on Windows (winreg not available).")

import pygetwindow as gw

DEBUG = False

from pyclashbot.bot.nav import check_if_on_clash_main_menu
from pyclashbot.emulators.adb_base import AdbBasedController


class GooglePlayEmulatorController(AdbBasedController):
    def __init__(self, logger, render_settings: dict = {}):
        self.logger = logger
        # clear existing stuff
        self.stop()
        while self._is_emulator_running():
            self.stop()

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

        # configure the emulator via file
        self._configure_settings(render_settings)

        # emulator config
        self.google_play_emulator_process_name = "Google Play Games on PC Emulator"
        self.expected_dims = (419, 633)

        # boot the emulator
        # self.restart()

        while self.restart() is False:
            print("Restart failed, trying again...")
            time.sleep(2)

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
        print("Cant call self here so idk what to do.")
        print("Someone 10x try to clear google play processes here")

    def _connect(self):
        if DEBUG:
            print("[CONNECT DEBUG] Starting connection process...")

        if DEBUG:
            print("[CONNECT DEBUG] Disconnecting any existing connections...")
        disconnect_result = self.adb("disconnect localhost:6520")
        if DEBUG:
            print(f"[CONNECT DEBUG] Disconnect result: {disconnect_result.stdout}")

        if DEBUG:
            print("[CONNECT DEBUG] Attempting to connect to localhost:6520...")
        connect_result = self.adb("connect localhost:6520")
        if DEBUG:
            print(f"[CONNECT DEBUG] Connect result: {connect_result.stdout}")
            print(f"[CONNECT DEBUG] Connect return code: {connect_result.returncode}")

        time.sleep(1)

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

        if "offline" in result.stdout:
            self.logger.log("[!] Emulator is offline. Please check the connection.")
            return False

        elif "localhost:6520" in result.stdout and "device" in result.stdout:
            self.logger.log("Connected to emulator at localhost:6520")
            return True

        if DEBUG:
            print("[CONNECT DEBUG] Connection failed - device not found or not ready")
        return False

    def _find_install_location(self):
        """
        Locate the installation path of Google Play Games Developer Emulator using the Windows Registry.

        :return: The normalized installation path
        :raises FileNotFoundError: If the emulator is not found
        """
        # C:\Program Files\Google\Play Games Developer Emulator\Bootstrapper.exe
        registry_keys = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\GooglePlayGamesDeveloperEmulator",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\GooglePlayGames",
        ]

        for key in registry_keys:
            with suppress(FileNotFoundError):
                with OpenKey(ConnectRegistry(None, HKEY_LOCAL_MACHINE), key) as reg_key:
                    install_path = QueryValueEx(reg_key, "InstallLocation")[0]
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

    def adb(self, command, binary_output=False):
        """
        Runs an adb command using the located adb.exe path.
        This is the abstract method implementation for AdbBasedController.
        """
        full_command = f'"{self.adb_path}" {command}'
        if DEBUG:
            print(f"[ADB DEBUG] Executing: {full_command}")
            print(f"[ADB DEBUG] ADB path exists: {os.path.exists(self.adb_path)}")
            print(f"[ADB DEBUG] Binary output mode: {binary_output}")

        result = subprocess.run(
            full_command,
            shell=True,
            capture_output=True,
            text=not binary_output,
            check=False,
        )

        if DEBUG:
            print(f"[ADB DEBUG] Return code: {result.returncode}")
            if binary_output:
                print(f"[ADB DEBUG] Stdout type: {type(result.stdout)}")
                print(f"[ADB DEBUG] Stdout length: {len(result.stdout) if result.stdout else 'None'}")
            else:
                print(f"[ADB DEBUG] Stdout: {result.stdout[:200] if result.stdout else 'None'}...")
            print(f"[ADB DEBUG] Stderr: {result.stderr[:200] if result.stderr else 'None'}...")

        return result

    def _check_app_installed(self, package_name: str) -> bool:
        """
        Check if an app is installed using the emulator's bundled ADB.
        This is the abstract method implementation for AdbBasedController.
        """
        result = self.adb("shell pm list packages")
        return result.stdout is not None and package_name in result.stdout

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

    def _is_emulator_running(self):
        result = subprocess.run("tasklist", shell=True, capture_output=True, text=True, check=False)
        return "crosvm.exe" in result.stdout

    def _find_window(self, title_keyword):
        windows = gw.getWindowsWithTitle(title_keyword)
        return windows[0] if windows else None

    def _is_connected(self):
        """Returns True if emulator is connected and not offline."""
        result = self.adb("devices")
        for line in result.stdout.strip().splitlines():
            if DEBUG:
                print(line)
            if "localhost:6520" in line and "device" in line:
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

        # boot emulator
        self.logger.change_status("Starting Google Play emulator...")
        print("Starting emulator...")
        while not self._is_emulator_running():
            self.start()
            print("Waiting for google play emulator to start...")
            self.start()
            time.sleep(0.3)

        # wait for window to appear
        self.logger.change_status("Waiting for Google Play emulator window...")
        while self._find_window(self.google_play_emulator_process_name) is None:
            print("Waiting for emulator window to appear...")
            time.sleep(0.3)

        # reconnect to adb
        self.logger.change_status("Establishing ADB connection to Google Play emulator...")
        while not self._is_connected():
            self._connect()
            time.sleep(20)

        time.sleep(10)

        self.logger.change_status(f"Setting emulator screen size to {self.expected_dims}...")
        for i in range(3):
            print(f"Setting adb screen size to {self.expected_dims}")
            self._set_screen_size(*self.expected_dims)
            time.sleep(1)

        # validate image size
        self.logger.change_status("Validating Google Play emulator screen dimensions...")
        if not self._valid_screen_size(self.expected_dims):
            self.logger.change_status(f"Invalid screen size - expected {self.expected_dims}")
            print(
                f"[!] Fatal error: Emulator screen size is not {self.expected_dims}. "
                "Please check the emulator settings."
            )
            return False

        # boot clash
        self.logger.change_status("Launching Clash Royale application...")
        time.sleep(10)
        clash_royale_name = "com.supercell.clashroyale"
        start_app_count = 3
        for i in range(start_app_count):
            self.logger.change_status(f"Starting Clash Royale (attempt {i + 1}/{start_app_count})...")
            print(f"Starting clash app (attempt {i + 1}/{start_app_count})...")
            if not self.start_app(clash_royale_name) and i == 0:
                # App not installed, start_app triggered the wait.
                # We just wait for it to return, then the loop will retry.
                self.logger.log("App not installed. Waiting for user...")
            time.sleep(1)

        # wait for clash main to appear
        self.logger.change_status("Waiting for Clash Royale main menu to load...")
        print("Waiting for CR main menu")
        clash_main_wait_start_time = time.time()
        clash_main_wait_timeout = 240  # s
        time.sleep(12)
        while 1:
            if time.time() - clash_main_wait_start_time > clash_main_wait_timeout:
                self.logger.change_status("Timeout waiting for Clash Royale main menu - restarting...")
                self.logger.log("[!] Fatal error: Timeout reached while waiting for clash main menu to appear.")
                return self.restart()

            # if found main in time, break
            if check_if_on_clash_main_menu(self) is True:
                self.logger.change_status("Clash Royale main menu detected successfully!")
                self.logger.log("Detected clash main!")
                break

            # click deadspace
            self.click(5, 350)

        restart_duration = str(time.time() - restart_start_time)[:5]
        self.logger.change_status(f"Google Play emulator restart completed successfully in {restart_duration}s")
        self.logger.log("Emulator restarted and configured successfully.")
        return True

    def start(self):
        """
        Starts the emulator using the Windows shell to open the shortcut.
        """
        os.startfile(self.emulator_executable_path)
        time.sleep(5)

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
            result = subprocess.run(
                f'taskkill /f /im "{proc}"', shell=True, capture_output=True, text=True, check=False
            )

            if result.returncode == 0:
                print(f"[OK] {proc} terminated.")
            elif "not found" not in result.stderr.lower():
                print(f"[!] Failed to terminate {proc}")

    # click() is now inherited from AdbBasedController
    # swipe() is now inherited from AdbBasedController
    # screenshot() is now inherited from AdbBasedController

    def install_apk(self, apk_path: str):
        """
        This method is used to install an APK on the emulator.
        """
        raise NotImplementedError

    # start_app() is now inherited from AdbBasedController
    # _wait_for_clash_installation() is now inherited from AdbBasedController
    # _retry_installation_check() is now inherited from AdbBasedController

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
