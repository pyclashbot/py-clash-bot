import time

import numpy

from pyclashbot.bot.navigation import (
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

SHOP_PAGE_BUTTON = (33, 603)
CLASH_MAIN_ICON_FROM_SHOP_PAGE = (243, 603)
FREE_BUTTON = (216, 425)
FREE_BUTTON_CONDITION_1_COORD = (207, 398)


def free_offer_collection_state(vm_index, logger: Logger, NEXT_STATE: str):
    logger.change_status("Free offer collection state")

    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(f"ERROR 625436252356 Not on clash main menu")
        return "restart"

    # get to shop page
    click(vm_index, SHOP_PAGE_BUTTON[0], SHOP_PAGE_BUTTON[1])
    if wait_for_clash_main_shop_page(vm_index, logger) == "restart":
        logger.change_status(
            f"Error 085708235 Failure waiting for clash main shop page "
        )
        return "restart"

    logger.change_status("Searching for free offer")

    start_time = time.time()
    while 1:
        # if looped too much, return
        time_taken = time.time() - start_time
        if time_taken > 35:
            break

        logger.change_status(f"Searching for free offer: {str(time_taken)[:4]}")

        # look for free offer
        coord = find_free_offer_coords(vm_index)
        if coord is None:
            # scroll
            scroll_down_fast_on_left_side_of_screen(vm_index)
            time.sleep(1)
            continue

        # click the offer
        logger.change_status("Collecting an available free offer!")
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
            "Error 925878946724 Failure waiting for clash main after free offer collection loops"
        )
        return "restart"

    time.sleep(3)

    return NEXT_STATE


def check_for_free_button_condition_1(vm_index):
    if not check_line_for_color(
        vm_index, x1=186, y1=389, x2=187, y2=407, color=(255, 255, 255)
    ):
        return False
    if not check_line_for_color(
        vm_index, x1=222, y1=389, x2=221, y2=406, color=(255, 255, 255)
    ):
        return False

    if not region_is_color(vm_index, [236, 400, 9, 6], (56, 228, 72)):
        return False
    if not region_is_color(vm_index, [171, 398, 11, 10], (56, 228, 72)):
        return False

    return True


def find_free_offer_coords(vm_index):
    coord1 = find_free_offer_coords_1(vm_index)
    if coord1 is not None:
        return coord1

    coord2 = find_free_offer_coords_2(vm_index)
    if coord2 is not None:
        return coord2

    else:
        return None


def find_free_offer_coords_1(vm_index):
    green_pixel_coords = []
    iar = numpy.asarray(screenshot(vm_index))

    GREEN_COLOR = (99, 238, 153)

    for y in range(34, 538):
        this_pixel = iar[y][49]

        if pixel_is_equal(this_pixel, GREEN_COLOR, tol=30):
            green_pixel_coords.append((49, y))

    pix_list_length = len(green_pixel_coords)
    if pix_list_length > 100:
        index = int(pix_list_length / 2)
        coord = green_pixel_coords[index]
        coord = [coord[0] + 50, coord[1]]
        return coord


def find_free_offer_coords_2(vm_index):
    green_pixel_coords = []
    iar = numpy.asarray(screenshot(vm_index))

    GREEN_COLOR = (137, 242, 178)

    for y in range(34, 538):
        this_pixel = iar[y][132]

        if pixel_is_equal(this_pixel, GREEN_COLOR, tol=30):
            coord = (132, y)
            green_pixel_coords.append(coord)

    pix_list_length = len(green_pixel_coords)
    if pix_list_length > 45:
        index = int(pix_list_length / 2)
        coord = green_pixel_coords[index]
        coord = [coord[0] - 50, coord[1]]
        return coord


if __name__ == "__main__":
    # free_offer_collection_state(1, Logger())

    screenshot(1)