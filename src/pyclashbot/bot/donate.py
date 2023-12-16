"""
This module contains functions related to donating cards in Clash of Clans.
"""
import time

from pyclashbot.bot.nav import check_if_on_clash_main_menu,get_to_clan_tab_from_clash_main
from pyclashbot.detection.image_rec import (
    find_references,
    get_file_count,
    get_first_location,
    make_reference_image_list,
)
from pyclashbot.memu.client import screenshot, click, scroll_up_a_little, scroll_up
from pyclashbot.utils.logger import Logger


def donate_cards_state(vm_index, logger:Logger, next_state):
    """
    This function represents the state of donating cards in Clash of Clans.

    Args:
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object for logging.
        next_state: The next state to transition to.
    """
    logger.add_donate_attempt()

    donate_start_time = time.time()
    # if not on clash main, reutrn False
    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.log("Not on clash main for donate state. Returning False")
        return "restart"

    if donate_cards_main(vm_index, logger) is False:
        logger.log("Failure donating cards. Returning false")
        return "restart"

    time_taken = str(time.time() - donate_start_time)[:4]
    logger.change_status(f'Finished donating cards in {time_taken}s')

    return next_state


def donate_cards_main(vm_index, logger):
    """
    This function represents the main logic for donating cards in Clash of Clans.

    Args:
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object for logging.
    """
    # existing code...
    # get to clan chat page
    if get_to_clan_tab_from_clash_main(vm_index, logger) == "restart":
        logger.log("Failure getting to clan chat page for donate. Returning False")
        return False

    # click 'jump to beginning' button in clan chat
    click(vm_index, 389, 490)
    time.sleep(1)

    # for 3 iterations:
    logger.change_status('Donating cards...')
    for _ in range(3):
        # click available donates
        find_and_click_donates_for_period(vm_index, period=7)

        # scroll up a little
        scroll_up_a_little(vm_index)

    # for 2 iterations:
    for _ in range(2):
        # click available donates
        find_and_click_donates_for_period(vm_index, period=7)

        # scroll up a little
        scroll_up(vm_index)

    #click 'more donates' button
    for _ in range(2):
        click(vm_index, 38,129)
        time.sleep(1)
        find_and_click_donates_for_period(vm_index, period=7)

    # return to clash main from clan chat
    logger.change_status('Done donating. Returning to clash main...')
    click(vm_index, 175, 605)
    time.sleep(4)

    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.log("Not on clash main after donating. Returning False")
        return False

    return True


def find_and_click_donates_for_period(vm_index, period):
    """
    Find and click on available donates for a specified period of time.

    Args:
        vm_index (int): The index of the virtual machine.
        period (int): The period of time to search for available donates.

    Returns:
        None
    """
    start_time = time.time()
    while time.time() - start_time < period:
        coord = find_donate_button(vm_index)
        if coord is None:
            continue
        click(vm_index, coord[0] + 40, coord[1] + 24)


def find_donate_button(vm_index):
    """method to find the elixer price icon in a cropped image"""

    folder = "donate_button_icon"

    names = make_reference_image_list(get_file_count(folder))

    locations: list[list[int] | None] = find_references(
        screenshot(vm_index),
        folder,
        names,
        tolerance=0.92,
    )
    coord: list[int] | None = get_first_location(locations)

    if coord is None:
        return None

    return [coord[1], coord[0]]


if __name__ == "__main__":
    pass
