import time
from typing import Any

from pymemuc import PyMemuc
from pyclashbot.bot.clashmain import wait_for_clash_main_menu

from pyclashbot.interface import show_clash_royale_setup_gui
from pyclashbot.utils import setup_memu

launcher_path = setup_memu()  # setup memu, install if necessary
pmc = PyMemuc()


def configure_vm(logger, vm_index):
    logger.change_status("Configuring VM")

    # see https://pymemuc.readthedocs.io/pymemuc.html#the-vm-configuration-keys-table

    configuration: dict[str, str] = {
        "start_window_mode": "1",  # remember position
        "win_x": "0",
        "win_y": "0",
        "is_customed_resolution": "1",
        "resolution_width": "419",
        "resolution_height": "633",
        "vbox_dpi": "160",
        "fps": "30",
        "enable_audio": "0",
    }

    for key, value in configuration.items():
        pmc.set_configuration_vm(key, value, vm_index=vm_index)


def create_vm(logger):
    # create a vm named pyclashbot
    logger.change_status("VM not found, creating VM...")
    vm_index = pmc.create_vm()
    # configure_vm(logger, vm_index)
    # rename the vm to pyclashbot
    pmc.rename_vm(vm_index, new_name="pyclashbot")
    logger.change_status("VM created")
    return vm_index


def check_for_vm(logger):
    # get list of vms on machine
    vms: list[dict[str, Any]] = pmc.list_vm_info()  # type: ignore

    # find vm named pyclashbot
    found = any(vm["title"] == "pyclashbot" for vm in vms)

    return (
        next(vm["index"] for vm in vms if vm["title"] == "pyclashbot")
        if found
        else create_vm(logger)
    )


def start_vm(logger):
    # Method for starting the memu client
    logger.change_status("Starting Memu Client")
    vm_index = check_for_vm(logger)
    configure_vm(logger, vm_index)
    logger.change_status("Starting VM...")
    pmc.start_vm(vm_index=vm_index)
    logger.change_status("VM Started")
    # move_window_to_top_left("pyclashbot")

    return vm_index


def restart_and_open_clash(logger):
    # Method for restarting Memu, opening clash, and
    # waiting for the clash main menu to appear.

    # get list of running vms on machine
    vms: list[dict[str, Any]] = pmc.list_vm_info(running=True)  # type: ignore

    # stop any vms named pyclashbot
    for vm in vms:
        if vm["title"] == "pyclashbot":
            pmc.stop_vm(vm["index"])

    # orientate_terminal()

    # Open the Memu Multi Manager
    logger.change_status("Opening MEmu launcher")
    vm_index = start_vm(logger)
    time.sleep(10)

    skip_ads(logger, vm_index)
    start_clash_royale(logger, vm_index)

    wait_for_clash_main_menu(logger)

    # increment restart counter
    logger.add_restart()


def start_clash_royale(logger, vm_index):
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


def skip_ads(logger, vm_index):
    # Method for skipping the memu ads that popip up when you start memu

    logger.change_status("Skipping ads")
    for _ in range(4):
        pmc.trigger_keystroke_vm("home", vm_index=vm_index)
        time.sleep(1)


def close_vm(logger, vm_index):
    # Method to close memu
    logger.change_status("Closing VM")
    pmc.stop_vm(vm_index)
    logger.change_status("VM closed")


# method to move a given window to the top left of the screen
# def move_window_to_top_left(window_name):
#     # print("Moving", window_name, "to top left")
#     try:
#         window = pygetwindow.getWindowsWithTitle(window_name)[0]
#     except:
#         print("Window not found")
#         return
#     # print(window)
#     window.moveTo(0, 0)
