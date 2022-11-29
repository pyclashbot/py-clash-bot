import time

import numpy

from pyclashbot.bot.clashmain import check_if_on_clash_main_menu
from pyclashbot.detection.image_rec import (
    find_references,
    get_first_location,
    pixel_is_equal,
)
from pyclashbot.memu.client import (
    click,
    get_file_count,
    make_reference_image_list,
    screenshot,
    scroll_down_super_fast,
)


def collect_free_offer_from_shop(logger):
    logger.change_status("Collecting free offer from shop.")

    if not check_if_on_clash_main_menu():
        print("not on clash main so cant run collect_free_offer_from_shop()")
        print("Cant run collect_free_offer_from_shop() because not on main.")
        return "restart"

    # get to shop
    get_to_shop_page_from_main(logger)

    # scroll a few times, each time looking for the free offer
    logger.change_status("Looking for free offer")
    free_offer_coords = None
    loops = 0
    while free_offer_coords is None:
        scroll_down_super_fast()
        time.sleep(2)

        free_offer_coords = find_free_offer_icon()

        loops += 1
        if loops > 10:
            break

    if free_offer_coords is None:
        logger.change_status("Failed to find free offer icon.")
        # get to clash main from shop
        if get_to_clash_main_from_shop(logger) == "restart":
            print(
                "failed to get to clash main from shop page in collect_free_offer_from_shop()"
            )
            return "restart"
        return

    # click free offer
    logger.change_status("Found free offer icon. Collecting it.")
    click(free_offer_coords[0], free_offer_coords[1])
    time.sleep(2)
    if click_find_free_button_in_shop() != "fail":
        # implement logging for this later
        logger.add_free_offer_collection()

    # click deadspace
    for _ in range(4):
        click(18, 379)

    # get to clash main from shop
    if get_to_clash_main_from_shop(logger) == "restart":
        print(
            "failed to get to clash main from shop page in collect_free_offer_from_shop()"
        )
        return "restart"


def find_free_button_in_shop():
    current_image = screenshot()
    reference_folder = "find_free_button_in_shop"

    references = make_reference_image_list(
        get_file_count(
            "find_free_button_in_shop",
        )
    )

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97,
    )

    coord = get_first_location(locations)
    return None if coord is None else [coord[1], coord[0]]


def click_find_free_button_in_shop():
    coord = find_free_button_in_shop()
    if coord is None:
        return "fail"
    click(coord[0], coord[1])
    time.sleep(2)
    return "success"


def find_free_offer_icon():
    current_image = screenshot()
    reference_folder = "find_free_offer_icon"

    references = make_reference_image_list(
        get_file_count(
            "find_free_offer_icon",
        )
    )

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97,
    )

    coord = get_first_location(locations)
    return None if coord is None else [coord[1], coord[0]]


def get_to_clash_main_from_shop(logger):
    logger.change_status("Getting to clash main from shop.")
    # click main
    click(240, 630)
    time.sleep(2)

    loops = 0
    while not check_if_on_clash_main_menu():
        loops += 1
        if loops > 20:
            print(
                "Looped through get_to_clash_main_from_shop() too many times. Restarting"
            )
            return "restart"
        click(200, 620)
        time.sleep(2)

    logger.change_status("Made it to clash main from shop.")


def get_to_shop_page_from_main(logger):
    logger.change_status("Getting to shop from main.")

    # check if on main
    if not check_if_on_clash_main_menu():
        logger.change_status(
            "not no clash main so cant run get_to_shop_page_from_main()"
        )
        return "restart"

    # click shop icon
    click(35, 636)
    time.sleep(1)

    # check if on shop
    if not check_if_on_shop_page_with_delay():
        logger.change_status("Failed to get to shop page.")
        return "restart"

    logger.change_status("Made it to shop from main.")


def check_if_on_shop_page():
    iar = numpy.asarray(screenshot())

    pix_list = [
        iar[624][71],
        iar[636][55],
        iar[623][85],
        iar[625][71],
    ]
    color_list = [
        [103, 234, 56],
        [56, 85, 101],
        [247, 194, 75],
        [103, 236, 56],
    ]
    for n in range(4):
        this_pixel = pix_list[n]
        this_color = color_list[n]
        if not pixel_is_equal(this_pixel, this_color, tol=35):
            return False
    return True


def check_if_on_shop_page_with_delay():
    start_time = time.time()
    while time.time() - start_time < 3:
        print("looping thru")
        if check_if_on_shop_page():
            print("made it")
            return True
        time.sleep(0.5)
    return False
