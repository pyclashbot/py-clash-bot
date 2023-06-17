import os
import time

import numpy
import pygetwindow
import pythoncom
import wmi
from pymemuc import PyMemuc, PyMemucError, VMInfo

from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.interface import show_clash_royale_setup_gui
from pyclashbot.memu.client import click, screenshot
from pyclashbot.utils.dependency import get_memu_path
from pyclashbot.utils.logger import Logger

pmc = PyMemuc(debug=True)

ANDROID_VERSION = "96"  # android 9, 64 bit
EMULATOR_NAME = f"pyclashbot-{ANDROID_VERSION}"


#### launcher methods
def restart_emulator(logger):
    # restart the game, including the launcher and emulator

    # stop all vms
    logger.change_status("Closing everything Memu related. . .")
    pmc.stop_all_vm(timeout=10)
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
    if wait_for_clash_main_menu(logger) == "restart":
        return restart_emulator(logger)

    time.sleep(5)

    return True


#### making and configuring VMs


def configure_vm(logger: Logger, vm_index):
    logger.change_status("Configuring VM")

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
        "fps": "30",
        "enable_audio": "0",
    }

    for key, value in configuration.items():
        pmc.set_configuration_vm(key, value, vm_index=vm_index)


def create_vm(logger: Logger):
    # create a vm named pyclashbot
    logger.change_status("VM not found, creating VM...")
    vm_index = pmc.create_vm(vm_version=ANDROID_VERSION)
    while vm_index == -1:  # handle when vm creation fails
        vm_index = pmc.create_vm(vm_version=ANDROID_VERSION)
    configure_vm(logger, vm_index)
    # rename the vm to pyclashbot
    pmc.rename_vm(vm_index=vm_index, new_name=EMULATOR_NAME)
    logger.change_status(f"Created VM: {vm_index} - {EMULATOR_NAME}")
    return vm_index


def check_for_vm(logger: Logger) -> int:
    """Check for a vm named pyclashbot, create one if it doesn't exist

    Args:
        logger (Logger): Logger object

    Returns:
        int: index of the vm
    """

    # get list of vms on machine
    vms: list[VMInfo] = pmc.list_vm_info()

    # sorted by index, lowest to highest
    vms.sort(key=lambda x: x["index"])

    # get the indecies of all vms named pyclashbot
    vm_indices: list[int] = [vm["index"] for vm in vms if vm["title"] == EMULATOR_NAME]

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

    # return the index. if no vms named pyclashbot exist, create one.
    return vm_indices[0] if vm_indices else create_vm(logger)


def close_everything_memu():
    name_list = [
        "MEmuConsole.exe",
        "MEmu.exe",
        "MEmuHeadless.exe",
    ]

    pythoncom.CoInitialize()  # pylint: disable=no-member
    c = wmi.WMI()
    print("Entered close_everything_memu()")
    for process in c.Win32_Process():
        try:
            if process.name in name_list:
                print("Closing process", process.name)
                process.Terminate()
        except Exception as e:
            print("Couldnt close process", process.name)
            print("This error occured:", e)
    print("Exiting close_everything_memu(). . .")


#### interacting with the vm


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


def skip_ads(vm_index):
    # Method for skipping the memu ads that popip up when you start memu

    print("Trying to skipping ads")
    try:
        for _ in range(4):
            pmc.trigger_keystroke_vm("home", vm_index=vm_index)
            time.sleep(1)
    except Exception as e:
        print(f"Fail sending home clicks to skip ads... Redoing restart...\n{e}")
        input("Enter to cont")
        return "fail"


#### copy of clashmain's wait_for_clash_main_menu methods
def wait_for_clash_main_menu(logger):
    logger.change_status("Waiting for clash main menu")
    waiting = not check_if_on_clash_main_menu()

    loops = 0
    while waiting:
        # loop count
        loops += 1
        if loops > 25:
            logger.change_status("Looped through getting to clash main too many times")
            print(
                "wait_for_clash_main_menu() took too long waiting for clash main. Restarting."
            )
            return "restart"

        # wait 1 sec
        time.sleep(1)

        # click dead space
        click(32, 364)

        # check if stuck on trophy progression page
        if check_if_stuck_on_trophy_progression_page():
            logger.change_status("Stuck on trophy progression page. Trying to fix...")
            time.sleep(1)
            click(210, 621)

        # check if stuck in the middle of opening a lightning chest
        if check_if_stuck_on_lightning_chest():
            logger.change_status("Stuck on lightning chest. Trying to fix...")
            handle_stuck_on_lightning_chest()

        # check if still waiting
        waiting = not check_if_on_clash_main_menu()

    logger.change_status("Done waiting for clash main menu")


def check_if_stuck_on_lightning_chest():
    iar = numpy.asarray(screenshot())

    yellow_question_mark_exists = False
    for x in range(335, 355):
        this_pixel = iar[625][x]
        if pixel_is_equal(this_pixel, [255, 188, 40], tol=35):
            yellow_question_mark_exists = True

    lightning_symbol_exists = False
    for x in range(70, 80):
        this_pixel = iar[610][x]
        if pixel_is_equal(this_pixel, [120, 224, 255], tol=35):
            lightning_symbol_exists = True

    red_card_count_exists = False
    for x in range(260, 290):
        this_pixel = iar[339][x]
        if pixel_is_equal(this_pixel, [200, 49, 48], tol=35):
            red_card_count_exists = True

    if (
        yellow_question_mark_exists
        and lightning_symbol_exists
        and red_card_count_exists
    ):
        return True
    return False


def handle_stuck_on_lightning_chest():
    # skip thru chest
    click(20, 440, clicks=10, interval=1)

    # click skip strikes
    click(212, 610)
    time.sleep(1)

    # click deadspace a few times
    click(20, 440, clicks=5, interval=1)


def check_if_stuck_on_trophy_progression_page():
    iar = numpy.asarray(screenshot())
    pix_list = [
        # iar[620][225],
        iar[625][230],
        iar[630][238],
        iar[635][245],
    ]

    return all(pixel_is_equal(pix, [85, 177, 255], tol=45) for pix in pix_list)


def check_if_on_clash_main_menu():
    if not check_for_gem_logo_on_main():
        # print("gem fail")
        return False

    # if not check_for_blue_background_on_main():
    #     # print("blue fail")
    #     return False

    if not check_for_friends_logo_on_main():
        # print("friends logo")
        return False

    if not check_for_gold_logo_on_main():
        # print("gold logo")
        return False
    return True


def check_for_gem_logo_on_main():
    # Method to check if the clash main menu is on screen
    iar = numpy.array(screenshot())

    pix_list = [
        iar[46][402],
        iar[52][403],
        iar[48][410],
    ]

    for pix in pix_list:
        return bool(pixel_is_equal(pix, [75, 180, 35], tol=45))


def check_for_gold_logo_on_main():
    # Method to check if the clash main menu is on screen
    iar = numpy.array(screenshot())

    pix_list = [
        iar[48][299],
        iar[52][300],
        iar[44][302],
        iar[49][297],
    ]
    color = [201, 177, 56]

    for pix in pix_list:
        return bool(pixel_is_equal(pix, color, tol=85))


def check_for_friends_logo_on_main():
    # Method to check if the clash main menu is on screen
    iar = numpy.array(screenshot())

    pix_list = [
        iar[90][269],
        iar[105][265],
        iar[103][272],
        iar[89][270],
        iar[107][266],
    ]
    color = [177, 228, 252]

    # pixel check
    for pix in pix_list:
        return bool(pixel_is_equal(pix, color, tol=65))
    return False
