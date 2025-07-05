import random
import time

import numpy

from pyclashbot.bot.nav import check_if_on_clash_main_menu
from pyclashbot.detection.image_rec import (
    find_references,
    get_file_count,
    get_first_location,
    make_reference_image_list,
    pixel_is_equal,
)
from pyclashbot.google_play_emulator.gpe import click, screenshot

from pyclashbot.utils.logger import Logger


def collect_battlepass_state( logger, next_state):
    if not check_if_on_clash_main_menu():
        logger.change_status(
            "Not on clash main before collecting battlepass, returning restart",
        )
        return "restart"

    if collect_battlepass( logger) is False:
        logger.change_status(
            "Failed somewhere in collect_battlepass(), returning restart",
        )
        return "restart"

    if not check_if_on_clash_main_menu():
        logger.change_status(
            "Not on clash main after collecting battlepass, returning restart",
        )
        return "restart"

    return next_state


def check_for_battlepass_reward_icon():
    iar = numpy.asarray(screenshot())

    pixels = [
        iar[125][286],
        iar[126][387],
    ]
    colors = [
        [0, 180, 248],
        [0, 178, 247],
    ]

    for i, p in enumerate(pixels):

        if not pixel_is_equal(colors[i], p, tol=10):
            return False

    return True


def check_if_on_battlepass_page():
    iar = numpy.asarray(screenshot())

    pixels = [
        iar[594][180],
        iar[606][234],
        iar[590][235],
        iar[599][213],
    ]
    colors = [
        [250, 185, 107],
        [254, 174, 80],
        [254, 184, 107],
        [250, 254, 255],
    ]

    for i, p in enumerate(pixels):

        if not pixel_is_equal(colors[i], p, tol=10):
            return False

    return True


def collect_battlepass( logger) -> bool:
    logger.change_status("Collecting battlepass rewards...")

    if not check_for_battlepass_reward_icon():
        logger.change_status("No battlepass rewards to collect")
        return True

    # while rewards exist:
    while check_for_battlepass_reward_icon() is True:
        if collect_1_battlepass_reward( logger) is True:
            logger.change_status("Successfully collected a battlepass reward")
        else:
            logger.change_status("Failed to collect a battlepass reward")
        time.sleep(1)

    time.sleep(10)

    # if not on clash main, return false
    if check_if_on_clash_main_menu() is not True:
        logger.change_status("Not on clash main after claiming battlepass rewards")
        return False

    return True


def collect_1_battlepass_reward( logger):
    logger.change_status("Collecting a battlepass reward")

    # open battlepass
    click( 341, 123)
    time.sleep(5)

    # if there isnt a claim rewards button, click more rewards button
    timeout = 30  # s
    start_time = time.time()
    while time.time() - start_time < timeout:
        claim_rewards_coord = find_claim_battlepass_rewards_button_with_delay(
            delay=3,
        )

        if claim_rewards_coord is None:
            logger.change_status(
                "No claim rewards button, clicking more rewards button",
            )
            click( 70, 120)
            time.sleep(3)
            continue

        # if collect coord is too high, scroll a little and continue
        if claim_rewards_coord[1] < 160:
            logger.change_status("Claim rewards button too high, scrolling a little")
            scroll_up_a_little()
            time.sleep(3)

        # find the claim rewards button again
        claim_rewards_coord = find_claim_battlepass_rewards_button_with_delay(
            delay=3,
        )

        if claim_rewards_coord is None:
            logger.change_status(
                """This part needs attention. This logic was written forever ago
                and I cant tell if claim_rewards_coord is supposed to be None at
                this point, because it CAN be. Should it return False here? Or
                should it continue and try again? Can't tell. Returning False for
                safety."""
            )
            return False

        # claim the reward
        logger.change_status('Clicking "Claim Rewards" button')
        click(
            claim_rewards_coord[0],
            claim_rewards_coord[1],
            clicks=3,
            interval=0.5,
        )
        time.sleep(3)

        # click deadspace until back to battlepass page + a little extra ;)
        logger.log("Skipping thru this battlepass reward")
        while not check_if_on_battlepass_page():
            logger.log("Skipping thru this battlepass reward")
            click( 404, 33)
        click( 404, 33, clicks=5, interval=0.5)

        logger.log("Collected 1 battlepass reward")
        logger.increment_battlepass_collects()

        # click the OK button to return to clash main
        click( 206, 594)
        time.sleep(3)

        return True

    return False


def find_claim_battlepass_rewards_button_with_delay( delay):
    start_time = time.time()
    while time.time() - start_time < delay:
        coord = find_claim_battlepass_rewards_button()
        if coord is not None:
            return coord
        time.sleep(1)

    return None


def find_claim_battlepass_rewards_button():
    """Method to find the elixer price icon in a cropped image"""
    folder = "claim_battlepass_button"

    names = make_reference_image_list(get_file_count(folder))

    locations: list[list[int] | None] = find_references(
        screenshot(),
        folder,
        names,
        tolerance=0.85,
    )

    coord = get_first_location(locations)

    if coord is None:
        return None

    return [coord[1], coord[0]]


if __name__ == "__main__":
    pass
