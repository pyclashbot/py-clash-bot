import random
import time
from typing import Literal

from pyclashbot.bot.battlepass_rewards_collection import collect_battlepass_rewards
from pyclashbot.bot.card_mastery_collection import collect_card_mastery_rewards
from pyclashbot.bot.clashmain import (
    check_if_in_a_clan,
    check_if_in_battle_with_delay,
    check_if_on_clan_page,
    check_if_on_clash_main_menu,
    check_if_on_first_card_page,
    get_to_account,
    get_to_card_page,
    get_to_clash_main_from_card_page,
    get_to_clash_main_from_clan_page,
    handle_card_mastery_notification,
    open_chests,
    start_2v2,
    verify_ssid_input,
    wait_for_battle_start,
    wait_for_clash_main_menu,
)
from pyclashbot.bot.deck import randomize_and_select_deck_2
from pyclashbot.bot.fight import (
    check_if_end_screen_is_exit_bottom_left,
    check_if_end_screen_is_ok_bottom_middle,
    check_if_past_game_is_win,
    do_fight,
    leave_end_battle_window,
)
from pyclashbot.bot.free_offer_collection import collect_free_offer_from_shop
from pyclashbot.bot.level_up_reward_collection import collect_level_up_rewards
from pyclashbot.bot.request import request_random_card_from_clash_main
from pyclashbot.bot.upgrade import upgrade_current_cards
from pyclashbot.bot.war import (
    check_if_has_a_deck_for_this_war_battle,
    click_war_icon,
    get_to_war_page_from_main,
    handle_war_attacks,
    make_a_random_deck_for_this_war_battle,
    wait_for_war_battle_loading,
)
from pyclashbot.memu import click, orientate_terminal, restart_and_open_clash
from pyclashbot.memu.launcher import restart_clash_app
from pyclashbot.utils import Logger


def detect_state(logger):
    # Method for detecting the state of the client in a given moment
    # sourcery skip: extract-duplicate-method
    # if we're on clan page get back to clash main and return
    if check_if_on_clan_page():
        if get_to_clash_main_from_clan_page(logger) == "restart":
            logger.change_status("Failure getting to clash main from clan page")
            return "restart"
        time.sleep(1)
        return "clashmain"

    # if we're on card page get back to clash main and return
    if check_if_on_first_card_page():
        if get_to_clash_main_from_card_page(logger) == "restart":
            logger.change_status("failure getting to clash main from card page")
            return "restart"
        time.sleep(1)
        return "clashmain"

    # if we're in battle return fighting
    if check_if_in_battle_with_delay():
        return "fighting"

    # if we're on end fight screen condition 1 (exit in bottom left)
    if check_if_end_screen_is_exit_bottom_left():
        click(79, 625)
        time.sleep(1)
        if wait_for_clash_main_menu(logger) == "restart":
            logger.change_status("waited for clash main too long")
            return "restart"
        return "clashmain"

    # if we're on end fight screen condition 2 (OK in bottom middle)
    if check_if_end_screen_is_ok_bottom_middle():
        click(206, 594)
        time.sleep(1)
        if wait_for_clash_main_menu(logger) == "restart":
            logger.change_status("waited for clash main too long")
            return "restart"
        return "clashmain"

    # if none of these conditions are met return "restart"
    return "restart"


