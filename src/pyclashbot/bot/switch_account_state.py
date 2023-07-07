import time
from typing import Literal

import numpy

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    wait_for_clash_main_burger_button_options_menu,
    wait_for_clash_main_menu,
    wait_for_switch_accounts_page,
)
from pyclashbot.detection.image_rec import pixel_is_equal, region_is_color
from pyclashbot.memu.client import click, screenshot

CLASH_MAIN_OPTIONS_BURGER_BUTTON: tuple[Literal[365], Literal[62]] = (365, 62)
SWITCH_ACCOUNTS_BUTTON: tuple[Literal[198], Literal[371]] = (198, 371)
ACCOUNT_1_COORD: tuple[Literal[166], Literal[312]] = (166, 312)
ACCOUNT_2_COORD: tuple[Literal[171], Literal[384]] = (171, 384)


def switch_account_state(
    vm_index, logger, account_index_to_switch_to, account_switch_order
):
    next_state = "open_chests"

    logger.change_status(status="Switch Account State")

    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            status="Error 597623485 Not on Clash main to begin switch account state"
        )
        return "restart", account_index_to_switch_to

    # get to clash main burger options button
    logger.change_status(status="Clicking clash main options buttons")
    click(
        vm_index,
        CLASH_MAIN_OPTIONS_BURGER_BUTTON[0],
        CLASH_MAIN_OPTIONS_BURGER_BUTTON[1],
    )
    if wait_for_clash_main_burger_button_options_menu(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 555 Waited too long for calsh main options menu, restarting vm"
        )
        return "restart", account_index_to_switch_to

    # if switch accounts button dosnt exist return to main and return
    if not check_for_switch_account_button(vm_index):
        logger.change_status(
            status="Cant switch accounts bc only one account is logged in"
        )
        click(vm_index, 15, 300)
        time.sleep(1)

        if not check_if_on_clash_main_menu(vm_index):
            logger.change_status(
                status="Error 87365345745 Not on Clash main to begin switch account state"
            )
            return "restart", account_index_to_switch_to
        return next_state, account_index_to_switch_to

    # click switch accounts button
    logger.change_status(status="Clicking switch accounts button")
    click(vm_index, SWITCH_ACCOUNTS_BUTTON[0], SWITCH_ACCOUNTS_BUTTON[1])
    if wait_for_switch_accounts_page(vm_index, logger) == "restart":
        return "restart", account_index_to_switch_to

    # click the correct account
    logger.change_status(status="clicking the right account")
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
        logger.change_status(
            status="Error 3452566345 Waited too long for clash main menu, restarting vm"
        )
        return "restart", account_index_to_switch_to

    return next_state, account_index_to_switch_to


def check_for_switch_account_button(vm_index) -> bool:
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

    return True


if __name__ == "__main__":
    pass
