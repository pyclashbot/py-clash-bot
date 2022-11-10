import time
from random import Random

import numpy

from pyclashbot.bot.clashmain import (
    check_if_in_a_clan,
    get_to_clan_page,
    get_to_clash_main_from_clan_page,
    handle_card_mastery_notification,
)
from pyclashbot.detection import find_references, get_first_location, pixel_is_equal
from pyclashbot.memu import (
    click,
    screenshot,
    scroll_down_super_fast,
    scroll_up_super_fast,
)
from pyclashbot.memu.client import get_file_count, make_reference_image_list


def request_random_card_from_clash_main(logger):
    # Method to request a random card if request is available
    # Starts on clash main ends on clash main

    # handle card mastery notification because it coveres the request button
    handle_card_mastery_notification()

    # Return if not in clan (starts on main, ends on main)
    logger.change_status("Checking if you're in a clan.")
    if not check_if_in_a_clan(logger):
        logger.change_status("Skipping request because we are not in a clan.")
        if get_to_clash_main_from_clan_page(logger) == "restart": return "restart"
        return None
    else: 
        if get_to_clash_main_from_clan_page(logger) == "restart": return "restart"
        time.sleep(1)

    # Return if request is not available (Starts on main, ends on clan page)
    time.sleep(1)
    logger.change_status("Checking if request is available.")
    if not check_if_can_request(logger):
        logger.change_status("Request isn't available.")
        if get_to_clash_main_from_clan_page(logger) == "restart":
            return "restart"
        return None

    # Click request button (getting to page of requestable cards)
    click(75, 565)
    time.sleep(1)

    # Count maximum scrolls (starts on requestable cards page, ends on top of requestable cards page)
    maximum_scrolls = count_maximum_request_scrolls(logger)
    if maximum_scrolls == "restart":
        return "restart"

    # request a random card (starts on requestable cards page, ends on clan chat page)
    if request_random_card(logger, maximum_scrolls=maximum_scrolls) == "restart":
        return "restart"

    # get back to clash main
    if get_to_clash_main_from_clan_page(logger) == "restart":
        return "restart"
    return None


def request_random_card(logger, maximum_scrolls=10):
    # method to request a random card
    # starts on the request screen (the one with a bunch of pictures of the cards)
    # ends back on the clash main menu
    logger.change_status("Requesting a random card.")

    # scroll down for randomness
    for _ in range(maximum_scrolls):
        scroll_down_super_fast()

    # click random cards in the card list until a request button appears.
    logger.change_status("Looking for card to request.")
    has_card_to_request = False
    loops = 0
    while not has_card_to_request:
        loops += 1
        if loops > 25:
            logger.change_status("Could not find a card to request.")
            return "restart"
        # click random coord in region of card selection
        click(Random().randint(72, 343), Random().randint(264, 570))
        time.sleep(2)

        # check if request button appears
        request_button_coord = look_for_request_button()

        if request_button_coord is not None:
            # change loop bool to exit loop
            has_card_to_request = True

            # click request buutton
            click(request_button_coord[1], request_button_coord[0])

            # increment request counter
            logger.add_request()


def look_for_request_button():
    # Method to look for the request button in the list of clan interaction
    # buttons on the clan page to see if we can request

    references = make_reference_image_list(
        get_file_count(
            "request_button",
        )
    )

    locations = find_references(
        screenshot=screenshot(),
        folder="request_button",
        names=references,
        tolerance=0.97,
    )
    return get_first_location(locations)


def check_if_can_request(logger):
    # Get to clan page
    if get_to_clan_page(logger) == "restart":
        return "restart"
    time.sleep(1)

    # Method to check if request is available
    iar = numpy.array(screenshot())
    pix_list = [
        iar[536][50],
        iar[542][56],
        iar[535][57],
        iar[536][47],
    ]
    color = [47, 69, 105]

    return all((pixel_is_equal(pix, color, tol=35)) for pix in pix_list)


def count_maximum_request_scrolls(logger):
    logger.change_status("Counting maximum request scrolls for the random scroling.")

    # count scrolls
    scrolls = 0

    loops = 0
    # loop until reach the bottom of card request list
    while check_if_can_still_scroll_in_request_page():
        loops += 1
        if loops > 35:
            return "restart"
        scroll_down_super_fast()
        scrolls += 1

    for _ in range(10):
        scroll_up_super_fast()

    return scrolls


def check_if_can_still_scroll_in_request_page():
    iar = numpy.asarray(screenshot())
    pix_list = [
        iar[575][85],
        iar[575][165],
        iar[575][275],
        iar[575][350],
    ]
    color = [222, 235, 241]

    return any(not pixel_is_equal(pix, color, tol=45) for pix in pix_list)
