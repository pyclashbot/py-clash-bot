import time
import numpy
from bot.navigation import (
    check_if_on_clash_main_burger_button_options_menu,
    check_if_on_clash_main_menu,
    wait_for_clash_main_burger_button_options_menu,
    wait_for_clash_main_menu,
    wait_for_switch_accounts_page,
)
from detection.image_rec import pixel_is_equal, region_is_color
from memu.client import click, screenshot
from utils.logger import Logger

CLASH_MAIN_OPTIONS_BURGER_BUTTON = (365, 62)
SWITCH_ACCOUNTS_BUTTON = (198, 371)
ACCOUNT_1_COORD = (166, 312)
ACCOUNT_2_COORD = (171, 384)


def switch_account_state(
    vm_index, logger, account_index_to_switch_to, account_switch_order
):
    NEXT_STATE = "open_chests"

    logger.log("Switch Account State")

    if not check_if_on_clash_main_menu(vm_index):
        logger.log("Error 597623485 Not on Clash main to begin switch account state")
        return "restart", account_index_to_switch_to

    # get to clash main burger options button
    logger.log("Clicking clash main options buttons")
    click(
        vm_index,
        CLASH_MAIN_OPTIONS_BURGER_BUTTON[0],
        CLASH_MAIN_OPTIONS_BURGER_BUTTON[1],
    )
    if wait_for_clash_main_burger_button_options_menu(vm_index, logger) == "restart":
        logger.log(
            "Error 547625624572457 Waited too long for calsh main burger button options menu, restarting vm"
        )
        return "restart", account_index_to_switch_to

    # if switch accounts button dosnt exist return to main and return
    if not check_for_switch_account_button(vm_index):
        logger.log("Cant switch accounts bc only one account is logged in")
        click(vm_index, 15, 300)
        time.sleep(1)

        if not check_if_on_clash_main_menu(vm_index):
            logger.log(
                "Error 87365345745 Not on Clash main to begin switch account state"
            )
            return "restart", account_index_to_switch_to
        return NEXT_STATE, account_index_to_switch_to

    # click switch accounts button
    logger.log("Clicking switch accounts button")
    click(vm_index, SWITCH_ACCOUNTS_BUTTON[0], SWITCH_ACCOUNTS_BUTTON[1])
    if wait_for_switch_accounts_page(vm_index, logger) == "restart":
        return "restart", account_index_to_switch_to

    # click the correct account
    logger.log("clicking the right account")
    if account_switch_order[account_index_to_switch_to] == 0:
        click(vm_index, ACCOUNT_1_COORD[0], ACCOUNT_1_COORD[1])
    elif account_index_to_switch_to == 1:
        click(vm_index, ACCOUNT_2_COORD[0], ACCOUNT_2_COORD[1])

    # cycle the account_index_to_switch_to
    account_index_to_switch_to += 1
    if len(account_switch_order) == account_index_to_switch_to:
        account_index_to_switch_to = 0

    # wait for main
    if wait_for_clash_main_menu(vm_index, logger) == "restart":
        logger.log(
            f"Error 3452566345 Waited too long for clash main menu, restarting vm"
        )
        return "restart", account_index_to_switch_to

    return NEXT_STATE, account_index_to_switch_to


def check_for_switch_account_button(vm_index):
    start_time = time.time()

    if not region_is_color(vm_index, region=[204, 357, 6, 4], color=(104, 187, 255)):
        return False

    if not region_is_color(vm_index, region=[181, 381, 6, 4], color=(76, 174, 255)):
        return False

    iar = numpy.asarray(screenshot(vm_index))
    if not pixel_is_equal(iar[375][193], [255, 255, 255], tol=30):
        return False
    if not pixel_is_equal(iar[363][199], [255, 255, 255], tol=30):
        return False
    if not pixel_is_equal(iar[376][203], [255, 255, 255], tol=30):
        return False

    time_taken = time.time() - start_time


    return True


if __name__ == "__main__":
    pass
