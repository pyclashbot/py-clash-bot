"""This module contains functions for managing the Memu emulator."""

import subprocess
import time
from os import environ, makedirs
from os.path import exists, join

import psutil
from pymemuc import PyMemuc, PyMemucError, VMInfo

from pyclashbot.utils.logger import Logger

pmc = PyMemuc(debug=False)


def start_memuc_console() -> int:
    """Start the memuc console and return the process ID"""
    # pylint: disable=protected-access
    console_path = join(pmc._get_memu_top_level(), "MEMuConsole.exe")
    # pylint: disable=consider-using-with
    process = subprocess.Popen(console_path, creationflags=subprocess.DETACHED_PROCESS)

    print(f"Started memu console with PID {process.pid}")

    return process.pid


def stop_memuc_console(process_id: int) -> None:
    """Stop the memuc console with the given process ID"""
    try:
        process = psutil.Process(process_id)
        process.terminate()
    except psutil.NoSuchProcess:
        print("#975627345 Failure to stop memuc console")


def get_screenshot_folder() -> str:
    """Get the path to the screenshot folder"""
    screenshot_path = join(environ["APPDATA"], "pyclashbot", "screenshots")
    # make sure this folder exists
    if not exists(screenshot_path):
        makedirs(screenshot_path)
    return screenshot_path


def configure_vm(logger: Logger, vm_index):
    """Configure the vm"""
    logger.change_status("Configuring VM")

    # see https://pymemuc.martinmiglio.dev/en/latest/pymemuc.html#the-vm-configuration-keys-table

    configuration: dict[str, str] = {
        "start_window_mode": "1",  # remember window position
        "win_scaling_percent2": "100",  # 100% scaling
        "is_customed_resolution": "1",
        "resolution_width": "419",
        "resolution_height": "633",
        "vbox_dpi": "160",
        "fps": "15",
        "cpus": "4",
        "cpucap": "25",
        "turbo_mode": "0",
        "enable_audio": "0",
        "is_hide_toolbar": "1",
        "picturepath": get_screenshot_folder(),
    }

    for key, value in configuration.items():
        pmc.set_configuration_vm(key, value, vm_index=vm_index)
        # validate that the configuration was set correctly
        time.sleep(0.3)
        assert (
            pmc.get_configuration_vm(key, vm_index=vm_index).replace('"', "") == value
        ), f"Failed to set {key} to {value}"

    logger.change_status("Configured VM")


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
        time.sleep(0.1)


def create_vm(
    logger: Logger,
    name: str,
) -> int:
    """Create a vm with the given name and version"""
    logger.change_status("VM not found, creating VM...")
    vm_index = -1
    while vm_index == -1:
        vm_index = pmc.create_vm(vm_version="96")
        time.sleep(1)
    time.sleep(5)
    rename_vm(logger, vm_index, name)
    logger.change_status(f"Created and renamed VM: {vm_index} - {name}")
    return vm_index


def rename_vm(
    logger: Logger,
    vm_index: int,
    name: str,
):
    """rename the vm to name"""
    count = 0
    while get_vm_index(logger, name) != vm_index:
        logger.change_status(
            f"Renaming VM {vm_index} to {name} {f'(attempt {count})' if count > 0 else ''}"
        )
        pmc.rename_vm(vm_index=vm_index, new_name=name)
        count += 1


def get_vm_index(logger: Logger, name: str) -> int:
    """Get the index of the vm with the given name"""
    # get list of vms on machine
    vms: list[VMInfo] = pmc.list_vm_info()

    # sorted by index, lowest to highest
    vms.sort(key=lambda x: x["index"])

    # get the indecies of all vms named pyclashbot
    vm_indices: list[int] = [vm["index"] for vm in vms if vm["title"] == name]

    # delete all vms except the lowest index, keep looping until there is only one
    while len(vm_indices) > 1:
        # as long as no exception is raised, this while loop should exit on first iteration
        for vm_index in vm_indices[1:]:
            try:
                pmc.delete_vm(vm_index)
                vm_indices.remove(vm_index)
            except PyMemucError as err:
                logger.error(str(err))
                # don't raise error, just continue to loop until its deleted
                # raise err # if program hangs on deleting vm then uncomment this line

    # return the index. if no vms named pyclashbot exist, return -1
    return vm_indices[0] if vm_indices else -1
