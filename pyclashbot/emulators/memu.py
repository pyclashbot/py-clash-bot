import base64
import binascii
import contextlib
import json
import logging
import os
import re
import subprocess
import time
from os.path import join

import cv2
import numpy as np
import psutil
from pymemuc import PyMemuc, PyMemucError, VMInfo

from pyclashbot.bot.nav import check_if_on_clash_main_menu
from pyclashbot.emulators.base import BaseEmulatorController


class InvalidImageError(Exception):
    """Exception raised when an image is invalid"""

    def __init__(self, message: str, path: str | None = None):
        self.path = path
        self.message = message
        super().__init__(self.message)


class MemuScreenCapture:
    def __init__(self, pmc):
        self.pmc = pmc
        self.image_b64_pattern = re.compile(r"already connected to 127\.0\.0\.1:[\d]*\n\n")

    def open_from_b64(self, image_b64: str):
        """A method to validate and open an image from a base64 string
        :param image_b64: the base64 string to read the image from
        :return: the image as a numpy array
        :raises InvalidImageError: if the file is not a valid image
        """
        try:
            image_data = base64.b64decode(image_b64)
        except (TypeError, ValueError, binascii.Error) as error:
            raise InvalidImageError("image_b64 is not a valid base64 string") from error
        return self.open_from_buffer(image_data)

    def open_from_buffer(
        self,
        image_data,
    ):
        """A method to read an image from a byte array
        :param byte_array: the byte array to read the image from
        :return: the image as a numpy array
        :raises InvalidImageError: if the file is not a valid image
        """
        try:
            im_arr = np.frombuffer(image_data, dtype=np.uint8)
        except (BufferError, ValueError) as error:
            raise InvalidImageError("image_data is not a valid buffer") from error
        try:
            img = cv2.imdecode(im_arr, cv2.IMREAD_COLOR)  # pylint: disable=no-member
        except cv2.error as error:  # pylint: disable=catching-non-exception
            # pylint: disable=bad-exception-cause
            raise InvalidImageError("image_data bytes cannot be decoded") from error
        if img is None or len(img) == 0 or len(img.shape) != 3 or img.shape[2] != 3:
            raise InvalidImageError("image_data bytes are not a valid image")
        # if np.all(img == 255) or np.all(img == 0):
        #     raise InvalidImageError(
        #         "image_data bytes are not a valid image. Image is all white or all black"
        #     )
        return img

    def __getitem__(self, vm_index) -> np.ndarray:
        if vm_index is None:
            print("[!] Fatal error: vm_index is None in MemuScreenCapture.__getitem__()")
            return np.zeros((1, 1, 3), dtype=np.uint8)

        while True:  # loop until a valid image is returned
            try:
                # read screencap from vm using screencap output encoded in base64
                shell_out = self.pmc.send_adb_command_vm(
                    vm_index=vm_index,
                    command="shell screencap -p | base64",
                )

                # remove non-image data from shell output
                image_b64 = self.image_b64_pattern.sub("", shell_out).replace("\n", "")
                return self.open_from_b64(image_b64)

            except (PyMemucError, FileNotFoundError, InvalidImageError):
                time.sleep(0.1)


def verify_memu_installation():
    try:
        PyMemuc()
        return True
    except Exception:
        pass
    return False


