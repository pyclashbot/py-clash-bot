import time

import numpy

from pyclashbot.bot.nav import (
    check_if_on_card_page,
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
    wait_for_clash_main_menu,
)
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.memu.client import click, screenshot
from pyclashbot.utils.logger import Logger


def card_mastery_state(, logger, next_state):
    logger.change_status("Going to collect card mastery rewards")

    if check_if_on_clash_main_menu() is not True:
        logger.change_status(
            'Not on clash main menu for card_mastery_state() returning "restart"',
        )
        return "restart"

    if collect_card_mastery_rewards(, logger) is False:
        logger.change_status(
            'Failed somewhere in collect_card_mastery_rewards(), returning "restart"',
        )
        return "restart"

    return next_state


def collect_card_mastery_rewards(, logger: Logger) -> bool:
    # get to card page
    logger.change_status("Collecting card mastery rewards...")
    if get_to_card_page_from_clash_main(, logger) == "restart":
        logger.change_status(
            "Failed to get to card page to collect mastery rewards! Returning false",
        )
        return False
    time.sleep(3)

    if not card_mastery_rewards_exist_with_delay():
        logger.change_status("No card mastery rewards to collect.")
        time.sleep(1)

    else:
        # while card mastery icon exists:
        while card_mastery_rewards_exist_with_delay():
            logger.change_status("Detected card mastery rewards")
            #   click card mastery icon
            collect_first_mastery_reward()
            logger.change_status("Collected a card mastery reward!")
            logger.add_card_mastery_reward_collection()
            time.sleep(2)

    # get to clash main
    logger.change_status("Returning to clash main menu")
    click(, 243, 600)

    # wait for main to appear
    if wait_for_clash_main_menu(, logger) is False:
        logger.change_status(
            "Failed to get back to clash main menu from card page! Returning false",
        )
        return False

    return True


def collect_first_mastery_reward():
    # click the card mastery reward icon
    click(, 362, 444)
    time.sleep(0.5)

    # click first card
    click(, 99, 166)
    time.sleep(0.5)

    # click rewards at specific Y positions
    y_positions = [316, 403, 488]
    for y in y_positions:
        click(, 200, y)
        time.sleep(1)
        if check_for_inventory_full_popup():
            print('Inventory full popup detected!\nClicking it')
            click(,260,420)
            time.sleep(1)

    # click deadspace
    ds = (14, 278)
    ds_click_timeout = 60  # s
    ds_start_time = time.time()
    while not check_if_on_card_page():
        click(, *ds)

        if time.time() - ds_start_time > ds_click_timeout:
            print("Clicked deadspace after collecting card mastery reward for too long")
            return False

    return True


def card_mastery_rewards_exist_with_delay():
    timeout = 2  # s
    start_time = time.time()
    while time.time() - start_time < timeout:
        if card_mastery_rewards_exist():
            return True

    return False


def card_mastery_rewards_exist():
    # Convert the screenshot to a NumPy array for easier access
    iar = numpy.asarray(screenshot())

    pixels = [
        iar[432][366],
        iar[432][376],
    ]

    target_color = [57, 9, 236]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, target_color, tol=10):
            return False

    return True

def check_for_inventory_full_popup():
    iar = screenshot()
    pixels = [
        iar[410][220],
        iar[420][225],
        iar[416][225],
        iar[418][230],
        iar[420][240],
        iar[430][250],
        iar[435][260],
        iar[427][270],
        iar[429][280],
        iar[435][290],
    ]
    # for p in pixels:print(p)
    colors = [
[255 ,187 ,105],
[255 ,187 ,105],
[255 ,187 ,105],
[244 ,233 ,220],
[60 ,52 ,43],
[255 ,175  ,78],
[255 ,175  ,78],
[255 ,255 ,255],
[241 ,165  ,74],
[255 ,175  ,78],
    ]
    for i, c in enumerate(colors):
        if not pixel_is_equal(c, pixels[i], tol = 15):
            return False
    return True


if __name__ == "__main__":
    collect_first_mastery_reward(1)
    # print('\n\n\n')
    # print(check_for_inventory_full_popup(1))
