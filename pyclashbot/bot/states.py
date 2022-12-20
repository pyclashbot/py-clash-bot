import random
import time
from typing import Literal

from pyclashbot.bot.battlepass_rewards_collection import collect_battlepass_rewards
from pyclashbot.bot.card_mastery_collection import collect_card_mastery_rewards
from pyclashbot.bot.clashmain import (
    check_if_in_a_clan,
    check_if_in_battle_with_delay,
    check_if_on_clash_main_menu,
    get_to_account,
    handle_card_mastery_notification,
    open_chests,
    start_2v2,
    verify_ssid_input,
    wait_for_battle_start,
)
from pyclashbot.bot.daily_challenge_reward_collection import (
    collect_daily_challenge_rewards,
)
from pyclashbot.bot.deck import randomize_and_select_deck_2
from pyclashbot.bot.fight import check_if_past_game_is_win, do_fight
from pyclashbot.bot.free_offer_collection import collect_free_offer_from_shop
from pyclashbot.bot.level_up_reward_collection import collect_level_up_rewards
from pyclashbot.bot.navigation import (
    check_if_on_clan_page,
    check_if_on_first_card_page,
    get_to_card_page,
    get_to_clash_main_from_card_page,
    get_to_clash_main_from_clan_page,
    leave_end_battle_window,
    wait_for_clash_main_menu,
)
from pyclashbot.bot.request import request_random_card_from_clash_main
from pyclashbot.bot.upgrade import upgrade_current_cards
from pyclashbot.bot.war import (
    check_if_has_a_deck_for_this_war_battle,
    click_war_icon,
    handle_war_attacks,
    make_a_random_deck_for_this_war_battle,
    wait_for_war_battle_loading,
)
from pyclashbot.memu import click, orientate_terminal
from pyclashbot.memu.launcher import restart_memu
from pyclashbot.utils import Logger




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




    if state == "intro":
        print("RUNNING INTRO STATE")
        logger.change_status("Running first startup sequence.")
        state = state_restart(logger)


    elif state == "restart":
        logger.change_status("Restarting because bot failed at some point. . .")

        # increment the restart_after_failure counter
        logger.add_restart_after_failure()

        # DEBUG::: wait forever instead of restarting
        # while True:time.sleep(1000)
        clip_that()

        # run restart state
        state = state_restart(logger)


    elif state == "auto_restart":
        logger.change_status("Doing automatic hourly restart. . .")

        # increment auto restart counter
        logger.add_auto_restart()

        # restart
        state = state_restart(logger)


    elif state == "account_switching":
        state,ssid = state_account_switching(logger,ssid,ssid_max)


    elif state=="chest_reward_collection":
        if "Open Chests" not in jobs: state = "free_offer_collection"
        else: state = state_chest_reward_collection(logger)


    elif state == "free_offer_collection":
        if "free offer collection" in jobs:
            state = state_free_offer_collection(logger)
        else:
            state = "daily_challenge_reward_collection"

        # if this time - most recent time in restart_log is more than an hour, always pass to restart
        if abs(logger.most_recent_restart_time - time.time()) > 3600:
            state = "auto_restart"


    elif state == "daily_challenge_reward_collection":
        if "daily challenge reward collection" in jobs: state = state_daily_challenge_reward_collection(logger)
        else: state = "battlepass_reward_collection"


    elif state == "battlepass_reward_collection":
        state = (
            state_battlepass_collection(logger)
            if "battlepass reward collection" in jobs
            else "level_up_reward_collection"
        )


    elif state == "level_up_reward_collection":
        state = (
            state_level_up_reward_collection(logger)
            if "level up reward collection" in jobs
            else "card_mastery_reward_collection"
        )

    
    elif state == "card_mastery_reward_collection":
        state = (
            state_card_mastery_collection(logger)
            if "card mastery collection" in jobs
            else "request"
        )


    elif state == "request":
        state = (
            state_request(logger) if "Request" in jobs else "upgrade"
        )


    elif state == "upgrade":
        state = (
            state_upgrade(logger) if "Upgrade" in jobs else "deck_randomization"
        )


    elif state == "deck_randomization":
        if "Randomize Deck" in jobs:random_deck_bool=True
        else:random_deck_bool=False
        state = (
            state_deck_randomization(logger,random_deck_bool)
            if "Randomize Deck" in jobs
            else "start_fight"
        )


    elif state == "start_fight":
        state = (
            state_startfight(logger, random_deck="Randomize Deck" in jobs)
            if "Fight" in jobs
            else "war"
        )


    elif state == "fighting":
        state = state_fight(logger)


    elif state == "endfight":
        state = state_endfight(logger)


    elif state == "war":
        state = (
            state_war(logger) if "war" in jobs else "account_switching"
        )

    
    return (state, ssid)


def state_restart(logger) -> Literal["account_switching", "restart"]:
    print("state is :state_restart")
    # Method for the restart state of the program

    # Restart state restarts Memu and MeMU Multi Manager, opens clash, and waits for the clash main menu to appear.

    # update most recent restart time
    logger.change_most_recent_restart_time(int(time.time()))

    # orietate gui
    orientate_terminal()
    logger.change_status("Restarting")

    # restart until it works, then return 'clashmain' as the next state
    if restart_memu(logger) == "restart":
        return "restart"
    else:
        return "account_switching"

