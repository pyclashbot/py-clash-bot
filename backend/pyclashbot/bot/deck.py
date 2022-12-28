import random
import time
from typing import Literal

import numpy

from pyclashbot.bot.navigation import get_to_card_page, get_to_clash_main_from_card_page
from pyclashbot.detection import (
    check_for_location,
    find_references,
    get_first_location,
    pixel_is_equal,
)
from pyclashbot.memu import (
    click,
    get_file_count,
    make_reference_image_list,
    screenshot,
    scroll_down,
    scroll_down_super_fast,
    scroll_up_fast,
    scroll_up_super_fast,
)


def check_if_mimimum_scroll_case():
    scroll_down()
    time.sleep(3)

    minimum_case = False
    seasonal_card_boosts_icon_coord = find_seasonal_card_boost_icon()
    if seasonal_card_boosts_icon_coord is None:
        minimum_case = True

    elif seasonal_card_boosts_icon_coord[1] < 515:
        minimum_case = False

    scroll_up_super_fast()
    return minimum_case


def find_seasonal_card_boost_icon():
    current_image = screenshot()
    reference_folder = "check_for_seasonal_card_boosts_icon"

    references = make_reference_image_list(
        get_file_count(
            "check_for_seasonal_card_boosts_icon",
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


def count_scrolls_in_card_page(logger) -> int | Literal["restart"]:
    print("Counting maximum scrolls in card page")

    # Count scrolls
    count: int = 1
    scroll_down_super_fast()
    loops = 0
    while check_if_can_still_scroll_in_card_page():
        print("Scrolling down in card page: ", count)
        loops += 1
        if loops > 40:
            logger.change_status("Failed counting scrolls in card page")
            return "restart"
        scroll_down_super_fast()
        time.sleep(0.1)
        count += 1

    # get back to top of page
    click(240, 621)
    click(111, 629)
    time.sleep(1)

    print(f"Counted scrolls: {count}")
    return 1 if count == 0 else count - 1


#### detection methods


def find_random_card_coord():
    region_list = [
        # cover the region that cards' elixer values can appear in once
        [50, 180, 50, 50],
        [100, 180, 50, 50],
        [150, 180, 50, 50],
        [200, 180, 50, 50],
        [250, 180, 50, 50],
        [300, 180, 50, 50],
        [350, 180, 50, 50],
        [50, 230, 50, 50],
        [100, 230, 50, 50],
        [150, 230, 50, 50],
        [200, 230, 50, 50],
        [250, 230, 50, 50],
        [300, 230, 50, 50],
        [350, 230, 50, 50],
        [50, 280, 50, 50],
        [100, 280, 50, 50],
        [150, 280, 50, 50],
        [200, 280, 50, 50],
        [250, 280, 50, 50],
        [300, 280, 50, 50],
        [350, 280, 50, 50],
        [50, 330, 50, 50],
        [100, 330, 50, 50],
        [150, 330, 50, 50],
        [200, 330, 50, 50],
        [250, 330, 50, 50],
        [300, 330, 50, 50],
        [350, 330, 50, 50],
        [50, 380, 50, 50],
        [100, 380, 50, 50],
        [150, 380, 50, 50],
        [200, 380, 50, 50],
        [250, 380, 50, 50],
        [300, 380, 50, 50],
        [350, 380, 50, 50],
        [50, 430, 50, 50],
        [100, 430, 50, 50],
        [150, 430, 50, 50],
        [200, 430, 50, 50],
        [250, 430, 50, 50],
        [300, 430, 50, 50],
        [350, 430, 50, 50],
        # cover the region that cards' elixer values can appear in twice (this time with different increments of regions)
        [50, 130, 81, 71],
        [131, 130, 81, 71],
        [212, 130, 81, 71],
        [293, 130, 81, 71],
        [50, 275, 81, 71],
        [50, 346, 81, 71],
        [50, 417, 81, 71],
        [50, 488, 81, 71],
        [131, 275, 81, 71],
        [131, 346, 81, 71],
        [131, 417, 81, 71],
        [131, 488, 81, 71],
        [212, 275, 81, 71],
        [212, 346, 81, 71],
        [212, 417, 81, 71],
        [212, 488, 81, 71],
        [293, 275, 81, 71],
        [293, 346, 81, 71],
        [293, 417, 81, 71],
        [293, 488, 81, 71],
    ]

    # loop through the region list in random order 3 times
    index = 0
    for _ in range(3):
        # randomize region list
        this_random_region_list: list[list[int]] = random.sample(
            region_list, len(region_list)
        )
        for region in this_random_region_list:
            index += 1
            coord = find_card_elixer_icon_in_card_list_in_given_image(
                screenshot(region)
            )
            if coord is not None:
                print("Found a random card at index: " + str(index))
                return (coord[0] + region[0], coord[1] + region[1])
    print("Looped through find_random_card_coord() too many times. Restarting")
    return "restart"


def find_card_elixer_icon_in_card_list_in_given_image(image):

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


def check_if_can_still_scroll_in_card_page_2():
    iar = numpy.asarray(screenshot())
    pix_list = [
        iar[552][341],
        iar[529][363],
        iar[561][237],
        iar[530][271],
    ]

    # print_pix_list(pix_list)

    # classify this pix list
    color_blue = [15, 70, 125]
    color_purple = [204, 102, 255]

    classified_pix_list = []
    for pix in pix_list:
        if pixel_is_equal(pix, color_blue, tol=45):
            classified_pix_list.append("Blue")
        elif check_if_pixel_is_grey(pix):
            classified_pix_list.append("Grey")
        elif pixel_is_equal(pix, color_purple, tol=45):
            classified_pix_list.append("Purple")
        else:
            classified_pix_list.append("Other")

    # if any of the pixels aren't grey or blue, we can keep scrolling
    for color in classified_pix_list:
        if color != "Grey" and color != "Blue" and color != "Purple":
            return True
    return False


def check_if_can_still_scroll_in_card_page_3():
    iar = numpy.asarray(screenshot())
    pix_list = [
        iar[489][66],
        iar[500][94],
        iar[495][155],
        iar[546][176],
    ]

    # print_pix_list(pix_list)

    # classify this pix list
    color_blue = [15, 70, 125]
    color_purple = [204, 102, 255]

    classified_pix_list = []
    for pix in pix_list:
        if pixel_is_equal(pix, color_blue, tol=45):
            classified_pix_list.append("Blue")
        elif check_if_pixel_is_grey(pix):
            classified_pix_list.append("Grey")
        elif pixel_is_equal(pix, color_purple, tol=45):
            classified_pix_list.append("Purple")
        else:
            classified_pix_list.append("Other")

    # if any of the pixels aren't grey or blue, we can keep scrolling
    for color in classified_pix_list:
        if color != "Grey" and color != "Blue" and color != "Purple":
            return True
    return False


def check_if_can_still_scroll_in_card_page_4():
    iar = numpy.asarray(screenshot())
    pix_list = [
        iar[313][147],
        iar[371][161],
        iar[306][235],
        iar[346][275],
    ]

    # print_pix_list(pix_list)

    # classify this pix list
    color_blue = [15, 70, 125]
    color_purple = [204, 102, 255]

    classified_pix_list = []
    for pix in pix_list:
        if pixel_is_equal(pix, color_blue, tol=45):
            classified_pix_list.append("Blue")
        elif check_if_pixel_is_grey(pix):
            classified_pix_list.append("Grey")
        elif pixel_is_equal(pix, color_purple, tol=45):
            classified_pix_list.append("Purple")
        else:
            classified_pix_list.append("Other")

    # if any of the pixels aren't grey or blue, we can keep scrolling
    for color in classified_pix_list:
        if color != "Grey" and color != "Blue" and color != "Purple":
            return True
    return False


def check_if_can_still_scroll_in_card_page():
    if not check_if_can_still_scroll_in_card_page_2():
        return False
    if not check_if_can_still_scroll_in_card_page_3():
        return False
    if not check_if_can_still_scroll_in_card_page_4():
        return False
    return True


def check_for_random_scroll_failure_in_deck_randomization():
    card_level_boost_icon_coord_height = find_seasonal_card_boost_icon()
    if card_level_boost_icon_coord_height is None:
        return False
    else:
        return True


#### etc


def check_if_pix_list_is_blue(pix_list):
    color_blue = [15, 70, 120]
    return all(pixel_is_equal(color_blue, pix, tol=45) for pix in pix_list)


def check_if_pixel_is_grey(pixel):
    r: int = pixel[0]
    g: int = pixel[1]
    b: int = pixel[2]

    # pixel to ignore
    ignore_pixel = [41, 40, 47]

    if pixel_is_equal(ignore_pixel, pixel, tol=10):
        return False

    return abs(r - g) <= 10 and abs(r - b) <= 10 and abs(g - b) <= 10


### TO SORT
def randomize_and_select_deck_2(logger):
    logger.change_status("Making a random deck before starting a 2v2. . .")

    # get to card page
    print("Getting to card page to randomize deck.")
    get_to_card_page(logger)
    print("Done getting to card page to randomize deck.")

    # click deck 2
    print("Clicking deck 2")
    click(173, 190)
    time.sleep(1)

    # check if minimum scroll case
    logger.change_status(
        "Checking how far the bot can randomly scroll in this account's deck list. . ."
    )
    minimum_scroll_case_boolean = check_if_mimimum_scroll_case()
    print(minimum_scroll_case_boolean, minimum_scroll_case_boolean)

    # for each card slot, scroll according to which case it is, then replace with random card
    logger.change_status("Randomizing this deck. . .")
    randomize_this_deck(logger, minimum_scroll_case_boolean)

    # return to clash main
    if get_to_clash_main_from_card_page(logger) == "restart":
        logger.change_status("Failure getting to clash main")
        return "restart"
    time.sleep(1)


def randomize_this_deck(logger, minimum_scroll_case_boolean):
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
    print("Coutning maximum scrolls for deck randomization.")
    maximum_scrolls = count_scrolls_in_card_page(logger)

    # for each card slot, replace with random card
    print("Starting card replacement loop")
    for card_to_replace_coord in card_coord_list:
        # calculate a an amount to randomly scroll
        if minimum_scroll_case_boolean:
            minimum_scrolls = 1
        else:
            minimum_scrolls = 3
        print(
            "minimum_scroll_case_boolean is ",
            minimum_scroll_case_boolean,
            " so minimum scrolls is ",
            minimum_scrolls,
        )

        # handle possiblity of minimum being higher than maximum
        if minimum_scrolls > maximum_scrolls:
            print(
                "minimum_scrolls is greater than maximum_scrolls so making minimum_scrolls = maximum_scrolls"
            )
            minimum_scrolls = maximum_scrolls

        random_scroll_amount = random.randint(minimum_scrolls, maximum_scrolls)
        print(
            "This random scroll amount is ",
            random_scroll_amount,
            " within a range of (",
            minimum_scrolls,
            ",",
            maximum_scrolls,
            ")",
        )

        # scroll that amount
        for _ in range(random_scroll_amount):
            scroll_down_super_fast()
            time.sleep(0.1)

        # check for scrolling failure here maybe
        if check_for_random_scroll_failure_in_deck_randomization():
            print(
                "detected a failure when randomly scrolling during deck randomization... attempting to save the bot"
            )
            for _ in range(3):
                scroll_down_super_fast()
                time.sleep(0.1)

        # click randomly until we get a 'use' button
        use_card_button_coord = None
        loops = 0

        print("Clicking randomly until we get a use button")
        while use_card_button_coord is None:
            print("Clicking cards randomly")
            loops += 1
            if loops > 30:
                print(
                    "Clicked around for a random card too many times. Returning to main regardless of how well this deck is randomized."
                )
                if get_to_clash_main_from_card_page(logger) == "restart":
                    return "restart"
                else:
                    return "fail"

            # find a random card on this page
            replacement_card_coord = find_random_card_coord()

            if replacement_card_coord == "restart":
                logger.change_status("Failure replacing card")
                if get_to_clash_main_from_card_page(logger) == "restart":
                    return "restart"
                else:
                    return

            # if replacement_card_coord is too high, we are at risk of clicking numbers on the top of the screen
            if replacement_card_coord[1] < 200:
                print("replacement_card_coord is too high on the screen. trying again")
                if random.randint(1, 2) == 2:
                    loops -= 1
                continue

            click(replacement_card_coord[0], replacement_card_coord[1])
            time.sleep(1)

            # get a random card from this screen to use
            use_card_button_coord = find_use_card_button()

        # click use card
        print("Clicking use card button")
        click(use_card_button_coord[0], use_card_button_coord[1])
        time.sleep(1)

        # select the card coord in the deck that we're replacing with the random card
        print("selecting the card to replace")
        click(card_to_replace_coord[0], card_to_replace_coord[1])
        time.sleep(0.22)

    return None
