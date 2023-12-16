"""
This module contains functions related to donating cards in Clash of Clans.
"""
import time

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_clan_tab_from_clash_main,
)
from pyclashbot.detection.image_rec import (
    find_references,
    get_file_count,
    get_first_location,
    make_reference_image_list,
    pixel_is_equal,
)
from pyclashbot.memu.client import screenshot, click, scroll_up_a_little, scroll_up
from pyclashbot.utils.logger import Logger


def donate_cards_state(vm_index, logger: Logger, next_state):
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
    logger.change_status(f"Finished donating cards in {time_taken}s")

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
    logger.change_status("Donating cards...")
    for _ in range(3):
        # click available donates
        find_and_click_donates_for_period(vm_index, logger, period=7)

        # scroll up a little
        scroll_up_a_little(vm_index)

    # for 2 iterations:
    for _ in range(2):
        # click available donates
        find_and_click_donates_for_period(vm_index, logger, period=7)

        # scroll up a little
        scroll_up(vm_index)

    # click 'more donates' button
    for _ in range(2):
        click(vm_index, 38, 129)
        time.sleep(1)
        find_and_click_donates_for_period(vm_index, logger, period=7)

    # return to clash main from clan chat
    logger.change_status("Done donating. Returning to clash main...")
    click(vm_index, 175, 605)
    time.sleep(4)

    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.log("Not on clash main after donating. Returning False")
        return False

    return True


def find_and_click_donates_for_period(vm_index, logger, period):
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
        find_and_click_donates(vm_index, logger)


def find_and_click_donates(vm_index, logger):
    coord = find_donate_button(vm_index)
    if coord is None:
        return False

    coord = [coord[0] + 40, coord[1] + 24]

    if check_region_for_donate_button_color(vm_index, coord):
        logger.change_status("Found a donate button")
        logger.add_donate()
        click(vm_index, coord[0], coord[1])


def check_region_for_donate_button_color(vm_index, coord):
    # specify the color of the positive donate button
    positive_color = [58, 228, 73]

    # compile coordinates to check based on coordinate of donate button
    coords_to_check = []
    for x in range(10):
        for y in range(10):
            coords_to_check.append([coord[0] + x, coord[1] + y])

    # grab a screenshot
    iar = screenshot(vm_index)

    # assemble pixel list of colors surrounding the donate button coord
    pixels = []
    for coord in coords_to_check:
        pixels.append(iar[coord[1], coord[0]])

    # count positive pixels surrounding the donate button coord
    postiive_count = 0
    for i, pixel in enumerate(pixels):
        if pixel_is_equal(pixel, positive_color, tol=20):
            postiive_count += 1

    # return True if postiive_count is great enough
    if postiive_count > 20:
        return True
    return False


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
