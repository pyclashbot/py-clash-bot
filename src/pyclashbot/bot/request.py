import time
from random import Random

import numpy

from pyclashbot.bot.clashmain import (
    check_if_in_a_clan,
    handle_card_mastery_notification,
)
from pyclashbot.bot.navigation import get_to_clan_page, get_to_clash_main_from_clan_page
from pyclashbot.detection import find_references, get_first_location, pixel_is_equal
from pyclashbot.memu import click, screenshot, scroll_down_fast, scroll_up_fast
from pyclashbot.memu.client import get_file_count, make_reference_image_list


def request_random_card_from_clash_main(logger):
    # Method to request a random card if request is available
    # Starts on clash main ends on clash main

    # handle card mastery notification because it coveres the request button
    print("Handling card mastery notification before requesting b/c obstruction.")
    handle_card_mastery_notification()
    time.sleep(1)

    # Return if not in clan (starts on main, ends on main)
    logger.change_status("Checking if you're in a clan.")

    in_a_clan_return_string = check_if_in_a_clan(logger)
    if in_a_clan_return_string == "restart":
        print(
            "failure with check_if_in_a_clan() in request_random_card_from_clash_main()"
        )
        return "restart"
    if not in_a_clan_return_string:
        logger.change_status("Skipping request because we are not in a clan.")
        return "continue"
    logger.change_status("We are in a clan. Continuing with request.")
    print("We are in a clan. Continuing with request.")

    time.sleep(1)
    logger.change_status("Checking if request is available.")
    # check_if_can_request gets to clan page and checks
    if not check_if_can_request(logger):
        logger.change_status("Request isn't available.")
        # if request isnt available, go back to main and return
        if get_to_clash_main_from_clan_page(logger) == "restart":
            logger.change_status(
                "failure getting to clash main from clan "
                "page in request_random_card_from_clash_main()"
            )
            return "restart"
        return "continue"

    print("Request IS available.")

    # Click request button (getting to page of requestable cards)
    print("Clicking request button.")
    click(75, 565)
    time.sleep(1)

    # Count maximum scrolls
    # (starts on requestable cards page, ends on top of requestable cards page)
    logger.change_status(
        "Checking how much the bot can randomly scroll in the request page. . ."
    )
    print("Counting maximum scrolls in request page.")
    maximum_scrolls = count_maximum_request_scrolls(logger)
    print("maximum scrolls in request page is", maximum_scrolls)
    if maximum_scrolls == "restart":
        logger.change_status(
            "failure with max scrolls in request_random_card_from_clash_main()"
        )
        return "restart"

    # request a random card (starts on requestable cards page, ends on clan chat page)
    if request_random_card(logger, maximum_scrolls=maximum_scrolls) == "restart":
        logger.change_status(
            "failed requesting random card in request_random_card_from_clash_main()"
        )
        return "restart"

    # get back to clash main
    if get_to_clash_main_from_clan_page(logger) == "restart":
        logger.change_status(
            "failed getting to clash main from clan page in request_random_card_from_clash_main()"
        )
        return "restart"
    return "continue"


def request_random_card(logger, maximum_scrolls=10):
    # method to request a random card
    # starts on the request screen (the one with a bunch of pictures of the cards)
    # ends back on the clash main menu
    logger.change_status("Requesting a random card.")

    # scroll down for randomness
    print("Scrolling randomly with maximum scrolls of ", maximum_scrolls)
    random_scroll_amount = Random().randint(0, maximum_scrolls)
    for _ in range(random_scroll_amount):
        scroll_down_fast()

    # click random cards in the card list until a request button appears.
    has_card_to_request = False
    loops = 0
    while not has_card_to_request:
        loops += 1
        if loops > 25:
            logger.change_status(
                "Could not find a card to request in request_random_card()"
            )
            return "restart"
        # click random coord in region of card selection
        click(Random().randint(72, 343), Random().randint(264, 570))
        time.sleep(2)

        # check if request button appears
        request_button_coord = look_for_request_button()

        if request_button_coord is not None:
            print("found a card to request with ", loops, " loops.")

            # change loop bool to exit loop
            has_card_to_request = True

            # click request buutton
            click(request_button_coord[1], request_button_coord[0])

            # increment request counter
            logger.add_request()
    return "continue"


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
        logger.change_status("failed getting to clan page in check_if_can_request()")
        return "restart"
    time.sleep(1)

    return check_for_request_icon_on_clan_page()


def check_for_request_icon_on_clan_page():
    iar = numpy.array(screenshot())
    pix_list = [
        iar[536][50],
        iar[542][56],
        iar[535][57],
        iar[536][47],
    ]
    color = [47, 69, 105]

    # print_pix_list(pix_list)

    # if some of these pixels are purple then it's EPIC SUNDAY special case
    for pix in pix_list:
        if pixel_is_equal(pix, [137, 46, 228], tol=35):
            return True

    return all((pixel_is_equal(pix, color, tol=35)) for pix in pix_list)


def count_maximum_request_scrolls(logger):
    logger.change_status("Counting maximum request scrolls for the random scroling.")

    # get to the top of this page
    # b/c on epic sunday it automatically scrolls sorta halfway down to show the epic cards.
    for _ in range(10):
        scroll_up_fast()

    # count scrolls
    scrolls = 0

    loops = 0
    # loop until reach the bottom of card request list
    while check_if_can_still_scroll_in_request_page():
        loops += 1
        if loops > 35:
            logger.change_status(
                "Failed counting maximum scrolls in request page in count_maximum_request_scrolls()"
            )
            return "restart"
        scroll_down_fast()
        scrolls += 1

    for _ in range(10):
        scroll_up_fast()

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
