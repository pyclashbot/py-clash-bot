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
    (48, 305),  # 1st account, index 0
    (48, 387),  # 2nd account, index 1
    (48, 471),  # 3rd account, index 2
    (48, 553),  # 4th account, index 3
    (48, 631),  # 5th account, index 4
    (48, 631),  # 6th account, index 5
    (48, 631),  # 7th account, index 6
    (48, 631),  # 8th account, index 7
]


def switch_accounts(vm_index: int, logger: Logger, account_index_to_switch_to):
    logger.add_switch_account_attempt()

    # if not on clash main, return False
    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status("293587 Not on clash main to do account switching")
        return False

    # click options burger
    logger.change_status("Opening clash main options menu")
    click(vm_index, 386, 66)
    time.sleep(3)

    # click switch SSID button
    logger.change_status("Clicking switch SSID button")
    click(vm_index, 221, 368)
    time.sleep(4)

    # wait for switch ssid page
    # wait_for_switch_ssid_page(vm_index, logger)
    # time.sleep(10)

    # Perform the scrolling
    if account_index_to_switch_to in [5, 6, 7]:
        logger.change_status(
            f"Scrolling down to reach account #{account_index_to_switch_to}"
        )
        if account_index_to_switch_to == 5:  # 6th account
            custom_swipe(vm_index, 215, 400, 215, 350, 2, 1)
        elif account_index_to_switch_to == 6:  # 7th account
            custom_swipe(vm_index, 215, 400, 215, 350, 4, 1)
        elif account_index_to_switch_to == 7:  # 8th account
            custom_swipe(vm_index, 215, 400, 215, 350, 6, 1)

    # click the account index in question
    account_coord = SSID_COORDS[account_index_to_switch_to]
    logger.change_status(f"Clicking account index #{account_index_to_switch_to}")
    click(vm_index, account_coord[0], account_coord[1], clicks=3, interval=0.33)
    logger.change_status(f"Selected account #{account_index_to_switch_to}")

    time.sleep(6)

    logger.change_status("Waiting for clash main on new account...")
    if wait_for_clash_main_menu(vm_index, logger) is False:
        return False
    time.sleep(4)

    if check_for_trophy_reward_menu(vm_index):
        handle_trophy_reward_menu(vm_index, logger, printmode=False)
        time.sleep(2)

    logger.change_status(f"Switched to account #{account_index_to_switch_to}")
    # Reset logger's in_a_clan value
    logger.update_in_a_clan_value(False)
    logger.increment_account_switches()
    return True


if __name__ == "__main__":
    vm_index = 12
    logger = Logger()

    my_list = [
        "matthew",
        "PY-CLASHBOT#1",
        "PY-CLASHBOT#3",
        "PY-CLASHBOT#4",
        "PY-CLASHBOT#7",
        "PY-CLASHBOT#10",
        "PY-CLASHBOT#11",
        "PY-CLASHBOT#12",
    ]

    for i, name in enumerate(my_list):
        print(f"Switching to name: {name} at index: {i}")
        switch_accounts(vm_index, logger, i)
        input(f"Is this {name}?")

    # switch_accounts(vm_index, logger, 4)

