import math
import random
import numpy
import time
from bot.navigation import (
    check_if_on_clash_main_menu,
    get_to_clan_tab_from_clash_main,
    get_to_clash_main_from_clan_page,
    get_to_profile_page,
    wait_for_clash_main_menu,
)

from detection.image_rec import (
    check_line_for_color,
    pixel_is_equal,
    region_is_color,
)
from memu.client import click, screenshot, scroll_down, scroll_up
from utils.logger import Logger


def request_state(vm_index, logger: Logger, NEXT_STATE: str):
    logger.change_status("Request state")

    # if not on main retunr
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(f"ERROR 62543636 Not on clash main menu")
        return "restart"

    # if not in a clan, return
    in_a_clan_return = request_state_check_if_in_a_clan(vm_index, logger)
    if in_a_clan_return == "restart":
        logger.change_status("Error 05708425 Failure with check_if_in_a_clan")
        return "restart"

    if not in_a_clan_return:
        return NEXT_STATE

    # get to clan page
    if get_to_clan_tab_from_clash_main(vm_index, logger) == "restart":
        logger.change_status(f"ERROR 74842744443 Not on clan tab")
        return "restart"

    # check if request exists
    if check_if_can_request(vm_index):
        # do request
        do_request(vm_index, logger)
    else:
        logger.change_status("Cant request right now.")

    # return to clash main
    if get_to_clash_main_from_clan_page(vm_index, logger) == "restart":
        logger.change_status("Error 876208476 Failure with get_to_clash_main_from_clan_page")
        return "restart"
    return NEXT_STATE


def do_random_scrolling_in_request_page(vm_index, logger, scrolls):
    logger.change_status("Doing random scrolling in request page")
    for _ in range(scrolls):
        scroll_down(vm_index)
        time.sleep(2)
    logger.change_status("Done with random scrolling in request page")


def count_scrolls_in_request_page(vm_index):
    # scroll down, counting each scroll, until cant scroll anymore
    scrolls = 0
    while check_if_can_scroll_in_request_page(vm_index):
        scroll_down(vm_index)
        scrolls += 1
        time.sleep(2)

    # scroll back to top
    for _ in range(10):
        scroll_up(vm_index)

    return scrolls


def check_if_can_scroll_in_request_page(vm_index):
    if not region_is_color(vm_index, region=[64, 500, 293, 55], color=(222, 235, 241)):
        return True
    return False


def request_state_check_if_in_a_clan(vm_index, logger: Logger):
    # if not on clash main, reutnr
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(f"ERROR 385462623 Not on clash main menu")
        return "restart"

    # get to profile page
    if get_to_profile_page(vm_index, logger) == "restart":
        logger.change_status("Error 9076092860923485 Failure with get_to_profile_page")
        return "restart"

    # check pixels for in a clan
    in_a_clan = request_state_check_pixels_for_clan_flag(vm_index)

    # click deadspace to leave
    click(vm_index, 15, 300)
    if wait_for_clash_main_menu(vm_index, logger) == "restart":
        logger.change_status("Error 87258301758939 Failure with wait_for_clash_main_menu")
        return "restart"

    return in_a_clan


def request_state_check_pixels_for_clan_flag(vm_index):
    iar = numpy.asarray(screenshot(vm_index))  # type: ignore

    for x in range(78, 97):
        this_pixel = iar[446][x]
        if not (pixel_is_equal([51, 51, 51], this_pixel, tol=25)):
            return True

    for y in range(437, 455):
        this_pixel = iar[y][87]
        if not (pixel_is_equal([51, 51, 51], this_pixel, tol=25)):
            return True

    return False


