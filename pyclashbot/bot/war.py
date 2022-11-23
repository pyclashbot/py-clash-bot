import random
import time

import numpy

from pyclashbot.bot.clashmain import (
    check_if_in_a_clan,
    check_if_in_battle_with_delay,
    get_to_clash_main_from_clan_page,
)
from pyclashbot.detection import find_references, get_first_location, pixel_is_equal
from pyclashbot.memu import (
    click,
    get_file_count,
    make_reference_image_list,
    screenshot,
    scroll_down_super_fast,
    scroll_up_super_fast,
)
from pyclashbot.memu.client import print_pix_list


def handle_war_attacks(logger):
    logger.change_status("Handling war attacks")

    # check if in a clan
    logger.change_status("Checking if in a clan")
    if not check_if_in_a_clan(logger):
        logger.change_status("Not in a clan. Returning.")
        return "clashmain"

    # get to war page
    logger.change_status("Getting to war page.")
    if get_to_war_page_from_main(logger) == "restart":
        logger.change_status("Failure getting to war page")
        return "restart"

    # click a war battle
    if click_war_icon() == "failed":
        logger.change_status("Couldn't find a war battle. Returning.")
        time.sleep(1)
        get_to_clash_main_from_clan_page(logger)
        return "clashmain"

    # click deadspace to get rid of the pop up
    for _ in range(5):
        click(220, 290)

    # if you dont have a deck make a random deck
    if not check_if_has_a_deck_for_this_war_battle():
        logger.change_status("Making a random deck for this war battle.")
        make_a_random_deck_for_this_war_battle()

    # sometimes the player lacks the cards to make a complete deck at this point
    # if you STILL done have a deck, return to main
    if not check_if_has_a_deck_for_this_war_battle():
        logger.change_status("Not enough cards to complete this deck. Returning.")
        for _ in range(5):
            click(20, 440)
        get_to_clash_main_from_clan_page(logger)
        return None

    # click start battle
    click(280, 445)
    time.sleep(5)

    # wait for the match to load
    if wait_for_war_battle_loading(logger) == "restart":
        logger.change_status(
            "Waiting for war battle loading took too long. Restarting."
        )
        return "restart"

    # fight for the duration of the war match (losses do not matter)
    if fight_war_battle(logger) == "restart":
        logger.change_status("Failure in war battle fight. Restarting.")
        return "restart"

    # exit battle
    logger.change_status("Exiting war battle")
    click(215, 585)
    time.sleep(10)

    logger.add_war_battle_fought()

    # get to clash main
    if get_to_clash_main_from_clan_page(logger) == "restart":
        logger.change_status("Failed getting to clash main from clan page")
        return "restart"
    return None


def fight_war_battle(logger):
    logger.change_status("Throwing war match")
    loops = 0
    while check_if_in_battle_with_delay():
        loops += 1
        if loops > 100:
            logger.change_status("Fought in war too long. Returning")
            return "restart"

        # click random card
        click(random.randint(125, 355), 585)
        time.sleep(1)

        # click random placement
        click(random.randint(70, 355), random.randint(320, 490))
        time.sleep(1)

    time.sleep(9)


def make_a_random_deck_for_this_war_battle():
    # Click edit deck
    click(155, 450)
    time.sleep(1)

    # click random deck button
    click(265, 495)
    time.sleep(1)

    # click close
    click(205, 95)
    time.sleep(1)


def check_if_on_war_page():
    iar = numpy.asarray(screenshot())
    pix_list = [
        iar[73][43],
        iar[83][43],
    ]
    color = [232, 225, 236]
    return all(pixel_is_equal(pix, color, tol=45) for pix in pix_list)


def get_to_war_page_from_main(logger):
    if check_if_on_war_page():
        return None

    click(315, 635)
    click(315, 635)
    time.sleep(2)

    loops = 0
    while not check_if_on_war_page():
        loops += 1
        if loops > 20:
            logger.change_status("failure getting to war page.")
            return "restart"
        click(280, 620)
        time.sleep(1)
    return None


def find_battle_icon_on_war_page():
    current_image = screenshot()
    reference_folder = "look_for_battle_on_war_page"

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


def click_war_icon():
    loops = 0
    coord = find_battle_icon_on_war_page()
    while coord is None:
        loops += 1
        if loops > 8:
            return "failed"

        if random.randint(0, 1) == 0:
            scroll_up_super_fast()
        else:
            scroll_down_super_fast()
        time.sleep(3)
        coord = find_battle_icon_on_war_page()
    click(coord[0], coord[1])
    return "success"


def check_if_has_a_deck_for_this_war_battle():
    iar = numpy.asarray(screenshot())
    pix_list = [
        # iar[435][250],
        iar[437][275],
        iar[441][300],
    ]
    color = [254, 199, 79]

    # for pix in pix_list:
    #     print(pix[0], pix[1], pix[2])

    return all(pixel_is_equal(pix, color, tol=45) for pix in pix_list)


def check_if_loading_war_battle():
    iar = numpy.asarray(screenshot())
    pix_list = [
        iar[435][150],
        iar[438][215],
        iar[442][245],
        iar[446][270],
    ]

    # print_pix_list(pix_list)

    color = [249, 99, 99]
    return all(pixel_is_equal(pix, color, tol=45) for pix in pix_list)


def wait_for_war_battle_loading(logger):
    logger.change_status("Waiting for war battle loading")
    loops = 0
    while check_if_loading_war_battle():
        loops += 1
        if loops > 100:
            logger.change_status("Waited for war battle loading too long. Restarting.")
            return "restart"
        time.sleep(0.5)
    time.sleep(4)
    logger.change_status("Done waiting for battle to load.")
