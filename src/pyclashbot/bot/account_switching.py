from pyclashbot.bot.nav import check_if_on_clash_main_menu, wait_for_clash_main_menu
from pyclashbot.memu.client import click, save_screenshot, send_swipe
import time

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

def custom_swipe(vm_index, start_x, start_y, end_x, end_y, repeat, delay):
    for _ in range(repeat):
        send_swipe(vm_index, start_x, start_y, end_x, end_y)
        time.sleep(delay)

def switch_accounts(vm_index, logger, account_index_to_switch_to):
    logger.add_switch_account_attempt()

    # if not on clash main, return False
    if not check_if_on_clash_main_menu(vm_index):
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

    # Perform the scrolling
    logger.change_status(f"Scrolling down to reach account #{account_index_to_switch_to}")
    if account_index_to_switch_to == 5:  # 6th account
        custom_swipe(vm_index, 215, 400, 215, 350, 2, 1)
    elif account_index_to_switch_to == 6:  # 7th account
        custom_swipe(vm_index, 215, 400, 215, 350, 4, 1)
    elif account_index_to_switch_to == 7:  # 8th account
        custom_swipe(vm_index, 215, 400, 215, 350, 6, 1)
        #send_swipe(vm_index, 215, 631, 215, 10)
        #time.sleep(2)

    # click the account index in question
    account_coord = SSID_COORDS[account_index_to_switch_to]
    logger.change_status(
        f"Clicking {account_coord}, switch account #{account_index_to_switch_to}"
    )
    click(vm_index, account_coord[0], account_coord[1])
    time.sleep(4)

    logger.change_status("Waiting for clash main on new account...")
    if wait_for_clash_main_menu(vm_index, logger) is False:
        return False

    logger.change_status(f"Switched to account #{account_index_to_switch_to}")
    return True


if __name__ == "__main__":
    save_screenshot(0)