def state_tree(
    jobs: list[str],
    logger: Logger,
    ssid_max: int,
    ssid: int,
    state: str,
) -> tuple[str, int]:
    """
    Method for the state tree of the program

    Args:
        jobs (list[str]): List of jobs to be done
        logger (Logger): Logger object
        ssid (int): Session ID
        state (str): Current state of the program

    Returns:
        tuple[str, int]: Tuple of the next state and the next session ID
    """
    if state == "clashmain":

        state = state_clashmain(
            logger=logger, ssid_max=ssid_max, account_number=ssid, jobs=jobs
        )

        # Increment account number, loop back to 0 if it's ssid_max
        ssid = ssid + 1 if ssid < (ssid_max - 1) else 0

        # if ssid==ssid_max:
        #     ssid=0
        # else:ssid+=1

    elif state == "intro":
        print("RUNNING INTRO STATE")
        state = state_restart(logger)

    elif state == "startfight":
        state = (
            state_startfight(logger, random_deck="Randomize Deck" in jobs)
            if "Fight" in jobs
            else "upgrade"
        )

    elif state == "fighting":
        state = state_fight(logger)

    elif state == "endfight":
        state = state_endfight(logger)

    elif state == "upgrade":
        state = (
            state_upgrade(logger) if "Upgrade" in jobs else "card mastery collection"
        )

    elif state == "request":
        state = (
            state_request(logger) if "Request" in jobs else "level up reward collection"
        )

    elif state == "restart":
        logger.change_status("Restarting because bot failed at some point. . .")

        # increment the restart_after_failure counter
        logger.add_restart_after_failure()

        # run restart state
        state = state_restart(logger)

    elif state == "auto_restart":
        logger.change_status("Doing automatic hourly restart. . .")

        # increment auto restart counter
        logger.add_auto_restart()

        # restart
        state = state_restart(logger)

    elif state == "card mastery collection":
        state = (
            state_card_mastery_collection(logger)
            if "card mastery collection" in jobs
            else "request"
        )

    elif state == "level up reward collection":
        state = (
            state_level_up_reward_collection(logger)
            if "level up reward collection" in jobs
            else "battlepass reward collection"
        )

    elif state == "battlepass reward collection":
        state = (
            state_battlepass_collection(logger)
            if "battlepass reward collection" in jobs
            else "war"
        )

    elif state == "war":
        state = state_war(logger) if "war" in jobs else "free_offer_collection"

    elif state == "free_offer_collection":
        # if this time - most recent time in restart_log is more than an hour, always pass to restart
        this_time = time.time()
        difference = abs(logger.most_recent_restart_time - this_time)

        print("Its been", difference, " seconds since the last restart.")
        if difference > 3600:
            state_free_offer_collection(logger)
            print("FORCING AN AUTO RESTART BECAUSE ITS BEEN ", difference, " SECONDS")
            state = "auto_restart"

        elif "free offer collection" in jobs:
            print("Should be running free offer collection")
            state = state_free_offer_collection(logger)
        else:
            print("Skipping free offer collection")
            state = "clashmain"

    return (state, ssid)


def state_free_offer_collection(logger) -> Literal["restart", "clashmain"]:
    if collect_free_offer_from_shop(logger) == "restart":
        print("Fail in collect_free_offer_from_shop()")
        return "restart"
    return "clashmain"


def state_war(logger) -> Literal["restart", "free_offer_collection"]:
    if handle_war_attacks(logger) == "restart":
        print("Failure with handle_war_attacks()")
        return "restart"
    else:
        return "free_offer_collection"


def state_battlepass_collection(logger) -> Literal["restart", "war"]:
    if collect_battlepass_rewards(logger) == "restart":
        print("Failure with collect_battlepass_rewards()")
        return "restart"
    else:
        return "war"


def state_level_up_reward_collection(
    logger,
) -> Literal["restart", "battlepass reward collection"]:
    # Method for level up reward collection state of the program

    # state_level_up_reward_collection state starts on clash main and ends on clash main
    if collect_level_up_rewards(logger) == "restart":
        print("Failure with collect_level_up_rewards()")
        return "restart"
    return "battlepass reward collection"


def state_card_mastery_collection(logger) -> Literal["restart", "request"]:
    # Method for the card mastery collection state of the program

    # card_mastery_collection state starts on clash main and ends on clash main
    if collect_card_mastery_rewards(logger) == "restart":
        print("Failure with collect_card_mastery_rewards()")
        return "restart"
    return "request"


def state_restart(logger) -> Literal["clashmain", "restart"]:
    # Method for the restart state of the program

    # Restart state restarts Memu and MeMU Multi Manager, opens clash, and waits for the clash main menu to appear.

    # update most recent restart time
    logger.change_most_recent_restart_time(int(time.time()))

    # orietate gui
    orientate_terminal()
    logger.change_status("Restarting")

    # restart until it works, then return 'clashmain' as the next state
    if restart_and_open_clash(logger) == "restart":
        return "restart"
    else:
        return "clashmain"


