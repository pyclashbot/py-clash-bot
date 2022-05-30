import time

from pyclashbot.client import check_quit_key_press, click, refresh_screen
from pyclashbot.image_rec import find_references, get_first_location
from pyclashbot.state import wait_for_clash_main_menu


def switch_accounts_to(logger, ssid):
    check_quit_key_press()
    time.sleep(0.5)
    handle_gold_rush_event()        
    time.sleep(0.5)

    logger.log("Opening settings")
    click(x=364, y=99)

    time.sleep(3)
    check_quit_key_press()
    logger.log("Clicking switch button")
    click(x=198, y=401)

    time.sleep(3)
    check_quit_key_press()
    if ssid == 1:
        logger.log("Clicking account 1")
        click(x=211, y=388)
    if ssid == 2:
        logger.log("Clicking account 2")
        click(x=193, y=471)
    if ssid == 3:
        logger.log("Clicking account 3")
        click(x=200, y=560)

    time.sleep(3)
    if wait_for_clash_main_menu(logger) == "quit":
        return "quit"
    check_quit_key_press()


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
    loc=get_first_location(locations)
    if loc is None:
        return False
    return True


def handle_gold_rush_event():
    time.sleep(0.5)
    if check_for_gold_rush_event():
        click(193,465)
        time.sleep(0.2)
        click(193,465)
        time.sleep(0.2)
    