def find_yellow_request_button_in_request_page(vm_index):
    iar = numpy.asarray(screenshot(vm_index))

    COLOR_WHITE = [255, 255, 255]
    YELLOW_1 = [255, 203, 85]
    YELLOW_2 = [255, 190, 43]

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

    bool_lists = [
        # row 1
        [
            pixel_is_equal(YELLOW_1, iar[345][74], tol=25),
            pixel_is_equal(YELLOW_1, iar[344][98], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[354][55], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[355][96], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[352][116], tol=25),
        ],
        [
            pixel_is_equal(YELLOW_1, iar[344][150], tol=25),
            pixel_is_equal(YELLOW_1, iar[345][192], tol=25),
            pixel_is_equal(YELLOW_1, iar[344][167], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[354][136], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[354][167], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[352][197], tol=25),
            pixel_is_equal(YELLOW_2, iar[364][170], tol=25),
            pixel_is_equal(YELLOW_2, iar[365][138], tol=25),
        ],
        [
            pixel_is_equal(YELLOW_1, iar[344][225], tol=25),
            pixel_is_equal(YELLOW_1, iar[344][265], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[354][218], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[355][249], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[352][279], tol=25),
            pixel_is_equal(YELLOW_2, iar[364][223], tol=25),
            pixel_is_equal(YELLOW_2, iar[364][253], tol=25),
            pixel_is_equal(YELLOW_2, iar[364][277], tol=25),
        ],
        [
            pixel_is_equal(YELLOW_1, iar[344][312], tol=25),
            pixel_is_equal(YELLOW_1, iar[344][333], tol=25),
            pixel_is_equal(YELLOW_1, iar[344][354], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[353][299], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[355][330], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[352][360], tol=25),
            pixel_is_equal(YELLOW_2, iar[364][332], tol=25),
            pixel_is_equal(YELLOW_2, iar[364][360], tol=25),
            pixel_is_equal(YELLOW_2, iar[364][340], tol=25),
        ],
        # row 2
        [
            pixel_is_equal(YELLOW_1, iar[486][76], tol=25),
            pixel_is_equal(YELLOW_1, iar[486][109], tol=25),
            pixel_is_equal(YELLOW_1, iar[486][95], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[498][55], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[498][81], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[496][116], tol=25),
            pixel_is_equal(YELLOW_2, iar[507][87], tol=25),
            pixel_is_equal(YELLOW_2, iar[507][117], tol=25),
            pixel_is_equal(YELLOW_2, iar[507][100], tol=25),
        ],
        [
            pixel_is_equal(YELLOW_1, iar[488][195], tol=25),
            pixel_is_equal(YELLOW_1, iar[488][165], tol=25),
            pixel_is_equal(YELLOW_1, iar[488][147], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[495][197], tol=25),
            pixel_is_equal(YELLOW_2, iar[508][202], tol=25),
            pixel_is_equal(YELLOW_2, iar[508][190], tol=25),
            pixel_is_equal(YELLOW_2, iar[508][170], tol=25),
        ],
        [
            pixel_is_equal(YELLOW_1, iar[487][275], tol=25),
            pixel_is_equal(YELLOW_1, iar[487][250], tol=25),
            pixel_is_equal(YELLOW_1, iar[487][229], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[497][218], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[498][249], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[496][279], tol=25),
            pixel_is_equal(YELLOW_2, iar[508][252], tol=25),
            pixel_is_equal(YELLOW_2, iar[508][275], tol=25),
            pixel_is_equal(YELLOW_2, iar[508][280], tol=25),
        ],
        [
            pixel_is_equal(YELLOW_1, iar[487][311], tol=25),
            pixel_is_equal(YELLOW_1, iar[487][338], tol=25),
            pixel_is_equal(YELLOW_1, iar[487][354], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[497][299], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[495][360], tol=25),
            pixel_is_equal(YELLOW_2, iar[508][360], tol=25),
            pixel_is_equal(YELLOW_2, iar[508][345], tol=25),
            pixel_is_equal(YELLOW_2, iar[508][330], tol=25),
        ],
        # row 3
        [
            pixel_is_equal(YELLOW_1, iar[514][109], tol=25),
            pixel_is_equal(YELLOW_1, iar[514][88], tol=25),
            pixel_is_equal(YELLOW_1, iar[514][65], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[524][55], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[522][117], tol=25),
            pixel_is_equal(YELLOW_2, iar[536][116], tol=25),
            pixel_is_equal(YELLOW_2, iar[536][100], tol=25),
            pixel_is_equal(YELLOW_2, iar[536][86], tol=25),
        ],
        [
            pixel_is_equal(YELLOW_1, iar[515][190], tol=25),
            pixel_is_equal(YELLOW_1, iar[515][177], tol=25),
            pixel_is_equal(YELLOW_1, iar[515][147], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[525][167], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[522][197], tol=25),
            pixel_is_equal(YELLOW_2, iar[535][200], tol=25),
            pixel_is_equal(YELLOW_2, iar[535][188], tol=25),
            pixel_is_equal(YELLOW_2, iar[535][169], tol=25),
        ],
        [
            pixel_is_equal(YELLOW_1, iar[515][228], tol=25),
            pixel_is_equal(YELLOW_1, iar[515][245], tol=25),
            pixel_is_equal(YELLOW_1, iar[515][274], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[524][218], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[526][244], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[522][279], tol=25),
            pixel_is_equal(YELLOW_2, iar[535][249], tol=25),
            pixel_is_equal(YELLOW_2, iar[535][266], tol=25),
            pixel_is_equal(YELLOW_2, iar[535][279], tol=25),
        ],
        [
            pixel_is_equal(YELLOW_1, iar[515][309], tol=25),
            pixel_is_equal(YELLOW_1, iar[515][335], tol=25),
            pixel_is_equal(YELLOW_1, iar[515][356], tol=25),
            pixel_is_equal(COLOR_WHITE, iar[522][361], tol=25),
            pixel_is_equal(YELLOW_2, iar[535][350], tol=25),
            pixel_is_equal(YELLOW_2, iar[535][360], tol=25),
            pixel_is_equal(YELLOW_2, iar[535][330], tol=25),
        ],
    ]

    index = 0
    for bool_list in bool_lists:
        index += 1
        if all(bool_list):
            break

    row, col = ((math.ceil(index / 4)), (((index - 1) % 4) + 1))

    return REQUEST_BUTTON_COORD_LIST[str(row)][col - 1]


