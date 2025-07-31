import time

import numpy

from pyclashbot.bot.nav import check_if_on_clash_main_menu
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.utils.logger import Logger

BANNERBOX_ICON_ON_CLASH_MAIN_PAGE = (350, 195)
FIRST_100_TICKETS_PURCHASE_BUTTON = (303, 576)
SECOND_100_TICKETS_PURCHASE_BUTTON = (209, 466)
CLASH_MAIN_DEADSPACE_COORD = (20, 520)


def check_if_bannerbox_icon_have_a_star(vm_index):
    iar = numpy.asarray(screenshot(vm_index))

    pixels = [
        iar[194][353],
        iar[188][353],
    ]
    colors = [
        [2, 199, 255],
        [2, 98, 176],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(colors[i], p, tol=10):
            return False

    return True


def collect_bannerbox_rewards_state(vm_index: int, logger: Logger, next_state: str):
    # if not in clash main, return false
    if check_if_on_clash_main_menu(emulator) is not True:
        logger.change_status("Not in clash main menu")
        return "restart"

    # if bannerbox rewards are done, return True
    if not check_if_bannerbox_icon_exists_on_clashmain(vm_index):
        logger.change_status(
            "Account doesn't have bannerbox icon. Skipping bannerbox rewards",
        )
        return next_state

    if collect_bannerbox_rewards(vm_index, logger):
        return next_state
    return "restart"


def collect_bannerbox_rewards(vm_index, logger: Logger) -> bool:
    logger.change_status("Trying to open bannerbox rewards...")

    # Open bannerbox button on clash main
    click(
        vm_index,
        BANNERBOX_ICON_ON_CLASH_MAIN_PAGE[0],
        BANNERBOX_ICON_ON_CLASH_MAIN_PAGE[1],
    )
    time.sleep(4)

    # if 100 tickets button is greyed, then we've collected all the banners this season
    if check_for_collected_all_bannerbox_rewards_icon(vm_index):
        logger.change_status("Already collected all bannerbox rewards this season.")

        # click deadspace to get back to main
        emulator.click(5, 450, clicks=4, interval=1)

        # if not back on main, return False
        if check_if_on_clash_main_menu(emulator) is not True:
            logger.change_status(
                "Failed to return to main after being maxed on bannerboxes. Restarting",
            )
            return False

        return True

    # click the '100 tickets' purchase button
    click(
        vm_index,
        FIRST_100_TICKETS_PURCHASE_BUTTON[0],
        FIRST_100_TICKETS_PURCHASE_BUTTON[1],
    )
    time.sleep(4)

    # check if the second '100 tickets' purchase button is Red or not
    if not check_if_can_purchase_100_tickets_bannerbox(vm_index):
        logger.change_status("Bannerbox not available.")

        # click deadspace a bunch, then return
        emulator.click(1, 500, clicks=10, interval=0.33)
        return True

    logger.change_status("Bannerbox is available! Buying it...")

    # click the second '100 tickets' purchase button
    click(
        vm_index,
        SECOND_100_TICKETS_PURCHASE_BUTTON[0],
        SECOND_100_TICKETS_PURCHASE_BUTTON[1],
    )
    logger.add_bannerbox_collect()

    # click deadspace until back on clash main
    logger.change_status("Skipping through bannerbox rewards...")
    deadspace_click_timeout = 30  # s
    deadspace_click_start_time = time.time()
    while check_if_on_clash_main_menu(emulator) is not True:
        # timeout check
        if time.time() - deadspace_click_start_time > deadspace_click_timeout:
            return False

        # click deadspace
        emulator.click(
            CLASH_MAIN_DEADSPACE_COORD[0],
            CLASH_MAIN_DEADSPACE_COORD[1],
            clicks=5,
            interval=0.33,
        )

    # return true if everything went well
    return True


def check_for_collected_all_bannerbox_rewards_icon(vm_index):
    iar = numpy.asarray(screenshot(vm_index))

    pixels = [
        iar[570][288],
        iar[587][353],
        iar[589][289],
        iar[563][296],
        iar[576][282],
    ]
    colors = [
        [36, 36, 36],
        [194, 189, 195],
        [190, 190, 190],
        [201, 202, 207],
        [252, 252, 252],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(colors[i], p, tol=10):
            return False
    return True


def check_if_bannerbox_icon_exists_on_clashmain(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[181][350],
        iar[190][334],
        iar[195][345],
        iar[220][364],
        iar[229][378],
        iar[240][400],
    ]

    colors = [
        [150, 113, 33],
        [178, 133, 43],
        [169, 126, 37],
        [150, 102, 28],
        [143, 104, 31],
        [128, 89, 22],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, colors[i], tol=35):
            return True

    return False


def check_if_can_purchase_100_tickets_bannerbox(vm_index):
    iar = emulator.screenshot()

    pixels = [
        iar[467][172],
        iar[473][172],
        iar[468][188],
    ]

    for p in pixels:
        if not check_if_pixel_is_red(p):
            return True

    return False


def check_if_pixel_is_red(p):
    r = p[2]
    g = p[1]
    b = p[0]

    # if r is less than 150, return False
    if r < 150:
        return False

    # if g is more than 50, return False
    if g > 50:
        return False

    # if b is more than 50, return False
    if b > 50:
        return False

    return True


if __name__ == "__main__":
    pass
