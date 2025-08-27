import os
import subprocess
import time
import xml.etree.ElementTree as ET
from contextlib import suppress
from os.path import normpath
from winreg import HKEY_LOCAL_MACHINE, ConnectRegistry, OpenKey, QueryValueEx

import cv2
import numpy as np
import pygetwindow as gw

DEBUG = False

from pyclashbot.bot.nav import check_if_on_clash_main_menu
from pyclashbot.emulators.base import BaseEmulatorController


class GooglePlayEmulatorController(BaseEmulatorController):
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
        self.restart()

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
        """Runs an adb command using the located adb.exe path."""
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
            check=False,  # Use binary mode for screenshots
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

    def _resize_emulator(self, width=None, height=None):
        default = self.expected_dims
        if None in [width, height]:
            width, height = default
        if DEBUG:
            print(f"Resizing emulator to {width}x{height}...")

        emulator_window = self._find_window(self.google_play_emulator_process_name)

        if emulator_window is None:
            return False
        if width is None:
            return False
        if height is None:
            return False

        emulator_window.resizeTo(width, (height + 150))

        self._set_screen_size(width, height)

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

        # configure emulator
        self.logger.change_status("Configuring Google Play emulator window size and settings...")
        for i in range(3):
            self._resize_emulator()
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
            self.start_app(clash_royale_name)
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

    def click(self, x_coord: int, y_coord: int, clicks: int = 1, interval: float = 0.0):
        for i in range(clicks):
            self.adb(f"shell input tap {x_coord} {y_coord}")
            if clicks == 1:
                break
            time.sleep(interval)

    def swipe(
        self,
        x_coord1: int,
        y_coord1: int,
        x_coord2: int,
        y_coord2: int,
    ):
        self.adb(f"shell input swipe {x_coord1} {y_coord1} {x_coord2} {y_coord2}")

    def screenshot(self) -> np.ndarray:
        """
        Captures a screenshot from the emulator and returns it as a NumPy BGR image (OpenCV format).
        """
        if DEBUG:
            print("[SCREENSHOT DEBUG] Starting screenshot capture...")

        # First test basic connectivity
        if DEBUG:
            print("[SCREENSHOT DEBUG] Testing ADB connectivity...")
        devices_result = self.adb("devices")
        if DEBUG:
            print(f"[SCREENSHOT DEBUG] ADB devices output: {devices_result.stdout}")

        if devices_result.returncode != 0:
            if DEBUG:
                print(f"[SCREENSHOT DEBUG] ADB devices failed with return code: {devices_result.returncode}")
                print(f"[SCREENSHOT DEBUG] ADB devices stderr: {devices_result.stderr}")
            raise RuntimeError(f"ADB connectivity test failed: {devices_result.stderr}")

        # Now try the screenshot command with binary output
        if DEBUG:
            print("[SCREENSHOT DEBUG] Executing screencap command...")
        result = self.adb("exec-out screencap -p", binary_output=True)

        if DEBUG:
            print(f"[SCREENSHOT DEBUG] Screenshot command return code: {result.returncode}")
            print(f"[SCREENSHOT DEBUG] Screenshot stdout type: {type(result.stdout)}")
            print(f"[SCREENSHOT DEBUG] Screenshot stdout is None: {result.stdout is None}")

        if result.returncode != 0:
            error_msg = result.stderr if result.stderr else "Unknown error"
            if DEBUG:
                print(f"[SCREENSHOT DEBUG] ADB screenshot failed with error: {error_msg}")
            raise RuntimeError(f"ADB screenshot failed: {error_msg}")

        if result.stdout is None:
            if DEBUG:
                print("[SCREENSHOT DEBUG] Screenshot stdout is None - this indicates ADB command failure")
            raise RuntimeError("ADB screenshot returned None stdout - command failed silently")

        if len(result.stdout) == 0:
            if DEBUG:
                print("[SCREENSHOT DEBUG] Screenshot stdout is empty")
            raise RuntimeError("ADB screenshot returned empty data")

        if DEBUG:
            print(f"[SCREENSHOT DEBUG] Screenshot data length: {len(result.stdout)} bytes")

        # Convert bytes to NumPy array
        try:
            img_array = np.frombuffer(result.stdout, dtype=np.uint8)
            if DEBUG:
                print(f"[SCREENSHOT DEBUG] NumPy array created, shape: {img_array.shape}")
        except Exception as e:
            if DEBUG:
                print(f"[SCREENSHOT DEBUG] Failed to create NumPy array: {e}")
            raise RuntimeError(f"Failed to convert screenshot data to NumPy array: {e}")

        # Decode PNG to image
        try:
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if DEBUG:
                print(f"[SCREENSHOT DEBUG] Image decoded, shape: {img.shape if img is not None else 'None'}")
        except Exception as e:
            if DEBUG:
                print(f"[SCREENSHOT DEBUG] Failed to decode image: {e}")
            raise RuntimeError(f"Failed to decode screenshot image: {e}")

        if img is None:
            if DEBUG:
                print("[SCREENSHOT DEBUG] cv2.imdecode returned None - invalid image data")
                # Let's save the raw data to analyze
                try:
                    with open("debug_screenshot_data.bin", "wb") as f:
                        f.write(result.stdout)
                    print("[SCREENSHOT DEBUG] Raw screenshot data saved to debug_screenshot_data.bin")
                except Exception as e:
                    print(f"[SCREENSHOT DEBUG] Failed to save debug data: {e}")
            raise ValueError("Failed to decode screenshot - image data may be corrupted")

        if DEBUG:
            print(f"[SCREENSHOT DEBUG] Screenshot successful! Image shape: {img.shape}")
        return img

    def install_apk(self, apk_path: str):
        """
        This method is used to install an APK on the emulator.
        """
        raise NotImplementedError

    def start_app(self, package_name: str):
        # Check if the app is installed first
        result = self.adb("shell pm list packages")
        if result.stdout and package_name not in result.stdout:
            return self._wait_for_clash_installation(package_name)
        
        self.adb(f"shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1")

    def _wait_for_clash_installation(self, package_name: str):
        """Wait for user to install Clash Royale using the logger action system"""
        self.current_package_name = package_name  # Store for retry logic
        self.logger.show_temporary_action(
            message=f"{package_name} not installed - please install it and complete tutorial",
            action_text="Retry",
            callback=self._retry_installation_check
        )
        
        self.logger.log(f"[!] {package_name} not installed.")
        self.logger.log("Please install it in the emulator, complete tutorial, then click Retry in the GUI")
        
        # Wait for the callback to be triggered
        self.installation_waiting = True
        while self.installation_waiting:
            time.sleep(0.5)
        
        self.logger.log("[+] Installation confirmed, continuing...")
        return True

    def _retry_installation_check(self):
        """Callback method triggered when user clicks Retry button"""
        self.logger.change_status("Checking for Clash Royale installation...")
        
        # Check if app is now installed
        package_name = getattr(self, 'current_package_name', 'com.supercell.clashroyale')
        result = self.adb("shell pm list packages")
        
        if result.stdout and package_name in result.stdout:
            # Installation successful!
            self.installation_waiting = False
            self.logger.change_status("Installation complete - continuing...")
        else:
            # Still not installed, show the retry button again
            self.logger.show_temporary_action(
                message=f"{package_name} still not found - please install it and complete tutorial",
                action_text="Retry",
                callback=self._retry_installation_check
            )
            self.logger.log(f"[!] {package_name} still not installed. Please try again.")

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
                result = self.adb("exec-out screencap -p", binary_output=True)
                print(f"   Screenshot return code: {result.returncode}")
                print(f"   Screenshot data type: {type(result.stdout)}")
                print(f"   Screenshot data length: {len(result.stdout) if result.stdout else 'None'}")

                if result.stdout and len(result.stdout) > 0:
                    # Check if it looks like PNG data
                    png_header = result.stdout[:8] if len(result.stdout) >= 8 else result.stdout
                    is_png = png_header.startswith(b"\x89PNG\r\n\x1a\n")
                    print(f"   Data appears to be PNG: {is_png}")
                    print(f"   First 16 bytes: {result.stdout[:16] if result.stdout else 'None'}")
                else:
                    print("   No screenshot data received")

            except Exception as e:
                print(f"   Screenshot test failed: {e}")
        else:
            print("\n6. Screenshot Test: Skipped (not connected)")

        print("\n" + "=" * 50)
        print("END DEBUG REPORT")
        print("=" * 50)


if __name__ == "__main__":
    pass
