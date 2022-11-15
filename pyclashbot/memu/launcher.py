import time
from typing import Any

from pymemuc import PyMemuc, PyMemucError, VMInfo

from pyclashbot.bot.clashmain import wait_for_clash_main_menu
from pyclashbot.interface import show_clash_royale_setup_gui
from pyclashbot.utils import setup_memu
from pyclashbot.utils.logger import Logger

launcher_path = setup_memu()  # setup memu, install if necessary
pmc = PyMemuc(debug=True)


def configure_vm(logger: Logger, vm_index):

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


def create_vm(logger: Logger):

    # create a vm named pyclashbot
    logger.change_status("VM not found, creating VM...")
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

    # delete all vms except the lowest index
    if len(vm_indices) > 1:
        for vm_index in vm_indices[1:]:
            pmc.delete_vm(vm_index)

    # return the index. if no vms named pyclashbot exist, create one.
    return vm_indices[0] if vm_indices else create_vm(logger)


def start_vm(logger: Logger):
    # Method for starting the memu client
    logger.change_status("Starting Memu Client")
    vm_index = check_for_vm(logger)
    configure_vm(logger, vm_index)
    logger.change_status("Starting VM...")
    pmc.start_vm(vm_index=vm_index)
    logger.change_status("VM Started")
    # move_window_to_top_left("pyclashbot")

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

    vm_index = restart_memu(logger)
    start_clash_royale(logger, vm_index)
    time.sleep(10)
    wait_for_clash_main_menu(logger)

    global first_run  # pylint: disable=global-statement
    if first_run:
        first_run = False
    else:
        logger.add_restart()


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
