import sys
import time

from pymemuc import PyMemuc

from pyclashbot.clashmain import wait_for_clash_main_menu
from pyclashbot.client import orientate_memu, orientate_terminal
from pyclashbot.dependency import setup_memu
from pyclashbot.layout import show_clash_royale_setup_gui

launcher_path = setup_memu()  # setup memu, install if necessary
pmc = PyMemuc()


def configure_vm(logger, vm_index):
    logger.change_status("Configuring VM")
    pmc.set_configuration_vm("is_customed_resolution", "1", vm_index=vm_index)
    pmc.set_configuration_vm("resolution_width", "460", vm_index=vm_index)
    pmc.set_configuration_vm("resolution_height", "680", vm_index=vm_index)
    pmc.set_configuration_vm("vbox_dpi", "160", vm_index=vm_index)
    pmc.set_configuration_vm(
        "start_window_mode", "1", vm_index=vm_index
    )  # set to remember window location


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

    orientate_terminal()

    # Open the Memu Multi Manager
    logger.change_status("Opening MEmu launcher")
    vm_index = start_vm(logger)
    time.sleep(10)
    orientate_memu()
    skip_ads(logger, vm_index)
    start_clash_royale(logger, vm_index)

    if wait_for_clash_main_menu(logger) == "restart":
        restart_and_open_clash(logger)
    time.sleep(3)

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
