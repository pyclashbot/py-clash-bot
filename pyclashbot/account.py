import time

from pyclashbot.client import check_quit_key_press, click
from pyclashbot.state import wait_for_clash_main_menu


def switch_accounts_to(logger, ssid):
    check_quit_key_press()

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
