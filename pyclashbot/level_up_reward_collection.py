import time
import numpy
from pyclashbot.clashmain import check_if_on_clash_main_menu

from pyclashbot.client import click, screenshot
from pyclashbot.image_rec import pixel_is_equal


def check_for_level_up_reward_pixels():
    # starts on clash main ends on clash main
    iar = numpy.asarray(screenshot())

    pix_list = [
        iar[58][7],
        iar[70][9],
    ]
    color = [255, 173, 20]



    return all(pixel_is_equal(pix, color, tol=65) for pix in pix_list)


def check_if_has_level_up_rewards():
    timer = 0
    while not (check_for_level_up_reward_pixels()):

        if timer > 0.36:
            return False
        timer += 0.02
        time.sleep(0.02)
    return True


def collect_level_up_rewards(logger):
    if not check_if_on_clash_main_menu():
        return "restart"

    # starts and ends on clash main
    logger.change_status("Collecting level up rewards.")
    while True:
        # return when no more rewards to collect
        if not check_if_has_level_up_rewards():
            logger.change_status("No more level up rewards to collect.")
            return "battlepass reward collection"

        # click level up reward logo in top left
        click(17, 65)

        # click chest
        click(135, 160)

        # skip through rewards
        for _ in range(20):
            click(20, 450)

        logger.add_level_up_chest_collection()
