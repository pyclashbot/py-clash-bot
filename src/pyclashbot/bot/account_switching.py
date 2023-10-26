from pyclashbot.bot.nav import check_if_on_clash_main_menu, wait_for_clash_main_menu
from pyclashbot.memu.client import click, save_screenshot
import time

SSID_COORDS = [
    (48, 305),
    (48, 387),
    (53, 471),
    (48, 553),
]


def switch_accounts(vm_index, logger, account_index_to_switch_to):
    # if not on clash main, return False
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status("293587 Not on clash main to do account switching")
        return False

    # click options burger
    click(vm_index, 386, 66)
    time.sleep(2)

    # click switch SSID button
    click(vm_index, 221, 368)
    time.sleep(4)

    # click the account index in question
    account_coord = SSID_COORDS[account_index_to_switch_to]
    click(vm_index, account_coord[0], account_coord[1])
    time.sleep(4)

    if wait_for_clash_main_menu(vm_index, logger) is False:
        return False

    return True


if __name__ == "__main__":
    save_screenshot(0)
