import math
import random
import time
from typing import Any, Literal

import numpy

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_clan_tab_from_clash_main,
    get_to_clash_main_from_clan_page,
    get_to_profile_page,
    wait_for_clash_main_menu,
)
from pyclashbot.detection.image_rec import (
    check_line_for_color,
    find_references,
    get_file_count,
    get_first_location,
    make_reference_image_list,
    pixel_is_equal,
    region_is_color,
)
from pyclashbot.memu.client import click, screenshot, scroll_down, scroll_up
from pyclashbot.utils.logger import Logger

COLOR_WHITE: list[int] = [255, 255, 255]
YELLOW_1: list[int] = [255, 203, 85]
YELLOW_2: list[int] = [255, 190, 43]

REQUEST_BUTTON_COORD_LIST = {
    "1": [
        (100, 353),
        (163, 353),
        (240, 353),
        (330, 353),
    ],
    "2": [
        (100, 493),
        (163, 493),
        (240, 493),
        (330, 493),
    ],
    "3": [
        (100, 521),
        (163, 521),
        (240, 521),
        (330, 521),
    ],
}


def find_request_button(vm_index):
    """
    Finds the location of the request button on the screen.

    Args:
        vm_index (int): The index of the virtual machine to search for the request button.

    Returns:
        list[int] or None: The coordinates of the request button if found, or None if not found.
    """
    folder_name = "request_button"

    size: int = get_file_count(folder_name)

    names = make_reference_image_list(size)

    locations = find_references(
        screenshot(vm_index),
        folder_name,
        names,
        0.88,
    )

    coord = get_first_location(locations)
    if coord is None:
        return None
    return [coord[1], coord[0]]


def request_state(vm_index, logger: Logger, next_state: str) -> str:
    """
    The request state of the bot. This state is responsible for checking if the bot is in a clan,
    checking if a request can be made, and making a request if possible.

    Args:
        vm_index (int): The index of the virtual machine to run the bot on.
        logger (Logger): The logger object to log messages to.
        next_state (str): The next state to transition to after this state is complete.

    Returns:
        str: The next state to transition to after this state is complete.
    """
    logger.change_status(status="Request state")
    logger.add_request_attempt()

    # if not on main: return
    clash_main_check = check_if_on_clash_main_menu(vm_index)
    if clash_main_check is not True:
        logger.change_status("Not on clash main for the start of request_state()")
        logger.log(f'There are the pixels the bot saw after failing to find clash main:')
        for pixel in clash_main_check:
            logger.log('   ',pixel)

        return "restart"

    # if not in a clan, return
    in_a_clan_return = request_state_check_if_in_a_clan(vm_index, logger)
    if in_a_clan_return == "restart":
        logger.change_status(status="Error 05708425 Failure with check_if_in_a_clan")
        return "restart"

    if not in_a_clan_return:
        return next_state

    # get to clan page
    if get_to_clan_tab_from_clash_main(vm_index, logger) == "restart":
        logger.change_status(status="ERROR 74842744443 Not on clan tab")
        return "restart"

    logger.update_time_of_last_request(time.time())

    # check if request exists
    if check_if_can_request_wrapper(vm_index):
        # do request
        if not do_request(vm_index, logger):
            return "restart"
    else:
        logger.change_status(status="Cant request right now.")

    # return to clash main
    if get_to_clash_main_from_clan_page(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 876208476 Failure with get_to_clash_main_from_clan_page"
        )
        return "restart"

    return next_state


def do_random_scrolling_in_request_page(vm_index, logger, scrolls) -> None:
    logger.change_status(status="Doing random scrolling in request page")
    for _ in range(scrolls):
        scroll_down(vm_index)
        time.sleep(2)
    logger.change_status(status="Done with random scrolling in request page")


def count_scrolls_in_request_page(vm_index) -> int:
    # scroll down, counting each scroll, until cant scroll anymore
    scrolls = 0
    while check_if_can_scroll_in_request_page(vm_index):
        scroll_down(vm_index)
        scrolls += 1
        time.sleep(2)

    # scroll back to top
    for _ in range(14):
        scroll_up(vm_index)
        time.sleep(0.1)

    return scrolls


def check_if_can_scroll_in_request_page(vm_index) -> bool:
    if not region_is_color(vm_index, region=[64, 500, 293, 55], color=(222, 235, 241)):
        return True
    return False


def request_state_check_if_in_a_clan(
    vm_index, logger: Logger
) -> bool | Literal["restart"]:
    # if not on clash main, reutnr
    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status(status="ERROR 385462623 Not on clash main menu")
        return "restart"

    # get to profile page
    if get_to_profile_page(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 9076092860923485 Failure with get_to_profile_page"
        )
        return "restart"

    time.sleep(1)
    # check pixels for in a clan
    in_a_clan = request_state_check_pixels_for_clan_flag(vm_index)

    # print clan status
    if not in_a_clan:
        logger.change_status("Not in a clan, so can't request!")

    # click deadspace to leave
    click(vm_index, 15, 300)
    if wait_for_clash_main_menu(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 87258301758939 Failure with wait_for_clash_main_menu"
        )
        return "restart"

    return in_a_clan