def state_account_switching(logger,ssid,ssid_max) -> Literal["chest_reward_collection", "restart"]:
    print("state is :state_account_switching")
    
    logger.change_status("Switching accounts. . .")

    # Get to correct account if more than one account is being used
    if ssid_max > 1 and get_to_account(logger, account_number=ssid) == "restart":
        print("Failure with get_to_account() in state_clashmain()")
        return "restart"

    ssid = ssid + 1 if ssid < (ssid_max - 1) else 0
    
    return "chest_reward_collection",ssid

def state_chest_reward_collection(logger) -> Literal["free_offer_collection", "restart"]:
    print("state is :state_chest_reward_collection")
    
    if not check_if_on_clash_main_menu():
        print("Not on clash main menu at start of state_chest_reward_collection, restarting")
        return "restart"
    

    open_chests(logger)

    if not check_if_on_clash_main_menu():
        print("Not on clash main menu at end of state_chest_reward_collection, restarting")
        return "restart"

    return "free_offer_collection"

def state_free_offer_collection(logger) -> Literal["restart", "daily_challenge_reward_collection"]:
    print("state is :state_free_offer_collection")
    
    if collect_free_offer_from_shop(logger) == "restart":
        print("Fail in collect_free_offer_from_shop()")
        return "restart"
    return "daily_challenge_reward_collection"

def state_daily_challenge_reward_collection(logger,) -> Literal["restart", "battlepass_reward_collection"]:
    print("state is :state_daily_challenge_reward_collection")
    
    return collect_daily_challenge_rewards(logger)

def state_battlepass_collection(logger) -> Literal["restart", "level_up_reward_collection"]:
    print("state is :state_battlepass_collection")
    
    if collect_battlepass_rewards(logger) == "restart":
        print("Failure with collect_battlepass_rewards()")
        return "restart"
    else:
        return "level_up_reward_collection"

def state_level_up_reward_collection(logger,) -> Literal["restart", "card_mastery_reward_collection"]:
    print("state is :state_level_up_reward_collection")
    
    # Method for level up reward collection state of the program

    # state_level_up_reward_collection state starts on clash main and ends on clash main
    if collect_level_up_rewards(logger) == "restart":
        print("Failure with collect_level_up_rewards()")
        return "restart"
    return "card_mastery_reward_collection"

def state_card_mastery_collection(logger) -> Literal["restart", "request"]:
    print("state is :state_card_mastery_collection")
    
    # Method for the card mastery collection state of the program

    # card_mastery_collection state starts on clash main and ends on clash main
    if collect_card_mastery_rewards(logger) == "restart":
        print("Failure with collect_card_mastery_rewards()")
        return "restart"
    return "request"

def state_request(logger) -> Literal["restart", "upgrade"]:
    print("state is :state_request")
    
    # Method for the state of the program when requesting cards
    # Request method goes to clan page, requests a random card if request is
    # available, then returns to the clash royale main menu

    logger.change_status("Requesting card")
    if request_random_card_from_clash_main(logger) == "restart":
        print("Failure with request_random_card_from_clash_main() in state_request()")
        return "restart"

    return "upgrade"

def state_upgrade(logger) -> Literal["restart", "deck_randomization"]:
    print("state is :state_upgrade")
    
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

    return "deck_randomization"

def state_deck_randomization(logger,random_deck_bool) -> Literal["restart", "start_fight"]:
    print("state is :state_deck_randomization")
    
    if random_deck_bool and randomize_and_select_deck_2(logger) == "restart":
        print("Failure with randomize_and_select_deck_2() in state_startfight()")
        return "restart"
    else:return "start_fight"

def state_startfight(logger, random_deck=True) -> Literal["restart", "fighting"]:
    print("state is :state_startfight")
    
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
    print("state is :state_fight")
    
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

def state_endfight(logger) -> Literal["war"]:
    print("state is :state_endfight")
    
    # Method for the state of the program after a fight

    # Checks if the last battle was a win or loss then adds this to the logger tally
    # Starts and ends on the clash royale main menu

    check_if_past_game_is_win(logger)
    return "war"

def state_war(logger) -> Literal["restart", "account_switching"]:
    print("state is :state_war")
    
    if handle_war_attacks(logger) == "restart":
        print("Failure with handle_war_attacks()")
        return "restart"
    else:
        return "account_switching"




#FOR OBS RECORDING OF ERRORS 
# def clip_that():
#     import pyautogui

#     #press key combination
#     pyautogui.keyDown("ctrl")
#     pyautogui.keyDown("shift")
#     time.sleep(0.33)
#     pyautogui.keyDown("r")
#     time.sleep(0.33)

#     #unpress
#     pyautogui.keyUp("r")
#     pyautogui.keyUp("ctrl")
#     pyautogui.keyUp("shift")
    
#     print("Clipped this error!")

    







