import random
import time
from typing import Literal

from pyclashbot.bot.navigation import get_to_card_page, get_to_clash_main_from_card_page
from pyclashbot.detection import find_references, get_first_location
from pyclashbot.memu import (
    click,
    get_file_count,
    make_reference_image_list,
    screenshot,
    scroll_down_fast,
)


def count_scrolls_in_card_page(logger) -> int | Literal["restart"]:
    """Method to cound the number of times the bot can scroll down in the card page while still having usable cards
    args:
        logger: the logger object
    returns:
        int,the number of scrolls that can be made in the card page
    """
    start_time = time.time()

    sleep_time = 1

    logger.change_status("Counting maximum scrolls in card page")

    # Count scrolls
    count: int = 1
    scroll_down_fast()
    time.sleep(sleep_time)
    loops = 0
    while find_card_elixer_icon_in_card_list_in_given_image(screenshot()) is not None:
        print(f"Looping in count scrolls: {count}")
        logger.change_status(f"Scrolling down in card page: {count}")
        loops += 1
        if loops > 40:
            print("Failed counting scrolls in card page")
            logger.change_status("Failed counting scrolls in card page")
            return "restart"
        scroll_down_fast()
        time.sleep(sleep_time)
        count += 1

    # get back to top of page
    print("returning top of card page")
    click(240, 621)
    click(111, 629)
    time.sleep(1)

    logger.change_status(
        f"Counted scrolls: {count} in {str(time.time() - start_time)[:5]} seconds"
    )
    return 1 if count == 0 else count - 1


def find_random_card_coord(logger):
    """method to find coordinates of a random card on the given page of usable cards using random regions to assure randomness
    args:
        None
    returns:
        coordinates of the card"""

    region_list = [
        # cover the region that cards' elixer values can appear in once
        (50, 180, 50, 50),
        (100, 180, 50, 50),
        (150, 180, 50, 50),
        (200, 180, 50, 50),
        (250, 180, 50, 50),
        (300, 180, 50, 50),
        (350, 180, 50, 50),
        (50, 230, 50, 50),
        (100, 230, 50, 50),
        (150, 230, 50, 50),
        (200, 230, 50, 50),
        (250, 230, 50, 50),
        (300, 230, 50, 50),
        (350, 230, 50, 50),
        (50, 280, 50, 50),
        (100, 280, 50, 50),
        (150, 280, 50, 50),
        (200, 280, 50, 50),
        (250, 280, 50, 50),
        (300, 280, 50, 50),
        (350, 280, 50, 50),
        (50, 330, 50, 50),
        (100, 330, 50, 50),
        (150, 330, 50, 50),
        (200, 330, 50, 50),
        (250, 330, 50, 50),
        (300, 330, 50, 50),
        (350, 330, 50, 50),
        (50, 380, 50, 50),
        (100, 380, 50, 50),
        (150, 380, 50, 50),
        (200, 380, 50, 50),
        (250, 380, 50, 50),
        (300, 380, 50, 50),
        (350, 380, 50, 50),
        (50, 430, 50, 50),
        (100, 430, 50, 50),
        (150, 430, 50, 50),
        (200, 430, 50, 50),
        (250, 430, 50, 50),
        (300, 430, 50, 50),
        (350, 430, 50, 50),
        # cover the region that cards' elixer values can appear in twice (this time with different increments of regions)
        (50, 130, 81, 71),
        (131, 130, 81, 71),
        (212, 130, 81, 71),
        (293, 130, 81, 71),
        (50, 275, 81, 71),
        (50, 346, 81, 71),
        (50, 417, 81, 71),
        (50, 488, 81, 71),
        (131, 275, 81, 71),
        (131, 346, 81, 71),
        (131, 417, 81, 71),
        (131, 488, 81, 71),
        (212, 275, 81, 71),
        (212, 346, 81, 71),
        (212, 417, 81, 71),
        (212, 488, 81, 71),
        (293, 275, 81, 71),
        (293, 346, 81, 71),
        (293, 417, 81, 71),
        (293, 488, 81, 71),
    ]

    start_time = time.time()

    # loop through the region list in random order 3 times
    index = 0
    for _ in range(3):
        # randomize region list
        this_random_region_list: list[tuple[int, int, int, int]] = random.sample(
            region_list, len(region_list)
        )
        for region in this_random_region_list:
            if time.time() - start_time > 7:
                return "restart"

            index += 1
            coord = find_card_elixer_icon_in_card_list_in_given_image(
                screenshot(region)
            )
            if coord is not None:
                logger.change_status("Found a random card at index: " + str(index))
                return (coord[0] + region[0], coord[1] + region[1])
    logger.change_status(
        "Looped through find_random_card_coord() too many times. Restarting"
    )
    return "restart"


