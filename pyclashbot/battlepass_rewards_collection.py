import time
from pyclashbot.client import screenshot

import numpy

from pyclashbot.image_rec import pixel_is_equal


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

    for pix in pix_list:
        if not pixel_is_equal(pix, color, tol=45):
            return False
    return True


def check_if_has_battlepass_rewards():
    timer = 0
    while not (check_for_battlepass_reward_pixels()):
        # print(timer)
        if timer > 0.36:
            return False
        timer += 0.02
        time.sleep(0.02)
    return True
