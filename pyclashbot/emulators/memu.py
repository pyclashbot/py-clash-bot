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
from pyclashbot.emulators import ActionCallback
from pyclashbot.emulators.base import BaseEmulatorController
from pyclashbot.utils.cancellation import interruptible_sleep
from pyclashbot.utils.platform import Platform

logger = logging.getLogger(__name__)

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

ANDROID_VERSION = "126"  # android 12, 64 bit
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
                interruptible_sleep(0.1)


def verify_memu_installation():
    try:
        PyMemuc()
        return True
    except Exception:
        pass
    return False


class MemuEmulatorController(BaseEmulatorController):
    supported_platforms = [Platform.WINDOWS]

    def __init__(
        self,
        render_mode: str = "directx",
        debug_mode: bool = False,
        action_callback: ActionCallback | None = None,
    ):
        """
        Initializes the MemuEmulatorController with a reference to PyMemuc and the selected VM index.
        Ensures only one VM with the given name exists.
        """
        self._action_callback = action_callback
        self.debug_mode = debug_mode
        init_start_time = time.time()
        self.pmc = PyMemuc()

        self.config = self._read_config_data()
        self.render_mode = render_mode

        # screenshot stuff
        self.screenshotter = MemuScreenCapture(self.pmc)

        # get a valid vm to use
        self._initalize_valid_vm()

        logger.info(f"Initializing MemuEmulatorController took {str(time.time() - init_start_time)[:5]} seconds")
        if self.debug_mode:
            logger.info("You are using Debug MODE (NO RESTART, NO CONFIGURE)")

    def __del__(self):
        logger.info("Need to clear residual memu processes here")

    def _initalize_valid_vm(self):
        # no timeout here bc if this fails, then something fatal is wrong
        logger.info("Initalizing memu vm...")
        vm_index = -1
        while 1:
            # check for a valid vm
            logger.info("Checking for an existing valid vm...")
            vm_index = self._get_clashbot_vm_index()
            if vm_index is not False:
                logger.info(f"[+] Found a valid vm: {vm_index}")
                self.vm_index = vm_index
                break

            # if none found, create a new one
            logger.info("No existing valid vm!")
            vm_index = self.create()
            if vm_index != -1:
                self._rename_vm("pyclashbot-126")
                logger.info(f"[+] Created a new vm: {vm_index}")
                break

        self.vm_index = vm_index

        if not self.debug_mode:
            logger.info("Configuring the vm...")
            self.configure()
            logger.info("Booting the vm...")
            self.restart()
        else:
            logger.info("Debug mode enabled - skipping configure and restart")

    def _set_screen_size(self, width, height):
        self.pmc.send_adb_command_vm(
            vm_index=self.vm_index,
            command=f"shell wm size {width}x{height}",
        )

    def _get_clashbot_vm_index(self):
        vms: list[VMInfo] = self.pmc.list_vm_info()

        for vm in vms:
            title = vm["title"]
            if "pyclashbot-126" in title:
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
            logger.info("[CONFIG] =======================================================")
            logger.info("[CONFIG] READING CONFIGURATION DATA")
            logger.info("[CONFIG] =======================================================")
            logger.info(f"[CONFIG] Configuration file path: {config_file_path}")
            logger.info(f"[CONFIG] Absolute path: {os.path.abspath(config_file_path)}")
            logger.info(f"[CONFIG] Current working directory: {os.getcwd()}")

        # Start with default configuration
        if debug_config_read:
            logger.info("[CONFIG] Loading default Memu configuration values:")
            logger.info(f"[CONFIG] Default configuration has {len(MEMU_CONFIGURATION)} entries:")
            for key, value in MEMU_CONFIGURATION.items():
                logger.info(f"[CONFIG]   Default {key}: {value} (type: {type(value)})")

        config_copy_start = time.time()
        final_config = MEMU_CONFIGURATION.copy()
        config_copy_end = time.time()

        if debug_config_read:
            logger.info(f"[CONFIG] Default config copy duration: {config_copy_end - config_copy_start:.3f}s")

        # Check if config file exists
        file_exists = os.path.exists(config_file_path)
        if debug_config_read:
            logger.info(f"[CONFIG] File existence check: {file_exists}")

        if not file_exists:
            if debug_config_read:
                logger.info("[CONFIG] ✗ CONFIGURATION FILE NOT FOUND")
                logger.info(f"[CONFIG] Searched at: {config_file_path}")
                logger.info(f"[CONFIG] Using all default configuration values ({len(final_config)} settings)")
            return final_config

        if debug_config_read:
            logger.info("[CONFIG] ✓ CONFIGURATION FILE FOUND")
            logger.info(f"[CONFIG] File path: {config_file_path}")

        # Try to read the config file
        file_read_start = time.time()
        try:
            if debug_config_read:
                logger.info("[CONFIG] Opening file for reading...")

            with open(config_file_path) as config_file:
                file_config_data = json.load(config_file)

            file_read_end = time.time()

            if debug_config_read:
                logger.info("[CONFIG] ✓ SUCCESSFULLY READ JSON FILE")
                logger.info(f"[CONFIG] File read duration: {file_read_end - file_read_start:.3f}s")
                logger.info(f"[CONFIG] Loaded {len(file_config_data)} entries from file:")
                for key, value in file_config_data.items():
                    logger.info(f"[CONFIG]   File {key}: {value} (type: {type(value)})")

            # Merge file config with defaults (string keys to string keys)
            override_count = 0
            unknown_count = 0

            for str_key, value in file_config_data.items():
                if str_key in MEMU_CONFIGURATION:
                    old_value = final_config[str_key]
                    final_config[str_key] = value
                    override_count += 1
                    if debug_config_read:
                        logger.info(f"[CONFIG]   ✓ OVERRIDE: {str_key}: {old_value} → {value}")
                else:
                    unknown_count += 1
                    if debug_config_read:
                        logger.info(f"[CONFIG]   ✗ UNKNOWN KEY: '{str_key}' not in default config, skipping")

            if not file_config_data:
                if debug_config_read:
                    logger.info("[CONFIG] ⚠ EMPTY CONFIGURATION FILE")
                    logger.info("[CONFIG] Using all default configuration values")

            if debug_config_read:
                logger.info("[CONFIG] Configuration merge summary:")
                logger.info(f"[CONFIG]   Total file entries: {len(file_config_data)}")
                logger.info(f"[CONFIG]   Successful overrides: {override_count}")
                logger.info(f"[CONFIG]   Unknown keys skipped: {unknown_count}")

        except json.JSONDecodeError as e:
            file_read_end = time.time()
            if debug_config_read:
                logger.info("[CONFIG] ✗ JSON DECODE ERROR")
                logger.info(f"[CONFIG] File read attempt duration: {file_read_end - file_read_start:.3f}s")
                logger.info(f"[CONFIG] JSON error: {e}")
                logger.info("[CONFIG] Using all default configuration values")
        except Exception as e:
            file_read_end = time.time()
            if debug_config_read:
                logger.info("[CONFIG] ✗ FILE READ ERROR")
                logger.info(f"[CONFIG] File read attempt duration: {file_read_end - file_read_start:.3f}s")
                logger.info(f"[CONFIG] Exception type: {type(e)}")
                logger.info(f"[CONFIG] Exception message: {e}")
                logger.info("[CONFIG] Using all default configuration values")

        if debug_config_read:
            logger.info("[CONFIG] =======================================================")
            logger.info("[CONFIG] FINAL MERGED CONFIGURATION")
            logger.info("[CONFIG] =======================================================")
            logger.info(f"[CONFIG] Total final config entries: {len(final_config)}")
            for key, value in final_config.items():
                source = "FILE" if config_file_path and os.path.exists(config_file_path) else "DEFAULT"
                logger.info(f"[CONFIG]   {key}: {value} ({source})")

        return final_config

    def _set_vm_language(self):
        """Set the language of the vm to english"""
        debug_language = DEBUG_CONFIGURATION.get("language", False)

        if debug_language:
            logger.info("[LANGUAGE] =======================================================")
            logger.info("[LANGUAGE] SETTING VM LANGUAGE TO ENGLISH")
            logger.info("[LANGUAGE] =======================================================")
            logger.info(f"[LANGUAGE] Target VM index: {self.vm_index}")

        settings_uri = "--uri content://settings/system"
        set_language_commands = [
            f"shell content query {settings_uri} --where \"name='system_locales'\"",
            f"shell content delete {settings_uri} --where \"name='system_locales'\"",
            f"shell content insert {settings_uri} --bind name:s:system_locales --bind value:s:en-US",
            "shell setprop ctl.restart zygote",
        ]

        if debug_language:
            logger.info(f"[LANGUAGE] Settings URI: {settings_uri}")
            logger.info(f"[LANGUAGE] Total language commands to execute: {len(set_language_commands)}")
            for i, cmd in enumerate(set_language_commands, 1):
                logger.info(f"[LANGUAGE]   Command {i}: {cmd}")

        language_start = time.time()
        successful_commands = 0
        failed_commands = 0

        for cmd_index, command in enumerate(set_language_commands, 1):
            if debug_language:
                logger.info("[LANGUAGE] -------------------------------------------------------")
                logger.info(f"[LANGUAGE] EXECUTING COMMAND {cmd_index}/{len(set_language_commands)}")
                logger.info("[LANGUAGE] -------------------------------------------------------")
                logger.info(f"[LANGUAGE] Command: {command}")
                logger.info(
                    f"[LANGUAGE] About to call: pmc.send_adb_command_vm(vm_index={self.vm_index}, command='{command}')"
                )

            cmd_start = time.time()
            try:
                result = self.pmc.send_adb_command_vm(vm_index=self.vm_index, command=command)
                cmd_end = time.time()
                successful_commands += 1

                if debug_language:
                    logger.info(f"[LANGUAGE] ✓ COMMAND {cmd_index} SUCCESSFUL")
                    logger.info(f"[LANGUAGE] Command duration: {cmd_end - cmd_start:.3f}s")
                    logger.info(f"[LANGUAGE] Command result: {result!r}")
                    logger.info(f"[LANGUAGE] Successful commands so far: {successful_commands}")
                    logger.info("[LANGUAGE] Sleeping for 0.33 seconds...")

            except Exception as e:
                cmd_end = time.time()
                failed_commands += 1

                if debug_language:
                    logger.info(f"[LANGUAGE] ✗ COMMAND {cmd_index} FAILED")
                    logger.info(f"[LANGUAGE] Exception type: {type(e)}")
                    logger.info(f"[LANGUAGE] Exception message: {e}")
                    logger.info(f"[LANGUAGE] Command duration: {cmd_end - cmd_start:.3f}s")
                    logger.info(f"[LANGUAGE] Failed commands so far: {failed_commands}")
                    logger.info("[LANGUAGE] Sleeping for 0.33 seconds...")

            interruptible_sleep(0.33)

        language_end = time.time()
        if debug_language:
            logger.info("[LANGUAGE] =======================================================")
            logger.info("[LANGUAGE] LANGUAGE SETTING SUMMARY")
            logger.info("[LANGUAGE] =======================================================")
            logger.info(f"[LANGUAGE] Total commands executed: {len(set_language_commands)}")
            logger.info(f"[LANGUAGE] Successful commands: {successful_commands}")
            logger.info(f"[LANGUAGE] Failed commands: {failed_commands}")
            logger.info(f"[LANGUAGE] Success rate: {(successful_commands / len(set_language_commands) * 100):.1f}%")
            logger.info(f"[LANGUAGE] Total language setting duration: {language_end - language_start:.3f}s")
            logger.info(
                f"[LANGUAGE] Average time per command: {(language_end - language_start) / len(set_language_commands):.3f}s"
            )

    def _get_current_config(self) -> dict[str, str]:
        """Get current VM configuration values from the emulator."""
        debug_config_read = DEBUG_CONFIGURATION.get("config_read", False)

        if debug_config_read:
            logger.info("[CONFIG] =======================================================")
            logger.info("[CONFIG] RETRIEVING CURRENT VM CONFIGURATION FROM EMULATOR")
            logger.info("[CONFIG] =======================================================")
            logger.info(f"[CONFIG] Target VM index: {self.vm_index}")
            logger.info(f"[CONFIG] Configuration keys to query: {len(self.config)}")
            for key in self.config.keys():
                logger.info(f"[CONFIG]   Will query: {key}")

        current_configuration = {}
        successful_reads = 0
        failed_reads = 0

        for key_index, key in enumerate(self.config.keys(), 1):
            if debug_config_read:
                logger.info("[CONFIG] -------------------------------------------------------")
                logger.info(f"[CONFIG] QUERYING {key_index}/{len(self.config)}: {key}")
                logger.info("[CONFIG] -------------------------------------------------------")
                logger.info(f"[CONFIG] About to call: pmc.get_configuration_vm({key!r}, vm_index={self.vm_index})")

            query_start = time.time()
            try:
                current_value = self.pmc.get_configuration_vm(key, vm_index=self.vm_index)
                query_end = time.time()
                current_configuration[key] = current_value
                successful_reads += 1

                if debug_config_read:
                    logger.info(f"[CONFIG] ✓ SUCCESSFULLY READ {key}")
                    logger.info(f"[CONFIG] Value: {current_value!r} (type: {type(current_value)})")
                    logger.info(f"[CONFIG] Query duration: {query_end - query_start:.3f}s")
                    logger.info(f"[CONFIG] Successful reads so far: {successful_reads}")

            except PyMemucError as e:
                query_end = time.time()
                failed_reads += 1

                if debug_config_read:
                    logger.info(f"[CONFIG] ✗ FAILED TO READ {key}")
                    logger.info(f"[CONFIG] PyMemucError: {e}")
                    logger.info(f"[CONFIG] Query duration: {query_end - query_start:.3f}s")
                    logger.info(f"[CONFIG] Failed reads so far: {failed_reads}")

                logging.exception("Failed to get configuration for key %s: %s", key, e)

        if debug_config_read:
            logger.info("[CONFIG] =======================================================")
            logger.info("[CONFIG] CONFIGURATION QUERY SUMMARY")
            logger.info("[CONFIG] =======================================================")
            logger.info(f"[CONFIG] Total keys queried: {len(self.config)}")
            logger.info(f"[CONFIG] Successful reads: {successful_reads}")
            logger.info(f"[CONFIG] Failed reads: {failed_reads}")
            logger.info(f"[CONFIG] Success rate: {(successful_reads / len(self.config) * 100):.1f}%")
            logger.info("[CONFIG] Final configuration retrieved:")
            for key, value in current_configuration.items():
                logger.info(f"[CONFIG]   {key}: {value}")

        return current_configuration

    def configure(self):
        """Configure the VM with proper settings, just like the working example."""
        debug_configure = DEBUG_CONFIGURATION.get("configure", False)
        debug_vm_ops = DEBUG_CONFIGURATION.get("vm_operations", False)
        debug_language = DEBUG_CONFIGURATION.get("language", False)
        debug_screen = DEBUG_CONFIGURATION.get("screen_size", False)

        if debug_configure:
            logger.info("[CONFIG] =======================================================")
            logger.info("[CONFIG] INITIALIZING CONFIGURE METHOD")
            logger.info("[CONFIG] =======================================================")
            logger.info("[CONFIG] Method called with parameters:")
            logger.info(f"[CONFIG]   self.vm_index: {self.vm_index} (type: {type(self.vm_index)})")
            logger.info(f"[CONFIG]   self.render_mode: {self.render_mode} (type: {type(self.render_mode)})")
            logger.info(f"[CONFIG]   self.config keys: {list(self.config.keys())}")
            logger.info(f"[CONFIG]   self.config length: {len(self.config)}")
            logger.info("[CONFIG] Debug flags active:")
            logger.info(f"[CONFIG]   debug_configure: {debug_configure}")
            logger.info(f"[CONFIG]   debug_vm_ops: {debug_vm_ops}")
            logger.info(f"[CONFIG]   debug_language: {debug_language}")
            logger.info(f"[CONFIG]   debug_screen: {debug_screen}")
            logger.info("[CONFIG] Current configuration data:")
            for key, value in self.config.items():
                logger.info(f"[CONFIG]   {key}: {value} (type: {type(value)})")

        if debug_configure:
            logger.info("[CONFIG] =======================================================")
            logger.info("[CONFIG] VALIDATING RENDER MODE PARAMETER")
            logger.info("[CONFIG] =======================================================")
            logger.info(f"[CONFIG] Raw render_mode input: {self.render_mode!r}")
            logger.info(f"[CONFIG] render_mode type: {type(self.render_mode)}")
            logger.info("[CONFIG] Attempting to convert to lowercase string...")

        # Validate and set render mode with extreme verbosity
        render_mode_start = time.time()
        try:
            if debug_configure:
                logger.info("[CONFIG] Converting render_mode to string...")

            render_mode_str = str(self.render_mode)
            if debug_configure:
                logger.info(f"[CONFIG] str() result: {render_mode_str!r}")
                logger.info("[CONFIG] Applying .lower() method...")

            render_mode = render_mode_str.lower()
            if debug_configure:
                logger.info(f"[CONFIG] .lower() result: {render_mode!r}")
                logger.info("[CONFIG] Checking if render_mode in ['opengl', 'directx']...")
                logger.info(f"[CONFIG]   render_mode == 'opengl': {render_mode == 'opengl'}")
                logger.info(f"[CONFIG]   render_mode == 'directx': {render_mode == 'directx'}")
                logger.info(f"[CONFIG]   render_mode in ['opengl', 'directx']: {render_mode in ['opengl', 'directx']}")

            if render_mode not in ["opengl", "directx"]:
                if debug_configure:
                    logger.info("[CONFIG] ✗ RENDER MODE VALIDATION FAILED")
                    logger.info(f"[CONFIG] Invalid render mode: {render_mode!r}")
                    logger.info('[CONFIG] Valid options are: ["opengl", "directx"]')
                    logger.info('[CONFIG] Applying fallback to "directx"...')
                render_mode = "directx"
            elif debug_configure:
                logger.info("[CONFIG] ✓ RENDER MODE VALIDATION PASSED")
                logger.info(f"[CONFIG] Valid render mode: {render_mode!r}")
        except Exception as e:
            render_mode_end = time.time()
            if debug_configure:
                logger.info("[CONFIG] ✗ EXCEPTION DURING RENDER MODE CONVERSION")
                logger.info(f"[CONFIG] Exception type: {type(e)}")
                logger.info(f"[CONFIG] Exception message: {e}")
                logger.info(f"[CONFIG] Render mode conversion duration: {render_mode_end - render_mode_start:.3f}s")
                logger.info('[CONFIG] Applying fallback to "directx"...')
            render_mode = "directx"

        render_mode_end = time.time()
        if debug_configure:
            logger.info("[CONFIG] ✓ RENDER MODE PROCESSING COMPLETE")
            logger.info(f"[CONFIG] Final render mode: {render_mode!r}")
            logger.info(f"[CONFIG] Render mode processing duration: {render_mode_end - render_mode_start:.3f}s")

        # Create working copy of configuration and set render mode with extreme verbosity
        if debug_configure:
            logger.info("[CONFIG] =======================================================")
            logger.info("[CONFIG] CREATING WORKING CONFIGURATION COPY")
            logger.info("[CONFIG] =======================================================")
            logger.info("[CONFIG] About to create copy of self.config...")
            logger.info(f"[CONFIG] Original config memory address: {id(self.config)}")

        config_copy_start = time.time()
        working_config = self.config.copy()
        config_copy_end = time.time()

        if debug_configure:
            logger.info(f"[CONFIG] Working config memory address: {id(working_config)}")
            logger.info(f"[CONFIG] Config copy duration: {config_copy_end - config_copy_start:.3f}s")
            logger.info(f"[CONFIG] Working config length: {len(working_config)}")
            logger.info("[CONFIG] About to override graphics_render_mode based on render_mode...")
            logger.info(
                f"[CONFIG] Current graphics_render_mode: {working_config.get('graphics_render_mode', 'NOT_FOUND')}"
            )

        if render_mode == "directx":
            old_value = working_config.get("graphics_render_mode")
            working_config["graphics_render_mode"] = 1  # directx
            if debug_configure:
                logger.info("[CONFIG] ✓ RENDER MODE OVERRIDE: DirectX")
                logger.info(f"[CONFIG]   Old graphics_render_mode: {old_value}")
                logger.info("[CONFIG]   New graphics_render_mode: 1 (DirectX)")
        else:
            old_value = working_config.get("graphics_render_mode")
            working_config["graphics_render_mode"] = 0  # opengl
            if debug_configure:
                logger.info("[CONFIG] ✓ RENDER MODE OVERRIDE: OpenGL")
                logger.info(f"[CONFIG]   Old graphics_render_mode: {old_value}")
                logger.info("[CONFIG]   New graphics_render_mode: 0 (OpenGL)")

        # Apply each configuration setting with extreme verbosity
        if debug_configure:
            logger.info("[CONFIG] =======================================================")
            logger.info("[CONFIG] APPLYING CONFIGURATION SETTINGS TO VM")
            logger.info("[CONFIG] =======================================================")
            logger.info(f"[CONFIG] Total settings to apply: {len(working_config)}")
            logger.info(f"[CONFIG] Target VM index: {self.vm_index}")
            logger.info("[CONFIG] About to iterate through working_config items...")

        logging.info("Configuring VM %s...", self.vm_index)

        config_apply_start = time.time()
        successful_configs = 0
        failed_configs = 0

        for config_index, (key, value) in enumerate(working_config.items(), 1):
            if debug_configure:
                logger.info("[CONFIG] -------------------------------------------------------")
                logger.info(f"[CONFIG] SETTING {config_index}/{len(working_config)}: {key}")
                logger.info("[CONFIG] -------------------------------------------------------")
                logger.info(f"[CONFIG] Key: {key!r} (type: {type(key)})")
                logger.info(f"[CONFIG] Value: {value!r} (type: {type(value)})")
                logger.info("[CONFIG] Converting value to string for PyMemuc...")

            try:
                str_value = str(value)
                if debug_configure:
                    logger.info(f"[CONFIG] String value: {str_value!r}")
                    logger.info(
                        f"[CONFIG] About to call: pmc.set_configuration_vm({key!r}, {str_value!r}, vm_index={self.vm_index})"
                    )

                setting_start = time.time()
                self.pmc.set_configuration_vm(key, str_value, vm_index=self.vm_index)
                setting_end = time.time()

                successful_configs += 1
                if debug_configure:
                    logger.info(f"[CONFIG] ✓ SUCCESSFULLY SET {key} = {value}")
                    logger.info(f"[CONFIG] Setting duration: {setting_end - setting_start:.3f}s")
                    logger.info(f"[CONFIG] Successful configs so far: {successful_configs}")

            except Exception as e:
                setting_end = time.time()
                failed_configs += 1
                if debug_configure:
                    logger.info(f"[CONFIG] ✗ FAILED TO SET {key} = {value}")
                    logger.info(f"[CONFIG] Exception type: {type(e)}")
                    logger.info(f"[CONFIG] Exception message: {e}")
                    logger.info(f"[CONFIG] Setting attempt duration: {setting_end - setting_start:.3f}s")
                    logger.info(f"[CONFIG] Failed configs so far: {failed_configs}")
                logging.exception("Failed to set configuration %s = %s: %s", key, value, e)

        config_apply_end = time.time()
        if debug_configure:
            logger.info("[CONFIG] =======================================================")
            logger.info("[CONFIG] CONFIGURATION APPLICATION SUMMARY")
            logger.info("[CONFIG] =======================================================")
            logger.info(f"[CONFIG] Total configurations processed: {len(working_config)}")
            logger.info(f"[CONFIG] Successful configurations: {successful_configs}")
            logger.info(f"[CONFIG] Failed configurations: {failed_configs}")
            logger.info(f"[CONFIG] Success rate: {(successful_configs / len(working_config) * 100):.1f}%")
            logger.info(f"[CONFIG] Total application duration: {config_apply_end - config_apply_start:.3f}s")
            logger.info(
                f"[CONFIG] Average time per setting: {(config_apply_end - config_apply_start) / len(working_config):.3f}s"
            )

        # Set VM language with extreme verbosity
        if debug_configure or debug_language:
            logger.info("[CONFIG] =======================================================")
            logger.info("[CONFIG] SETTING VM LANGUAGE TO ENGLISH")
            logger.info("[CONFIG] =======================================================")
            logger.info("[CONFIG] About to call self._set_vm_language()")

        language_start = time.time()
        try:
            self._set_vm_language()
            language_end = time.time()

            if debug_configure or debug_language:
                logger.info("[CONFIG] ✓ SUCCESSFULLY SET VM LANGUAGE TO ENGLISH")
                logger.info(f"[CONFIG] Language setting duration: {language_end - language_start:.3f}s")
        except Exception as e:
            language_end = time.time()
            if debug_configure or debug_language:
                logger.info("[CONFIG] ✗ FAILED TO SET VM LANGUAGE")
                logger.info(f"[CONFIG] Exception type: {type(e)}")
                logger.info(f"[CONFIG] Exception message: {e}")
                logger.info(f"[CONFIG] Language setting attempt duration: {language_end - language_start:.3f}s")

        logging.info("Configured VM %s", self.vm_index)

        # Set screen size with retry mechanism and extreme verbosity
        expected_width, expected_height = 419, 633
        if debug_configure or debug_screen:
            logger.info("[CONFIG] =======================================================")
            logger.info("[CONFIG] SETTING VM SCREEN SIZE WITH RETRY MECHANISM")
            logger.info("[CONFIG] =======================================================")
            logger.info(f"[CONFIG] Target screen size: {expected_width}x{expected_height}")
            logger.info("[CONFIG] Retry attempts: 3")

        screen_size_start = time.time()
        successful_attempts = 0
        failed_attempts = 0

        for attempt in range(1, 4):  # 3 attempts
            if debug_configure or debug_screen:
                logger.info("[CONFIG] -------------------------------------------------------")
                logger.info(f"[CONFIG] SCREEN SIZE ATTEMPT {attempt}/3")
                logger.info("[CONFIG] -------------------------------------------------------")
                logger.info(f"[CONFIG] About to call: self._set_screen_size({expected_width}, {expected_height})")

            attempt_start = time.time()
            try:
                self._set_screen_size(expected_width, expected_height)
                attempt_end = time.time()
                successful_attempts += 1

                if debug_configure or debug_screen:
                    logger.info(f"[CONFIG] ✓ SCREEN SIZE ATTEMPT {attempt} SUCCESSFUL")
                    logger.info(f"[CONFIG] Attempt duration: {attempt_end - attempt_start:.3f}s")
                    logger.info(f"[CONFIG] Successful attempts so far: {successful_attempts}")

            except Exception as e:
                attempt_end = time.time()
                failed_attempts += 1

                if debug_configure or debug_screen:
                    logger.info(f"[CONFIG] ✗ SCREEN SIZE ATTEMPT {attempt} FAILED")
                    logger.info(f"[CONFIG] Exception type: {type(e)}")
                    logger.info(f"[CONFIG] Exception message: {e}")
                    logger.info(f"[CONFIG] Attempt duration: {attempt_end - attempt_start:.3f}s")
                    logger.info(f"[CONFIG] Failed attempts so far: {failed_attempts}")

        screen_size_end = time.time()
        if debug_configure or debug_screen:
            logger.info("[CONFIG] =======================================================")
            logger.info("[CONFIG] SCREEN SIZE SETTING SUMMARY")
            logger.info("[CONFIG] =======================================================")
            logger.info("[CONFIG] Total attempts: 3")
            logger.info(f"[CONFIG] Successful attempts: {successful_attempts}")
            logger.info(f"[CONFIG] Failed attempts: {failed_attempts}")
            logger.info(f"[CONFIG] Success rate: {(successful_attempts / 3 * 100):.1f}%")
            logger.info(f"[CONFIG] Total screen size duration: {screen_size_end - screen_size_start:.3f}s")

        if debug_configure:
            total_config_time = time.time() - render_mode_start
            logger.info("[CONFIG] =======================================================")
            logger.info("[CONFIG] COMPLETE CONFIGURATION METHOD SUMMARY")
            logger.info("[CONFIG] =======================================================")
            logger.info(f"[CONFIG] VM Index: {self.vm_index}")
            logger.info(f"[CONFIG] Final render mode: {render_mode}")
            logger.info(f"[CONFIG] Configuration settings applied: {successful_configs}/{len(working_config)}")
            logger.info(f"[CONFIG] Language setting: {'SUCCESS' if language_end - language_start < 30 else 'UNKNOWN'}")
            logger.info(f"[CONFIG] Screen size attempts: {successful_attempts}/3")
            logger.info(f"[CONFIG] Total configuration time: {total_config_time:.3f}s")
            logger.info("[CONFIG] =======================================================")
            logger.info("[CONFIG] VM CONFIGURATION COMPLETE")
            logger.info("[CONFIG] =======================================================")

    def _start_memuc_console(self):
        """Start the memuc console and return the process ID"""
        logger.info("Starting memuc console...")

        # check if memu console is already running
        for process in psutil.process_iter():
            with contextlib.suppress(psutil.NoSuchProcess, psutil.AccessDenied):
                if process.name() == "MEMuConsole.exe":
                    logger.info("[+] Memu console is already running.")
                    return process.pid

        console_path = join(self.pmc._get_memu_top_level(), "MEMuConsole.exe")
        logger.info("[+] Starting memu console at:" + str(console_path))
        process = subprocess.Popen(console_path, creationflags=subprocess.DETACHED_PROCESS)

        interruptible_sleep(2)

        if process.pid is not None:
            logger.info("[+] Memu console started successfully.")
        else:
            logger.info("[!] Failed to start memu console.")

    def create(self):
        self._start_memuc_console()
        vm_index = self.pmc.create_vm(vm_version=ANDROID_VERSION)
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
                    logger.info("[!] Non-fatal error: Failed to kill process: %s", proc.name())

    def _skip_ads(self):
        """Skip ads in the emulator.

        Returns:
            bool: True if ads skipped successfully, False otherwise
        """
        debug_ads = DEBUG_CONFIGURATION.get("ads", False)

        if debug_ads:
            logger.info("[ADS] =======================================================")
            logger.info("[ADS] SKIPPING MEMU ADS")
            logger.info("[ADS] =======================================================")
            logger.info(f"[ADS] Target VM index: {self.vm_index}")
            logger.info("[ADS] Method: Send 'home' keystrokes to dismiss ads")
            logger.info("[ADS] Total attempts: 4")
            logger.info("[ADS] Sleep between attempts: 1 second")

        ads_start = time.time()
        successful_keypresses = 0
        failed_keypresses = 0

        try:
            if debug_ads:
                logger.info("[ADS] About to start home button press sequence...")

            for i in range(4):
                attempt_num = i + 1
                if debug_ads:
                    logger.info("[ADS] -------------------------------------------------------")
                    logger.info(f"[ADS] AD SKIP ATTEMPT {attempt_num}/4")
                    logger.info("[ADS] -------------------------------------------------------")
                    logger.info(f"[ADS] About to call: pmc.trigger_keystroke_vm('home', vm_index={self.vm_index})")

                keypress_start = time.time()
                try:
                    result = self.pmc.trigger_keystroke_vm("home", vm_index=self.vm_index)
                    keypress_end = time.time()
                    successful_keypresses += 1

                    if debug_ads:
                        logger.info(f"[ADS] ✓ KEYPRESS {attempt_num} SUCCESSFUL")
                        logger.info(f"[ADS] Keypress duration: {keypress_end - keypress_start:.3f}s")
                        logger.info(f"[ADS] Keypress result: {result!r}")
                        logger.info(f"[ADS] Successful keypresses so far: {successful_keypresses}")
                        logger.info("[ADS] Sleeping for 1 second...")

                except Exception as keypress_err:
                    keypress_end = time.time()
                    failed_keypresses += 1

                    if debug_ads:
                        logger.info(f"[ADS] ✗ KEYPRESS {attempt_num} FAILED")
                        logger.info(f"[ADS] Exception type: {type(keypress_err)}")
                        logger.info(f"[ADS] Exception message: {keypress_err}")
                        logger.info(f"[ADS] Keypress duration: {keypress_end - keypress_start:.3f}s")
                        logger.info(f"[ADS] Failed keypresses so far: {failed_keypresses}")
                        logger.info("[ADS] Sleeping for 1 second...")

                interruptible_sleep(1)

            ads_end = time.time()
            if debug_ads:
                logger.info("[ADS] =======================================================")
                logger.info("[ADS] AD SKIP SUMMARY")
                logger.info("[ADS] =======================================================")
                logger.info("[ADS] Total attempts: 4")
                logger.info(f"[ADS] Successful keypresses: {successful_keypresses}")
                logger.info(f"[ADS] Failed keypresses: {failed_keypresses}")
                logger.info(f"[ADS] Success rate: {(successful_keypresses / 4 * 100):.1f}%")
                logger.info(f"[ADS] Total ad skip duration: {ads_end - ads_start:.3f}s")
                logger.info("[ADS] ✓ ALL AD SKIP ATTEMPTS COMPLETED SUCCESSFULLY")

        except Exception as err:
            ads_end = time.time()
            if debug_ads:
                logger.info("[ADS] =======================================================")
                logger.info("[ADS] AD SKIP FAILED - OUTER EXCEPTION")
                logger.info("[ADS] =======================================================")
                logger.info(f"[ADS] Exception type: {type(err)}")
                logger.info(f"[ADS] Exception message: {err}")
                logger.info(f"[ADS] Total attempts made: {successful_keypresses + failed_keypresses}")
                logger.info(f"[ADS] Successful keypresses: {successful_keypresses}")
                logger.info(f"[ADS] Failed keypresses: {failed_keypresses}")
                logger.info(f"[ADS] Duration until failure: {ads_end - ads_start:.3f}s")
                logger.info("[ADS] RETURNING FALSE DUE TO EXCEPTION")
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
            logger.info("[SCREEN] =======================================================")
            logger.info("[SCREEN] CHECKING VM SCREEN SIZE")
            logger.info("[SCREEN] =======================================================")
            logger.info(f"[SCREEN] Target VM index: {self.vm_index}")
            logger.info(f"[SCREEN] Expected dimensions: {expected_width}x{expected_height}")
            logger.info("[SCREEN] Method: Take screenshot and validate dimensions")

        size_check_start = time.time()

        try:
            # Step 1: Press home key to prepare
            if debug_screen:
                logger.info("[SCREEN] Step 1: Pressing home key to prepare for screen size check...")
                logger.info(f"[SCREEN] About to call: pmc.trigger_keystroke_vm('home', vm_index={self.vm_index})")

            logger.info("Pressing home key to prepare for screen size check...")

            keypress_start = time.time()
            self.pmc.trigger_keystroke_vm("home", vm_index=self.vm_index)
            keypress_end = time.time()

            if debug_screen:
                logger.info("[SCREEN] ✓ Home key pressed successfully")
                logger.info(f"[SCREEN] Keypress duration: {keypress_end - keypress_start:.3f}s")
                logger.info("[SCREEN] Waiting 2 seconds for screen to stabilize...")

            interruptible_sleep(2)  # Wait for screen to stabilize

            # Step 2: Take screenshot
            if debug_screen:
                logger.info("[SCREEN] Step 2: Taking screenshot to verify screen dimensions...")
                logger.info("[SCREEN] About to call: self.screenshot()")

            logger.info("Taking screenshot to verify screen dimensions...")

            screenshot_start = time.time()
            image = self.screenshot()
            screenshot_end = time.time()

            if debug_screen:
                logger.info("[SCREEN] ✓ Screenshot captured successfully")
                logger.info(f"[SCREEN] Screenshot duration: {screenshot_end - screenshot_start:.3f}s")
                logger.info(f"[SCREEN] Image type: {type(image)}")
                logger.info(f"[SCREEN] Image shape: {image.shape}")

            # Step 3: Extract dimensions
            height, width, channels = image.shape

            if debug_screen:
                logger.info("[SCREEN] Step 3: Analyzing screenshot dimensions...")
                logger.info("[SCREEN] Extracted dimensions:")
                logger.info(f"[SCREEN]   Width: {width}px")
                logger.info(f"[SCREEN]   Height: {height}px")
                logger.info(f"[SCREEN]   Channels: {channels}")
                logger.info("[SCREEN] Expected dimensions:")
                logger.info(f"[SCREEN]   Expected width: {expected_width}px")
                logger.info(f"[SCREEN]   Expected height: {expected_height}px")

            logger.info(f"Screen dimensions: {width}x{height} (expected: {expected_width}x{expected_height})")

            # Step 4: Validate dimensions
            width_correct = width == expected_width
            height_correct = height == expected_height
            dimensions_correct = width_correct and height_correct

            if debug_screen:
                logger.info("[SCREEN] Step 4: Validating dimensions...")
                logger.info(f"[SCREEN] Width validation: {width} == {expected_width} → {width_correct}")
                logger.info(f"[SCREEN] Height validation: {height} == {expected_height} → {height_correct}")
                logger.info(f"[SCREEN] Overall validation: {dimensions_correct}")

            if not dimensions_correct:
                size_check_end = time.time()
                validation_msg = (
                    f"Screen size validation FAILED: got {width}x{height}, expected {expected_width}x{expected_height}"
                )
                logger.info(validation_msg)

                if debug_screen:
                    logger.info("[SCREEN] ✗ SCREEN SIZE VALIDATION FAILED")
                    logger.info(f"[SCREEN] Actual: {width}x{height}")
                    logger.info(f"[SCREEN] Expected: {expected_width}x{expected_height}")
                    logger.info(f"[SCREEN] Width difference: {width - expected_width}")
                    logger.info(f"[SCREEN] Height difference: {height - expected_height}")
                    logger.info(f"[SCREEN] Total validation time: {size_check_end - size_check_start:.3f}s")
                    logger.info("[SCREEN] RETURNING FALSE")

                return False

            size_check_end = time.time()
            logger.info("Screen size validation PASSED")

            if debug_screen:
                logger.info("[SCREEN] ✓ SCREEN SIZE VALIDATION PASSED")
                logger.info(f"[SCREEN] Dimensions match perfectly: {width}x{height}")
                logger.info(f"[SCREEN] Total validation time: {size_check_end - size_check_start:.3f}s")
                logger.info("[SCREEN] RETURNING TRUE")

            return True

        except Exception as e:
            size_check_end = time.time()
            error_msg = f"Error during screen size check: {e}"
            logger.info(error_msg)

            if debug_screen:
                logger.info("[SCREEN] ✗ EXCEPTION DURING SCREEN SIZE CHECK")
                logger.info(f"[SCREEN] Exception type: {type(e)}")
                logger.info(f"[SCREEN] Exception message: {e}")
                logger.info(f"[SCREEN] Time until exception: {size_check_end - size_check_start:.3f}s")
                logger.info("[SCREEN] Assuming valid size to avoid infinite loops")

        # in the case of errors, assume size is correct to avoid infinite loops
        logger.info("Screen size check error - assuming valid size")

        if debug_screen:
            logger.info("[SCREEN] =======================================================")
            logger.info("[SCREEN] SCREEN SIZE CHECK ERROR RECOVERY")
            logger.info("[SCREEN] =======================================================")
            logger.info("[SCREEN] Assuming screen size is valid to prevent infinite restart loops")
            logger.info("[SCREEN] RETURNING TRUE (ERROR RECOVERY)")

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
            logger.info("[RESTART] =====================================================")
            logger.info("[RESTART] INITIALIZING RESTART METHOD")
            logger.info("[RESTART] =====================================================")
            logger.info("[RESTART] Method parameters:")
            logger.info(f"[RESTART]   open_clash: {open_clash} (type: {type(open_clash)})")
            logger.info(f"[RESTART]   start_time: {start_time} (type: {type(start_time)})")
            logger.info("[RESTART] Debug flags active:")
            logger.info(f"[RESTART]   debug_restart: {debug_restart}")
            logger.info(f"[RESTART]   debug_vm_ops: {debug_vm_ops}")
            logger.info(f"[RESTART]   debug_clash: {debug_clash}")

        if start_time is None:
            start_time = time.time()
            if debug_restart:
                logger.info(f"[RESTART] start_time was None, set to current time: {start_time}")
        elif debug_restart:
            logger.info(f"[RESTART] Using provided start_time: {start_time}")

        # Validate vm_index with extreme verbosity
        if debug_restart:
            logger.info("[RESTART] =====================================================")
            logger.info("[RESTART] VALIDATING VM INDEX")
            logger.info("[RESTART] =====================================================")
            logger.info(f"[RESTART] Current self.vm_index: {self.vm_index} (type: {type(self.vm_index)})")
            logger.info("[RESTART] Checking if vm_index is in [None, -1, '']...")
            logger.info(f"[RESTART]   vm_index == None: {self.vm_index is None}")
            logger.info(f"[RESTART]   vm_index == -1: {self.vm_index == -1}")
            logger.info(f"[RESTART]   vm_index == '': {self.vm_index == ''}")
            logger.info(f"[RESTART]   vm_index in [None, -1, '']: {self.vm_index in [None, -1, '']}")

        if self.vm_index in [None, -1, ""]:
            error_msg = "[!] Fatal error: No valid vm_index in MemuEmulatorController.restart()"
            logger.info(error_msg)
            logger.info(error_msg)
            if debug_restart:
                logger.info("[RESTART] VM INDEX VALIDATION FAILED - RETURNING FALSE")
            return False

        if debug_restart:
            logger.info("[RESTART] ✓ VM INDEX VALIDATION PASSED")
            logger.info(f"[RESTART] Valid vm_index: {self.vm_index}")

        if debug_restart:
            logger.info("[RESTART] =====================================================")
            logger.info("[RESTART] STARTING EMULATOR RESTART SEQUENCE")
            logger.info("[RESTART] =====================================================")
            logger.info("[RESTART] Restart sequence parameters:")
            logger.info(f"[RESTART]   VM Index: {self.vm_index}")
            logger.info(f"[RESTART]   Render Mode: {self.render_mode}")
            logger.info(f"[RESTART]   Open Clash: {open_clash}")
            logger.info(f"[RESTART]   Start Time: {start_time}")
            logger.info(f"[RESTART]   Current Time: {time.time()}")

        # Step 1: Stop all MEmu processes with extreme verbosity
        if debug_restart:
            logger.info("[RESTART] =====================================================")
            logger.info("[RESTART] STEP 1: STOPPING ALL MEMU PROCESSES")
            logger.info("[RESTART] =====================================================")

        logger.info("Stopping all MEmu processes...")
        if debug_restart:
            logger.info("[RESTART] Logger status updated to: 'Stopping all MEmu processes...'")
            logger.info("[RESTART] About to call self._close_everything_memu()")

        process_close_start = time.time()
        self._close_everything_memu()
        process_close_end = time.time()

        if debug_restart:
            logger.info("[RESTART] self._close_everything_memu() completed")
            logger.info(f"[RESTART] Process close duration: {process_close_end - process_close_start:.3f}s")

        logger.info("All MEmu processes stopped")
        if debug_restart:
            logger.info("[RESTART] ✓ ALL MEMU PROCESSES STOPPED")
            logger.info("[RESTART] Logger status updated to: 'All MEmu processes stopped'")

        # Step 2: Configure the VM (while stopped) with extreme verbosity
        if debug_restart:
            logger.info("[RESTART] =====================================================")
            logger.info("[RESTART] STEP 2: CONFIGURING VM SETTINGS (WHILE STOPPED)")
            logger.info("[RESTART] =====================================================")
            logger.info("[RESTART] About to call self.configure() - this will apply all VM settings")
            logger.info(f"[RESTART] Configuration will be applied to VM {self.vm_index}")

        logger.info("Configuring VM settings...")
        if debug_restart:
            logger.info("[RESTART] Logger status updated to: 'Configuring VM settings...'")

        config_start = time.time()
        if not self.debug_mode:
            self.configure()  # This will do its own verbose configuration
        config_end = time.time()

        if debug_restart:
            logger.info("[RESTART] self.configure() completed")
            logger.info(f"[RESTART] Configuration duration: {config_end - config_start:.3f}s")

        logger.info("VM configuration complete")
        if debug_restart:
            logger.info("[RESTART] ✓ VM CONFIGURATION COMPLETE")
            logger.info("[RESTART] Logger status updated to: 'VM configuration complete'")

        # Step 3: Start the VM with extreme verbosity
        if debug_restart or debug_vm_ops:
            logger.info("[RESTART] =====================================================")
            logger.info("[RESTART] STEP 3: STARTING THE VIRTUAL MACHINE")
            logger.info("[RESTART] =====================================================")
            logger.info(f"[RESTART] About to start VM with index: {self.vm_index}")
            logger.info(f"[RESTART] Using PyMemuc command: self.pmc.start_vm(vm_index={self.vm_index})")

        logger.info("Starting emulator...")
        if debug_restart:
            logger.info("[RESTART] Logger status updated to: 'Starting emulator...'")

        vm_start_time = time.time()
        try:
            if debug_vm_ops:
                logger.info(f"[RESTART] Executing: self.pmc.start_vm(vm_index={self.vm_index})")

            result = self.pmc.start_vm(vm_index=self.vm_index)
            vm_start_end = time.time()

            if debug_vm_ops:
                logger.info(f"[RESTART] VM start command result: {result}")
                logger.info(f"[RESTART] VM start command duration: {vm_start_end - vm_start_time:.3f}s")
                logger.info("[RESTART] ✓ EMULATOR START COMMAND SENT SUCCESSFULLY")

        except Exception as e:
            vm_start_end = time.time()
            error_msg = f"Failed to start emulator: {e}"

            if debug_restart:
                logger.info("[RESTART] ✗ EXCEPTION DURING VM START")
                logger.info(f"[RESTART] Exception type: {type(e)}")
                logger.info(f"[RESTART] Exception message: {e}")
                logger.info(f"[RESTART] VM start attempt duration: {vm_start_end - vm_start_time:.3f}s")
                logger.info("[RESTART] RETURNING FALSE DUE TO VM START FAILURE")

            logger.info(error_msg)
            return False

        # Step 4: Skip ads with extreme verbosity
        if debug_restart or DEBUG_CONFIGURATION.get("ads", False):
            logger.info("[RESTART] =====================================================")
            logger.info("[RESTART] STEP 4: SKIPPING MEMU ADS")
            logger.info("[RESTART] =====================================================")

        logger.info("Skipping MEmu ads...")
        if debug_restart:
            logger.info("[RESTART] Logger status updated to: 'Skipping MEmu ads...'")
            logger.info("[RESTART] About to call self._skip_ads()")

        ads_start = time.time()
        ads_result = self._skip_ads()
        ads_end = time.time()

        if debug_restart:
            logger.info(f"[RESTART] self._skip_ads() returned: {ads_result}")
            logger.info(f"[RESTART] Ad skip duration: {ads_end - ads_start:.3f}s")

        if not ads_result:
            if debug_restart:
                logger.info("[RESTART] ✗ AD SKIP FAILED - INITIATING RECURSIVE RESTART")
                logger.info(f"[RESTART] Calling self.restart(open_clash={open_clash}, start_time={start_time})")

            logger.info("Failed to skip ads, restarting...")
            return self.restart(open_clash=open_clash, start_time=start_time)

        if debug_restart:
            logger.info("[RESTART] ✓ SUCCESSFULLY SKIPPED ADS")

        # Step 5: Validate screen size with extreme verbosity
        if debug_restart or DEBUG_CONFIGURATION.get("screen_size", False):
            logger.info("[RESTART] =====================================================")
            logger.info("[RESTART] STEP 5: VALIDATING SCREEN SIZE")
            logger.info("[RESTART] =====================================================")

        logger.info("Validating screen size...")
        if debug_restart:
            logger.info("[RESTART] Logger status updated to: 'Validating screen size...'")
            logger.info("[RESTART] About to call self._check_vm_size()")

        size_check_start = time.time()
        size_valid = self._check_vm_size()
        size_check_end = time.time()

        if debug_restart:
            logger.info(f"[RESTART] self._check_vm_size() returned: {size_valid}")
            logger.info(f"[RESTART] Size check duration: {size_check_end - size_check_start:.3f}s")

        if not size_valid:
            if debug_restart:
                logger.info("[RESTART] ✗ SCREEN SIZE VALIDATION FAILED - INITIATING RECURSIVE RESTART")
                logger.info(f"[RESTART] Calling self.restart(open_clash={open_clash}, start_time={start_time})")

            logger.info("VM size validation failed, restarting...")
            return self.restart(open_clash=open_clash, start_time=start_time)

        if debug_restart:
            logger.info("[RESTART] ✓ SCREEN SIZE VALIDATION PASSED")

        # Step 6: Start Clash Royale if requested with extreme verbosity
        if open_clash:
            if debug_restart or debug_clash:
                logger.info("[RESTART] =====================================================")
                logger.info("[RESTART] STEP 6: STARTING CLASH ROYALE")
                logger.info("[RESTART] =====================================================")
                logger.info("[RESTART] open_clash is True, proceeding with Clash Royale startup")

            logger.info("Starting Clash Royale...")
            if debug_restart:
                logger.info("[RESTART] Logger status updated to: 'Starting Clash Royale...'")
                logger.info("[RESTART] About to call self.start_app('com.supercell.clashroyale')")

            clash_start_time = time.time()
            try:
                app_start_result = self.start_app("com.supercell.clashroyale")
                clash_start_end = time.time()

                if debug_clash:
                    logger.info(f"[RESTART] self.start_app() returned: {app_start_result}")
                    logger.info(f"[RESTART] Clash start duration: {clash_start_end - clash_start_time:.3f}s")

                if not app_start_result:
                    if debug_restart:
                        logger.info("[RESTART] ✗ CLASH ROYALE START FAILED")
                        logger.info("[RESTART] RETURNING FALSE DUE TO CLASH START FAILURE")
                    return False

                if debug_restart:
                    logger.info("[RESTART] ✓ CLASH ROYALE STARTED SUCCESSFULLY")

            except Exception as e:
                clash_start_end = time.time()
                if debug_restart:
                    logger.info("[RESTART] ✗ EXCEPTION DURING CLASH ROYALE START")
                    logger.info(f"[RESTART] Exception type: {type(e)}")
                    logger.info(f"[RESTART] Exception message: {e}")
                    logger.info(f"[RESTART] Clash start attempt duration: {clash_start_end - clash_start_time:.3f}s")
                return False

            # Step 7: Wait for Clash main menu with extreme verbosity
            if debug_restart or debug_clash:
                logger.info("[RESTART] =====================================================")
                logger.info("[RESTART] STEP 7: WAITING FOR CLASH ROYALE MAIN MENU")
                logger.info("[RESTART] =====================================================")

            logger.info("Waiting for Clash Royale main menu...")
            if debug_restart:
                logger.info("[RESTART] Logger status updated to: 'Waiting for Clash Royale main menu...'")

            clash_main_wait_start_time = time.time()
            clash_main_wait_timeout = 240  # seconds

            if debug_clash:
                logger.info("[RESTART] Wait parameters:")
                logger.info(f"[RESTART]   wait_start_time: {clash_main_wait_start_time}")
                logger.info(f"[RESTART]   wait_timeout: {clash_main_wait_timeout}s")
                logger.info(f"[RESTART]   wait_end_time: {clash_main_wait_start_time + clash_main_wait_timeout}")
                logger.info("[RESTART] Initial 12-second wait before checking main menu...")

            interruptible_sleep(12)  # Initial wait

            if debug_clash:
                logger.info("[RESTART] Initial wait complete, starting main menu detection loop...")

            loop_iteration = 0
            while time.time() - clash_main_wait_start_time < clash_main_wait_timeout:
                loop_iteration += 1
                current_time = time.time()
                elapsed_wait = current_time - clash_main_wait_start_time
                remaining_time = clash_main_wait_timeout - elapsed_wait

                if debug_clash:
                    logger.info(f"[RESTART] Main menu wait loop iteration {loop_iteration}")
                    logger.info(f"[RESTART]   Current time: {current_time}")
                    logger.info(f"[RESTART]   Elapsed wait: {elapsed_wait:.1f}s")
                    logger.info(f"[RESTART]   Remaining time: {remaining_time:.1f}s")
                    logger.info("[RESTART] Checking if on Clash main menu...")

                menu_check_start = time.time()
                if check_if_on_clash_main_menu(self):
                    menu_check_end = time.time()
                    total_elapsed = str(time.time() - start_time)[:5]

                    if debug_clash:
                        logger.info("[RESTART] ✓ CLASH MAIN MENU DETECTED!")
                        logger.info(f"[RESTART] Menu check duration: {menu_check_end - menu_check_start:.3f}s")
                        logger.info(f"[RESTART] Total wait time: {elapsed_wait:.1f}s")
                        logger.info(f"[RESTART] Total restart time: {total_elapsed}s")

                    logger.info("Clash main menu detected!")
                    logger.info(f"Emulator restart completed in {total_elapsed}s")

                    if debug_restart:
                        logger.info("[RESTART] =====================================================")
                        logger.info("[RESTART] RESTART SEQUENCE COMPLETED SUCCESSFULLY")
                        logger.info("[RESTART] =====================================================")

                    return True

                menu_check_end = time.time()
                if debug_clash:
                    logger.info(
                        f"[RESTART] Main menu not detected (check took {menu_check_end - menu_check_start:.3f}s)"
                    )
                    logger.info("[RESTART] Clicking deadspace at (5, 350) to handle popups...")

                # Click deadspace to handle any popups
                click_start = time.time()
                self.click(35, 405)
                click_end = time.time()

                if debug_clash:
                    logger.info(f"[RESTART] Deadspace click completed ({click_end - click_start:.3f}s)")
                    logger.info("[RESTART] Sleeping for 1 second before next iteration...")

                interruptible_sleep(1)

            # Timeout waiting for main menu
            final_elapsed_wait = time.time() - clash_main_wait_start_time
            if debug_restart or debug_clash:
                logger.info("[RESTART] ✗ TIMEOUT WAITING FOR CLASH MAIN MENU")
                logger.info(f"[RESTART] Total wait time: {final_elapsed_wait:.1f}s")
                logger.info(f"[RESTART] Timeout threshold: {clash_main_wait_timeout}s")
                logger.info(f"[RESTART] Loop iterations: {loop_iteration}")
                logger.info("[RESTART] INITIATING RECURSIVE RESTART DUE TO TIMEOUT")

            logger.info("Timeout waiting for Clash main menu, restarting...")
            return self.restart(open_clash=open_clash, start_time=start_time)

        # If not opening Clash, we're done
        else:
            total_elapsed = str(time.time() - start_time)[:5]

            if debug_restart:
                logger.info("[RESTART] =====================================================")
                logger.info("[RESTART] RESTART SEQUENCE COMPLETED (NO CLASH)")
                logger.info("[RESTART] =====================================================")
                logger.info("[RESTART] open_clash was False, skipping Clash Royale startup")
                logger.info(f"[RESTART] Total restart time: {total_elapsed}s")

            logger.info(f"Emulator restart completed in {total_elapsed}s")
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
                logger.info(f"[!] Non fatal error: Timeout of {timeout} seconds reached while stopping the emulator.\n")
                return False

            self.pmc.stop_vm(vm_index=self.vm_index)
            interruptible_sleep(3)

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
                interruptible_sleep(interval)

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
        logger.info("Successfully initialized Clash app")
        return True

    def _wait_for_clash_installation(self, package_name: str):
        """Wait for user to install Clash Royale using the action callback system"""
        self.current_package_name = package_name  # Store for retry logic
        if self._action_callback:
            self._action_callback(
                message=f"{package_name} not installed - please install it and complete tutorial",
                action_text="Retry",
                callback=self._retry_installation_check,
            )

        logger.info(f"[!] {package_name} not installed.")
        logger.info("Please install it in the emulator, complete tutorial, then click Retry in the GUI")

        # Wait for the callback to be triggered
        self.installation_waiting = True
        while self.installation_waiting:
            interruptible_sleep(0.5)

        logger.info("[+] Installation confirmed, continuing...")
        return True

    def _retry_installation_check(self):
        """Callback method triggered when user clicks Retry button"""
        logger.info("Checking for Clash Royale installation...")

        # Check if app is now installed
        package_name = getattr(self, "current_package_name", "com.supercell.clashroyale")
        installed_apps = self.pmc.get_app_info_list_vm(vm_index=self.vm_index)
        found = [app for app in installed_apps if package_name in app]

        if found:
            # Installation successful!
            self.installation_waiting = False
            logger.info("Installation complete - continuing...")
        else:
            # Still not installed, show the retry button again
            if self._action_callback:
                self._action_callback(
                    message=f"{package_name} still not found - please install it and complete tutorial",
                    action_text="Retry",
                    callback=self._retry_installation_check,
                )
            logger.info(f"[!] {package_name} still not installed. Please try again.")


if __name__ == "__main__":
    memu = MemuEmulatorController(render_mode="directx")
    while 1:
        logger.info("Running")
        interruptible_sleep(10)
