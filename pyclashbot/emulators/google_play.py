import numpy as np
import os
from os.path import join, normpath
from contextlib import suppress
from winreg import OpenKey, QueryValueEx, ConnectRegistry, HKEY_LOCAL_MACHINE
import subprocess
import time
import cv2
import pygetwindow as gw
import xml.etree.ElementTree as ET  # for parsing config file


from pyclashbot.emulators.base import BaseEmulatorController
from pyclashbot.bot.nav import check_if_on_clash_main_menu


def adb(command):
    """Runs an adb command, prints and returns its output."""
    result = subprocess.run(
        f"adb {command}", shell=True, capture_output=True, text=True
    )

    return result


class GooglePlayEmulatorController(BaseEmulatorController):
    def __init__(self, render_settings: dict = {}):
        # clear existing stuff
        self.stop()
        while self._is_emulator_running():
            self.stop()

        # search for base installation folder
        self.base_folder = self._find_install_location()
        if not self.base_folder:
            raise FileNotFoundError("Google Play Games Developer Emulator not found.")

        # locate the executable
        self.emulator_executable_path = os.path.join(
            self.base_folder, "Bootstrapper.exe"
        )

        # locate the config file
        # C:\Program Files\Google\Play Games Developer Emulator\current\service\Service.exe.config
        self.service_config_path = os.path.join(
            self.base_folder, "current", "service", "Service.exe.config"
        )

        # verify all those paths exist
        for path in [
            self.base_folder,
            self.emulator_executable_path,
            self.service_config_path,
        ]:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Required file or directory not found: {path}")

        # configure the emulator via file
        current_settings = self._get_settings_configuration()
        for k, v in current_settings.items():
            print("current setting:", k, v)
        self._configure_settings(render_settings)

        final_settings = self._get_settings_configuration()
        for k, v in final_settings.items():
            print("final setting:", k, v)

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
        updates = {
            k: v for k, v in settings.items() if k in valid_keys and v is not None
        }

        if not updates:
            print("[!] No valid settings provided for update.")
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

        print(f"[✓] Updated EmulatorGpuGuestAngle settings:\n{new_value}")

    def __del__(self):
        print("Cleaning up google emulator controller object...")
        print("Cant call self here so idk what to do.")
        print("Someone 10x try to clear google play processes here")

    def _connect(self):
        print("Connecting...")
        subprocess.run("adb disconnect localhost:6520", shell=True)
        subprocess.run("adb connect localhost:6520", shell=True)
        time.sleep(1)

        result = subprocess.run(
            "adb devices", shell=True, capture_output=True, text=True
        )
        if "offline" in result.stdout:
            print("[!] Emulator is offline. Please check the connection.")

        elif "localhost:6520" in result.stdout and "device" in result.stdout:
            print("Connected to emulator at localhost:6520")
            return True

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
        result = subprocess.run("tasklist", shell=True, capture_output=True, text=True)
        return "crosvm.exe" in result.stdout

    def _find_window(self, title_keyword):
        windows = gw.getWindowsWithTitle(title_keyword)
        return windows[0] if windows else None

    def _is_connected(self):
        """Returns True if emulator is connected and not offline."""
        result = subprocess.run(
            "adb devices", shell=True, capture_output=True, text=True
        )
        for line in result.stdout.strip().splitlines():
            print(line)
            if "localhost:6520" in line and "device" in line:
                return True
        return False

    def _valid_screen_size(self, expected_dims: tuple):
        # reverse expected_dims just because that's how cv2 works
        print("Validating screen size...")
        expected_dims = (expected_dims[1], expected_dims[0])
        image = self.screenshot()
        dims = image.shape[:2]
        print(f"Image of size {dims} received, expected {expected_dims}")
        if dims != expected_dims:
            return False

        return True

    def _set_screen_size(self, width, height):
        adb(f"shell wm size {width}x{height}")

    def _resize_emulator(self, width=None, height=None):
        default = self.expected_dims
        if None in [width, height]:
            width, height = default
        print(f"Resizing emulator to {width}x{height}...")
        self._set_screen_size(width, height)

    def _test_adb(self):
        result = subprocess.run(
            "adb devices", shell=True, capture_output=True, text=True
        )
        std_out = result.stdout.strip()
        error = result.stderr.strip()
        if "'adb' is not recognized as an internal or external command" in error:
            print(f"Looks like adb isnt installed")
            return False
        return True

    def restart(self):
        # close emulator
        print("Restarting emulator...")
        print("Closing emulator...")
        while self._is_emulator_running():
            self.stop()

        # boot emulator
        print("Starting emulator...")
        while not self._is_emulator_running():
            self.start()
            print("Waiting for google play emulator to start...")
            self.start()
            time.sleep(0.3)

        # wait for window to appear
        while self._find_window(self.google_play_emulator_process_name) is None:
            print("Waiting for emulator window to appear...")
            time.sleep(0.3)

        # reconnect to adb
        while not self._is_connected():
            self._connect()

        # configure emulator
        for i in range(3):
            self._resize_emulator()
            time.sleep(1)

        # validate image size
        if not self._valid_screen_size(self.expected_dims):
            print(
                f"[!] Fatal error: Emulator screen size is not {self.expected_dims}. "
                "Please check the emulator settings."
            )
            return False

        # make sure adb is installated and working
        print(f"testing adb...")
        if self._test_adb() is False:
            print(
                "[!] Fatal error: adb is not working. Please check your adb installation."
            )
            return False

        # boot clash
        clash_royale_name = "com.supercell.clashroyale"
        self.start_app(clash_royale_name)

        # wait for clash main to appear
        print("Waiting for CR main menu")
        clash_main_wait_start_time = time.time()
        clash_main_wait_timeout = 240  # s
        time.sleep(12)
        while 1:
            # self.start_app(clash_royale_name)
            # if timed out, retry restarting
            if time.time() - clash_main_wait_start_time > clash_main_wait_timeout:
                print(
                    "[!] Fatal error: Timeout reached while waiting for clash main menu to appear."
                )
                return self.restart()

            # if found main in time, break
            if check_if_on_clash_main_menu(self) is True:
                print("Detected clash main!")
                break

            # click deadspace
            self.click(5, 350)

        print("Emulator restarted and configured successfully.")
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
                f'taskkill /f /im "{proc}"', shell=True, capture_output=True, text=True
            )

            if result.returncode == 0:
                print(f"[✓] {proc} terminated.")
            elif "not found" not in result.stderr.lower():
                print(f"[!] Failed to terminate {proc}:\n{result.stderr.strip()}")

    def click(self, x_coord: int, y_coord: int, clicks: int = 1, interval: float = 0.0):
        for i in range(clicks):
            adb(f"shell input tap {x_coord} {y_coord}")
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
        adb(f"shell input swipe {x_coord1} {y_coord1} {x_coord2} {y_coord2}")

    def screenshot(self) -> np.ndarray:
        """
        Captures a screenshot from the emulator and returns it as a NumPy BGR image (OpenCV format).
        """

        result = subprocess.run(
            "adb exec-out screencap -p", shell=True, capture_output=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"ADB screenshot failed: {result.stderr.decode()}")

        # Convert bytes to NumPy array
        img_array = np.frombuffer(result.stdout, dtype=np.uint8)

        # Decode PNG to image
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Failed to decode screenshot")

        # bgr to rgb
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        return img

    def install_apk(self, apk_path: str):
        """
        This method is used to install an APK on the emulator.
        """
        raise NotImplementedError

    def start_app(self, package_name: str):
        adb(f"shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1")


if __name__ == "__main__":
    matt_old_settings = {
        "angle": True,
        "backend": "gfxstream",
        "egl": True,
        "gles": False,
        "glx": False,
        "surfaceless": False,
        "vulkan": True,
        "wsi": "vk",
    }

    matt_boof_settings = {
        "angle": False,
        "backend": "gfxstream",
        "egl": True,
        "gles": False,
        "glx": True,
        "surfaceless": True,
        "vulkan": True,
        "wsi": "vk",
    }

    empty_settings = {}

    google_play_emulator = GooglePlayEmulatorController(render_settings=empty_settings)
    while 1:
        print("Running google play emulator")
        time.sleep(10)
