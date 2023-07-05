"""
This module contains functions for launching and controlling MEmu virtual machines,
as well as starting and stopping the Clash Royale app within them.
"""

import subprocess
import time
from os.path import join

import numpy
import psutil
import pythoncom
import wmi
from pymemuc import PyMemuc, PyMemucError, VMInfo

from detection.image_rec import pixel_is_equal
from memu.app_handler import check_for_clash_royale_installed
from memu.client import screenshot
from memu.emulator import set_vm_language
from bot.navigation import wait_for_clash_main_menu
from utils.logger import Logger
import sys
import PySimpleGUI as sg

pmc = PyMemuc(debug=False)

ANDROID_VERSION = "96"  # android 9, 64 bit
EMULATOR_NAME = f"pyclashbot-{ANDROID_VERSION}"


# launcher specific methods


def restart_emulator(logger):
    # restart the game, including the launcher and emulator

    # stop all vms
    logger.change_status("Closing everything Memu related. . .")
    close_everything_memu()

    # check for the pyclashbot vm, if not found then create it
    vm_index = check_for_vm(logger)
    print(f"Found vm of index {vm_index}")
    configure_vm(logger, vm_index=vm_index)

    # start the vm
    # logger.change_status("Starting a new Memu Client using the launcher. . .")
    # start_emulator_without_pmc(logger) # this is the old way
    logger.change_status("Starting emulator...")
    pmc.start_vm(vm_index=vm_index)

    # wait for the window to appear
    sleep_time = 10
    for n in range(sleep_time):
        print(f"Waiting for VM to load {n}/{sleep_time}")
        time.sleep(1)

    # wait_for_memu_window(logger)

    # skip ads
    if skip_ads(vm_index) == "fail":
        return restart_emulator(logger)

    # start clash royale
    start_clash_royale(logger, vm_index)

    # manually wait for clash main
    sleep_time = 10
    for n in range(sleep_time):
        print(f"Manually waiting for clash main page. {n}/{sleep_time}")
        time.sleep(1)

    # check-wait for clash main if need to wait longer
    if wait_for_clash_main_menu(vm_index, logger) == "restart":
        return restart_emulator(logger)

    time.sleep(5)

    return True


def skip_ads(vm_index):
    # Method for skipping the memu ads that popip up when you start memu

    print("Trying to skipping ads")
    try:
        for _ in range(4):
            pmc.trigger_keystroke_vm("home", vm_index=vm_index)
            time.sleep(1)
    except Exception as err:  # pylint: disable=broad-except
        print(f"Fail sending home clicks to skip ads... Redoing restart...\n{err}")
        input("Enter to cont")
        return "fail"
    return "success"


def check_for_vm(logger: Logger) -> int:
    """Check for a vm named pyclashbot, create one if it doesn't exist

    Args:
        logger (Logger): Logger object

    Returns:
        int: index of the vm
    """

    vm_index = get_vm_index(logger, EMULATOR_NAME)

    # return the index. if no vms named pyclashbot exist, create one.
    return vm_index if vm_index != -1 else create_vm(logger)


def start_clash_royale(logger: Logger, vm_index):
    # using pymemuc check if clash royale is installed
    apk_base_name = "com.supercell.clashroyale"

    # get list of installed apps
    installed_apps = pmc.get_app_info_list_vm(vm_index=vm_index)

    # check list of installed apps for names containing base name
    found = [app for app in installed_apps if apk_base_name in app]

    if not found:
        # notify user that clash royale is not installed, program will exit
        logger.change_status(
            "Clash royale is not installed. Please install it and restart"
        )
        show_clash_royale_setup_gui()

    # start clash royale
    pmc.start_app_vm(apk_base_name, vm_index)
    logger.change_status("Clash Royale started")


# making/configuring emulator methods
def create_vm(logger: Logger):
    # create a vm named pyclashbot
    logger.change_status("Creating VM...")
    memuc_pid = start_memuc_console()

    vm_index = pmc.create_vm(vm_version=ANDROID_VERSION)
    while vm_index == -1:  # handle when vm creation fails
        vm_index = pmc.create_vm(vm_version=ANDROID_VERSION)
        time.sleep(1)
    time.sleep(5)
    configure_vm(logger, vm_index)
    # rename the vm to pyclashbot
    rename_vm(logger, vm_index, EMULATOR_NAME)
    stop_memuc_console(memuc_pid)
    logger.change_status(f"Created VM: {vm_index} - {EMULATOR_NAME}")
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


