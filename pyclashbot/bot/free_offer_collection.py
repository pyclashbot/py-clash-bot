import time

import numpy

from pyclashbot.bot.clashmain import check_if_on_clash_main_menu
from pyclashbot.bot.navigation import (
    get_to_clash_main_from_shop,
    get_to_shop_page_from_main,
)
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
        print("Cant run collect_free_offer_from_shop() because not on main.")
        return "restart"

    # get to shop
    print("getting to shop from main")
    get_to_shop_page_from_main(logger)

    # scroll a few times, each time looking for the free offer
    logger.change_status("Looking for free offer")
    free_offer_coords = None
    loops = 0
    print("Scrolling and looking for a free offer")
    while free_offer_coords is None:
        scroll_down_super_fast()
        time.sleep(2)

        free_offer_coords = find_free_offer_icon()

        loops += 1
        if loops > 10:
            print("looped looking for free offer too many times.")
            break

    if free_offer_coords is None:
        logger.change_status("Failed to find free offer icon.")
        # get to clash main from shop
        print("Getting to clash main then returning.")
        if get_to_clash_main_from_shop(logger) == "restart":
            print(
                "failed to get to clash main from shop page in collect_free_offer_from_shop()"
            )
            return "restart"
        return

    # click free offer
    logger.change_status("Found free offer. Clicking this free offer.")
    click(free_offer_coords[0], free_offer_coords[1])
    time.sleep(2)

    print("Clicking on the 'free' collect button in the next screen")
    if click_find_free_button_in_shop() != "fail":
        # implement logging for this later
        logger.add_free_offer_collection()

    # click deadspace
    print("Clicking deadspace to skip through free reward")
    click(20, 380, clicks=15, interval=0.33)

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
