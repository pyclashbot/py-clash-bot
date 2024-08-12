"""
A module for configuring Memu VMs.
"""

import time
import logging
from pymemuc import ConfigKeys

from pyclashbot.memu.pmc import pmc

# see https://pymemuc.readthedocs.io/pymemuc.html#the-vm-configuration-keys-table
MEMU_CONFIGURATION: dict[ConfigKeys, str | int | float] = {
    "start_window_mode": 1,  # remember window position
    "win_scaling_percent2": 100,  # 100% scaling
    "is_customed_resolution": 1,
    "resolution_width": 419,
    "graphics_render_mode": "1",  # use DirectX to avoid black screenshot issue
    "resolution_height": 633,
    "vbox_dpi": 160,
    "cpucap": 50,
    "fps": 40,
    "turbo_mode": 0,
    "enable_audio": 0,
    "is_hide_toolbar": 1,
}


def set_vm_language(vm_index: int):
    """Set the language of the vm to english"""
    settings_uri = "--uri content://settings/system"
    set_language_commands = [
        f"shell content query {settings_uri} --where \"name='system_locales'\"",
        f"shell content delete {settings_uri} --where \"name='system_locales'\"",
        f"shell content insert {settings_uri} --bind name:s:system_locales --bind value:s:en-US",
        "shell setprop ctl.restart zygote",
    ]

    for command in set_language_commands:
        pmc.send_adb_command_vm(vm_index=vm_index, command=command)
        time.sleep(0.33)


def configure_vm(vm_index):
    """Configure the virtual machine with the given index."""
    logging.info("Configuring VM %s...", vm_index)

    for key, value in MEMU_CONFIGURATION.items():
        pmc.set_configuration_vm(key, str(value), vm_index=vm_index)

    set_vm_language(vm_index=vm_index)
    set_vm_language(vm_index=vm_index)
    set_vm_language(vm_index=vm_index)
    logging.info("Configured VM %s", vm_index)


if __name__ == "__main__":
    pass
