"""
This module contains functions related to donating cards in Clash of Clans.
"""
import time
import random

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_clan_tab_from_clash_main,
    handle_trophy_reward_menu,
    check_for_trophy_reward_menu,
)
from pyclashbot.detection.image_rec import (
    find_references,
    get_file_count,
    get_first_location,
    make_reference_image_list,
    pixel_is_equal,
    crop_image,
    condense_coordinates,
)
from pyclashbot.memu.client import screenshot, click, scroll_up
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


def donate_cards_main(vm_index, logger: Logger) -> bool:
    # get to clan chat page
    logger.change_status("Getting to clan tab to donate cards")
    if get_to_clan_tab_from_clash_main(vm_index, logger) is False:
        return False
    time.sleep(2)

    # click jump to bottom button
    click(vm_index, 385, 488)
    time.sleep(2)

    logger.change_status("Starting donate sequence")
    for _ in range(2):
        # click donate buttons that exist on this page, then scroll a little
        for _ in range(3):
            loops = 0
            while find_and_click_donates(vm_index, logger) is True:
                logger.change_status("Found a donate button")
                loops += 1
                if loops > 50:
                    return False
                time.sleep(0.5)

            logger.change_status("Scrolling up to search for more donate requests")
            scroll_up(vm_index)
            time.sleep(1)

        # click the more requests button that may exist
        click(vm_index, 48, 132)
        time.sleep(1)

        # click deadspace
        click(vm_index, 10, 233)
        time.sleep(0.33)

    # get to clash main
    logger.change_status("Returning to clash main after donating")
    click(vm_index, 175, 600, clicks=3)
    time.sleep(5)

    # handle geting stuck on trophy road screen
    if check_for_trophy_reward_menu(vm_index):
        handle_trophy_reward_menu(vm_index, logger)
        time.sleep(2)

    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.log("Failed to get to clash main after doanting! Retsrating")
        return False
    time.sleep(3)

    return True


def find_and_click_donates(vm_index, logger):
    logger.change_status("Searching for donate buttons...")
    coords = find_donate_buttons(vm_index)

    found_donates = False
    start_time = time.time()
    timeout = 30  # s
    for coord in coords:
        # if coord is too high
        if coord[1] < 108:
            print("Found a donate button but its too high to do anything with")
            continue

        # if coord is in range, click it until its grey
        while check_for_positive_donate_button_coords(vm_index, coord):
            # timeout check
            if time.time() - start_time > timeout:
                logger.change_status("Timed out while donating... Restarting")
                return "restart"

            # do clicking, increment counter, toggle found_donates
            click(vm_index, coord[0], coord[1])
            logger.change_status("Donated a card!")
            found_donates = True
            logger.add_donate()
            time.sleep(0.5)

    return found_donates


def find_donate_buttons(vm_index):
    start_time = time.time()
    coords = []

    for _ in range(100):
        try:
            left = random.randint(0, 360)
            top = random.randint(0, 400)
            width = random.randint(75, 150)
            height = random.randint(30, 100)
            region = [left, top, width, height]

            image = screenshot(vm_index)
            image = crop_image(image, region)

            coord = find_donate_button(image)

            if coord is None:
                continue

            coord = [coord[0] + left, coord[1] + top]

            # adjust coord to make it more central to the icon
            coord = [coord[0] + 37, coord[1] + 3]

            coords.append(coord)
        except:
            pass

    print(f"Finished find_donate_buttons() in {str(time.time() - start_time):5}s")
    return condense_coordinates(coords, distance_threshold=15)


def find_donate_button(image):
    """method to find the elixer price icon in a cropped image"""

    folder = "donate_button_icon"

    names = make_reference_image_list(get_file_count(folder))

    locations: list[list[int] | None] = find_references(
        image,
        folder,
        names,
        tolerance=0.96,
    )

    coord = get_first_location(locations)

    if coord is None:
        return None

    return [coord[1], coord[0]]


def check_for_positive_donate_button_coords(vm_index, coord):
    # if pixel is too high, always return False

    iar = screenshot(vm_index)

    positive_color = [58, 228, 73]

    pixels = []
    region_width = 50
    region_height = 50
    c1 = [int(coord[0] - region_width / 2), int(coord[1] - region_height / 2)]
    for x in range(region_width):
        for y in range(region_height):
            pixels.append(iar[c1[1] + y, c1[0] + x])

    positive_count = 0
    for pixel in pixels:
        if pixel_is_equal(pixel, positive_color, tol=20):
            positive_count += 1

    if (positive_count) > 5:
        return True
    return False


if __name__ == "__main__":
    vm_index = 12
    # scroll_up(vm_index)
    time.sleep(1)

    # click deadspace after scroll