def state_clashmain(
    logger, ssid_max, account_number, jobs
) -> Literal["restart", "startfight"]:
    # Method for the clash royale main menu state of the program

    # Clashmain state gets to the correct account of the current state then
    # opens their chests

    logger.change_status("On clash main")

    # verifying the amount of SSID accounts in this client is the same as the amount inputted into the gui
    # if ssid_max != 1:
    #     if verify_ssid_input(logger, inputted_ssid_max=ssid_max) == "failure":
    #         logger.change_status(
    #             "SSID inputted is not the same as the amount of accounts in this client!!!"
    #         )
    #         time.sleep(100000)
    #         return "restart"

    # Get to correct account if more than one account is being used
    if ssid_max > 1 and get_to_account(logger, account_number) == "restart":
        print("Failure with get_to_account() in state_clashmain()")
        return "restart"

    time.sleep(3)

    # Open chests
    if "Open Chests" in jobs:
        open_chests(logger)
    time.sleep(3)
    return "startfight"


def state_startfight(logger, random_deck=True) -> Literal["restart", "fighting"]:
    # Method for the starting of a fight state of the program

    # Begins on clash main, ends in the beginning of a fight

    logger.change_status("Starting a fight")

    # make a random deck
    if random_deck and randomize_and_select_deck_2(logger) == "restart":
        print("Failure with randomize_and_select_deck_2() in state_startfight()")
        return "restart"
    # Start 2v2 quickmatch
    if start_2v2(logger) == "restart" or wait_for_battle_start(logger) == "restart":
        print("Failure with start_2v2() in state_startfight()")
        return "restart"
    return "fighting"


def state_fight(logger) -> Literal["restart", "endfight"]:
    # Method for the state of the program when fighting

    # Method that plays cards with certain logic until the fight is over then
    # returns to the clash royale main screen

    logger.change_status("Fighting")
    logger.add_fight()

    if do_fight(logger) == "restart":
        print("Failure with do_fight() in state_fight()")
        return "restart"

    if leave_end_battle_window(logger) == "restart":
        print("Failure with leave_end_battle_window() in state_fight()")
        return "restart"
    return "endfight"


def state_endfight(logger) -> Literal["upgrade"]:
    # Method for the state of the program after a fight

    # Checks if the last battle was a win or loss then adds this to the logger tally
    # Starts and ends on the clash royale main menu

    logger.change_status("Post fight")

    check_if_past_game_is_win(logger)
    return "upgrade"


def state_upgrade(logger) -> Literal["restart", "card mastery collection"]:
    # Method for the state of the program when upgrading cards

    # Starts on the clash royale main menu and ends on the clash royale main
    # menu

    logger.change_status("Upgrading cards")

    handle_card_mastery_notification()

    # Get to card page
    if get_to_card_page(logger) == "restart":
        print("Failure with get_to_card_page() in state_upgrade()")
        return "restart"

    # Upgrade user cards
    upgrade_current_cards(logger)

    # return to clash main
    if get_to_clash_main_from_card_page(logger) == "restart":
        print("Failure with get_to_clash_main_from_card_page() in state_upgrade()")
        return "restart"

    return "card mastery collection"


def state_request(logger) -> Literal["restart", "level up reward collection"]:
    # Method for the state of the program when requesting cards
    # Request method goes to clan page, requests a random card if request is
    # available, then returns to the clash royale main menu

    logger.change_status("Requesting card")
    if request_random_card_from_clash_main(logger) == "restart":
        print("Failure with request_random_card_from_clash_main() in state_request()")
        return "restart"

    return "level up reward collection"


def state_restart_clash_app(logger):
    print("RUNNING RESTART CLASH APP STATE")

    # run restart clash from launcher.py
    if restart_clash_app(logger) != "success":
        print("FAILURE WITH RESTART CLASH APP")
        return "restart"
