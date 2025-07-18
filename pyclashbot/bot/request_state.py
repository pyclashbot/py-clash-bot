import random
import time
from typing import Literal

import numpy

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_clan_tab_from_clash_main,
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
from pyclashbot.memu.client import (
    click,
    screenshot,
    scroll_down_in_request_page,
    scroll_up_on_left_side_of_screen,
)
from pyclashbot.utils.logger import Logger

CLASH_MAIN_DEADSPACE_COORD = (20, 520)


def find_request_button(vm_index, logger: Logger):
    """Finds the location of the request button on the screen.

    Args:
    ----
        vm_index (int): The index of the virtual machine to search for the request button.

    Returns:
    -------
        list[int] or None: The coordinates of the request button if found, or None if not found.

    """
    folder_name = "request_button"
    size: int = get_file_count(folder_name)
    names = make_reference_image_list(size)

    locations = find_references(
        screenshot(vm_index),
        folder_name,
        names,
        0.7,
    )

    coord = get_first_location(locations)

    # Check if coord is None before logging and returning the coordinates
    if coord is None:
        logger.log("Request button not found.")
        return None
    logger.log(f"The button coordinates were found, X: {coord[1]} Y: {coord[0]}")
    return [coord[1], coord[0]]


def request_state(vm_index, logger: Logger, next_state: str) -> str:
    """The request state of the bot. This state is responsible for checking if the bot is in a clan,
    checking if a request can be made, and making a request if possible.

    Args:
    ----
        vm_index (int): The index of the virtual machine to run the bot on.
        logger (Logger): The logger object to log messages to.
        next_state (str): The next state to transition to after this state is complete.

    Returns:
    -------
        str: The next state to transition to after this state is complete.

    """
    logger.change_status(status="Doing request state!")

    # if not on main: return
    clash_main_check = check_if_on_clash_main_menu(vm_index)
    if clash_main_check is not True:
        logger.change_status("Not on clash main for the start of request_state()")
        # logger.log(
        #     "These are the pixels the bot saw after failing to find clash main:")
        # # for pixel in clash_main_check:
        # #     logger.log(f"   {pixel}")

        return "restart"

    # if logger says we're not in a clan, check if we are in a clan
    if logger.is_in_clan() is False:
        logger.change_status("Checking if in a clan before requesting")
        in_a_clan_return = request_state_check_if_in_a_clan(vm_index, logger)
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

    # get to clan page
    logger.change_status("Getting to clan tab to request a card")
    if get_to_clan_tab_from_clash_main(vm_index, logger) is False:
        logger.change_status(status="ERROR 74842744443 Not on clan tab")
        return "restart"

    # check if request exists
    if check_if_can_request_wrapper(vm_index):
        # do request
        if not do_request(vm_index, logger):
            return "restart"
    else:
        logger.change_status(status="Can't request right now.")

    # click clash main icon
    click(vm_index, 178, 593)

    # return to clash main
    wait_for_clash_main_menu(vm_index, logger, deadspace_click=False)

    return next_state


def do_random_scrolling_in_request_page(vm_index, logger, scrolls) -> None:
    logger.change_status(status="Doing random scrolling in request page")
    # scroll up to top
    for _ in range(3):
        scroll_up_on_left_side_of_screen(vm_index)

    for _ in range(scrolls):
        scroll_down_in_request_page(vm_index)
        time.sleep(1)
    logger.change_status(status="Done with random scrolling in request page")


def count_scrolls_in_request_page(vm_index) -> int:
    # scroll up to top
    for _ in range(3):
        scroll_up_on_left_side_of_screen(vm_index)

    # scroll down, counting each scroll, until can't scroll anymore
    scrolls = 0
    timeout = 60  # s
    start_time = time.time()
    while check_if_can_scroll_in_request_page(vm_index):
        print(f"One scroll down. Count is {scrolls}")
        scroll_down_in_request_page(vm_index)
        scrolls += 1
        time.sleep(2)

        # if taken too much time, return 5
        if time.time() - start_time > timeout:
            return 5

    # close request screen with deadspace click
    click(vm_index, 15, 300, clicks=3)
    time.sleep(0.1)

    # reopen request page
    click(vm_index=vm_index, x_coord=77, y_coord=536)
    time.sleep(0.1)

    return scrolls


