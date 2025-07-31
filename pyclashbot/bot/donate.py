"""This module contains functions related to donating cards in Clash of Clans."""

import random
import time
from typing import Literal

import numpy

from pyclashbot.bot.nav import (
    check_for_trophy_reward_menu,
    check_if_on_clash_main_menu,
    get_to_clan_tab_from_clash_main,
    get_to_profile_page,
    handle_trophy_reward_menu,
    wait_for_clash_main_menu,
)
from pyclashbot.detection.image_rec import (
    condense_coordinates,
    crop_image,
    find_references,
    get_file_count,
    get_first_location,
    make_reference_image_list,
    pixel_is_equal,
)
from pyclashbot.utils.logger import Logger

CLASH_MAIN_DEADSPACE_COORD = (20, 520)


def find_claim_button(vm_index):
    """Finds the location of the claim button for the free gift in the clan page.

    Args:
    ----
        vm_index (int): The index of the virtual machine to search for the claim button.

    Returns:
    -------
        list[int] or None: The coordinates of the claim button if found, or None if not found.

    """
    folder_name = "claim_clan_button"
    size = get_file_count(folder_name)
    names = make_reference_image_list(size)

    locations = find_references(
        screenshot(vm_index),
        folder_name,
        names,
        0.79,
    )

    coord = get_first_location(locations)
    if coord is not None:
        return [coord[1], coord[0]]  # Return coordinates

    return None


def donate_cards_state(vm_index, logger: Logger, next_state, free_donate_toggle: bool):
    """This function represents the state of donating cards in Clash of Clans.

    Args:
    ----
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object for logging.
        next_state: The next state to transition to.

    """

    donate_start_time = time.time()

    # if not on main: return
    clash_main_check = check_if_on_clash_main_menu(emulator)
    if clash_main_check is not True:
        logger.change_status("Not on clash main for the start of request_state()")
        logger.log("These are the pixels the bot saw after failing to find clash main:")
        # for pixel in clash_main_check:
        #     logger.log(f"   {pixel}")

        return "restart"

    # if logger says we're not in a clan, check if we are in a clan
    if logger.is_in_clan() is False:
        logger.change_status("Checking if in a clan before donating")
        in_a_clan_return = donate_state_check_if_in_a_clan(vm_index, logger)
        if in_a_clan_return == "restart":
            logger.change_status(
                status="Error 05708425 Failure with check_if_in_a_clan",
            )
            return "restart"

        if not in_a_clan_return:
            return next_state
    else:
        print(f"Logger's in_a_clan value is: {logger.is_in_clan()} so skipping check")

    # if in a clan, update logger's in_a_clan value
    logger.update_in_a_clan_value(True)
    print(f"Set Logger's in_a_clan value to: {logger.is_in_clan()}!")

    # run donate cards main
    if (
        donate_cards_main(vm_index, logger, only_free_donates=free_donate_toggle)
        is False
    ):
        logger.log("Failure donating cards. Returning false")
        return "restart"

    # print time taken
    time_taken = str(time.time() - donate_start_time)[:4]
    logger.change_status(f"Finished donating cards in {time_taken}s")

    # return next state
    return next_state


def donate_state_check_pixels_for_clan_flag(vm_index) -> bool:
    iar = numpy.asarray(screenshot(vm_index))  # type: ignore  # noqa: PGH003

    pix_list = []
    for x_coord in range(80, 96):
        pixel = iar[445][x_coord]
        pix_list.append(pixel)

    for y_coord in range(437, 453):
        pixel = iar[y_coord][88]
        pix_list.append(pixel)

    # for every pixel in the pix_list: format to be of format [r,g,b]
    for index, pix in enumerate(pix_list):
        pix_list[index] = [pix[0], pix[1], pix[2]]

    for pix in pix_list:
        total = int(pix[0]) + int(pix[1]) + int(pix[2])

        if total < 130:
            return True

        if total > 170:
            return True

    return False


def donate_state_check_if_in_a_clan(
    vm_index,
    logger: Logger,
) -> bool | Literal["restart"]:
    # if not on clash main, return
    if check_if_on_clash_main_menu(emulator) is not True:
        logger.change_status(status="ERROR 385462623 Not on clash main menu")
        return "restart"

    # get to profile page
    if get_to_profile_page(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 9076092860923485 Failure with get_to_profile_page",
        )
        return "restart"

    # check pixels for in a clan
    in_a_clan = donate_state_check_pixels_for_clan_flag(vm_index)

    # print clan status
    if not in_a_clan:
        logger.change_status("Not in a clan, so can't request!")

    # click deadspace to leave
    emulator.click(CLASH_MAIN_DEADSPACE_COORD[0], CLASH_MAIN_DEADSPACE_COORD[1])
    if wait_for_clash_main_menu(vm_index, logger) is False:
        logger.change_status(
            status="Error 87258301758939 Failure with wait_for_clash_main_menu",
        )
        return "restart"

    return in_a_clan


