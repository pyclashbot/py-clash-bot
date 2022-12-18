import time

from pyclashbot.memu.client import click
from pyclashbot.memu.launcher import check_if_on_clash_main_menu


def collect_daily_challenge_rewards(logger):
    logger.change_status("Collecting daily challenge rewards...")

    # should be on clash main at this point
    if not check_if_on_clash_main_menu():
        logger.change_status(
            "Failure with state_collect_daily_challenge_rewards bc not on main at the start"
        )
        return "restart"

    # click daily challenge icon on clash main
    click(60, 230)
    time.sleep(1)

    # click first reward icon
    click(200, 225)
    time.sleep(1)

    # click second reward icon
    click(200, 285)
    time.sleep(1)

    # skip through a little bit of the rewards
    click(20, 540, clicks=10, interval=0.3)
    time.sleep(1)

    # reopen daily challenge tab
    click(60, 230)
    time.sleep(1)

    # click third reward icon
    click(200, 355)
    time.sleep(1)

    # click daily reward icon
    click(200, 440)
    time.sleep(1)

    # skip through thoroughly
    click(20, 540, clicks=20, interval=0.3)
    time.sleep(1)

    # reopen daily challenge tab
    click(60, 230)
    time.sleep(1)

    # click weekly reward icon
    click(220, 550)
    time.sleep(1)

    # skip through thoroughly
    click(20, 540, clicks=30, interval=0.3)
    time.sleep(1)

    logger.change_status("Done collecting daily challenge rewards...")

    # should be on clash main at this point
    if not check_if_on_clash_main_menu():
        logger.change_status(
            "Failure with state_collect_daily_challenge_rewards bc not on main at the start"
        )
        return "restart"

    return "free_offer_collection"
