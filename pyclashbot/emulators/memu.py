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

# Debug configuration flags - set to True to enable verbose logging for specific areas
DEBUG_CONFIGURATION = {
    "restart": False,  # Enable verbose logging for restart() method
    "configure": True,  # Enable verbose logging for configure() method
    "config_read": True,  # Enable verbose logging for configuration file reading
    "vm_operations": False,  # Enable verbose logging for VM operations
    "screen_size": True,  # Enable verbose logging for screen size operations
    "language": False,  # Enable verbose logging for language setting
    "ads": False,  # Enable verbose logging for ad skipping
    "clash_startup": False,  # Enable verbose logging for Clash Royale startup
}

ANDROID_VERSION = "96"  # android 9, 64 bit
EMULATOR_NAME = f"pyclashbot-{ANDROID_VERSION}"

# Default Memu configuration - matches the working example
# see https://pymemuc.readthedocs.io/pymemuc.html#the-vm-configuration-keys-table
MEMU_CONFIGURATION: dict[str, str | int | float] = {
    "cpus": 2,  # allocate 2 virtual CPU cores
    "memory": 2048,  # allocate 2048 MB RAM (2 GB)
    "start_window_mode": 1,  # remember window position
    "win_scaling_percent2": 100,  # 100% scaling
    "is_customed_resolution": 1,
    "resolution_width": 419,
    "graphics_render_mode": 0,  # opengl (will be overridden by render_mode param)
    "resolution_height": 633,
    "vbox_dpi": 160,
    "cpucap": 50,
    "fps": 40,
    "turbo_mode": 0,
    "enable_audio": 0,
    "is_hide_toolbar": 1,
}


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
    def __init__(self, logger, render_mode: str = "directx"):
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

        self.logger.log(f"Initializing MemuEmulatorController took {str(time.time() - init_start_time)[:5]} seconds")

    def __del__(self):
        self.logger.log("Need to clear residual memu processes here")

    def _initalize_valid_vm(self):
        # no timeout here bc if this fails, then something fatal is wrong
        self.logger.log("Initalizing memu vm...")
        vm_index = -1
        while 1:
            # check for a valid vm
            self.logger.log("Checking for an existing valid vm...")
            vm_index = self._get_clashbot_vm_index()
            if vm_index is not False:
                self.logger.log(f"[+] Found a valid vm: {vm_index}")
                self.vm_index = vm_index
                break

            # if none found, create a new one
            self.logger.log("No existing valid vm!")
            vm_index = self.create()
            if vm_index != -1:
                self._rename_vm("pyclashbot-96")
                self.logger.log(f"[+] Created a new vm: {vm_index}")
                break

        self.vm_index = vm_index
        self.logger.log("Configuring the vm...")
        self.configure()

        self.logger.log("Booting the vm...")
        self.restart()

    def _set_screen_size(self, width, height):
        self.pmc.send_adb_command_vm(
            vm_index=self.vm_index,
            command=f"shell wm size {width}x{height}",
        )

    def _get_clashbot_vm_index(self):
        vms: list[VMInfo] = self.pmc.list_vm_info()

        for vm in vms:
            title = vm["title"]
            if "pyclashbot-96" in title:
                self.vm_index = vm["index"]
                return vm["index"]

        return False

    def _read_config_data(self):
        """Read configuration data from JSON file and merge with defaults.

        This method provides verbose logging about configuration source and fallbacks.
        Returns a dictionary with string keys and proper values.
        """
        debug_config_read = DEBUG_CONFIGURATION.get("config_read", False)

        config_file_path = r"pyclashbot\emulators\configs\memu_config.json"

        if debug_config_read:
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log("[CONFIG] READING CONFIGURATION DATA")
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log(f"[CONFIG] Configuration file path: {config_file_path}")
            self.logger.log(f"[CONFIG] Absolute path: {os.path.abspath(config_file_path)}")
            self.logger.log(f"[CONFIG] Current working directory: {os.getcwd()}")

        # Start with default configuration
        if debug_config_read:
            self.logger.log("[CONFIG] Loading default Memu configuration values:")
            self.logger.log(f"[CONFIG] Default configuration has {len(MEMU_CONFIGURATION)} entries:")
            for key, value in MEMU_CONFIGURATION.items():
                self.logger.log(f"[CONFIG]   Default {key}: {value} (type: {type(value)})")

        config_copy_start = time.time()
        final_config = MEMU_CONFIGURATION.copy()
        config_copy_end = time.time()

        if debug_config_read:
            self.logger.log(f"[CONFIG] Default config copy duration: {config_copy_end - config_copy_start:.3f}s")

        # Check if config file exists
        file_exists = os.path.exists(config_file_path)
        if debug_config_read:
            self.logger.log(f"[CONFIG] File existence check: {file_exists}")

        if not file_exists:
            if debug_config_read:
                self.logger.log("[CONFIG] ✗ CONFIGURATION FILE NOT FOUND")
                self.logger.log(f"[CONFIG] Searched at: {config_file_path}")
                self.logger.log(f"[CONFIG] Using all default configuration values ({len(final_config)} settings)")
            return final_config

        if debug_config_read:
            self.logger.log("[CONFIG] ✓ CONFIGURATION FILE FOUND")
            self.logger.log(f"[CONFIG] File path: {config_file_path}")

        # Try to read the config file
        file_read_start = time.time()
        try:
            if debug_config_read:
                self.logger.log("[CONFIG] Opening file for reading...")

            with open(config_file_path) as config_file:
                file_config_data = json.load(config_file)

            file_read_end = time.time()

            if debug_config_read:
                self.logger.log("[CONFIG] ✓ SUCCESSFULLY READ JSON FILE")
                self.logger.log(f"[CONFIG] File read duration: {file_read_end - file_read_start:.3f}s")
                self.logger.log(f"[CONFIG] Loaded {len(file_config_data)} entries from file:")
                for key, value in file_config_data.items():
                    self.logger.log(f"[CONFIG]   File {key}: {value} (type: {type(value)})")

            # Merge file config with defaults (string keys to string keys)
            override_count = 0
            unknown_count = 0

            for str_key, value in file_config_data.items():
                if str_key in MEMU_CONFIGURATION:
                    old_value = final_config[str_key]
                    final_config[str_key] = value
                    override_count += 1
                    if debug_config_read:
                        self.logger.log(f"[CONFIG]   ✓ OVERRIDE: {str_key}: {old_value} → {value}")
                else:
                    unknown_count += 1
                    if debug_config_read:
                        self.logger.log(f"[CONFIG]   ✗ UNKNOWN KEY: '{str_key}' not in default config, skipping")

            if not file_config_data:
                if debug_config_read:
                    self.logger.log("[CONFIG] ⚠ EMPTY CONFIGURATION FILE")
                    self.logger.log("[CONFIG] Using all default configuration values")

            if debug_config_read:
                self.logger.log("[CONFIG] Configuration merge summary:")
                self.logger.log(f"[CONFIG]   Total file entries: {len(file_config_data)}")
                self.logger.log(f"[CONFIG]   Successful overrides: {override_count}")
                self.logger.log(f"[CONFIG]   Unknown keys skipped: {unknown_count}")

        except json.JSONDecodeError as e:
            file_read_end = time.time()
            if debug_config_read:
                self.logger.log("[CONFIG] ✗ JSON DECODE ERROR")
                self.logger.log(f"[CONFIG] File read attempt duration: {file_read_end - file_read_start:.3f}s")
                self.logger.log(f"[CONFIG] JSON error: {e}")
                self.logger.log("[CONFIG] Using all default configuration values")
        except Exception as e:
            file_read_end = time.time()
            if debug_config_read:
                self.logger.log("[CONFIG] ✗ FILE READ ERROR")
                self.logger.log(f"[CONFIG] File read attempt duration: {file_read_end - file_read_start:.3f}s")
                self.logger.log(f"[CONFIG] Exception type: {type(e)}")
                self.logger.log(f"[CONFIG] Exception message: {e}")
                self.logger.log("[CONFIG] Using all default configuration values")

        if debug_config_read:
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log("[CONFIG] FINAL MERGED CONFIGURATION")
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log(f"[CONFIG] Total final config entries: {len(final_config)}")
            for key, value in final_config.items():
                source = "FILE" if config_file_path and os.path.exists(config_file_path) else "DEFAULT"
                self.logger.log(f"[CONFIG]   {key}: {value} ({source})")

        return final_config

    def _set_vm_language(self):
        """Set the language of the vm to english"""
        debug_language = DEBUG_CONFIGURATION.get("language", False)

        if debug_language:
            self.logger.log("[LANGUAGE] =======================================================")
            self.logger.log("[LANGUAGE] SETTING VM LANGUAGE TO ENGLISH")
            self.logger.log("[LANGUAGE] =======================================================")
            self.logger.log(f"[LANGUAGE] Target VM index: {self.vm_index}")

        settings_uri = "--uri content://settings/system"
        set_language_commands = [
            f"shell content query {settings_uri} --where \"name='system_locales'\"",
            f"shell content delete {settings_uri} --where \"name='system_locales'\"",
            f"shell content insert {settings_uri} --bind name:s:system_locales --bind value:s:en-US",
            "shell setprop ctl.restart zygote",
        ]

        if debug_language:
            self.logger.log(f"[LANGUAGE] Settings URI: {settings_uri}")
            self.logger.log(f"[LANGUAGE] Total language commands to execute: {len(set_language_commands)}")
            for i, cmd in enumerate(set_language_commands, 1):
                self.logger.log(f"[LANGUAGE]   Command {i}: {cmd}")

        language_start = time.time()
        successful_commands = 0
        failed_commands = 0

        for cmd_index, command in enumerate(set_language_commands, 1):
            if debug_language:
                self.logger.log("[LANGUAGE] -------------------------------------------------------")
                self.logger.log(f"[LANGUAGE] EXECUTING COMMAND {cmd_index}/{len(set_language_commands)}")
                self.logger.log("[LANGUAGE] -------------------------------------------------------")
                self.logger.log(f"[LANGUAGE] Command: {command}")
                self.logger.log(
                    f"[LANGUAGE] About to call: pmc.send_adb_command_vm(vm_index={self.vm_index}, command='{command}')"
                )

            cmd_start = time.time()
            try:
                result = self.pmc.send_adb_command_vm(vm_index=self.vm_index, command=command)
                cmd_end = time.time()
                successful_commands += 1

                if debug_language:
                    self.logger.log(f"[LANGUAGE] ✓ COMMAND {cmd_index} SUCCESSFUL")
                    self.logger.log(f"[LANGUAGE] Command duration: {cmd_end - cmd_start:.3f}s")
                    self.logger.log(f"[LANGUAGE] Command result: {result!r}")
                    self.logger.log(f"[LANGUAGE] Successful commands so far: {successful_commands}")
                    self.logger.log("[LANGUAGE] Sleeping for 0.33 seconds...")

            except Exception as e:
                cmd_end = time.time()
                failed_commands += 1

                if debug_language:
                    self.logger.log(f"[LANGUAGE] ✗ COMMAND {cmd_index} FAILED")
                    self.logger.log(f"[LANGUAGE] Exception type: {type(e)}")
                    self.logger.log(f"[LANGUAGE] Exception message: {e}")
                    self.logger.log(f"[LANGUAGE] Command duration: {cmd_end - cmd_start:.3f}s")
                    self.logger.log(f"[LANGUAGE] Failed commands so far: {failed_commands}")
                    self.logger.log("[LANGUAGE] Sleeping for 0.33 seconds...")

            time.sleep(0.33)

        language_end = time.time()
        if debug_language:
            self.logger.log("[LANGUAGE] =======================================================")
            self.logger.log("[LANGUAGE] LANGUAGE SETTING SUMMARY")
            self.logger.log("[LANGUAGE] =======================================================")
            self.logger.log(f"[LANGUAGE] Total commands executed: {len(set_language_commands)}")
            self.logger.log(f"[LANGUAGE] Successful commands: {successful_commands}")
            self.logger.log(f"[LANGUAGE] Failed commands: {failed_commands}")
            self.logger.log(f"[LANGUAGE] Success rate: {(successful_commands / len(set_language_commands) * 100):.1f}%")
            self.logger.log(f"[LANGUAGE] Total language setting duration: {language_end - language_start:.3f}s")
            self.logger.log(
                f"[LANGUAGE] Average time per command: {(language_end - language_start) / len(set_language_commands):.3f}s"
            )

    def _get_current_config(self) -> dict[str, str]:
        """Get current VM configuration values from the emulator."""
        debug_config_read = DEBUG_CONFIGURATION.get("config_read", False)

        if debug_config_read:
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log("[CONFIG] RETRIEVING CURRENT VM CONFIGURATION FROM EMULATOR")
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log(f"[CONFIG] Target VM index: {self.vm_index}")
            self.logger.log(f"[CONFIG] Configuration keys to query: {len(self.config)}")
            for key in self.config.keys():
                self.logger.log(f"[CONFIG]   Will query: {key}")

        current_configuration = {}
        successful_reads = 0
        failed_reads = 0

        for key_index, key in enumerate(self.config.keys(), 1):
            if debug_config_read:
                self.logger.log("[CONFIG] -------------------------------------------------------")
                self.logger.log(f"[CONFIG] QUERYING {key_index}/{len(self.config)}: {key}")
                self.logger.log("[CONFIG] -------------------------------------------------------")
                self.logger.log(f"[CONFIG] About to call: pmc.get_configuration_vm({key!r}, vm_index={self.vm_index})")

            query_start = time.time()
            try:
                current_value = self.pmc.get_configuration_vm(key, vm_index=self.vm_index)
                query_end = time.time()
                current_configuration[key] = current_value
                successful_reads += 1

                if debug_config_read:
                    self.logger.log(f"[CONFIG] ✓ SUCCESSFULLY READ {key}")
                    self.logger.log(f"[CONFIG] Value: {current_value!r} (type: {type(current_value)})")
                    self.logger.log(f"[CONFIG] Query duration: {query_end - query_start:.3f}s")
                    self.logger.log(f"[CONFIG] Successful reads so far: {successful_reads}")

            except PyMemucError as e:
                query_end = time.time()
                failed_reads += 1

                if debug_config_read:
                    self.logger.log(f"[CONFIG] ✗ FAILED TO READ {key}")
                    self.logger.log(f"[CONFIG] PyMemucError: {e}")
                    self.logger.log(f"[CONFIG] Query duration: {query_end - query_start:.3f}s")
                    self.logger.log(f"[CONFIG] Failed reads so far: {failed_reads}")

                logging.exception("Failed to get configuration for key %s: %s", key, e)

        if debug_config_read:
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log("[CONFIG] CONFIGURATION QUERY SUMMARY")
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log(f"[CONFIG] Total keys queried: {len(self.config)}")
            self.logger.log(f"[CONFIG] Successful reads: {successful_reads}")
            self.logger.log(f"[CONFIG] Failed reads: {failed_reads}")
            self.logger.log(f"[CONFIG] Success rate: {(successful_reads / len(self.config) * 100):.1f}%")
            self.logger.log("[CONFIG] Final configuration retrieved:")
            for key, value in current_configuration.items():
                self.logger.log(f"[CONFIG]   {key}: {value}")

        return current_configuration

    def configure(self):
        """Configure the VM with proper settings, just like the working example."""
        debug_configure = DEBUG_CONFIGURATION.get("configure", False)
        debug_vm_ops = DEBUG_CONFIGURATION.get("vm_operations", False)
        debug_language = DEBUG_CONFIGURATION.get("language", False)
        debug_screen = DEBUG_CONFIGURATION.get("screen_size", False)

        if debug_configure:
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log("[CONFIG] INITIALIZING CONFIGURE METHOD")
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log("[CONFIG] Method called with parameters:")
            self.logger.log(f"[CONFIG]   self.vm_index: {self.vm_index} (type: {type(self.vm_index)})")
            self.logger.log(f"[CONFIG]   self.render_mode: {self.render_mode} (type: {type(self.render_mode)})")
            self.logger.log(f"[CONFIG]   self.config keys: {list(self.config.keys())}")
            self.logger.log(f"[CONFIG]   self.config length: {len(self.config)}")
            self.logger.log("[CONFIG] Debug flags active:")
            self.logger.log(f"[CONFIG]   debug_configure: {debug_configure}")
            self.logger.log(f"[CONFIG]   debug_vm_ops: {debug_vm_ops}")
            self.logger.log(f"[CONFIG]   debug_language: {debug_language}")
            self.logger.log(f"[CONFIG]   debug_screen: {debug_screen}")
            self.logger.log("[CONFIG] Current configuration data:")
            for key, value in self.config.items():
                self.logger.log(f"[CONFIG]   {key}: {value} (type: {type(value)})")

        if debug_configure:
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log("[CONFIG] VALIDATING RENDER MODE PARAMETER")
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log(f"[CONFIG] Raw render_mode input: {self.render_mode!r}")
            self.logger.log(f"[CONFIG] render_mode type: {type(self.render_mode)}")
            self.logger.log("[CONFIG] Attempting to convert to lowercase string...")

        # Validate and set render mode with extreme verbosity
        render_mode_start = time.time()
        try:
            if debug_configure:
                self.logger.log("[CONFIG] Converting render_mode to string...")

            render_mode_str = str(self.render_mode)
            if debug_configure:
                self.logger.log(f"[CONFIG] str() result: {render_mode_str!r}")
                self.logger.log("[CONFIG] Applying .lower() method...")

            render_mode = render_mode_str.lower()
            if debug_configure:
                self.logger.log(f"[CONFIG] .lower() result: {render_mode!r}")
                self.logger.log("[CONFIG] Checking if render_mode in ['opengl', 'directx']...")
                self.logger.log(f"[CONFIG]   render_mode == 'opengl': {render_mode == 'opengl'}")
                self.logger.log(f"[CONFIG]   render_mode == 'directx': {render_mode == 'directx'}")
                self.logger.log(
                    f"[CONFIG]   render_mode in ['opengl', 'directx']: {render_mode in ['opengl', 'directx']}"
                )

            if render_mode not in ["opengl", "directx"]:
                if debug_configure:
                    self.logger.log("[CONFIG] ✗ RENDER MODE VALIDATION FAILED")
                    self.logger.log(f"[CONFIG] Invalid render mode: {render_mode!r}")
                    self.logger.log('[CONFIG] Valid options are: ["opengl", "directx"]')
                    self.logger.log('[CONFIG] Applying fallback to "directx"...')
                render_mode = "directx"
            elif debug_configure:
                self.logger.log("[CONFIG] ✓ RENDER MODE VALIDATION PASSED")
                self.logger.log(f"[CONFIG] Valid render mode: {render_mode!r}")
        except Exception as e:
            render_mode_end = time.time()
            if debug_configure:
                self.logger.log("[CONFIG] ✗ EXCEPTION DURING RENDER MODE CONVERSION")
                self.logger.log(f"[CONFIG] Exception type: {type(e)}")
                self.logger.log(f"[CONFIG] Exception message: {e}")
                self.logger.log(f"[CONFIG] Render mode conversion duration: {render_mode_end - render_mode_start:.3f}s")
                self.logger.log('[CONFIG] Applying fallback to "directx"...')
            render_mode = "directx"

        render_mode_end = time.time()
        if debug_configure:
            self.logger.log("[CONFIG] ✓ RENDER MODE PROCESSING COMPLETE")
            self.logger.log(f"[CONFIG] Final render mode: {render_mode!r}")
            self.logger.log(f"[CONFIG] Render mode processing duration: {render_mode_end - render_mode_start:.3f}s")

        # Create working copy of configuration and set render mode with extreme verbosity
        if debug_configure:
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log("[CONFIG] CREATING WORKING CONFIGURATION COPY")
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log("[CONFIG] About to create copy of self.config...")
            self.logger.log(f"[CONFIG] Original config memory address: {id(self.config)}")

        config_copy_start = time.time()
        working_config = self.config.copy()
        config_copy_end = time.time()

        if debug_configure:
            self.logger.log(f"[CONFIG] Working config memory address: {id(working_config)}")
            self.logger.log(f"[CONFIG] Config copy duration: {config_copy_end - config_copy_start:.3f}s")
            self.logger.log(f"[CONFIG] Working config length: {len(working_config)}")
            self.logger.log("[CONFIG] About to override graphics_render_mode based on render_mode...")
            self.logger.log(
                f"[CONFIG] Current graphics_render_mode: {working_config.get('graphics_render_mode', 'NOT_FOUND')}"
            )

        if render_mode == "directx":
            old_value = working_config.get("graphics_render_mode")
            working_config["graphics_render_mode"] = 1  # directx
            if debug_configure:
                self.logger.log("[CONFIG] ✓ RENDER MODE OVERRIDE: DirectX")
                self.logger.log(f"[CONFIG]   Old graphics_render_mode: {old_value}")
                self.logger.log("[CONFIG]   New graphics_render_mode: 1 (DirectX)")
        else:
            old_value = working_config.get("graphics_render_mode")
            working_config["graphics_render_mode"] = 0  # opengl
            if debug_configure:
                self.logger.log("[CONFIG] ✓ RENDER MODE OVERRIDE: OpenGL")
                self.logger.log(f"[CONFIG]   Old graphics_render_mode: {old_value}")
                self.logger.log("[CONFIG]   New graphics_render_mode: 0 (OpenGL)")

        # Apply each configuration setting with extreme verbosity
        if debug_configure:
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log("[CONFIG] APPLYING CONFIGURATION SETTINGS TO VM")
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log(f"[CONFIG] Total settings to apply: {len(working_config)}")
            self.logger.log(f"[CONFIG] Target VM index: {self.vm_index}")
            self.logger.log("[CONFIG] About to iterate through working_config items...")

        logging.info("Configuring VM %s...", self.vm_index)

        config_apply_start = time.time()
        successful_configs = 0
        failed_configs = 0

        for config_index, (key, value) in enumerate(working_config.items(), 1):
            if debug_configure:
                self.logger.log("[CONFIG] -------------------------------------------------------")
                self.logger.log(f"[CONFIG] SETTING {config_index}/{len(working_config)}: {key}")
                self.logger.log("[CONFIG] -------------------------------------------------------")
                self.logger.log(f"[CONFIG] Key: {key!r} (type: {type(key)})")
                self.logger.log(f"[CONFIG] Value: {value!r} (type: {type(value)})")
                self.logger.log("[CONFIG] Converting value to string for PyMemuc...")

            try:
                str_value = str(value)
                if debug_configure:
                    self.logger.log(f"[CONFIG] String value: {str_value!r}")
                    self.logger.log(
                        f"[CONFIG] About to call: pmc.set_configuration_vm({key!r}, {str_value!r}, vm_index={self.vm_index})"
                    )

                setting_start = time.time()
                self.pmc.set_configuration_vm(key, str_value, vm_index=self.vm_index)
                setting_end = time.time()

                successful_configs += 1
                if debug_configure:
                    self.logger.log(f"[CONFIG] ✓ SUCCESSFULLY SET {key} = {value}")
                    self.logger.log(f"[CONFIG] Setting duration: {setting_end - setting_start:.3f}s")
                    self.logger.log(f"[CONFIG] Successful configs so far: {successful_configs}")

            except Exception as e:
                setting_end = time.time()
                failed_configs += 1
                if debug_configure:
                    self.logger.log(f"[CONFIG] ✗ FAILED TO SET {key} = {value}")
                    self.logger.log(f"[CONFIG] Exception type: {type(e)}")
                    self.logger.log(f"[CONFIG] Exception message: {e}")
                    self.logger.log(f"[CONFIG] Setting attempt duration: {setting_end - setting_start:.3f}s")
                    self.logger.log(f"[CONFIG] Failed configs so far: {failed_configs}")
                logging.exception("Failed to set configuration %s = %s: %s", key, value, e)

        config_apply_end = time.time()
        if debug_configure:
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log("[CONFIG] CONFIGURATION APPLICATION SUMMARY")
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log(f"[CONFIG] Total configurations processed: {len(working_config)}")
            self.logger.log(f"[CONFIG] Successful configurations: {successful_configs}")
            self.logger.log(f"[CONFIG] Failed configurations: {failed_configs}")
            self.logger.log(f"[CONFIG] Success rate: {(successful_configs / len(working_config) * 100):.1f}%")
            self.logger.log(f"[CONFIG] Total application duration: {config_apply_end - config_apply_start:.3f}s")
            self.logger.log(
                f"[CONFIG] Average time per setting: {(config_apply_end - config_apply_start) / len(working_config):.3f}s"
            )

        # Set VM language with extreme verbosity
        if debug_configure or debug_language:
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log("[CONFIG] SETTING VM LANGUAGE TO ENGLISH")
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log("[CONFIG] About to call self._set_vm_language()")

        language_start = time.time()
        try:
            self._set_vm_language()
            language_end = time.time()

            if debug_configure or debug_language:
                self.logger.log("[CONFIG] ✓ SUCCESSFULLY SET VM LANGUAGE TO ENGLISH")
                self.logger.log(f"[CONFIG] Language setting duration: {language_end - language_start:.3f}s")
        except Exception as e:
            language_end = time.time()
            if debug_configure or debug_language:
                self.logger.log("[CONFIG] ✗ FAILED TO SET VM LANGUAGE")
                self.logger.log(f"[CONFIG] Exception type: {type(e)}")
                self.logger.log(f"[CONFIG] Exception message: {e}")
                self.logger.log(f"[CONFIG] Language setting attempt duration: {language_end - language_start:.3f}s")

        logging.info("Configured VM %s", self.vm_index)

        # Set screen size with retry mechanism and extreme verbosity
        expected_width, expected_height = 419, 633
        if debug_configure or debug_screen:
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log("[CONFIG] SETTING VM SCREEN SIZE WITH RETRY MECHANISM")
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log(f"[CONFIG] Target screen size: {expected_width}x{expected_height}")
            self.logger.log("[CONFIG] Retry attempts: 3")

        screen_size_start = time.time()
        successful_attempts = 0
        failed_attempts = 0

        for attempt in range(1, 4):  # 3 attempts
            if debug_configure or debug_screen:
                self.logger.log("[CONFIG] -------------------------------------------------------")
                self.logger.log(f"[CONFIG] SCREEN SIZE ATTEMPT {attempt}/3")
                self.logger.log("[CONFIG] -------------------------------------------------------")
                self.logger.log(f"[CONFIG] About to call: self._set_screen_size({expected_width}, {expected_height})")

            attempt_start = time.time()
            try:
                self._set_screen_size(expected_width, expected_height)
                attempt_end = time.time()
                successful_attempts += 1

                if debug_configure or debug_screen:
                    self.logger.log(f"[CONFIG] ✓ SCREEN SIZE ATTEMPT {attempt} SUCCESSFUL")
                    self.logger.log(f"[CONFIG] Attempt duration: {attempt_end - attempt_start:.3f}s")
                    self.logger.log(f"[CONFIG] Successful attempts so far: {successful_attempts}")

            except Exception as e:
                attempt_end = time.time()
                failed_attempts += 1

                if debug_configure or debug_screen:
                    self.logger.log(f"[CONFIG] ✗ SCREEN SIZE ATTEMPT {attempt} FAILED")
                    self.logger.log(f"[CONFIG] Exception type: {type(e)}")
                    self.logger.log(f"[CONFIG] Exception message: {e}")
                    self.logger.log(f"[CONFIG] Attempt duration: {attempt_end - attempt_start:.3f}s")
                    self.logger.log(f"[CONFIG] Failed attempts so far: {failed_attempts}")

        screen_size_end = time.time()
        if debug_configure or debug_screen:
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log("[CONFIG] SCREEN SIZE SETTING SUMMARY")
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log("[CONFIG] Total attempts: 3")
            self.logger.log(f"[CONFIG] Successful attempts: {successful_attempts}")
            self.logger.log(f"[CONFIG] Failed attempts: {failed_attempts}")
            self.logger.log(f"[CONFIG] Success rate: {(successful_attempts / 3 * 100):.1f}%")
            self.logger.log(f"[CONFIG] Total screen size duration: {screen_size_end - screen_size_start:.3f}s")

        if debug_configure:
            total_config_time = time.time() - render_mode_start
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log("[CONFIG] COMPLETE CONFIGURATION METHOD SUMMARY")
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log(f"[CONFIG] VM Index: {self.vm_index}")
            self.logger.log(f"[CONFIG] Final render mode: {render_mode}")
            self.logger.log(f"[CONFIG] Configuration settings applied: {successful_configs}/{len(working_config)}")
            self.logger.log(
                f"[CONFIG] Language setting: {'SUCCESS' if language_end - language_start < 30 else 'UNKNOWN'}"
            )
            self.logger.log(f"[CONFIG] Screen size attempts: {successful_attempts}/3")
            self.logger.log(f"[CONFIG] Total configuration time: {total_config_time:.3f}s")
            self.logger.log("[CONFIG] =======================================================")
            self.logger.log("[CONFIG] VM CONFIGURATION COMPLETE")
            self.logger.log("[CONFIG] =======================================================")

    def _start_memuc_console(self):
        """Start the memuc console and return the process ID"""
        self.logger.log("Starting memuc console...")

        # check if memu console is already running
        for process in psutil.process_iter():
            with contextlib.suppress(psutil.NoSuchProcess, psutil.AccessDenied):
                if process.name() == "MEMuConsole.exe":
                    self.logger.log("[+] Memu console is already running.")
                    return process.pid

        console_path = join(self.pmc._get_memu_top_level(), "MEMuConsole.exe")
        self.logger.log("[+] Starting memu console at:" + str(console_path))
        process = subprocess.Popen(console_path, creationflags=subprocess.DETACHED_PROCESS)

        time.sleep(2)

        if process.pid is not None:
            self.logger.log("[+] Memu console started successfully.")
        else:
            self.logger.log("[!] Failed to start memu console.")

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

        loops = 3

        for _ in range(loops):
            for proc in psutil.process_iter():
                try:
                    if proc.name() in name_list:
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    self.logger.log("[!] Non-fatal error: Failed to kill process:", proc.name())

    def _skip_ads(self):
        """Skip ads in the emulator.

        Returns:
            bool: True if ads skipped successfully, False otherwise
        """
        debug_ads = DEBUG_CONFIGURATION.get("ads", False)

        if debug_ads:
            self.logger.log("[ADS] =======================================================")
            self.logger.log("[ADS] SKIPPING MEMU ADS")
            self.logger.log("[ADS] =======================================================")
            self.logger.log(f"[ADS] Target VM index: {self.vm_index}")
            self.logger.log("[ADS] Method: Send 'home' keystrokes to dismiss ads")
            self.logger.log("[ADS] Total attempts: 4")
            self.logger.log("[ADS] Sleep between attempts: 1 second")

        ads_start = time.time()
        successful_keypresses = 0
        failed_keypresses = 0

        try:
            if debug_ads:
                self.logger.log("[ADS] About to start home button press sequence...")

            for i in range(4):
                attempt_num = i + 1
                if debug_ads:
                    self.logger.log("[ADS] -------------------------------------------------------")
                    self.logger.log(f"[ADS] AD SKIP ATTEMPT {attempt_num}/4")
                    self.logger.log("[ADS] -------------------------------------------------------")
                    self.logger.log(f"[ADS] About to call: pmc.trigger_keystroke_vm('home', vm_index={self.vm_index})")

                keypress_start = time.time()
                try:
                    result = self.pmc.trigger_keystroke_vm("home", vm_index=self.vm_index)
                    keypress_end = time.time()
                    successful_keypresses += 1

                    if debug_ads:
                        self.logger.log(f"[ADS] ✓ KEYPRESS {attempt_num} SUCCESSFUL")
                        self.logger.log(f"[ADS] Keypress duration: {keypress_end - keypress_start:.3f}s")
                        self.logger.log(f"[ADS] Keypress result: {result!r}")
                        self.logger.log(f"[ADS] Successful keypresses so far: {successful_keypresses}")
                        self.logger.log("[ADS] Sleeping for 1 second...")

                except Exception as keypress_err:
                    keypress_end = time.time()
                    failed_keypresses += 1

                    if debug_ads:
                        self.logger.log(f"[ADS] ✗ KEYPRESS {attempt_num} FAILED")
                        self.logger.log(f"[ADS] Exception type: {type(keypress_err)}")
                        self.logger.log(f"[ADS] Exception message: {keypress_err}")
                        self.logger.log(f"[ADS] Keypress duration: {keypress_end - keypress_start:.3f}s")
                        self.logger.log(f"[ADS] Failed keypresses so far: {failed_keypresses}")
                        self.logger.log("[ADS] Sleeping for 1 second...")

                time.sleep(1)

            ads_end = time.time()
            if debug_ads:
                self.logger.log("[ADS] =======================================================")
                self.logger.log("[ADS] AD SKIP SUMMARY")
                self.logger.log("[ADS] =======================================================")
                self.logger.log("[ADS] Total attempts: 4")
                self.logger.log(f"[ADS] Successful keypresses: {successful_keypresses}")
                self.logger.log(f"[ADS] Failed keypresses: {failed_keypresses}")
                self.logger.log(f"[ADS] Success rate: {(successful_keypresses / 4 * 100):.1f}%")
                self.logger.log(f"[ADS] Total ad skip duration: {ads_end - ads_start:.3f}s")
                self.logger.log("[ADS] ✓ ALL AD SKIP ATTEMPTS COMPLETED SUCCESSFULLY")

        except Exception as err:
            ads_end = time.time()
            if debug_ads:
                self.logger.log("[ADS] =======================================================")
                self.logger.log("[ADS] AD SKIP FAILED - OUTER EXCEPTION")
                self.logger.log("[ADS] =======================================================")
                self.logger.log(f"[ADS] Exception type: {type(err)}")
                self.logger.log(f"[ADS] Exception message: {err}")
                self.logger.log(f"[ADS] Total attempts made: {successful_keypresses + failed_keypresses}")
                self.logger.log(f"[ADS] Successful keypresses: {successful_keypresses}")
                self.logger.log(f"[ADS] Failed keypresses: {failed_keypresses}")
                self.logger.log(f"[ADS] Duration until failure: {ads_end - ads_start:.3f}s")
                self.logger.log("[ADS] RETURNING FALSE DUE TO EXCEPTION")
            return False

        return True

    def _rename_vm(
        self,
        name: str,
    ):
        """Rename the vm to name"""
        self.pmc.rename_vm(vm_index=self.vm_index, new_name=name)

    def _check_vm_size(self):
        debug_screen = DEBUG_CONFIGURATION.get("screen_size", False)
        expected_width, expected_height = 419, 633

        if debug_screen:
            self.logger.log("[SCREEN] =======================================================")
            self.logger.log("[SCREEN] CHECKING VM SCREEN SIZE")
            self.logger.log("[SCREEN] =======================================================")
            self.logger.log(f"[SCREEN] Target VM index: {self.vm_index}")
            self.logger.log(f"[SCREEN] Expected dimensions: {expected_width}x{expected_height}")
            self.logger.log("[SCREEN] Method: Take screenshot and validate dimensions")

        size_check_start = time.time()

        try:
            # Step 1: Press home key to prepare
            if debug_screen:
                self.logger.log("[SCREEN] Step 1: Pressing home key to prepare for screen size check...")
                self.logger.log(f"[SCREEN] About to call: pmc.trigger_keystroke_vm('home', vm_index={self.vm_index})")

            self.logger.change_status("Pressing home key to prepare for screen size check...")

            keypress_start = time.time()
            self.pmc.trigger_keystroke_vm("home", vm_index=self.vm_index)
            keypress_end = time.time()

            if debug_screen:
                self.logger.log("[SCREEN] ✓ Home key pressed successfully")
                self.logger.log(f"[SCREEN] Keypress duration: {keypress_end - keypress_start:.3f}s")
                self.logger.log("[SCREEN] Waiting 2 seconds for screen to stabilize...")

            time.sleep(2)  # Wait for screen to stabilize

            # Step 2: Take screenshot
            if debug_screen:
                self.logger.log("[SCREEN] Step 2: Taking screenshot to verify screen dimensions...")
                self.logger.log("[SCREEN] About to call: self.screenshot()")

            self.logger.change_status("Taking screenshot to verify screen dimensions...")

            screenshot_start = time.time()
            image = self.screenshot()
            screenshot_end = time.time()

            if debug_screen:
                self.logger.log("[SCREEN] ✓ Screenshot captured successfully")
                self.logger.log(f"[SCREEN] Screenshot duration: {screenshot_end - screenshot_start:.3f}s")
                self.logger.log(f"[SCREEN] Image type: {type(image)}")
                self.logger.log(f"[SCREEN] Image shape: {image.shape}")

            # Step 3: Extract dimensions
            height, width, channels = image.shape

            if debug_screen:
                self.logger.log("[SCREEN] Step 3: Analyzing screenshot dimensions...")
                self.logger.log("[SCREEN] Extracted dimensions:")
                self.logger.log(f"[SCREEN]   Width: {width}px")
                self.logger.log(f"[SCREEN]   Height: {height}px")
                self.logger.log(f"[SCREEN]   Channels: {channels}")
                self.logger.log("[SCREEN] Expected dimensions:")
                self.logger.log(f"[SCREEN]   Expected width: {expected_width}px")
                self.logger.log(f"[SCREEN]   Expected height: {expected_height}px")

            self.logger.change_status(
                f"Screen dimensions: {width}x{height} (expected: {expected_width}x{expected_height})"
            )

            # Step 4: Validate dimensions
            width_correct = width == expected_width
            height_correct = height == expected_height
            dimensions_correct = width_correct and height_correct

            if debug_screen:
                self.logger.log("[SCREEN] Step 4: Validating dimensions...")
                self.logger.log(f"[SCREEN] Width validation: {width} == {expected_width} → {width_correct}")
                self.logger.log(f"[SCREEN] Height validation: {height} == {expected_height} → {height_correct}")
                self.logger.log(f"[SCREEN] Overall validation: {dimensions_correct}")

            if not dimensions_correct:
                size_check_end = time.time()
                validation_msg = (
                    f"Screen size validation FAILED: got {width}x{height}, expected {expected_width}x{expected_height}"
                )
                self.logger.change_status(validation_msg)

                if debug_screen:
                    self.logger.log("[SCREEN] ✗ SCREEN SIZE VALIDATION FAILED")
                    self.logger.log(f"[SCREEN] Actual: {width}x{height}")
                    self.logger.log(f"[SCREEN] Expected: {expected_width}x{expected_height}")
                    self.logger.log(f"[SCREEN] Width difference: {width - expected_width}")
                    self.logger.log(f"[SCREEN] Height difference: {height - expected_height}")
                    self.logger.log(f"[SCREEN] Total validation time: {size_check_end - size_check_start:.3f}s")
                    self.logger.log("[SCREEN] RETURNING FALSE")

                return False

            size_check_end = time.time()
            self.logger.change_status("Screen size validation PASSED")

            if debug_screen:
                self.logger.log("[SCREEN] ✓ SCREEN SIZE VALIDATION PASSED")
                self.logger.log(f"[SCREEN] Dimensions match perfectly: {width}x{height}")
                self.logger.log(f"[SCREEN] Total validation time: {size_check_end - size_check_start:.3f}s")
                self.logger.log("[SCREEN] RETURNING TRUE")

            return True

        except Exception as e:
            size_check_end = time.time()
            error_msg = f"Error during screen size check: {e}"
            self.logger.change_status(error_msg)

            if debug_screen:
                self.logger.log("[SCREEN] ✗ EXCEPTION DURING SCREEN SIZE CHECK")
                self.logger.log(f"[SCREEN] Exception type: {type(e)}")
                self.logger.log(f"[SCREEN] Exception message: {e}")
                self.logger.log(f"[SCREEN] Time until exception: {size_check_end - size_check_start:.3f}s")
                self.logger.log("[SCREEN] Assuming valid size to avoid infinite loops")

        # in the case of errors, assume size is correct to avoid infinite loops
        self.logger.change_status("Screen size check error - assuming valid size")

        if debug_screen:
            self.logger.log("[SCREEN] =======================================================")
            self.logger.log("[SCREEN] SCREEN SIZE CHECK ERROR RECOVERY")
            self.logger.log("[SCREEN] =======================================================")
            self.logger.log("[SCREEN] Assuming screen size is valid to prevent infinite restart loops")
            self.logger.log("[SCREEN] RETURNING TRUE (ERROR RECOVERY)")

        return True

    def restart(self, open_clash=True, start_time=None):
        """Restart the emulator with full configuration and app startup sequence.

        Args:
            open_clash (bool): Whether to start Clash Royale after emulator boot
            start_time (float): Start time for timing calculations

        Returns:
            bool: True if restart successful, False otherwise
        """
        debug_restart = DEBUG_CONFIGURATION.get("restart", False)
        debug_vm_ops = DEBUG_CONFIGURATION.get("vm_operations", False)
        debug_clash = DEBUG_CONFIGURATION.get("clash_startup", False)

        if debug_restart:
            self.logger.log("[RESTART] =====================================================")
            self.logger.log("[RESTART] INITIALIZING RESTART METHOD")
            self.logger.log("[RESTART] =====================================================")
            self.logger.log("[RESTART] Method parameters:")
            self.logger.log(f"[RESTART]   open_clash: {open_clash} (type: {type(open_clash)})")
            self.logger.log(f"[RESTART]   start_time: {start_time} (type: {type(start_time)})")
            self.logger.log("[RESTART] Debug flags active:")
            self.logger.log(f"[RESTART]   debug_restart: {debug_restart}")
            self.logger.log(f"[RESTART]   debug_vm_ops: {debug_vm_ops}")
            self.logger.log(f"[RESTART]   debug_clash: {debug_clash}")

        if start_time is None:
            start_time = time.time()
            if debug_restart:
                self.logger.log(f"[RESTART] start_time was None, set to current time: {start_time}")
        elif debug_restart:
            self.logger.log(f"[RESTART] Using provided start_time: {start_time}")

        # Validate vm_index with extreme verbosity
        if debug_restart:
            self.logger.log("[RESTART] =====================================================")
            self.logger.log("[RESTART] VALIDATING VM INDEX")
            self.logger.log("[RESTART] =====================================================")
            self.logger.log(f"[RESTART] Current self.vm_index: {self.vm_index} (type: {type(self.vm_index)})")
            self.logger.log("[RESTART] Checking if vm_index is in [None, -1, '']...")
            self.logger.log(f"[RESTART]   vm_index == None: {self.vm_index is None}")
            self.logger.log(f"[RESTART]   vm_index == -1: {self.vm_index == -1}")
            self.logger.log(f"[RESTART]   vm_index == '': {self.vm_index == ''}")
            self.logger.log(f"[RESTART]   vm_index in [None, -1, '']: {self.vm_index in [None, -1, '']}")

        if self.vm_index in [None, -1, ""]:
            error_msg = "[!] Fatal error: No valid vm_index in MemuEmulatorController.restart()"
            self.logger.change_status(error_msg)
            self.logger.log(error_msg)
            if debug_restart:
                self.logger.log("[RESTART] VM INDEX VALIDATION FAILED - RETURNING FALSE")
            return False

        if debug_restart:
            self.logger.log("[RESTART] ✓ VM INDEX VALIDATION PASSED")
            self.logger.log(f"[RESTART] Valid vm_index: {self.vm_index}")

        if debug_restart:
            self.logger.log("[RESTART] =====================================================")
            self.logger.log("[RESTART] STARTING EMULATOR RESTART SEQUENCE")
            self.logger.log("[RESTART] =====================================================")
            self.logger.log("[RESTART] Restart sequence parameters:")
            self.logger.log(f"[RESTART]   VM Index: {self.vm_index}")
            self.logger.log(f"[RESTART]   Render Mode: {self.render_mode}")
            self.logger.log(f"[RESTART]   Open Clash: {open_clash}")
            self.logger.log(f"[RESTART]   Start Time: {start_time}")
            self.logger.log(f"[RESTART]   Current Time: {time.time()}")

        # Step 1: Stop all MEmu processes with extreme verbosity
        if debug_restart:
            self.logger.log("[RESTART] =====================================================")
            self.logger.log("[RESTART] STEP 1: STOPPING ALL MEMU PROCESSES")
            self.logger.log("[RESTART] =====================================================")

        self.logger.change_status("Stopping all MEmu processes...")
        if debug_restart:
            self.logger.log("[RESTART] Logger status updated to: 'Stopping all MEmu processes...'")
            self.logger.log("[RESTART] About to call self._close_everything_memu()")

        process_close_start = time.time()
        self._close_everything_memu()
        process_close_end = time.time()

        if debug_restart:
            self.logger.log("[RESTART] self._close_everything_memu() completed")
            self.logger.log(f"[RESTART] Process close duration: {process_close_end - process_close_start:.3f}s")

        self.logger.change_status("All MEmu processes stopped")
        if debug_restart:
            self.logger.log("[RESTART] ✓ ALL MEMU PROCESSES STOPPED")
            self.logger.log("[RESTART] Logger status updated to: 'All MEmu processes stopped'")

        # Step 2: Configure the VM (while stopped) with extreme verbosity
        if debug_restart:
            self.logger.log("[RESTART] =====================================================")
            self.logger.log("[RESTART] STEP 2: CONFIGURING VM SETTINGS (WHILE STOPPED)")
            self.logger.log("[RESTART] =====================================================")
            self.logger.log("[RESTART] About to call self.configure() - this will apply all VM settings")
            self.logger.log(f"[RESTART] Configuration will be applied to VM {self.vm_index}")

        self.logger.change_status("Configuring VM settings...")
        if debug_restart:
            self.logger.log("[RESTART] Logger status updated to: 'Configuring VM settings...'")

        config_start = time.time()
        self.configure()  # This will do its own verbose configuration
        config_end = time.time()

        if debug_restart:
            self.logger.log("[RESTART] self.configure() completed")
            self.logger.log(f"[RESTART] Configuration duration: {config_end - config_start:.3f}s")

        self.logger.change_status("VM configuration complete")
        if debug_restart:
            self.logger.log("[RESTART] ✓ VM CONFIGURATION COMPLETE")
            self.logger.log("[RESTART] Logger status updated to: 'VM configuration complete'")

        # Step 3: Start the VM with extreme verbosity
        if debug_restart or debug_vm_ops:
            self.logger.log("[RESTART] =====================================================")
            self.logger.log("[RESTART] STEP 3: STARTING THE VIRTUAL MACHINE")
            self.logger.log("[RESTART] =====================================================")
            self.logger.log(f"[RESTART] About to start VM with index: {self.vm_index}")
            self.logger.log(f"[RESTART] Using PyMemuc command: self.pmc.start_vm(vm_index={self.vm_index})")

        self.logger.change_status("Starting emulator...")
        if debug_restart:
            self.logger.log("[RESTART] Logger status updated to: 'Starting emulator...'")

        vm_start_time = time.time()
        try:
            if debug_vm_ops:
                self.logger.log(f"[RESTART] Executing: self.pmc.start_vm(vm_index={self.vm_index})")

            result = self.pmc.start_vm(vm_index=self.vm_index)
            vm_start_end = time.time()

            if debug_vm_ops:
                self.logger.log(f"[RESTART] VM start command result: {result}")
                self.logger.log(f"[RESTART] VM start command duration: {vm_start_end - vm_start_time:.3f}s")
                self.logger.log("[RESTART] ✓ EMULATOR START COMMAND SENT SUCCESSFULLY")

        except Exception as e:
            vm_start_end = time.time()
            error_msg = f"Failed to start emulator: {e}"

            if debug_restart:
                self.logger.log("[RESTART] ✗ EXCEPTION DURING VM START")
                self.logger.log(f"[RESTART] Exception type: {type(e)}")
                self.logger.log(f"[RESTART] Exception message: {e}")
                self.logger.log(f"[RESTART] VM start attempt duration: {vm_start_end - vm_start_time:.3f}s")
                self.logger.log("[RESTART] RETURNING FALSE DUE TO VM START FAILURE")

            self.logger.change_status(error_msg)
            return False

        # Step 4: Skip ads with extreme verbosity
        if debug_restart or DEBUG_CONFIGURATION.get("ads", False):
            self.logger.log("[RESTART] =====================================================")
            self.logger.log("[RESTART] STEP 4: SKIPPING MEMU ADS")
            self.logger.log("[RESTART] =====================================================")

        self.logger.change_status("Skipping MEmu ads...")
        if debug_restart:
            self.logger.log("[RESTART] Logger status updated to: 'Skipping MEmu ads...'")
            self.logger.log("[RESTART] About to call self._skip_ads()")

        ads_start = time.time()
        ads_result = self._skip_ads()
        ads_end = time.time()

        if debug_restart:
            self.logger.log(f"[RESTART] self._skip_ads() returned: {ads_result}")
            self.logger.log(f"[RESTART] Ad skip duration: {ads_end - ads_start:.3f}s")

        if not ads_result:
            if debug_restart:
                self.logger.log("[RESTART] ✗ AD SKIP FAILED - INITIATING RECURSIVE RESTART")
                self.logger.log(f"[RESTART] Calling self.restart(open_clash={open_clash}, start_time={start_time})")

            self.logger.change_status("Failed to skip ads, restarting...")
            return self.restart(open_clash=open_clash, start_time=start_time)

        if debug_restart:
            self.logger.log("[RESTART] ✓ SUCCESSFULLY SKIPPED ADS")

        # Step 5: Validate screen size with extreme verbosity
        if debug_restart or DEBUG_CONFIGURATION.get("screen_size", False):
            self.logger.log("[RESTART] =====================================================")
            self.logger.log("[RESTART] STEP 5: VALIDATING SCREEN SIZE")
            self.logger.log("[RESTART] =====================================================")

        self.logger.change_status("Validating screen size...")
        if debug_restart:
            self.logger.log("[RESTART] Logger status updated to: 'Validating screen size...'")
            self.logger.log("[RESTART] About to call self._check_vm_size()")

        size_check_start = time.time()
        size_valid = self._check_vm_size()
        size_check_end = time.time()

        if debug_restart:
            self.logger.log(f"[RESTART] self._check_vm_size() returned: {size_valid}")
            self.logger.log(f"[RESTART] Size check duration: {size_check_end - size_check_start:.3f}s")

        if not size_valid:
            if debug_restart:
                self.logger.log("[RESTART] ✗ SCREEN SIZE VALIDATION FAILED - INITIATING RECURSIVE RESTART")
                self.logger.log(f"[RESTART] Calling self.restart(open_clash={open_clash}, start_time={start_time})")

            self.logger.change_status("VM size validation failed, restarting...")
            return self.restart(open_clash=open_clash, start_time=start_time)

        if debug_restart:
            self.logger.log("[RESTART] ✓ SCREEN SIZE VALIDATION PASSED")

        # Step 6: Start Clash Royale if requested with extreme verbosity
        if open_clash:
            if debug_restart or debug_clash:
                self.logger.log("[RESTART] =====================================================")
                self.logger.log("[RESTART] STEP 6: STARTING CLASH ROYALE")
                self.logger.log("[RESTART] =====================================================")
                self.logger.log("[RESTART] open_clash is True, proceeding with Clash Royale startup")

            self.logger.change_status("Starting Clash Royale...")
            if debug_restart:
                self.logger.log("[RESTART] Logger status updated to: 'Starting Clash Royale...'")
                self.logger.log("[RESTART] About to call self.start_app('com.supercell.clashroyale')")

            clash_start_time = time.time()
            try:
                app_start_result = self.start_app("com.supercell.clashroyale")
                clash_start_end = time.time()

                if debug_clash:
                    self.logger.log(f"[RESTART] self.start_app() returned: {app_start_result}")
                    self.logger.log(f"[RESTART] Clash start duration: {clash_start_end - clash_start_time:.3f}s")

                if not app_start_result:
                    if debug_restart:
                        self.logger.log("[RESTART] ✗ CLASH ROYALE START FAILED")
                        self.logger.log("[RESTART] RETURNING FALSE DUE TO CLASH START FAILURE")
                    return False

                if debug_restart:
                    self.logger.log("[RESTART] ✓ CLASH ROYALE STARTED SUCCESSFULLY")

            except Exception as e:
                clash_start_end = time.time()
                if debug_restart:
                    self.logger.log("[RESTART] ✗ EXCEPTION DURING CLASH ROYALE START")
                    self.logger.log(f"[RESTART] Exception type: {type(e)}")
                    self.logger.log(f"[RESTART] Exception message: {e}")
                    self.logger.log(
                        f"[RESTART] Clash start attempt duration: {clash_start_end - clash_start_time:.3f}s"
                    )
                return False

            # Step 7: Wait for Clash main menu with extreme verbosity
            if debug_restart or debug_clash:
                self.logger.log("[RESTART] =====================================================")
                self.logger.log("[RESTART] STEP 7: WAITING FOR CLASH ROYALE MAIN MENU")
                self.logger.log("[RESTART] =====================================================")

            self.logger.change_status("Waiting for Clash Royale main menu...")
            if debug_restart:
                self.logger.log("[RESTART] Logger status updated to: 'Waiting for Clash Royale main menu...'")

            clash_main_wait_start_time = time.time()
            clash_main_wait_timeout = 240  # seconds

            if debug_clash:
                self.logger.log("[RESTART] Wait parameters:")
                self.logger.log(f"[RESTART]   wait_start_time: {clash_main_wait_start_time}")
                self.logger.log(f"[RESTART]   wait_timeout: {clash_main_wait_timeout}s")
                self.logger.log(f"[RESTART]   wait_end_time: {clash_main_wait_start_time + clash_main_wait_timeout}")
                self.logger.log("[RESTART] Initial 12-second wait before checking main menu...")

            time.sleep(12)  # Initial wait

            if debug_clash:
                self.logger.log("[RESTART] Initial wait complete, starting main menu detection loop...")

            loop_iteration = 0
            while time.time() - clash_main_wait_start_time < clash_main_wait_timeout:
                loop_iteration += 1
                current_time = time.time()
                elapsed_wait = current_time - clash_main_wait_start_time
                remaining_time = clash_main_wait_timeout - elapsed_wait

                if debug_clash:
                    self.logger.log(f"[RESTART] Main menu wait loop iteration {loop_iteration}")
                    self.logger.log(f"[RESTART]   Current time: {current_time}")
                    self.logger.log(f"[RESTART]   Elapsed wait: {elapsed_wait:.1f}s")
                    self.logger.log(f"[RESTART]   Remaining time: {remaining_time:.1f}s")
                    self.logger.log("[RESTART] Checking if on Clash main menu...")

                menu_check_start = time.time()
                if check_if_on_clash_main_menu(self):
                    menu_check_end = time.time()
                    total_elapsed = str(time.time() - start_time)[:5]

                    if debug_clash:
                        self.logger.log("[RESTART] ✓ CLASH MAIN MENU DETECTED!")
                        self.logger.log(f"[RESTART] Menu check duration: {menu_check_end - menu_check_start:.3f}s")
                        self.logger.log(f"[RESTART] Total wait time: {elapsed_wait:.1f}s")
                        self.logger.log(f"[RESTART] Total restart time: {total_elapsed}s")

                    self.logger.change_status("Clash main menu detected!")
                    self.logger.log(f"Emulator restart completed in {total_elapsed}s")

                    if debug_restart:
                        self.logger.log("[RESTART] =====================================================")
                        self.logger.log("[RESTART] RESTART SEQUENCE COMPLETED SUCCESSFULLY")
                        self.logger.log("[RESTART] =====================================================")

                    return True

                menu_check_end = time.time()
                if debug_clash:
                    self.logger.log(
                        f"[RESTART] Main menu not detected (check took {menu_check_end - menu_check_start:.3f}s)"
                    )
                    self.logger.log("[RESTART] Clicking deadspace at (5, 350) to handle popups...")

                # Click deadspace to handle any popups
                click_start = time.time()
                self.click(5, 350)
                click_end = time.time()

                if debug_clash:
                    self.logger.log(f"[RESTART] Deadspace click completed ({click_end - click_start:.3f}s)")
                    self.logger.log("[RESTART] Sleeping for 1 second before next iteration...")

                time.sleep(1)

            # Timeout waiting for main menu
            final_elapsed_wait = time.time() - clash_main_wait_start_time
            if debug_restart or debug_clash:
                self.logger.log("[RESTART] ✗ TIMEOUT WAITING FOR CLASH MAIN MENU")
                self.logger.log(f"[RESTART] Total wait time: {final_elapsed_wait:.1f}s")
                self.logger.log(f"[RESTART] Timeout threshold: {clash_main_wait_timeout}s")
                self.logger.log(f"[RESTART] Loop iterations: {loop_iteration}")
                self.logger.log("[RESTART] INITIATING RECURSIVE RESTART DUE TO TIMEOUT")

            self.logger.change_status("Timeout waiting for Clash main menu, restarting...")
            return self.restart(open_clash=open_clash, start_time=start_time)

        # If not opening Clash, we're done
        else:
            total_elapsed = str(time.time() - start_time)[:5]

            if debug_restart:
                self.logger.log("[RESTART] =====================================================")
                self.logger.log("[RESTART] RESTART SEQUENCE COMPLETED (NO CLASH)")
                self.logger.log("[RESTART] =====================================================")
                self.logger.log("[RESTART] open_clash was False, skipping Clash Royale startup")
                self.logger.log(f"[RESTART] Total restart time: {total_elapsed}s")

            self.logger.log(f"Emulator restart completed in {total_elapsed}s")
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
                self.logger.log(
                    f"[!] Non fatal error: Timeout of {timeout} seconds reached while stopping the emulator.\n"
                )
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
            return self._wait_for_clash_installation(package_name)

        # start Clash Royale
        self.pmc.start_app_vm(package_name, vm_index=self.vm_index)
        self.logger.log("Successfully initialized Clash app")
        return True

    def _wait_for_clash_installation(self, package_name: str):
        """Wait for user to install Clash Royale using the logger action system"""
        self.current_package_name = package_name  # Store for retry logic
        self.logger.show_temporary_action(
            message=f"{package_name} not installed - please install it and complete tutorial",
            action_text="Retry",
            callback=self._retry_installation_check,
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
        package_name = getattr(self, "current_package_name", "com.supercell.clashroyale")
        installed_apps = self.pmc.get_app_info_list_vm(vm_index=self.vm_index)
        found = [app for app in installed_apps if package_name in app]

        if found:
            # Installation successful!
            self.installation_waiting = False
            self.logger.change_status("Installation complete - continuing...")
        else:
            # Still not installed, show the retry button again
            self.logger.show_temporary_action(
                message=f"{package_name} still not found - please install it and complete tutorial",
                action_text="Retry",
                callback=self._retry_installation_check,
            )
            self.logger.log(f"[!] {package_name} still not installed. Please try again.")


if __name__ == "__main__":
    from pyclashbot.utils.logger import Logger

    test_logger = Logger()
    memu = MemuEmulatorController(test_logger, render_mode="directx")
    while 1:
        test_logger.log("Running")
        time.sleep(10)
