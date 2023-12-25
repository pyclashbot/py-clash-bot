"""
This module contains functions for launching and controlling MEmu virtual machines,
as well as starting and stopping the Clash Royale app within them.
"""


import contextlib
import subprocess
import sys
import time
from os.path import join

import psutil
import PySimpleGUI as sg
from pymemuc import PyMemucError, VMInfo

from pyclashbot.bot.nav import wait_for_clash_main_menu
from pyclashbot.memu.configure import configure_vm
from pyclashbot.memu.pmc import pmc
from pyclashbot.utils.logger import Logger

ANDROID_VERSION = "96"  # android 9, 64 bit
EMULATOR_NAME = f"pyclashbot-{ANDROID_VERSION}"
APK_BASE_NAME = "com.supercell.clashroyale"


MANUAL_VM_WAIT_TIME = 10
MANUAL_CLASH_MAIN_WAIT_TIME = 10


def restart_emulator(logger, start_time=time.time()):
    """
    Restart the emulator.

    Args:
        logger (Logger): Logger object
        start_time (float, optional): Start time. Defaults to time.time().
    """
    # Rest of the code...
    # stop all vms
    close_everything_memu()

    # check for the pyclashbot vm, if not found then create it
    vm_index = check_for_vm(logger)

    logger.change_status(status="Confinguring the pyclashbot emulator...")
    configure_vm(vm_index=vm_index)

    # start the vm
    logger.change_status(status="Opening the pyclashbot emulator...")
    out = pmc.start_vm(vm_index=vm_index)
    print(f"Opened the pyclashbot emulator with output:\n{out}")

    # skip ads
    if skip_ads(vm_index) == "fail":
        logger.log("Error 99 Failed to skip ads")
        return restart_emulator(logger, start_time)

    # start clash royale
    logger.change_status("Starting clash royale")
    start_clash_royale(logger, vm_index)

    # check-wait for clash main if need to wait longer
    if wait_for_clash_main_menu(vm_index, logger) == "restart":
        logger.log("#34 Looping restart_emulator() b/c fail waiting for clash main")
        return restart_emulator(logger, start_time)

    time.sleep(1)

    logger.log(f"Took {str(time.time() - start_time)[:5]}s to launch emulator")
    return True


def skip_ads(vm_index):
    """
    Skip ads in the emulator.

    Args:
        vm_index (int): Index of the virtual machine.

    Returns:
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


def check_for_vm(logger: Logger) -> int:
    """Check for a vm named pyclashbot, create one if it doesn't exist

    Args:
        logger (Logger): Logger object

    Returns:
        int: index of the vm
    """
    start_time = time.time()

    find_vm_timeout = 20  # s
    find_vm_start_time = time.time()
    find_vm_tries = 0
    while time.time() - find_vm_start_time < find_vm_timeout:
        find_vm_tries += 1
        vm_index = get_vm_index(logger, EMULATOR_NAME)

        if vm_index != -1:
            logger.change_status(
                f'Found a vm named "pyclashbot" (#{vm_index}) in {find_vm_tries} tries'
            )
            return vm_index

        logger.change_status('Failed to find "pyclashbot" emulator. Retrying...')

    logger.change_status("Didn't find a vm named 'pyclashbot', creating one...")

    new_vm_index = create_vm()
    logger.change_status(f"New VM index is {new_vm_index}")

    logger.change_status("Configuring emualtor")
    configure_vm(vm_index=new_vm_index)

    logger.change_status("Setting language")
    rename_vm(vm_index=new_vm_index, name=EMULATOR_NAME)

    logger.change_status(
        f"Created and configured new pyclashbot emulator in {str(time.time() - start_time)[:5]}s"
    )

    return create_vm()


def start_clash_royale(logger: Logger, vm_index):
    """
    Start Clash Royale in the emulator.

    Args:
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
            status="Clash royale is not installed. Please install it and restart"
        )
        show_clash_royale_setup_gui()

    # start Clash Royale
    pmc.start_app_vm(APK_BASE_NAME, vm_index)
    logger.change_status(status="Successfully initialized Clash app")


# making/configuring emulator methods
def create_vm():
    """Create a vm with the given name and version"""
    start_memuc_console()

    vm_index = pmc.create_vm(vm_version="96")
    return vm_index


def rename_vm(
    vm_index: int,
    name: str,
):
    """rename the vm to name"""
    pmc.rename_vm(vm_index=vm_index, new_name=name)


# emulator interaction methods


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


def home_button_press(vm_index, clicks=4):
    """Method for skipping the memu ads that popip up when you start memu"""
    for _ in range(clicks):
        print("ad skip...")
        pmc.trigger_keystroke_vm("home", vm_index=vm_index)
        time.sleep(1)


# starting/closing memu vms/apps


def stop_vm(logger, vm_index):
    """Stops the VM with the given index."""
    logger.change_status(status=f"Stopping VM {vm_index}")
    pmc.stop_vm(vm_index=vm_index)
    time.sleep(5)


def launch_vm(logger, vm_index):
    """Launches the VM with the given index."""
    logger.change_status(status=f"Launching VM {vm_index}")
    pmc.start_vm(vm_index=vm_index)


def restart_vm(logger, vm_index):
    """Restarts the VM with the given index."""
    stop_vm(logger, vm_index)
    launch_vm(logger, vm_index)


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
    """using pymemuc check if clash royale is installed"""
    apk_base_name = "com.supercell.clashroyale"

    pmc.stop_app_vm(apk_base_name, vm_index)
    logger.change_status(status=f"Clash Royale stopped on vm {vm_index}")


def close_everything_memu():
    """
    Closes all MEmu processes.
    """
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
    """
    Displays a GUI window indicating that Clash Royale is not installed or setup.
    """

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


if __name__ == "__main__":
    configure_vm(4)
