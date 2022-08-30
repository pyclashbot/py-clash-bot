import time

from pyclashbot.client import check_quit_key_press, click, refresh_screen
from pyclashbot.image_rec import find_references, get_first_location
from pyclashbot.state import (check_if_on_trophy_progession_rewards_page,
                              return_to_clash_main_menu,
                              wait_for_clash_main_menu)


def switch_accounts_to(logger, ssid):
    check_quit_key_press()
    time.sleep(0.5)
    
    
    handle_gold_rush_event(logger)
    
    
    
    time.sleep(0.5)

    logger.log("Opening settings")
    click(x=364, y=99)

    time.sleep(3)
    check_quit_key_press()
    logger.log("Clicking switch button")
    click(x=198, y=401)

    time.sleep(3)
    check_quit_key_press()
    if ssid == 0:
        logger.log("Clicking account 1")
        click(x=211, y=388)
    if ssid == 1:
        logger.log("Clicking account 2")
        click(x=193, y=471)
    if ssid == 2:
        logger.log("Clicking account 3")
        click(x=200, y=560)

    time.sleep(3)
    if wait_for_clash_main_menu(logger) == "quit":
        return "quit"
    check_quit_key_press()

    # handling the various things notifications and such that need to be
    # cleared before bot can get going
    time.sleep(0.5)
    handle_gold_rush_event(logger)
    time.sleep(0.5)
    handle_new_challenge(logger)
    time.sleep(0.5)
    handle_special_offer(logger)
    time.sleep(0.5)


def check_for_gold_rush_event():
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
    ]
    locations = find_references(
        screenshot=refresh_screen(),
        folder="gold_rush_event",
        names=references,
        tolerance=0.97
    )
    loc = get_first_location(locations)
    if loc is None:
        return False
    return True


def handle_gold_rush_event(logger):
    logger.log(
        "Handling the possibility of a gold rush event notification obstructing the bot.")
    time.sleep(0.5)
    click(193, 465)
    time.sleep(0.2)
    click(193, 465)
    time.sleep(0.5)


def handle_new_challenge(logger):
    logger.log(
        "Handling the possibility of a new challenge notification obstructing the bot.")
    time.sleep(0.5)
    click(376, 639)
    time.sleep(0.5)
    click(196, 633)
    time.sleep(0.5)
    if check_if_on_trophy_progession_rewards_page():
        click(212, 633)
        time.sleep(0.5)


def handle_special_offer(logger):
    logger.log(
        "Handling the possibility of special offer notification obstructing the bot.")
    time.sleep(0.5)
    click(35, 633)
    time.sleep(0.5)
    click(242, 633)
    time.sleep(0.5)
    if check_if_on_trophy_progession_rewards_page():
        click(212, 633)
        time.sleep(0.5)
