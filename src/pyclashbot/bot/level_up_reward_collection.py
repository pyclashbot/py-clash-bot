import time

import numpy

from pyclashbot.bot.clashmain import check_if_on_clash_main_menu
from pyclashbot.detection import pixel_is_equal
from pyclashbot.memu import click, screenshot


def check_for_level_up_reward_pixels():
    """check_for_level_up_reward_pixels looks for level
    up reward icon pixels while on clash main menu

    returns:
        bool: yes if rewards icon exists
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
    """method that spams the check_for_level_up_reward_pixels() pixel check a
        few times over a few seconds because the animation sometimes obstructs the pixels

    returns:
        bool: yes if rewards icon pixels existed anytime in the last 0.36 seconds
    """

    timer = 0
    while not check_for_level_up_reward_pixels():
        if timer > 0.36:
            return False
        timer += 0.02
        time.sleep(0.02)
    return True


def collect_level_up_rewards(logger):
    """checks if the level up reward icon exists,clicks icon, clicks chest,
        skips through chest rewards, then returns to clash main,
        all on a loop until the rewards icon no longer appears on the clash main menu
    args:
        logger: logger from logger class initiaed in main

    returns:
        "restart" if any failure occurs, else "battlepass reward collection"
    """
    # starts and ends on clash main
    logger.change_status("Collecting level up rewards.")
    loops = 0

    # should be on clash main at this point
    if not check_if_on_clash_main_menu():
        logger.change_status("not on main so cant run collect_level_up_rewards()")
        return "restart"

    # loop until the level up rewards icon on the main menu indicates there are no more rewards
    while check_if_has_level_up_rewards():
        logger.change_status("Found level up rewards to collect...")

        # loop counter
        loops += 1
        if loops > 20:
            logger.change_status(
                "looped through check_if_has_level_up_rewards() too many times"
            )
            return "restart"

        # click logo in top left
        click(17, 48)
        time.sleep(1)

        # click chest
        click(135, 160)
        time.sleep(1)

        logger.change_status("Collecting this battlepass reward...")
        # click dead space to skip through rewards
        for _ in range(20):
            click(20, 450)
            time.sleep(0.33)

        # increment counter
        logger.add_level_up_chest_collection()

        # should be on clash main at this point, if not click deadspace a little, then check again.
        if not check_if_on_clash_main_menu():
            # try to get to main by clicking deadspace more
            for _ in range(20):
                click(20, 450)
                time.sleep(0.33)
            # if this didnt help getting to main then return restart
            if not check_if_on_clash_main_menu():
                logger.change_status(
                    "check_if_has_level_up_rewards() didnt finish "
                    "its loop on clash main. Restarting"
                )
                return "restart"
        logger.change_status("Done collecting level-up rewards.")
    return "continue"
