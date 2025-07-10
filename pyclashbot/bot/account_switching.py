import time

from pyclashbot.bot.nav import (
    check_for_trophy_reward_menu,
    check_if_on_clash_main_menu,
    handle_trophy_reward_menu,
    wait_for_clash_main_menu,
)
from pyclashbot.memu.client import click, custom_swipe
from pyclashbot.utils.logger import Logger

SSID_COORDS = [
    (48, 376),  # 1st account, index 0
    (48, 472),  # 2nd account, index 1
    (48, 567),  # 3rd account, index 2
]


def switch_accounts(: int, logger: Logger, account_index_to_switch_to):
    # if not on clash main, return False
    if check_if_on_clash_main_menu() is not True:
        logger.change_status("293587 Not on clash main to do account switching")
        return False

    # click options burger
    logger.log("Opening clash main options menu")
    click(, 386, 66)
    time.sleep(3)

    # click switch SSID button
    logger.log("Clicking switch SSID button")
    click(, 221, 368)
    time.sleep(4)

    # click the account index in question
    account_coord = SSID_COORDS[account_index_to_switch_to]
    logger.log(f"Clicking account index #{account_index_to_switch_to}")
    click(, account_coord[0], account_coord[1], clicks=3, interval=0.33)
    logger.change_status(f"Selected account #{account_index_to_switch_to}")
    time.sleep(6)

    #wait for main page
    logger.change_status("Waiting for clash main on new account...")
    if wait_for_clash_main_menu(, logger) is False:
        return False
    time.sleep(4)
    if check_for_trophy_reward_menu():
        handle_trophy_reward_menu(, logger, printmode=False)
        time.sleep(2)

    logger.change_status(f"Switched to account #{account_index_to_switch_to}")
    logger.increment_account_switches()
    return True


if __name__ == "__main__":
     = 0
    logger = Logger()

    switch_accounts(, logger, 1)
