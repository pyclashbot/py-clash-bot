"""This module contains functions for launching and controlling MEmu virtual machines,
as well as starting and stopping the Clash Royale app within them.
"""

import contextlib
import subprocess
import sys
import time
from os.path import join

import psutil
import PySimpleGUI as sg

from pyclashbot.bot.nav import check_if_in_battle_at_start, check_if_on_clash_main_menu
from pyclashbot.memu.client import click, screenshot
from pyclashbot.memu.configure import EMULATOR_NAME, configure_vm
from pyclashbot.memu.pmc import get_vm_index, pmc
from pyclashbot.utils.logger import Logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pymemuc import VMInfo


APK_BASE_NAME = "com.supercell.clashroyale"


MANUAL_VM_WAIT_TIME = 10
MANUAL_CLASH_MAIN_WAIT_TIME = 10


def check_vm_size(vm_index):
    try:
        home_button_press(vm_index, clicks=1)

        image = screenshot(vm_index)

        height, width, _ = image.shape

        if width != 419 or height != 633:
            print(f"Size is bad: {width},{height}")
            return False

        return True
    except Exception as e:
        print("sizing error:", e)

    # in the case of errors, just return True to avoid infinite loop
    return True


def restart_emulator(logger, render_mode, start_time=time.time(), open_clash=True):
    """Restart the emulator.

    Args:
    ----
        logger (Logger): Logger object
        start_time (float, optional): Start time. Defaults to time.time().

    """
    # Rest of the code...
    # stop all vms
    close_everything_memu()

    # check for the pyclashbot vm, if not found then create it
    vm_index = get_vm(logger, render_mode)

    # start the vm
    logger.change_status(status="Opening the pyclashbot emulator...")
    out = pmc.start_vm(vm_index=vm_index)
    print(f"Opened the pyclashbot emulator with output:\n{out}")

    # skip ads
    if skip_ads(vm_index) == "fail":
        logger.log("Error 99 Failed to skip ads")
        return restart_emulator(logger, render_mode, start_time)

    print(check_vm_size(vm_index))
    if not check_vm_size(vm_index):
        logger.log("Error 1010 VM size is bad")
        return restart_emulator(logger, render_mode, start_time)

    # if open_clash is toggled, open CR
    if open_clash:
        # start clash royale
        logger.change_status("Starting clash royale")
        start_clash_royale(logger, vm_index)

        # wait for clash main to appear
        logger.change_status("Waiting for CR main menu")
        clash_main_wait_start_time = time.time()
        clash_main_wait_timeout = 240  # s
        time.sleep(12)
        while time.time() - clash_main_wait_start_time < clash_main_wait_timeout:
            if check_if_on_clash_main_menu(vm_index) is True:
                logger.change_status("Detected clash main!")
                logger.log(
                    f"Took {str(time.time() - start_time)[:5]}s to launch emulator",
                )
                return True
            # Check if a battle is detected at start
            battle_start_result = check_if_in_battle_at_start(vm_index, logger)
            if battle_start_result == "good":
                return True  # Successfully handled starting battle or end-of-battle scenario
            if battle_start_result == "restart":
                # Need to restart the process due to issues detected
                return restart_emulator(logger, render_mode, start_time)

            # click deadspace
            click(vm_index, 5, 350)

            # logger.log("Not on clash main")
            # logger.log("Pixels are: ")
            # for p in clash_main_check:
            #     logger.log(p)

        if check_if_on_clash_main_menu(vm_index) is not True:
            logger.log("Clash main wait timed out! These are the pixels it saw:")
            # for p in clash_main_check:
            #     logger.log(p)
            return restart_emulator(logger, render_mode, start_time)

    print("Skipping clash open sequence")
    logger.log(f"Took {str(time.time() - start_time)[:5]}s to launch emulator")
    return True


def skip_ads(vm_index):
    """Skip ads in the emulator.

    Args:
    ----
        vm_index (int): Index of the virtual machine.

    Returns:
    -------
        str: "success" if ads are skipped successfully, "fail" otherwise.

    """
    try:
        for _ in range(4):
            pmc.trigger_keystroke_vm("home", vm_index=vm_index)
            time.sleep(1)
    except Exception as err:  # pylint: disable=broad-except
        print(f"Fail sending home clicks to skip ads... Redoing restart...\n{err}")
        return "fail"
    return "success"


def get_vm(logger: Logger, render_mode) -> int:
    # find existing vm
    find_vm_timeout = 5  # s
    find_vm_start_time = time.time()
    vm_index = -1
    while vm_index == -1 and time.time() - find_vm_start_time < find_vm_timeout:
        vm_index = get_vm_index(EMULATOR_NAME)
        logger.change_status('Failed to find "pyclashbot" emulator. Retrying...')
    if vm_index != -1:
        logger.change_status(f'Found a vm named "pyclashbot" (#{vm_index})!')

    # if we didnt find a vm, make a new one
    if vm_index == -1:
        print("Creating a new vm...")
        vm_index = create_vm()
        print("Renaming this new vm to", EMULATOR_NAME)
        rename_vm(vm_index, name=EMULATOR_NAME)

    # config the vm
    print("Configuring the vm...")
    configure_vm(vm_index, render_mode)

    print("Done in get_vm()")
    return vm_index