def check_if_can_scroll_in_request_page(vm_index) -> bool:
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[533][58],
        iar[533][63],
        iar[533][60],
        iar[533][90],
        iar[533][120],
        iar[533][150],
        iar[533][180],
        iar[533][210],
        iar[533][240],
        iar[533][270],
        iar[533][300],
        iar[529][337],
    ]
    colors = [
        [241, 235, 222],
        [241, 235, 222],
        [241, 235, 222],
        [241, 235, 222],
        [241, 235, 222],
        [241, 235, 222],
        [241, 235, 222],
        [241, 235, 222],
        [241, 235, 222],
        [241, 235, 222],
        [241, 235, 222],
        [241, 235, 222],
    ]

    for i, c in enumerate(colors):
        if not pixel_is_equal(c, pixels[i], tol=10):
            return True
    return False


def request_state_check_if_in_a_clan(
    vm_index,
    logger: Logger,
) -> bool | Literal["restart"]:
    # if not on clash main, reutnr
    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status(status="ERROR 385462623 Not on clash main menu")
        return "restart"

    # get to profile page
    if get_to_profile_page(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 9076092860923485 Failure with get_to_profile_page",
        )
        return "restart"

    # check pixels for in a clan
    in_a_clan = request_state_check_pixels_for_clan_flag(vm_index)

    # print clan status
    if not in_a_clan:
        logger.change_status("Not in a clan, so can't request!")

    # click deadspace to leave
    click(vm_index, CLASH_MAIN_DEADSPACE_COORD[0], CLASH_MAIN_DEADSPACE_COORD[1])
    if wait_for_clash_main_menu(vm_index, logger) is False:
        logger.change_status(
            status="Error 87258301758939 Failure with wait_for_clash_main_menu",
        )
        return "restart"

    return in_a_clan


def request_state_check_pixels_for_clan_flag(vm_index) -> bool:
    iar = numpy.asarray(screenshot(vm_index))  # type: ignore  # noqa: PGH003

    pix_list = []
    for x_coord in range(80, 96):
        pixel = iar[350][x_coord]
        pix_list.append(pixel)

    for y_coord in range(345, 360):
        pixel = iar[y_coord][88]
        pix_list.append(pixel)

    # if all the pixels are grey the its not in a clan
    grey = [51, 51, 51]
    grey_count = sum([1 if pixel_is_equal(grey, pixel, tol=1) else 0 for pixel in pix_list])
    grey_ratio = grey_count / len(pix_list)
    if grey_ratio > 0.75:
        return False

    return True


def click_random_requestable_card(vm_index) -> bool:
    def make_coord_list(x_range, y_range):
        coords = []
        for x in range(x_range[0], x_range[1]):
            for y in range(y_range[0], y_range[1]):
                c = [x, y]
                coords.append(c)

        random.shuffle(coords)
        return coords

    def is_valid_pixel(pixel):
        def is_greyscale_pixel(pixel):
            # if all the values are wihtin 5 of eachother, it's greyscale
            if abs(pixel[0] - pixel[1]) < 5 and abs(pixel[1] - pixel[2]) < 5:
                return True

            return False

        if is_greyscale_pixel(pixel):
            return False

        if pixel_is_equal(pixel, [222, 235, 241], tol=20):
            return False

        return True

    # check pixels in the request card grid region
    iar = screenshot(vm_index)
    for coord in make_coord_list((69, 356), (213, 557)):
        pixel = iar[coord[1]][coord[0]]
        # if the pixel indicates requestable, click it, return True
        if is_valid_pixel(pixel):
            click(vm_index, coord[0], coord[1])
            return True

    # fail return
    return False