def do_request(vm_index, logger: Logger):
    logger.change_status("Doing request")

    # click request button
    logger.change_status("Clicking request button")
    click(vm_index, 77, 536)
    time.sleep(3)

    # max scrolls
    logger.change_status("Counting the maximum scrolls in the request page")
    max_scrolls = count_scrolls_in_request_page(vm_index)
    random_scroll_amount = random.randint(0, max_scrolls)
    do_random_scrolling_in_request_page(vm_index, logger, scrolls=random_scroll_amount)

    # click card
    logger.change_status("Clicking random card to request")
    click(vm_index, random.randint(67, 358), random.randint(211, 547))
    time.sleep(3)

    logger.change_status("Clicking request")

    # get request button coord
    coord = find_yellow_request_button_in_request_page(vm_index)
    if coord is None:
        logger.change_status("Error 987359835 Couldnt find request button")
        return

    # Click request button coord
    click(vm_index, coord[0], coord[1])
    logger.add_request()
    time.sleep(3)


def check_for_trade_cards_icon(vm_index):
    lines = [
        check_line_for_color(
            vm_index, x1=33, y1=502, x2=56, y2=502, color=(47, 69, 105)
        ),
        check_line_for_color(
            vm_index, x1=56, y1=507, x2=108, y2=506, color=(253, 253, 203)
        ),
        check_line_for_color(
            vm_index, x1=37, y1=515, x2=125, y2=557, color=(255, 188, 42)
        ),
    ]

    return all(lines)


def check_if_can_request(vm_index):
    if check_for_trade_cards_icon(vm_index):
        return False

    iar = numpy.asarray(screenshot(vm_index))

    region_is_white = True
    for x in range(48, 55):
        this_pixel = iar[530][x]
        if not pixel_is_equal([212, 228, 255], this_pixel, tol=25):
            region_is_white = False
            break

    for y in range(528, 535):
        this_pixel = iar[y][52]
        if not pixel_is_equal([212, 228, 255], this_pixel, tol=25):
            region_is_white = False
            break

    yellow_button_exists = False
    for x in range(106, 118):
        this_pixel = iar[542][x]
        if pixel_is_equal([255, 188, 42], this_pixel, tol=25):
            yellow_button_exists = True
            break

    if region_is_white and yellow_button_exists:
        return True
    return False


if __name__ == "__main__":
    # screenshot(1)
    do_request(1, Logger())
