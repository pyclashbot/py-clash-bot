import random
from pyclashbot.detection.image_rec import (
    make_reference_image_list,
    get_file_count,
    find_references,
    get_first_location,
)
from pyclashbot.bot.nav import check_if_on_clash_main_menu
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.utils.logger import Logger
import numpy
from pyclashbot.memu.client import screenshot, click
import time


def collect_battlepass_state(vm_index, logger, next_state):
    if collect_battlepass(vm_index, logger) is False:
        logger.change_status(
            "Failed somewhere in collect_battlepass(), returning restart"
        )
        return "restart"

    return next_state


def check_for_battlepass_reward_icon_with_delay(vm_index, delay):
    start_time = time.time()
    while time.time() - start_time < delay:
        if check_for_battlepass_reward_icon(vm_index):
            return True
        time.sleep(1)

    return False


def check_for_battlepass_reward_icon(vm_index):
    iar = numpy.asarray(screenshot(vm_index))

    pixels = [
        iar[125][286],
        iar[126][387],
    ]
    colors = [
        [0, 180, 248],
        [0, 178, 247],
    ]

    for i, p in enumerate(pixels):
        # print(p)
        if not pixel_is_equal(colors[i], p, tol=10):
            return False

    return True


def check_if_on_battlepass_page(vm_index):
    iar = numpy.asarray(screenshot(vm_index))

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
        # print(p)
        if not pixel_is_equal(colors[i], p, tol=10):
            return False

    return True


def collect_battlepass(vm_index, logger):
    logger.change_status("Collecting battlepass rewards...")

    # if not on main to begin, return False
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            "Not on clash main to being battlepass collection. returning False"
        )
        return False

    if not check_for_battlepass_reward_icon_with_delay(vm_index, delay=3):
        logger.change_status("No battlepass rewards to collect")
        return True

    # while rewards exist:
    while check_for_battlepass_reward_icon_with_delay(vm_index, delay=3) is True:
        if collect_1_battlepass_reward(vm_index, logger) is True:
            logger.change_status("Successfully collected a battlepass reward")
        else:
            logger.change_status("Failed to collect a battlepass reward")

    # if not on clash main, return false
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status("Not on clash main after claiming battlepass rewards")
        return False

    return True


def collect_1_battlepass_reward(vm_index, logger):
    logger.change_status("Collecting a battlepass reward")

    # open battlepass
    click(vm_index, 341, 123)
    time.sleep(5)

    # if there isnt a claim rewards button, click more rewards button
    timeout = 30  # s
    start_time = time.time()
    while time.time() - start_time < timeout:
        claim_rewards_coord = find_claim_battlepass_rewards_button_with_delay(
            vm_index, delay=3
        )
        if claim_rewards_coord is None:
            logger.change_status(
                "No claim rewards button, clicking more rewards button"
            )
            click(vm_index, 70, 120)
            time.sleep(3)
            continue

        # claim the reward
        logger.change_status('Clicking "Claim Rewards" button')
        click(vm_index, claim_rewards_coord[0], claim_rewards_coord[1])
        time.sleep(1)

        # click deadspace until back to battlepass page
        logger.log("Skipping thru this battlepass reward")
        while not check_if_on_battlepass_page(vm_index):
            if random.randint(1, 5):
                logger.log("Skipping thru this battlepass reward")
            click(vm_index, 404, 33)

        logger.log("Collected 1 battlepass reward")
        logger.increment_battlepass_collects()

        # click the OK button to return to clash main
        click(vm_index, 206, 594)
        time.sleep(3)

        return True

    return False


def find_claim_battlepass_rewards_button_with_delay(vm_index, delay):
    start_time = time.time()
    while time.time() - start_time < delay:
        coord = find_claim_battlepass_rewards_button(vm_index)
        if coord is not None:
            return coord
        time.sleep(1)

    return None


def find_claim_battlepass_rewards_button(vm_index):
    """method to find the elixer price icon in a cropped image"""

    folder = "claim_battlepass_button"

    names = make_reference_image_list(get_file_count(folder))

    locations: list[list[int] | None] = find_references(
        screenshot(vm_index),
        folder,
        names,
        tolerance=0.85,
    )

    coord = get_first_location(locations)

    if coord is None:
        return None

    return [coord[1], coord[0]]


def check_for_more_rewards_button(vm_index):
    iar = numpy.asarray(screenshot(vm_index))

    pixels = [
        iar[115][72],
        iar[144][109],
        iar[118][118],
        iar[146][67],
    ]
    colors = [
        [63, 203, 254],
        [41, 182, 255],
        [65, 203, 252],
        [40, 183, 255],
    ]

    for i, p in enumerate(pixels):
        # print(p)
        if not pixel_is_equal(colors[i], p, tol=10):
            return False

    return True


if __name__ == "__main__":
    vm_index = 12
    logger = Logger(None)

    print(collect_battlepass_state(vm_index, logger, "next_state"))
