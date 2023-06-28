"""
This module contains functions for launching and controlling MEmu virtual machines,
as well as starting and stopping the Clash Royale app within them.
"""

import time

import numpy
import pythoncom
import wmi
from pymemuc import PyMemuc

from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.memu.app_handler import check_for_clash_royale_installed
from pyclashbot.memu.client import click, screenshot
from pyclashbot.memu.emulator import set_vm_language
from pyclashbot.utils.logger import Logger



pmc = PyMemuc(debug=False)

ANDROID_VERSION = "96"  # android 9, 64 bit
EMULATOR_NAME = f"pyclashbot-{ANDROID_VERSION}"


def launch_vm(logger, vm_index):
    """Launches the VM with the given index."""
    logger.change_status(f"Launching VM {vm_index}")
    pmc.start_vm(vm_index=vm_index)
    time.sleep(10)
    set_vm_language(vm_index=vm_index)
    time.sleep(10)


def stop_vm(logger, vm_index):
    """Stops the VM with the given index."""
    logger.change_status(f"Stopping VM {vm_index}")
    pmc.stop_vm(vm_index=vm_index)
    time.sleep(10)


def restart_vm(logger, vm_index):
    """Restarts the VM with the given index."""
    stop_vm(logger, vm_index)
    launch_vm(logger, vm_index)




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