class MemuEmulatorController(BaseEmulatorController):
    def __init__(self, render_mode: str = "opengl", logger=None):
        """
        Initializes the MemuEmulatorController with a reference to PyMemuc and the selected VM index.
        Ensures only one VM with the given name exists.
        """
        self.logger = logger
        init_start_time = time.time()
        self.pmc = PyMemuc()

        self.config = self._read_config_data()
        self.render_mode = render_mode

        # screenshot stuff
        self.screenshotter = MemuScreenCapture(self.pmc)

        # get a valid vm to use
        self._initalize_valid_vm()

        print(
            "Initializing MemuEmulatorController took",
            str(time.time() - init_start_time)[:5],
            "seconds",
        )

    def __del__(self):
        print("Need to clear residual memu processes here")

    def _initalize_valid_vm(self):
        # no timeout here bc if this fails, then something fatal is wrong
        print("Initalizing memu vm...")
        vm_index = -1
        while 1:
            # check for a valid vm
            print("Checking for an existing valid vm...")
            vm_index = self._get_clashbot_vm_index()
            if vm_index is not False:
                print(f"[+] Found a valid vm: {vm_index}")
                self.vm_index = vm_index
                break

            # if none found, create a new one
            print("No existing valid vm!")
            vm_index = self.create()
            if vm_index != -1:
                self._rename_vm("pyclashbot-96")
                print(f"[+] Created a new vm: {vm_index}")
                break

        self.vm_index = vm_index
        print("Configuring the vm...")
        self.configure()

        print("Booting the vm...")
        self.restart()

    def _get_clashbot_vm_index(self):
        vms: list[VMInfo] = self.pmc.list_vm_info()

        for vm in vms:
            title = vm["title"]
            if "pyclashbot-96" in title:
                self.vm_index = vm["index"]
                return vm["index"]

        return False

    def _read_config_data(self):
        # validate file exists
        config_file_path = r"pyclashbot\emulators\configs\memu_config.json"
        if not os.path.exists(config_file_path):
            print(f"[!] Fatal Error: Config file not found at {config_file_path}")
            return {}

        # read the config file, return data
        with open(config_file_path) as config_file:
            config_data = json.load(config_file)

        return config_data

    def _set_vm_language(
        self,
    ):
        """Set the language of the vm to english"""
        settings_uri = "--uri content://settings/system"
        set_language_commands = [
            f"shell content query {settings_uri} --where \"name='system_locales'\"",
            f"shell content delete {settings_uri} --where \"name='system_locales'\"",
            f"shell content insert {settings_uri} --bind name:s:system_locales --bind value:s:en-US",
            "shell setprop ctl.restart zygote",
        ]

        for command in set_language_commands:
            self.pmc.send_adb_command_vm(vm_index=self.vm_index, command=command)
            time.sleep(0.33)

    def _get_current_config(self) -> dict[str, str]:
        current_configuration = {}
        for key in self.config:
            try:
                current_value = self.pmc.get_configuration_vm(key, vm_index=self.vm_index)
                current_configuration[key] = current_value
            except PyMemucError as e:
                logging.exception("Failed to get configuration for key %s: %s", key, e)
        return current_configuration

    def configure(self):
        # render_mode = either 'opengl' or 'directx'
        print("Configuring vm with render mode:", self.render_mode)

        # render mode type safety
        if self.render_mode not in ["opengl", "directx"]:
            print(
                '[!] Non fatal error: Render mode must be either "opengl" or "directx"\nRecieved:',
                self.render_mode,
                "\nUsing opengl as default render mode",
            )
            self.render_mode = "opengl"

        # override to user choice
        self.config["graphics_render_mode"] = 1  # directx
        if self.render_mode == "opengl":
            self.config["graphics_render_mode"] = 0  # opengl

        # do config for each key
        print("Setting each config key...")
        logging.info("Configuring VM %s...", self.vm_index)
        for key, value in self.config.items():
            self.pmc.set_configuration_vm(key, str(value), vm_index=self.vm_index)

        # set language
        print("Setting vm language...")
        self._set_vm_language()
        logging.info("Configured VM %s", self.vm_index)

    def _start_memuc_console(self):
        """Start the memuc console and return the process ID"""
        print("Starting memuc console...")

        # check if memu console is already running
        for process in psutil.process_iter():
            with contextlib.suppress(psutil.NoSuchProcess, psutil.AccessDenied):
                if process.name() == "MEMuConsole.exe":
                    print("[+] Memu console is already running.")
                    return process.pid

        console_path = join(self.pmc._get_memu_top_level(), "MEMuConsole.exe")
        print("[+] Starting memu console at:", console_path)
        process = subprocess.Popen(console_path, creationflags=subprocess.DETACHED_PROCESS)

        time.sleep(2)

        if process.pid is not None:
            print("[+] Memu console started successfully.")
        else:
            print("[!] Failed to start memu console.")

    def create(self):
        self._start_memuc_console()
        vm_index = self.pmc.create_vm(vm_version="96")
        self.vm_index = vm_index
        return vm_index

    def _close_everything_memu(self):
        """Closes all MEmu processes."""
        name_list = [
            "MEmuConsole.exe",
            "MEmu.exe",
            "MEmuHeadless.exe",
        ]

        for proc in psutil.process_iter():
            try:
                if proc.name() in name_list:
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                print("[!] Non-fatal error: Failed to kill process:", proc.name())

    def _skip_ads(self):
        """Skip ads in the emulator.

        Args:
        ----
            vm_index (int): Index of the virtual machine.


        """
        try:
            for _ in range(4):
                self.pmc.trigger_keystroke_vm("home", vm_index=self.vm_index)
                time.sleep(1)
        except Exception as err:  # pylint: disable=broad-except
            print(f"Fail sending home clicks to skip ads... Redoing restart...\n{err}")
            return False
        return True

    def _rename_vm(
        self,
        name: str,
    ):
        """Rename the vm to name"""
        self.pmc.rename_vm(vm_index=self.vm_index, new_name=name)

    def _check_vm_size(self):
        expected_width, expected_height = 419, 633
        try:
            if self.logger:
                self.logger.change_status("Pressing home key to prepare for screen size check...")
            self.pmc.trigger_keystroke_vm("home", vm_index=self.vm_index)

            time.sleep(2)  # Wait for screen to stabilize
            
            if self.logger:
                self.logger.change_status("Taking screenshot to verify screen dimensions...")
            image = self.screenshot()

            height, width, _ = image.shape

            if self.logger:
                self.logger.change_status(f"Screen dimensions: {width}x{height} (expected: {expected_width}x{expected_height})")

            if width != expected_width or height != expected_height:
                if self.logger:
                    self.logger.change_status(f"Screen size validation FAILED: got {width}x{height}, expected {expected_width}x{expected_height}")
                print(f"Size is bad: {width},{height}")
                return False

            if self.logger:
                self.logger.change_status("Screen size validation PASSED")
            return True
        except Exception as e:
            if self.logger:
                self.logger.change_status(f"Error during screen size check: {e}")
            print("sizing error:", e)

        # in the case of errors, assume size is correct to avoid infinite loops
        if self.logger:
            self.logger.change_status("Screen size check error - assuming valid size")
        return True

    def restart(self):
        """Restart the emulator.
        Args:
        ----
            logger (Logger): Logger object
            start_time (float, optional): Start time. Defaults to time.time().
        """
        restart_start_time = time.time()
        
        if self.logger:
            self.logger.change_status("Starting MEmu emulator restart process...")

        # stop all vms
        if self.logger:
            self.logger.change_status("Stopping all MEmu processes...")
        self._close_everything_memu()

        # start the vm
        if self.logger:
            self.logger.change_status("Starting MEmu virtual machine...")
        print("Opening the pyclashbot emulator...")
        out = self.pmc.start_vm(vm_index=self.vm_index)
        print(f"Opened the pyclashbot emulator with output:\n{out}")

        # skip ads
        if self.logger:
            self.logger.change_status("Skipping MEmu startup ads...")
        if self._skip_ads() is False:
            if self.logger:
                self.logger.change_status("Failed to skip ads, retrying restart...")
            print("[!] Fatal error! Failed to skip ads during memu startup.")
            return self.restart()

        # ensure valid size with retry logic
        max_size_check_attempts = 3
        for size_attempt in range(max_size_check_attempts):
            if self.logger:
                self.logger.change_status(f"Validating MEmu screen dimensions (attempt {size_attempt + 1}/{max_size_check_attempts})...")
            
            valid_size = self._check_vm_size()
            if valid_size:
                break
            
            if size_attempt < max_size_check_attempts - 1:
                if self.logger:
                    self.logger.change_status(f"Invalid screen size detected, reconfiguring VM and trying again...")
                print(f"[!] VM size is not valid (attempt {size_attempt + 1}). Reconfiguring...")
                
                # Reconfigure the VM before trying again
                if self.logger:
                    self.logger.change_status("Reconfiguring VM settings...")
                self.configure()
                
                # Give time for configuration to take effect
                time.sleep(5)
            else:
                if self.logger:
                    self.logger.change_status("Screen size validation failed after maximum attempts - continuing anyway to avoid infinite loop")
                print("[!] Warning: VM size validation failed after multiple attempts. Continuing anyway.")
                break

        # start clash royale
        if self.logger:
            self.logger.change_status("Launching Clash Royale application...")
        print("Starting clash royale")
        clash_apk_base_name = "com.supercell.clashroyale"
        if self.start_app(clash_apk_base_name) is False:
            if self.logger:
                self.logger.change_status("Failed to start Clash Royale - restart failed")
            print("[!] Fatal error! Failed to start Clash Royale.")
            return False

        # wait for clash main to appear
        if self.logger:
            self.logger.change_status("Waiting for Clash Royale main menu to load...")
        print("Waiting for CR main menu")
        clash_main_wait_start_time = time.time()
        clash_main_wait_timeout = 240  # s
        time.sleep(12)
        while 1:
            # if timed out, retry restarting
            if time.time() - clash_main_wait_start_time > clash_main_wait_timeout:
                if self.logger:
                    self.logger.change_status("Timeout waiting for Clash Royale main menu - restarting...")
                print("[!] Fatal error: Timeout reached while waiting for clash main menu to appear.")
                return self.restart()

            # if found main in time, break
            if check_if_on_clash_main_menu(self) is True:
                if self.logger:
                    self.logger.change_status("Clash Royale main menu detected successfully!")
                print("Detected clash main!")
                break

            # click deadspace
            self.click(5, 350)

        restart_duration = str(time.time() - restart_start_time)[:5]
        if self.logger:
            self.logger.change_status(f"MEmu emulator restart completed successfully in {restart_duration}s")
        print(
            f"Took {restart_duration}s to launch emulator",
        )
        return True

    def start(self):
        self.pmc.start_vm(vm_index=self.vm_index)

    def _check_for_emulator_running(self):
        vms: list[VMInfo] = self.pmc.list_vm_info()

        for vm in vms:
            if vm["index"] != self.vm_index:
                continue

            return vm["running"]

        return False

    def stop(self):
        timeout = 30  # s
        start_time = time.time()
        while self._check_for_emulator_running() is True:
            if time.time() - start_time > timeout:
                print(f"[!] Non fatal error: Timeout of {timeout} seconds reached while stopping the emulator.\n")
                return False

            self.pmc.stop_vm(vm_index=self.vm_index)
            time.sleep(3)

        return True

    def click(self, x_coord, y_coord, clicks=1, interval=0.1):
        if clicks == 1:
            self.pmc.send_adb_command_vm(
                vm_index=self.vm_index,
                command=f"shell input tap {x_coord} {y_coord}",
            )
        else:
            for _ in range(clicks):
                self.pmc.send_adb_command_vm(
                    vm_index=self.vm_index,
                    command=f"shell input tap {x_coord} {y_coord}",
                )
                time.sleep(interval)

    def swipe(
        self,
        x_coord1: int,
        y_coord1: int,
        x_coord2: int,
        y_coord2: int,
    ):
        """Method for sending a swipe command to the given vm

        Args:
        ----
            vm_index (int): Index of the vm to send the command to
            x_coord1 (int): X coordinate of the start of the swipe
            y_coord1 (int): Y coordinate of the start of the swipe
            x_coord2 (int): X coordinate of the end of the swipe
            y_coord2 (int): Y coordinate of the end of the swipe

        """
        self.pmc.send_adb_command_vm(
            vm_index=self.vm_index,
            command=f"shell input swipe {x_coord1} {y_coord1} {x_coord2} {y_coord2}",
        )

    def screenshot(self) -> np.ndarray:
        return self.screenshotter[self.vm_index]

    def install_apk(self, apk_path: str):
        """
        This method is used to install an APK on the emulator.
        """
        raise NotImplementedError

    def start_app(self, package_name: str):
        """Start package_name in the emulator.
        Args:
        ----
            logger (Logger): Logger object.

        """
        # Function implementation goes here

        # get list of installed apps
        installed_apps = self.pmc.get_app_info_list_vm(vm_index=self.vm_index)

        # check list of installed apps for names containing base name
        found = [app for app in installed_apps if package_name in app]

        if not found:
            # notify user that clash royale is not installed, program will exit
            print(f"[!] Fatal error: {package_name} is not installed.\nPlease install it and restart")
            return False

        # start Clash Royale
        self.pmc.start_app_vm(package_name, vm_index=self.vm_index)
        print("Successfully initialized Clash app")
        return True


if __name__ == "__main__":
    memu = MemuEmulatorController(render_mode="directx")
    while 1:
        print("Running")
        time.sleep(10)