def start_clash_royale(logger: Logger, vm_index):
    """Start Clash Royale in the emulator.

    Args:
    ----
        logger (Logger): Logger object.
        vm_index (int): Index of the virtual machine.

    """
    # Function implementation goes here

    # get list of installed apps
    installed_apps = pmc.get_app_info_list_vm(vm_index=vm_index)

    # check list of installed apps for names containing base name
    found = [app for app in installed_apps if APK_BASE_NAME in app]

    if not found:
        # notify user that clash royale is not installed, program will exit
        logger.change_status(
            status="Clash royale is not installed. Please install it and restart",
        )
        show_clash_royale_setup_gui()

    # start Clash Royale
    pmc.start_app_vm(APK_BASE_NAME, vm_index)
    logger.change_status(status="Successfully initialized Clash app")


# making/configuring emulator methods
def create_vm() -> int:
    """Create a vm with the given name and version"""
    print("Starting console")
    start_memuc_console()

    print("Creating vm...")
    vm_index = pmc.create_vm(vm_version="96")
    return vm_index


def rename_vm(
    vm_index: int,
    name: str,
):
    """Rename the vm to name"""
    pmc.rename_vm(vm_index=vm_index, new_name=name)


# emulator interaction methods
def home_button_press(vm_index, clicks=4):
    """Method for skipping the memu ads that popip up when you start memu"""
    for _ in range(clicks):
        print("ad skip...")
        pmc.trigger_keystroke_vm("home", vm_index=vm_index)
        time.sleep(1)


# starting/closing memu vms/apps


def stop_vm(vm_index):
    """Stops the VM with the given index."""
    while check_for_emulator_running(vm_index) is True:
        pmc.stop_vm(vm_index=vm_index)
        time.sleep(3)


def launch_vm(logger, vm_index):
    """Launches the VM with the given index."""
    logger.change_status(status=f"Launching VM {vm_index}")
    pmc.start_vm(vm_index=vm_index)


def start_memuc_console() -> int:
    """Start the memuc console and return the process ID"""
    # check if memu console is already running
    for process in psutil.process_iter():
        with contextlib.suppress(psutil.NoSuchProcess, psutil.AccessDenied):
            if process.name() == "MEMuConsole.exe":
                return process.pid

    # start memu console
    # pylint: disable=protected-access
    console_path = join(pmc._get_memu_top_level(), "MEMuConsole.exe")
    # pylint: disable=consider-using-with
    process = subprocess.Popen(console_path, creationflags=subprocess.DETACHED_PROCESS)

    # ensure the process actually started
    time.sleep(2)
    return process.pid if psutil.pid_exists(process.pid) else start_memuc_console()


def stop_memuc_console(process_id: int) -> None:
    """Stop the memuc console with the given process ID"""
    try:
        process = psutil.Process(process_id)
        process.terminate()
    except psutil.NoSuchProcess:
        print("#975627345 Failure to stop memuc console")


def close_clash_royale_app(logger, vm_index):
    """Using pymemuc check if clash royale is installed"""
    apk_base_name = "com.supercell.clashroyale"

    pmc.stop_app_vm(apk_base_name, vm_index)
    logger.change_status(status=f"Clash Royale stopped on vm {vm_index}")


def close_everything_memu():
    """Closes all MEmu processes."""
    name_list = [
        "MEmuConsole.exe",
        "MEmu.exe",
        "MEmuHeadless.exe",
    ]

    print("Closing memu processes...")
    for proc in psutil.process_iter():
        try:
            if proc.name() in name_list:
                print("Closing process", proc.name())
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            print("Couldnt close process", proc.name())


# error popup guis


def show_clash_royale_setup_gui():
    """Displays a GUI window indicating that Clash Royale is not installed or setup."""
    out_text = """Clash Royale is not installed or setup.
Please install Clash Royale, finish the in-game tutorial
and login before using this bot."""

    _layout = [
        [sg.Text(out_text)],
    ]
    _window = sg.Window("Clash Royale Not Setup!", _layout)
    while True:
        read = _window.read()
        if read is None:
            break
        _event, _ = read
        if _event in [sg.WIN_CLOSED]:
            break
    _window.close()
    sys.exit(0)


# new


def get_clashbot_vm_index():
    vms: list[VMInfo] = pmc.list_vm_info()

    start_time = time.time()
    timeout = 60  # s

    while time.time() - start_time < timeout:
        for vm in vms:
            title = vm["title"]
            if "pyclashbot-96" in title:
                return vm["index"]

    return False


def delete_vm(vm_index):
    start_time = time.time()
    timeout = 60  # s

    while pmc.delete_vm(vm_index) is not True:
        if time.time() - start_time > timeout:
            print(f"Timed out while trying to delete vm#{vm_index}")
            return False

        print("Failed to delete vm... retrying")

    return True


def check_for_emulator_running(vm_index):
    vms: list[VMInfo] = pmc.list_vm_info()

    for vm in vms:
        if vm["index"] != vm_index:
            continue

        return vm["running"]

    return False


if __name__ == "__main__":
    pass
