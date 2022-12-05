import subprocess
import time

import numpy
import pygetwindow
from pymemuc import PyMemuc, PyMemucError, VMInfo

from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.interface import show_clash_royale_setup_gui
from pyclashbot.memu.client import click, screenshot
from pyclashbot.utils import setup_memu
from pyclashbot.utils.logger import Logger

launcher_path = setup_memu()  # setup memu, install if necessary
pmc = PyMemuc(debug=True)


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
    vm_index = pmc.create_vm()
    while vm_index == -1:  # handle when vm creation fails
        vm_index = pmc.create_vm()
    # configure_vm(logger, vm_index)
    # rename the vm to pyclashbot
    pmc.rename_vm(vm_index, new_name="pyclashbot")
    logger.change_status("VM created")
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
    vm_indices: list[int] = [vm["index"] for vm in vms if vm["title"] == "pyclashbot"]

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


def start_vm(logger: Logger):
    # Method for starting the memu client
    logger.change_status("Starting Memu Client")
    vm_index = check_for_vm(logger)
    configure_vm(logger, vm_index)
    logger.change_status("Starting VM...")
    pmc.start_vm(vm_index=vm_index)
    orientate_memu()
    # move_window_to_top_left("pyclashbot")
    logger.change_status("VM Started")
    return vm_index


def restart_memu(logger: Logger):
    # stop all vms
    try:
        pmc.stop_all_vm()
        # get list of running vms on machine
        vms: list[VMInfo] = pmc.list_vm_info(running=True)
        # stop any vms named pyclashbot
        for vm in vms:
            if vm["title"] == "pyclashbot":
                pmc.stop_vm(vm["index"])
    except PyMemucError as err:
        if vms := pmc.list_vm_info(running=True):
            logger.change_status("Error stopping VM")
            logger.error(str(err))
            raise err

    # orientate_terminal()

    logger.change_status("Opening MEmu launcher")
    vm_index = start_vm(logger)
    time.sleep(15)
    skip_ads(logger, vm_index)
    return vm_index


first_run = True


def restart_and_open_clash(logger: Logger):
    # Method for restarting (and starting) Memu, opening clash, and
    # waiting for the clash main menu to appear.

    close_memu()
    vm_index = restart_memu(logger)
    start_clash_royale(logger, vm_index)
    time.sleep(10)
    wait_for_clash_main_menu(logger)

    global first_run  # pylint: disable=global-statement
    if first_run:
        first_run = False
    else:
        # logger.add_restart()
        pass


def close_memu():
    try:
        memu_window = pygetwindow.getWindowsWithTitle("(pyclashbot)")[0]
        if memu_window is not None:
            print("Found a memu process to kill.")
        memu_window.close()
        subprocess.call("TASKKILL /F /IM MEmu.exe", shell=True)
    except:
        print("Couldn't close memu b/c couldn't find it's window")


def start_clash_royale(logger: Logger, vm_index):

    logger.change_status("Finding Clash Royale...")

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


def skip_ads(logger: Logger, vm_index):

    # Method for skipping the memu ads that popip up when you start memu

    logger.change_status("Skipping ads")
    for _ in range(4):
        pmc.trigger_keystroke_vm("home", vm_index=vm_index)
        time.sleep(1)


def close_vm(logger: Logger, vm_index):

    # Method to close memu
    logger.change_status("Closing VM")
    pmc.stop_vm(vm_index)
    logger.change_status("VM closed")


def orientate_memu():
    """Method for orientating Memu client"""
    try:
        window_memu = pygetwindow.getWindowsWithTitle("MEmu")[0]
        window_memu.minimize()
        window_memu.restore()

        time.sleep(0.2)
        try:
            window_memu.moveTo(0, 0)
        except pygetwindow.PyGetWindowException:
            print("Had trouble moving MEmu window.")
        time.sleep(0.2)
        try:
            window_memu.resizeTo(460, 680)
        except pygetwindow.PyGetWindowException:
            print("Had trouble resizing MEmu window")
    except Exception:
        print("Couldnt orientate MEmu")


def close_clash(logger, pmc, vm_index):
    logger.change_status("Closing Clash Royale Application")

    apk_base_name = "com.supercell.clashroyale"

    # close clash app
    pmc.stop_app_vm(apk_base_name, vm_index)


def restart_clash_app(logger):
    logger.change_status("Restarting Clash Royale Application")

    # get this vm index
    vm_index = check_for_vm(logger)

    # close app
    close_clash(logger, pmc, vm_index)

    # start app
    start_clash_royale(logger, vm_index)

    # manual wait time for clash main
    for n in range(5):
        print("Manual wait time for clash main: ", n)
        time.sleep(1)

    # wait for main
    wait_for_clash_main_menu(logger)

    # log to new restarts var


# copy of clashmain's wait_for_clash_main_menu methods
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
            time.sleep(1)
            click(210, 621)

        # check if still waiting
        waiting = not check_if_on_clash_main_menu()

    logger.change_status("Done waiting for clash main menu")


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

    if not check_for_blue_background_on_main():
        # print("blue fail")
        return False

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


def check_for_blue_background_on_main():
    # Method to check if the clash main menu is on screen
    iar = numpy.array(screenshot())

    pix_list = [
        iar[350][3],
        iar[360][6],
        iar[368][7],
        iar[372][9],
    ]

    for pix in pix_list:
        return bool(pixel_is_equal(pix, [9, 69, 119], tol=45))


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
