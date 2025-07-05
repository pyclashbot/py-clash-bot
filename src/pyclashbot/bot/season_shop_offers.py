import random
import time

import numpy

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_challenges_tab_from_main,
    wait_for_clash_main_menu,
)
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.google_play_emulator.gpe import click, screenshot
from pyclashbot.utils.logger import Logger


def check_if_can_collect_season_shop_offers() -> bool:
    iar = numpy.asarray(screenshot())

    pixels = [
        iar[209][312],
        iar[208][333],
        iar[208][336],
        iar[208][338],
        iar[208][340],
        iar[208][343],
        iar[208][344],
        iar[208][346],
        iar[208][367],
    ]

    colors = [
        [55, 193, 43],
        [55, 193, 43],
        [153, 188, 150],
        [252, 254, 252],
        [18, 64, 14],
        [252, 254, 252],
        [173, 206, 170],
        [55, 193, 43],
        [55, 193, 43],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(colors[i], p, tol=35):
            return True

    return False


def click_random_season_shop_offer():
    x = random.randint(66, 354)
    y = random.randint(230, 512)
    click( x, y)


def check_for_purchase_confirmation_page() -> bool:
    iar = numpy.asarray(screenshot())
    pixels = [
        iar[166][326],
        iar[171][334],
        iar[169][342],
        iar[178][341],
        iar[179][327],
    ]
    colors = [
        [115, 107, 253],
        [255, 255, 255],
        [130, 130, 254],
        [68, 66, 253],
        [49, 49, 252],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(colors[i], p, tol=35):
            return False

    return True


def click_buy_season_shop_offer():
    click( 207, 425)


def season_shop_deadspace_click():
    click( 195, 91)


def close_season_shop_page():
    for _ in range(5):
        click( 361, 41)


def buy_season_shop_offers( logger: Logger):
    logger.change_status("Collecting season shop offers!")

    # open shop
    click( 328, 187)
    time.sleep(2)

    # while we have currency, keep buying
    while 1:
        # #either scroll up or scroll down
        # if random.randint(0,1)== 1:
        #     scroll( 200, 240, 200, 400)
        # else:
        #     scroll( 200, 400, 200, 240)

        # click a random offer
        logger.change_status("Clicking random season shop offer")
        click_random_season_shop_offer()
        time.sleep(2)

        # if purchase confirmation doesnt appear, that means we're out of money
        if not check_for_purchase_confirmation_page():
            logger.change_status("No more currency to buy season shop offers!")
            break

        # buy this random offer
        logger.change_status("Buying this random season shop offer")
        click_buy_season_shop_offer()
        logger.increment_season_shop_buys()
        time.sleep(1)

        # click deadspace to close the purchase confirmation
        logger.change_status("Bought this random season shop offer!")
        for _ in range(6):
            season_shop_deadspace_click()
            time.sleep(0.33)

    # get back to events page
    close_season_shop_page()

    # get back to clash main
    click( 182, 608)
    time.sleep(3)

    # if not on main by the end, return 'restart'
    if not check_if_on_clash_main_menu():
        logger.change_status("Not on clash main after buying season shop offers!")
        return False

    # otherwise return True for good return
    return True


def get_to_clash_main_from_event_page( logger: Logger) -> bool:
    cr_main_coord = (175, 600)
    click( *cr_main_coord)
    time.sleep(3)

    return wait_for_clash_main_menu( logger)


def collect_season_shop_offers_state( logger: Logger, next_state: str):
    # if not on main, return 'restart'
    if not check_if_on_clash_main_menu():
        logger.change_status("Not on clash main for collect_season_shop_offers_state()")

    # get to events tab
    get_to_challenges_tab_from_main( logger)
    time.sleep(3)

    # if cant collect rewards, return next_state
    if not check_if_can_collect_season_shop_offers():
        logger.change_status(
            f"Cant collect season shop offers. Returning next state as : {next_state}",
        )
        get_to_clash_main_from_event_page( logger)
        return next_state

    if not buy_season_shop_offers( logger):
        return "restart"

    return next_state


if __name__ == "__main__":
    # scroll(12, 200, 240, 200, 400)
    scroll(12, 200, 400, 200, 240)
