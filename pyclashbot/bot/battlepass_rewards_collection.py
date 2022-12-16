import time

import numpy
from ahk import AHK

from pyclashbot.bot.clashmain import check_if_on_clash_main_menu
from pyclashbot.detection import pixel_is_equal
from pyclashbot.memu import click, screenshot

ahk = AHK()


def check_for_battlepass_reward_pixels():
    # starts and ends on clash main
    iar = numpy.asarray(screenshot())

    pix_list = [
        iar[130][366],
        iar[135][373],
    ]
    color = [240, 180, 20]

    # print_pix_list(pix_list)

    return all(pixel_is_equal(pix, color, tol=45) for pix in pix_list)


def check_if_has_battlepass_rewards():
    timer = 0
    while not check_for_battlepass_reward_pixels():

        if timer > 0.36:
            return False
        timer += 0.02
        time.sleep(0.02)
    return True


def collect_battlepass_rewards(logger):
    logger.change_status("Collecting battlepass rewards.")

    # should be on clash main at this point
    if not check_if_on_clash_main_menu():
        print("Not on main so cant run collect_battlepass_rewards()")
        return "restart"

    # declare locations of reward coords
    chest_locations = [
        [300, 280],
        [300, 340],
        [300, 380],
        [300, 430],
        [300, 480],
        [300, 540],
        [125, 280],
        [125, 340],
        [125, 380],
        [125, 430],
        [125, 480],
        [125, 540],
    ]

    # loop until the battlepass rewards icon on the main menu indicates there are no more rewards
    loops = 0
    while check_if_has_battlepass_rewards():
        # if too many loops
        if loops > 15:
            logger.change_status("looped through collect battlepass too many times.")
            return "restart"
        loops += 1

        # click battlepass icon on clash main
        click(315, 165)
        time.sleep(1)

        # click every chest locations in the chest_locations list
        for coord in chest_locations:
            click(coord[0], coord[1], duration=0.1)
            time.sleep(0.33)

        # click deadspace
        for _ in range(15):
            click(20, 440, duration=0.1)
            time.sleep(0.1)

        # close battlepass to reset UI and return to clash main
        click(210, 630)
        time.sleep(1)

        # increment the battlepass reward collection counter
        logger.add_battlepass_reward_collection()

    logger.change_status("Done collecting battlepass rewards.")
    time.sleep(1)

    # should be on clash main at this point
    if check_if_on_clash_main_menu():
        return "clashmain"
    else:
        print(
            "Not on clash main at the end of collecting battlepass rewards loop. returning restart"
        )
        return "restart"
