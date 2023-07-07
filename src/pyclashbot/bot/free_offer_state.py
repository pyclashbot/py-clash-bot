import time
from typing import Any, Literal

import numpy

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    wait_for_clash_main_menu,
    wait_for_clash_main_shop_page,
)
from pyclashbot.detection.image_rec import (
    check_line_for_color,
    pixel_is_equal,
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


def free_offer_collection_state(vm_index, logger: Logger, next_state: str) -> str:
    logger.change_status(status="Free offer collection state")

    if not check_if_on_clash_main_menu(vm_index):
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

    start_time = time.time()
    while 1:
        # if looped too much, return
        time_taken = time.time() - start_time
        if time_taken > 35:
            break

        logger.change_status(status=f"Searching for free offer: {str(time_taken)[:4]}")

        # look for free offer
        coord = find_free_offer_coords(vm_index)
        if coord is None:
            # scroll
            scroll_down_fast_on_left_side_of_screen(vm_index)
            time.sleep(1)
            continue

        # click the offer
        logger.change_status(status="Collecting an available free offer!")
        logger.log("Clicking this free offer: " + str(coord))
        click(vm_index, coord[0], coord[1])
        time.sleep(2)

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
        logger.add_free_offer_collection()
        time.sleep(2)

        # click deadspace for if its a chest
        logger.log("Clicking deadspace if its a chest")
        click(vm_index, 10, 344, clicks=15, interval=0.75)
        break

    # return to clash main
    click(
        vm_index, CLASH_MAIN_ICON_FROM_SHOP_PAGE[0], CLASH_MAIN_ICON_FROM_SHOP_PAGE[1]
    )
    if wait_for_clash_main_menu(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 925878946724 Failure waiting for clash main after free offer collection loops"
        )
        return "restart"

    time.sleep(3)

    return next_state


def check_for_free_button_condition_1(vm_index) -> bool:
    if not check_line_for_color(
        vm_index=vm_index, x1=186, y1=389, x2=187, y2=407, color=(255, 255, 255)
    ):
        return False
    if not check_line_for_color(
        vm_index=vm_index, x1=222, y1=389, x2=221, y2=406, color=(255, 255, 255)
    ):
        return False

    if not region_is_color(vm_index=vm_index, region=[236, 400, 9, 6], color=(56, 228, 72)):
        return False
    if not region_is_color(vm_index=vm_index, region=[171, 398, 11, 10], color=(56, 228, 72)):
        return False

    return True


def find_free_offer_coords(vm_index):
    coord1 = find_free_offer_coords_1(vm_index=vm_index)
    if coord1 is not None:
        return coord1

    coord2 = find_free_offer_coords_2(vm_index=vm_index)
    if coord2 is not None:
        return coord2

    return None


def find_free_offer_coords_1(vm_index):
    green_pixel_coords = []
    iar: numpy.ndarray[Any, numpy.dtype[Any]] = numpy.asarray(screenshot(vm_index))


    for y_coord in range(34, 538):
        this_pixel = iar[y_coord][49]

        if pixel_is_equal(pix1=this_pixel, pix2=GREEN_COLOR, tol=30):
            green_pixel_coords.append((49, y_coord))

    pix_list_length: int = len(green_pixel_coords)
    if pix_list_length > 100:
        index = int(pix_list_length / 2)
        coord = green_pixel_coords[index]
        coord = [coord[0] + 50, coord[1]]
        return coord
    return "fail"


def find_free_offer_coords_2(vm_index):
    green_pixel_coords = []
    iar: numpy.ndarray[Any, numpy.dtype[Any]] = numpy.asarray(
        screenshot(vm_index=vm_index)
    )

    for y_index in range(34, 538):
        this_pixel = iar[y_index][132]

        if pixel_is_equal(pix1=this_pixel, pix2=GREEN_COLOR, tol=30):
            coord: tuple[Literal[132], int] = (132, y_index)
            green_pixel_coords.append(coord)

    pix_list_length: int = len(green_pixel_coords)
    if pix_list_length > 45:
        index = int(pix_list_length / 2)
        coord = green_pixel_coords[index]
        coord = [coord[0] - 50, coord[1]]  # type: ignore
        return coord
    return "fail"


if __name__ == "__main__":
    # free_offer_collection_state(1, Logger())

    screenshot(1)