def configure_vm(logger: Logger, vm_index):
    logger.change_status("Configuring VM")

    memuc_pid = start_memuc_console()

    cpu_count: int = psutil.cpu_count(logical=False)
    cpu_count: int = numpy.clip(cpu_count // 2, 2, 6)
    c_interface = wmi.WMI()
    total_mem = int(c_interface.Win32_ComputerSystem()[0].TotalPhysicalMemory)
    total_mem = total_mem // 1024 // 1024
    total_mem: int = numpy.clip(total_mem // 2, 2048, 4096)

    # see https://pymemuc.readthedocs.io/pymemuc.html#the-vm-configuration-keys-table
    configuration: dict[str, str] = {
        "start_window_mode": "2",  # custom window position
        "win_x": "0",
        "win_y": "0",
        "win_scaling_percent2": "100",  # 100% scaling
        "is_customed_resolution": "1",
        "resolution_width": "419",
        "resolution_height": "633",
        "vbox_dpi": "160",
        "cpucap": "50",
        "cpus": str(cpu_count),
        "memory": str(total_mem),
        "fps": "30",
        "enable_audio": "0",
    }

    for key, value in configuration.items():
        pmc.set_configuration_vm(key, value, vm_index=vm_index)

    time.sleep(3)
    set_vm_language(vm_index=vm_index)
    time.sleep(10)

    stop_memuc_console(memuc_pid)


# emulator interaction methods


def get_vm_index(logger: Logger, name: str) -> int:
    """Get the index of the vm with the given name"""
    # get list of vms on machine
    vms: list[VMInfo] = pmc.list_vm_info()

    # sorted by index, lowest to highest
    vms.sort(key=lambda x: x["index"])

    # get the indecies of all vms named clanspam
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

    # return the index. if no vms named clanspam exist, return -1
    return vm_indices[0] if vm_indices else -1


def home_button_press(vm_index, clicks=4):
    """Method for skipping the memu ads that popip up when you start memu"""
    for _ in range(clicks):
        print("ad skip...")
        pmc.trigger_keystroke_vm("home", vm_index=vm_index)
        time.sleep(1)


def check_if_clash_banned(vm_index):
    iar = numpy.asarray(screenshot(vm_index))

    red_okay_text_exists = False
    for x in range(140, 190):
        this_pixel = iar[405][x]
        if pixel_is_equal([252, 67, 69], this_pixel, tol=35):
            red_okay_text_exists = True
            break

    blue_loading_bar_exists = False
    for x in range(40, 120):
        this_pixel = iar[623][x]
        if pixel_is_equal([25, 113, 214], this_pixel, tol=35):
            blue_loading_bar_exists = True
            break

    white_account_information_text_exists = False
    for x in range(100, 180):
        this_pixel = iar[209][x]
        if pixel_is_equal([255, 255, 255], this_pixel, tol=35):
            white_account_information_text_exists = True
            break

    if (
        red_okay_text_exists
        and blue_loading_bar_exists
        and white_account_information_text_exists
    ):
        return True
    return False


def check_if_on_clash_main_menu(vm_index):
    """
    Checks if the user is on the clash main menu.
    Returns True if on main menu, False if not.
    """
    iar = numpy.asarray(screenshot(vm_index))

    gem_icon_exists = False
    for x_val in range(395, 412):
        this_pixel = iar[17][x_val]
        if pixel_is_equal([65, 198, 24], this_pixel, tol=35):
            gem_icon_exists = True

    friends_icon_exists = False
    for x_val in range(255, 280):
        this_pixel = iar[72][x_val]
        if pixel_is_equal([244, 244, 255], this_pixel, tol=35):
            friends_icon_exists = True

    gold_icon_exists = False
    for x_val in range(290, 310):
        this_pixel = iar[13][x_val]
        if pixel_is_equal([223, 175, 56], this_pixel, tol=35):
            gold_icon_exists = True

    return bool(gem_icon_exists and friends_icon_exists and gold_icon_exists)


# starting/closing memu vms/apps


def stop_vm(logger, vm_index):
    """Stops the VM with the given index."""
    logger.change_status(f"Stopping VM {vm_index}")
    pmc.stop_vm(vm_index=vm_index)
    time.sleep(10)


def launch_vm(logger, vm_index):
    """Launches the VM with the given index."""
    logger.change_status(f"Launching VM {vm_index}")
    pmc.start_vm(vm_index=vm_index)
    time.sleep(10)
    set_vm_language(vm_index=vm_index)
    time.sleep(10)


def restart_vm(logger, vm_index):
    """Restarts the VM with the given index."""
    stop_vm(logger, vm_index)
    launch_vm(logger, vm_index)


def start_memuc_console() -> int:
    """Start the memuc console and return the process ID"""
    # pylint: disable=protected-access
    console_path = join(pmc._get_memu_top_level(), "MEMuConsole.exe")
    # pylint: disable=consider-using-with
    process = subprocess.Popen(console_path, creationflags=subprocess.DETACHED_PROCESS)

    print(f"Started memu console with PID {process.pid}")

    return process.pid


def close_clash_royale_app(logger, vm_index):
    """using pymemuc check if clash royale is installed"""
    apk_base_name = "com.supercell.clashroyale"

    pmc.stop_app_vm(apk_base_name, vm_index)
    logger.change_status(f"Clash Royale stopped on vm {vm_index}")


def start_clash_royale_app(logger: Logger, vm_index):
    """using pymemuc check if clash royale is installed"""
    try:
        check_for_clash_royale_installed(logger, vm_index)
    except FileNotFoundError as exc:
        logger.log("Clash royale is not installed. Please install it and restart")
        for _ in range(3):
            print(f"CRITICAL ERROR!! CLASH ROYALE NOT INSTALLED ON VM #{vm_index} !!!")
        raise FileNotFoundError from exc

    # start clash royale
    pmc.start_app_vm("com.supercell.clashroyale", vm_index)
    logger.log("Clash Royale started")


def close_everything_memu():
    """
    Closes all MEmu processes.
    """
    name_list = [
        "MEmuConsole.exe",
        "MEmu.exe",
        "MEmuHeadless.exe",
    ]

    pythoncom.CoInitialize()  # pylint: disable=no-member
    win_interface = wmi.WMI()
    print("Entered close_everything_memu()")
    for process in win_interface.Win32_Process():
        try:
            if process.name in name_list:
                print("Closing process", process.name)
                process.Terminate()
        except wmi.x_wmi as err:
            print("Couldnt close process", process.name)
            print("This error occured:", err)
    print("Exiting close_everything_memu(). . .")


def stop_memuc_console(process_id: int) -> None:
    """Stop the memuc console with the given process ID"""
    try:
        process = psutil.Process(process_id)
        process.terminate()
    except psutil.NoSuchProcess:
        print("#975627345 Failure to stop memuc console")


# error popup guis


def show_clash_royale_setup_gui():
    # a method to notify the user that clashroayle is not installed or setup

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