def do_request(vm_index, logger: Logger) -> bool:
    logger.change_status(status="Initiating request process")

    # Click the request button
    logger.change_status(status="Clicking the request button")
    click(vm_index=vm_index, x_coord=77, y_coord=536)
    time.sleep(3)

    # Determine the maximum number of scrolls in the request page
    logger.change_status(status="Determining maximum scrolls in the request page")
    max_scrolls: int = count_scrolls_in_request_page(vm_index=vm_index)
    logger.log(f"Maximum scrolls found in the request page: {max_scrolls}")
    random_scroll_amount: int = random.randint(a=0, b=max_scrolls)
    logger.log(f"Scrolling {random_scroll_amount} times in the request page")

    # Perform random scrolling in the request page
    do_random_scrolling_in_request_page(
        vm_index=vm_index,
        logger=logger,
        scrolls=random_scroll_amount,
    )

    # Timeout settings for random clicking
    random_click_timeout = 35  # seconds
    random_click_start_time = time.time()
    attempt_count = 0  # Keep track of the number of attempts

    # Attempt to click on a random card and find the request button
    coord = None
    while coord is None:
        # Timeout check to avoid infinite loop
        if time.time() - random_click_start_time > random_click_timeout or attempt_count > 6:
            logger.change_status(
                "Timeout or too many attempts while trying to click a random card for request",
            )
            return False

        # Click on a random card
        logger.change_status(status="Clicking a random card to request")

        click_try_limit = 10
        click_tries = 0
        while click_random_requestable_card(vm_index) is False:
            print("Failed to click an upgradable card.")
            click_tries += 1
            if click_tries > click_try_limit:
                logger.change_status("Failed to click an upgradable card. too many times")
                return False

        time.sleep(3)

        # Attempt to find the request button
        coord = find_request_button(vm_index, logger)
        attempt_count += 1

    # Click the found request button
    logger.change_status(status="Clicking the request button")
    click(vm_index, coord[0], coord[1])

    # Update request statistics
    prev_requests = logger.get_requests()
    logger.add_request()
    requests = logger.get_requests()
    logger.log(f"Request stats updated from {prev_requests} to {requests}")
    time.sleep(3)

    return True


def check_if_can_request_wrapper(vm_index) -> bool:
    if check_for_epic_sunday_icon_with_delay(vm_index, 3):
        print("Detected epic sunday icon")
        return True

    if check_for_trade_cards_icon(vm_index):
        print("Detected trade cards icon")
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


def check_for_epic_sunday_icon_with_delay(vm_index, delay):
    start_time = time.time()
    while time.time() - start_time < delay:
        if check_for_epic_sunday_icon(vm_index):
            return True
        time.sleep(1)
    return False


def check_for_epic_sunday_icon(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[507][43],
        iar[508][120],
    ]
    colors = [
        [250, 50, 149],
        [251, 48, 149],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(colors[i], p, tol=10):
            return False
    return True


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
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[518][38],
        iar[520][42],
        iar[525][75],
        iar[526][45],
        iar[527][50],
        iar[529][60],
        iar[530][60],
        iar[535][70],
        iar[537][80],
        iar[540][90],
        iar[541][100],
        iar[543][104],
    ]
    colors = [
        [64, 46, 36],
        [46, 191, 255],
        [73, 111, 129],
        [78, 185, 232],
        [255, 238, 237],
        [224, 204, 205],
        [219, 199, 200],
        [37, 83, 104],
        [82, 112, 125],
        [254, 255, 255],
        [250, 253, 255],
        [43, 189, 253],
    ]
    # for p in pixels:print(p)
    for i, c in enumerate(colors):
        if not pixel_is_equal(c, pixels[i], tol=10):
            return False
    return True


def check_if_can_request_3(vm_index):
    if not region_is_color(vm_index, [48, 529, 8, 7], (216, 229, 255)):
        return False
    if not region_is_color(vm_index, [106, 538, 12, 7], (255, 188, 42)):
        return False

    return True


if __name__ == "__main__":
    print(request_state(1, Logger(), "next_state"))
