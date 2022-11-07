import time
from random import Random

import numpy

from pyclashbot.bot.clashmain import (
    check_if_in_a_clan,
    get_to_clash_main_from_clan_page,
    handle_card_mastery_notification,
)
from pyclashbot.detection import find_references, get_first_location, pixel_is_equal
from pyclashbot.memu import (
    click,
    screenshot,
    scroll_down,
    scroll_down_super_fast,
    scroll_up_super_fast,
)


def request_random_card_from_clash_main(logger):
    # Method to request a random card if request is available
    # Starts on clash main ends on clash main

    # handle card mastery notification because it coveres the request button
    handle_card_mastery_notification()

    # Return if not in clan (starts on main, ends on main)
    logger.change_status("Checking if you're in a clan.")
    if not (check_if_in_a_clan(logger)):
        logger.change_status("Skipping request because we are not in a clan.")
        if get_to_clash_main_from_clan_page(logger) == "restart":
            return "restart"

    # Return if request is not available (Starts on main, ends on clan page)
    logger.change_status("Checking if request is available.")
    if not check_if_can_request(logger):
        logger.change_status("Request isn't available.")
        if get_to_clash_main_from_clan_page(logger) == "restart":
            return "restart"
        return

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
    while not (has_card_to_request):
        loops += 1
        if loops > 25:
            logger.change_status("Could not find a card to request.")
            return "restart"
        # click random coord in region of card selection
        click(Random().randint(72, 343), Random().randint(264, 570))
        time.sleep(1)

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

    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
        "6.png",
        "7.png",
        "8.png",
        "9.png",
        "10.png",
        "11.png",
        "12.png",
        "13.png",
        "14.png",
        "15.png",
        "16.png",
        "17.png",
        "18.png",
        "19.png",
        "20.png",
        "21.png",
        "ifhy_1.png",
        "ifhy_2.png",
        "ifhy_3.png",
        "ifhy_4.png",
        "ifhy_5.png",
        "ifhy_6.png",
        "ifhy_7.png",
        "ifhy_8.png",
        "iuyfgh_1.png",
        "iuyfgh_2.png",
        "iuyfgh_3.png",
        "iuyfgh_4.png",
        "iuyfgh_5.png",
        "iuyfgh_6.png",
        "iuyfgh_7.png",
        "iuyfgh_8.png",
        "royal_guards_1.png",
        "royal_guards_2.png",
        "royal_guards_3.png",
        "royal_guards_4.png",
        "royal_guards_5.png",
        "royal_guards_6.png",
        "royal_guards_7.png",
        "royal_guards_8.png",
        "telotet_1.png",
        "telotet_2.png",
        "telotet_3.png",
        "telotet_4.png",
        "telotet_5.png",
        "telotet_6.png",
        "telotet_7.png",
        "telotet_8.png",
        "22.png",
        "23.png",
        "24.png",
        "25.png",
        "26.png",
    ]
    locations = find_references(
        screenshot=screenshot(),
        folder="request_button",
        names=references,
        tolerance=0.97,
    )
    return get_first_location(locations)


def get_to_clan_page(logger):
    # method to get to clan chat page from clash main
    click(312, 629)
    on_clan_chat_page = check_if_on_clan_page()
    loops = 0
    while not (on_clan_chat_page):
        loops += 1
        if loops > 25:
            logger.change_status("Could not get to clan page.")
            return "restart"
        click(278, 631)
        time.sleep(1)
        scroll_down()
        time.sleep(1)

        on_clan_chat_page = check_if_on_clan_page()


def check_if_on_clan_page():
    # Method to check if we're on the clan chat page

    iar = numpy.array(screenshot())

    pix_list = [
        iar[570][216],
        iar[575][149],
        iar[557][150],
        iar[575][215],
    ]
    color = [183, 105, 253]
    return all((pixel_is_equal(pix, color, tol=45)) for pix in pix_list)


def check_if_can_request(logger):
    # Get to clan page
    if get_to_clan_page(logger) == "restart":
        return "restart"

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
