import time

import numpy
from ahk import AHK

from pyclashbot.detection import pixel_is_equal
from pyclashbot.memu import click, screenshot

ahk = AHK()


def check_for_battlepass_reward_pixels():
    # starts and ends on clash main
    iar = numpy.asarray(screenshot())

    pix_list = [
        iar[156][263],
        iar[188][264],
        iar[191][355],
        iar[157][354],
    ]
    color = [240, 180, 20]

    return all(pixel_is_equal(pix, color, tol=45) for pix in pix_list)


def check_if_has_battlepass_rewards():
    timer = 0
    while not (check_for_battlepass_reward_pixels()):

        if timer > 0.36:
            return False
        timer += 0.02
        time.sleep(0.02)
    return True


def collect_battlepass_rewards(logger):
    logger.change_status("Collecting battlepass rewards.")
    chest_locations = [
        [300, 280],
        [300, 340],
        [300, 380],
        [300, 430],
        [300, 480],
        [300, 540],
    ]

    loops = 0
    while check_if_has_battlepass_rewards():

        if loops > 15:
            return "restart"
        loops += 1

        # click battlepass
        click(315, 165)

        # click chest locations
        for coord in chest_locations:
            ahk.click(coord[0], coord[1])
            time.sleep(0.1)

        # click deadspace
        for _ in range(15):
            ahk.click(20, 440)
            time.sleep(0.1)

        # close battlepass to reset UI
        click(210, 630)
        time.sleep(1)

        logger.add_battlepass_rewards_collection()

    logger.change_status("Done collecting battlepass rewards.")
    return "clashmain"