def donate_cards_main(vm_index, logger: Logger, only_free_donates: bool) -> bool:
    # get to clan chat page
    logger.change_status("Getting to clan tab to donate cards")
    if get_to_clan_tab_from_clash_main(vm_index, logger) is False:
        return False

    # click jump to bottom button
    emulator.click(385, 488)
    time.sleep(2)

    logger.change_status("Starting donate sequence")
    for _ in range(2):
        # click donate buttons that exist on this page, then scroll a little
        for _ in range(3):
            loops = 0
            # Try to claim free gift if available
            claim_button_coord = find_claim_button(vm_index)
            if claim_button_coord:
                logger.log("Claim button found. Claiming free gift from clan mate.")
                emulator.click(*claim_button_coord)
                time.sleep(3)
            while find_and_click_donates(vm_index, logger, only_free_donates) is True:
                logger.change_status("Found a donate button")
                loops += 1
                if loops > 50:
                    return False
                time.sleep(0.5)

            logger.change_status("Scrolling up...")
            scroll_up(vm_index)
            time.sleep(1)

        # click the more requests button that may exist
        emulator.click(48, 132)
        time.sleep(1)

        # click deadspace
        emulator.click(10, 233)
        time.sleep(0.33)

    # get to clash main
    logger.change_status("Returning to clash main after donating")
    emulator.click(175, 600, clicks=1)
    time.sleep(5)

    # handle geting stuck on trophy road screen
    if check_for_trophy_reward_menu(emulator):
        handle_trophy_reward_menu(emulator, logger)
        time.sleep(2)

    if check_if_on_clash_main_menu(emulator) is not True:
        logger.log("Failed to get to clash main after doanting! Retsrating")
        return False
    time.sleep(3)

    return True


def find_and_click_donates(vm_index, logger, only_free_donates):
    logger.change_status("Searching for donate buttons...")
    coords = find_donate_buttons(vm_index, only_free_donates)

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
            emulator.click(coord[0], coord[1])
            logger.change_status("Donated a card!")
            found_donates = True
            logger.add_donate()
            time.sleep(0.5)

    return found_donates


def region_contains_donate_button(image, region):
    # print(f'checking if region: {region} has green')
    l, t, w, h = region  # noqa: E741
    y_range = (t, t + h)
    x_coord = 343
    green_color = [73, 228, 58]
    for i in range(y_range[0], y_range[1]):
        pixel = image[i, x_coord]
        # print(f'Region: {region} saw pixel: {pixel}')
        if pixel_is_equal(pixel, green_color, tol=5):
            # print(f'Region has green')
            return True

    # print(f'Region: {region} does not have green')
    return False


def find_donate_buttons(vm_index, only_free_donates):
    start_time = time.time()
    coords = []

    look_time = 1  # s
    looks = 0

    look_start_time = time.time()
    base_image = screenshot(vm_index)
    while time.time() - look_start_time < look_time:
        looks += 1
        try:
            # calculate a random roi this search try, grab image
            left = 238
            right = 375
            top = 80
            bottom = 475
            t = random.randint(top, bottom)
            width = right - left
            region = [left, t, width, 100]  # [x,y,w,h]
            roi_image = crop_image(base_image, region)

            # pixel check to see if region even has green
            if region_contains_donate_button(base_image, region) is False:
                continue

            # find one donate button in the roi image
            coord = find_donate_button(roi_image)
            if coord is None:
                continue

            # if only_free_donates is enabled, assure free_button_exists
            if (
                only_free_donates
                and coord is not None
                and not free_button_exists(vm_index, coord, region)
            ):
                # if not free_button_exists retry
                continue

            # convert ROI coord to usable coord
            coord = [coord[0] + region[0], coord[1] + region[1]]

            # adjust coord to make it more central to the icon
            coord = [coord[0] + 37, coord[1] + 3]

            coords.append(coord)
        except:  # noqa: E722
            pass

    # remove dupes from coords list
    coords = condense_coordinates(coords, distance_threshold=15)

    # time taken printout
    str(time.time() - start_time)[:5]
    # print(f"Finished find_donate_buttons() in {time_taken}s")
    # print(f"Found {len(coords)} donate buttons in {looks} looks")

    return coords


def free_button_exists(vm_index, coord, region):
    """Method to find the donate icon for FREE in a cropped image"""
    # grab ROI image
    x = coord[1] + region[0]
    y = coord[0] + region[1]
    roi_region = [x - 200, y - 30, 120, 60]
    roi_image = screenshot(vm_index)
    roi_image = crop_image(roi_image, roi_region)

    # find first occurence of free image in ROI image
    folder = "free_donate_icon"
    names = make_reference_image_list(get_file_count(folder))
    locations: list[list[int] | None] = find_references(
        roi_image,
        folder,
        names,
        tolerance=0.80,
    )
    free_coord = get_first_location(locations)

    # return first coord else None
    return [coord[1], coord[0]] if free_coord is not None else None


def find_donate_button(image):
    """Method to find the donate icon in a cropped image"""
    folder = "donate_button_icon"

    names = make_reference_image_list(get_file_count(folder))

    locations: list[list[int] | None] = find_references(
        image,
        folder,
        names,
        tolerance=0.80,
    )

    coord = get_first_location(locations)

    if coord is None:
        return None

    return [coord[1], coord[0]]


def check_for_positive_donate_button_coords(vm_index, coord):
    # if pixel is too high, always return False

    iar = emulator.screenshot()

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
    coords = find_donate_buttons(0, False)
    print("\n")
    for i, coord in enumerate(coords):
        print(i, coord)