def request_state_check_pixels_for_clan_flag(vm_index) -> bool:
    iar = numpy.asarray(screenshot(vm_index))  # type: ignore

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


def do_request(vm_index, logger: Logger) -> None:
    logger.change_status(status="Doing request")

    # click request button
    logger.change_status(status="Clicking request button")
    click(vm_index=vm_index, x_coord=77, y_coord=536)
    time.sleep(3)

    # max scrolls
    logger.change_status(status="Counting the maximum scrolls in the request page")
    max_scrolls: int = count_scrolls_in_request_page(vm_index=vm_index)
    logger.log(f"Found {max_scrolls} scrolls maximum in request page")
    random_scroll_amount: int = random.randint(a=0, b=max_scrolls)
    logger.log(f"Gonna do {random_scroll_amount} scrolls in request page")

    do_random_scrolling_in_request_page(
        vm_index=vm_index, logger=logger, scrolls=random_scroll_amount
    )

    random_click_timeout = 35  # s
    random_click_start_time = time.time()

    while 1:
        if time.time() - random_click_start_time > random_click_timeout:
            logger.change_status(
                "5913578 Clicked randomly for a random card to request too many times!"
            )
            return False

        # click card
        logger.change_status(status="Clicking random card to request")
        click(
            vm_index=vm_index,
            x_coord=random.randint(a=67, b=358),
            y_coord=random.randint(a=211, b=547),
        )
        time.sleep(3)

        logger.change_status(status="Clicking request")

        # get request button coord
        coord = find_request_button(vm_index)
        if coord is None:
            continue

        # Click request button coord
        click(vm_index, coord[0], coord[1])

        prev_requests = logger.get_requests()

        logger.add_request()

        requests = logger.get_requests()
        logger.log(f"Incremented requests stat from {prev_requests} to {requests}")

        time.sleep(3)
        break

    return True


def check_if_can_request_wrapper(vm_index):
    if check_for_trade_cards_icon(vm_index):
        return False

    if check_for_trade_cards_icon_2(vm_index):
        return False

    if check_if_can_request_3(vm_index):
        return True
    if check_if_can_request(vm_index):
        return True
    if check_if_can_request_2(vm_index):
        return True
    return False


def check_if_can_request(vm_index) -> bool:
    iar = numpy.asarray(screenshot(vm_index))

    region_is_white = True
    for x_index in range(48, 55):
        this_pixel = iar[530][x_index]
        if not pixel_is_equal([212, 228, 255], this_pixel, tol=25):
            region_is_white = False
            break

    for y_index in range(528, 535):
        this_pixel = iar[y_index][52]
        if not pixel_is_equal([212, 228, 255], this_pixel, tol=25):
            region_is_white = False
            break

    yellow_button_exists = False
    for x_index in range(106, 118):
        this_pixel = iar[542][x_index]
        if pixel_is_equal([255, 188, 42], this_pixel, tol=25):
            yellow_button_exists = True
            break

    if region_is_white and yellow_button_exists:
        return True
    return False


def check_if_can_request_2(vm_index) -> bool:
    if not check_line_for_color(vm_index, 300, 522, 300, 544, (76, 176, 255)):
        return False
    if not check_line_for_color(vm_index, 362, 522, 362, 544, (76, 174, 255)):
        return False
    if not check_line_for_color(vm_index, 106, 537, 106, 545, (255, 188, 42)):
        return False
    if not check_line_for_color(vm_index, 107, 537, 119, 545, (255, 188, 42)):
        return False
    if not check_line_for_color(vm_index, 46, 529, 57, 539, (178, 79, 244)):
        return False
    if not check_line_for_color(vm_index, 50, 540, 54, 527, (176, 79, 244)):
        return False
    return True


def check_for_trade_cards_icon(vm_index) -> bool:
    lines = [
        check_line_for_color(
            vm_index, x_1=33, y_1=502, x_2=56, y_2=502, color=(47, 69, 105)
        ),
        check_line_for_color(
            vm_index, x_1=56, y_1=507, x_2=108, y_2=506, color=(253, 253, 203)
        ),
        check_line_for_color(
            vm_index, x_1=37, y_1=515, x_2=125, y_2=557, color=(255, 188, 42)
        ),
    ]

    return all(lines)


def check_for_trade_cards_icon_2(vm_index):
    if not check_line_for_color(vm_index, 67, 524, 74, 534, (255, 255, 254)):
        return False
    if not check_line_for_color(vm_index, 90, 523, 91, 534, (255, 255, 254)):
        return False
    if not check_line_for_color(vm_index, 97, 536, 102, 543, (255, 253, 250)):
        return False

    if not region_is_color(vm_index, [50, 530, 4, 8], (212, 228, 255)):
        return False
    if not region_is_color(vm_index, [106, 523, 4, 8], (255, 200, 80)):
        return False
    if not region_is_color(vm_index, [104, 536, 12, 8], (255, 188, 42)):
        return False
    return True


def check_if_can_request_3(vm_index):
    if not region_is_color(vm_index, [48, 529, 8, 7], (216, 229, 255)):
        return False
    if not region_is_color(vm_index, [106, 538, 12, 7], (255, 188, 42)):
        return False

    return True


if __name__ == "__main__":
    pass
