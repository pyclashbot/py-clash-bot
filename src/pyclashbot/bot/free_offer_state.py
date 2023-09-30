"""time module for timing methods and for sleeping while interacting with client"""
import time
from typing import Literal

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    wait_for_clash_main_menu,
    wait_for_clash_main_shop_page,
)
from pyclashbot.detection.image_rec import (
    check_line_for_color,
    find_references,
    get_file_count,
    get_first_location,
    make_reference_image_list,
    region_is_color,
)
from pyclashbot.memu.client import (
    click,
    screenshot,
    scroll_down_fast_on_left_side_of_screen,
)
from pyclashbot.utils.logger import Logger

SHOP_PAGE_BUTTON: tuple[Literal[33], Literal[603]] = (33, 603)
CLASH_MAIN_ICON_FROM_SHOP_PAGE: tuple[Literal[243], Literal[603]] = (243, 603)
FREE_BUTTON: tuple[Literal[216], Literal[425]] = (216, 425)
FREE_BUTTON_CONDITION_1_COORD: tuple[Literal[207], Literal[398]] = (207, 398)

GREEN_COLOR: tuple[Literal[137], Literal[242], Literal[178]] = (137, 242, 178)

FREE_OFFER_SCROLL_TIMEOUT = 35  # seconds


def free_offer_collection_state(vm_index, logger: Logger, next_state: str) -> str:
    """method to handle the entirety of the free offer collection state in the state tree"""
    logger.set_current_state("free_offer_collection")
    logger.change_status(status="Free offer collection state")
    logger.add_free_offer_collection_attempt()


    clash_main_check = check_if_on_clash_main_menu(vm_index)
    if clash_main_check is not True:
        logger.change_status(status="ERROR 356 Not on clash main menu for free_offer_collection_state")
        logger.log(f'There are the pixels the bot saw after failing to find clash main:')
        for pixel in clash_main_check:
            logger.log('   ',pixel)

        return "restart"


    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status(status="ERROR 625436252356 Not on clash main menu")
        return "restart"

    # get to shop page
    click(vm_index, SHOP_PAGE_BUTTON[0], SHOP_PAGE_BUTTON[1])
    if wait_for_clash_main_shop_page(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 085708235 Failure waiting for clash main shop page "
        )
        return "restart"

    logger.change_status(status="Searching for free offer")

    start_time: float = time.time()
    prints = 0
    while 1:
        # if looped too much, return
        time_taken: float = time.time() - start_time
        if time_taken > FREE_OFFER_SCROLL_TIMEOUT:
            logger.log(
                f"Scrolled longer than {FREE_OFFER_SCROLL_TIMEOUT} seconds so breaking"
            )
            break

        if prints * 10 < time_taken:
            logger.change_status(
                status=f"Searching for free offer: {str(time_taken)[:4]}"
            )
            prints += 1

        # look for free offer
        if find_and_click_free_offer(vm_index, logger) == "fail":
            continue

        if buy_this_free_offer(vm_index, logger) == "good":
            break

    # return to clash main
    click(
        vm_index, CLASH_MAIN_ICON_FROM_SHOP_PAGE[0], CLASH_MAIN_ICON_FROM_SHOP_PAGE[1]
    )
    if wait_for_clash_main_menu(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 777724 Failure waiting for clash main after free offer collection loops"
        )
        return "restart"

    time.sleep(3)

    return next_state


def find_and_click_free_offer(vm_index, logger: Logger) -> Literal["fail", "good"]:
    """method to find the click the free offer
    image that appears in the clash shop page"""

    # look for a free offer
    free_offer_coord = find_free_offer_icon(vm_index)

    # if the coord doesn't exist, scroll again, and return
    if free_offer_coord is None:
        # scroll
        scroll_down_fast_on_left_side_of_screen(vm_index)
        time.sleep(1)
        return "fail"

    # if the coord exists, click the offer
    logger.change_status(status="Collecting an available free offer!")
    logger.log("Clicking this free offer: " + str(free_offer_coord))
    click(vm_index, free_offer_coord[0], free_offer_coord[1])
    time.sleep(2)
    return "good"


def buy_this_free_offer(vm_index, logger) -> Literal["good"]:
    """method to click the free! button that appears after
    first clicking a free offer on the clash shop page"""
    # click the 'Free!' button
    logger.log("Cliking the free! price button")
    if check_for_free_button_condition_1(vm_index):
        click(
            vm_index,
            FREE_BUTTON_CONDITION_1_COORD[0],
            FREE_BUTTON_CONDITION_1_COORD[1],
        )
    else:
        click(vm_index, FREE_BUTTON[0], FREE_BUTTON[1])

    time.sleep(2)

    # click deadspace for if its a chest
    logger.log("Clicking deadspace if its a chest")
    click(vm_index, 10, 344, clicks=15, interval=0.75)
    time.sleep(1)

    return "good"


def check_for_free_button_condition_1(vm_index) -> bool:
    """method to check if the free! button exists"""

    if not check_line_for_color(
        vm_index=vm_index, x_1=186, y_1=389, x_2=187, y_2=407, color=(255, 255, 255)
    ):
        return False
    if not check_line_for_color(
        vm_index=vm_index, x_1=222, y_1=389, x_2=221, y_2=406, color=(255, 255, 255)
    ):
        return False

    if not region_is_color(
        vm_index=vm_index, region=[236, 400, 9, 6], color=(56, 228, 72)
    ):
        return False
    if not region_is_color(
        vm_index=vm_index, region=[171, 398, 11, 10], color=(56, 228, 72)
    ):
        return False

    return True


def find_free_offer_icon(vm_index):
    """method to find the free offer icon image in the shop pages"""

    folder_name = "free_offer_icon"
    size = get_file_count(folder_name)
    names = make_reference_image_list(size)
    locations = find_references(
        screenshot(vm_index),
        folder_name,
        names,
        0.9,
    )
    coord = get_first_location(locations)
    if coord is None:
        return None
    return [coord[1], coord[0]]


if __name__ == "__main__":
    pass