def find_card_elixer_icon_in_card_list_in_given_image(image):
    """Method to find a card's elixer icon in a given image
    args:
        image: image to search for the elixer icon in
    returns:
        int[],coordinates of the elixer icon
    """

    current_image = image
    reference_folder = "find_card_elixer_icon_in_card_list"

    references = make_reference_image_list(
        get_file_count(
            "find_card_elixer_icon_in_card_list",
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


def find_use_card_button():
    """method to find the use card button after clicking on a card to use
    args:
        none
    returns:
        int[], coordinates of the use card button
    """

    current_image = screenshot()
    reference_folder = "find_use_card_button"

    references = make_reference_image_list(
        get_file_count(
            "card_collection_icon",
        )
    )

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.9,
    )

    coord = get_first_location(locations)
    return None if coord is None else [coord[1], coord[0]]


def randomize_and_select_deck_2(logger):
    """Main method for randomizing and selecting deck 2
    args:
        logger: Logger object
    returns:
        restart state upon failure
    """

    logger.change_status("Making a random deck before starting a 2v2. . .")

    # get to card page
    logger.change_status("Getting to card page to randomize deck.")
    if get_to_card_page(logger) == "restart":
        logger.change_status("failure with get_to_card_page")
        return "restart"
    logger.change_status("Done getting to card page to randomize deck.")

    # click deck 2
    logger.change_status("Clicking deck 2")
    click(173, 190)
    time.sleep(1)

    # check if minimum scroll case
    logger.change_status(
        "Checking how far the bot can randomly scroll in this account's deck list. . ."
    )

    # for each card slot, scroll according to which case it is, then replace with random card
    logger.change_status("Randomizing this deck. . .")
    randomize_this_deck(logger)

    # return to clash main
    if get_to_clash_main_from_card_page(logger) == "restart":
        logger.change_status("Failure getting to clash main")
        return "restart"
    time.sleep(1)


def randomize_this_deck(logger):
    """main method for randomizing the current deck
    args:
        logger: Logger object
    returns:
        restart state upon failure
    """

    card_coord_list = [
        [75, 271],
        [162, 277],
        [250, 267],
        [337, 267],
        [77, 400],
        [174, 398],
        [250, 411],
        [325, 404],
    ]

    # count maximum scrolls
    print("counting scrolls")
    logger.change_status("Counting maximum scrolls for deck randomization.")

    # calculate maximum scrolls, -4 represents a buffer at the bottom of the card list in case scrolling is inconsistent
    counted_scrolls = count_scrolls_in_card_page(logger)

    if counted_scrolls == "restart":
        logger.change_status("Failure with count_scrolls_in_card_page")
        return "restart"

    print(f"Counted scrolls: {counted_scrolls}")

    maximum_scrolls = counted_scrolls - 3
    print(f"Calculated maximum scrolls: {maximum_scrolls}")

    # calculate  an amount to randomly scroll
    minimum_scrolls = 3

    # handle possiblity of minimum being higher than maximum
    if minimum_scrolls > maximum_scrolls:
        minimum_scrolls = maximum_scrolls

    # for each card slot, replace with random card
    logger.change_status("Starting card replacement loop")
    for card_to_replace_coord in card_coord_list:
        random_scroll_amount = random.randint(minimum_scrolls, maximum_scrolls)

        logger.change_status(
            f"This random scroll amount is {random_scroll_amount} within a range of ({minimum_scrolls}, {maximum_scrolls})"
        )

        # scroll that amount
        for _ in range(random_scroll_amount):
            scroll_down_fast()
            time.sleep(1)

        # click randomly until we get a 'use' button
        use_card_button_coord = None
        loops = 0

        logger.change_status("Clicking randomly until we get a use button")
        while use_card_button_coord is None:
            logger.change_status("Clicking cards randomly")
            loops += 1
            if loops > 30:
                logger.change_status(
                    "Clicked around for a random card too many times. Returning to main regardless of how well this deck is randomized."
                )
                if get_to_clash_main_from_card_page(logger) == "restart":
                    return "restart"
                return "fail"

            # find a random card on this page
            replacement_card_coord = find_random_card_coord(logger)

            if replacement_card_coord == "restart":
                logger.change_status("Failure replacing card")
                if get_to_clash_main_from_card_page(logger) == "restart":
                    return "restart"
                return

            # if replacement_card_coord is too high, we are at risk of clicking numbers on the top of the screen
            if replacement_card_coord[1] < 200:
                logger.change_status(
                    "replacement_card_coord is too high on the screen. trying again"
                )
                if random.randint(1, 2) == 2:
                    loops -= 1
                continue

            click(replacement_card_coord[0], replacement_card_coord[1])
            time.sleep(1)

            # get a random card from this screen to use
            use_card_button_coord = find_use_card_button()

        # click use card
        logger.change_status("Clicking use card button")
        click(use_card_button_coord[0], use_card_button_coord[1])
        time.sleep(1)

        # select the card coord in the deck that we're replacing with the random card
        logger.change_status("selecting the card to replace")
        click(card_to_replace_coord[0], card_to_replace_coord[1])
        time.sleep(0.22)

    return None
