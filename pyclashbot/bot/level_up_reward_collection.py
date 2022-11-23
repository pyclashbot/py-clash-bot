import time

import numpy

from pyclashbot.bot.clashmain import check_if_on_clash_main_menu
from pyclashbot.detection import pixel_is_equal
from pyclashbot.memu import click, screenshot
from pyclashbot.memu.client import print_pix_list


def check_for_level_up_reward_pixels():
    """
    check_for_level_up_reward_pixels looks for level up reward icon pixels while on clash main menu

    :

    :return: bool: yes if rewards icon exists
    """
    iar = numpy.asarray(screenshot())

    pix_list = [
        iar[54][24],
        iar[53][9],
        iar[54][19],
    ]

    # print_pix_list(pix_list)

    color = [255, 173, 20]

    return all(pixel_is_equal(pix, color, tol=65) for pix in pix_list)


def check_if_has_level_up_rewards():
    """
    test_function spams the check_for_level_up_reward_pixels() pixel check a few
    times over a few seconds because the animation sometimes obstructs the pixels

    :return: bool: yes if rewards icon pixels existed anytime in the last 0.36 seconds
    """

    timer = 0
    while not check_for_level_up_reward_pixels():

        if timer > 0.36:
            return False
        timer += 0.02
        time.sleep(0.02)
    return True


def collect_level_up_rewards(logger):
    """
    test_function collect_level_up_rewards() checks if the level up reward icon exists,
    clicks icon, clicks chest, skips through chest rewards, then returns to clash main,
    all on a loop until the rewards icon no longer appears on the clash main menu
    :logger: logger from logger class initiaed in main

    :return: "restart" if any failure occurs, else "battlepass reward collection"
    """

    if not check_if_on_clash_main_menu():
        return "restart"

    # starts and ends on clash main
    logger.change_status("Collecting level up rewards.")
    loops = 0
    while True:
        loops += 1
        if loops > 20:
            logger.change_status(
                "Looped through level up reward collection too many times"
            )
            return "restart"

        # return when no more rewards to collect
        if not check_if_has_level_up_rewards():
            logger.change_status("No more level up rewards to collect.")
            return "battlepass reward collection"

        # click level up reward logo in top left
        click(17, 48)
        time.sleep(1)

        # click chest
        click(135, 160)

        # skip through rewards
        for _ in range(20):
            click(20, 450)
            time.sleep(0.33)

        logger.add_level_up_chest_collection()
