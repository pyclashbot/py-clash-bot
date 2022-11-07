import time

import numpy

from pyclashbot.bot.clashmain import check_if_on_clash_main_menu, get_to_card_page
from pyclashbot.detection import pixel_is_equal
from pyclashbot.memu import click, screenshot


def collect_card_mastery_rewards(logger):
    # starts on clash main, collects mastery rewards, returns to clash main
    logger.change_status("Collecting card mastery rewards")

    reward_coords = [
        [210, 360],
        [190, 450],
        [210, 520],
        [205, 480],
    ]

    # if no mastery rewards to collect return
    logger.change_status("Checking if there are card mastery rewards to collect")

    # check if there are rewards to collect
    has_rewards = check_if_can_collect_card_mastery_rewards(logger)

    # if reward to collect check fails return restart
    if has_rewards == "restart":
        return "restart"

    # if there are no rewards then return
    if not has_rewards:
        logger.change_status(
            "No card mastery rewards to collect. Returning to clash main."
        )
        if get_to_clash_main_from_card_page(logger) == "restart":
            return "restart"
        return None

    # otherwise there are rewards to collect so continue
    logger.change_status("There are card mastery rewards to collect!")

    # if made it to here, increment mastery reward collection counter
    logger.add_card_mastery_reward_collection()

    # get to card page
    if get_to_card_page(logger) == "restart":
        return "restart"

    # click mastery reward button
    click(257, 505)
    time.sleep(1)

    # click topleft most card in card mastery reward list
    click(104, 224)
    time.sleep(1)

    # click all reward regions
    for coord in reward_coords:
        click(coord[0], coord[1])
        time.sleep(1)

    # click dead space
    for _ in range(8):
        click(20, 400)

    # get back to clash main
    if get_to_clash_main_from_card_page(logger) == "restart":
        return "restart"

    return None


def check_if_can_collect_card_mastery_rewards(logger):
    # starts clash main , checks if there are mastery rewards, then returns to clash main

    # get to card page
    if get_to_card_page(logger) == "restart":
        return "restart"

    pixel = numpy.asarray(screenshot())[499][239]

    has_rewards = bool(pixel_is_equal(pixel, [255, 166, 13], tol=45))
    # return to cash main
    if get_to_clash_main_from_card_page(logger) == "restart":
        return "restart"

    return has_rewards


def get_to_clash_main_from_card_page(logger):
    # logger.change_status("Getting to Clash main menu from card page")

    # get to card page
    click(240, 627)
    time.sleep(1)

    loops = 0
    while not check_if_on_clash_main_menu():
        if loops > 15:
            logger.change_status("Couldn't get to Clash main menu from card page")
            return "restart"

        # if not on menu at this point cycle the screen off trophy progression page and back on
        click(212, 637)
        time.sleep(1)
