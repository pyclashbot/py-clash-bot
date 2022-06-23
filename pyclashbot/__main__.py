import random
import sys
import time
from itertools import cycle

import numpy
from matplotlib import pyplot as plt

from pyclashbot.account import switch_accounts_to
from pyclashbot.auto_update import auto_update
from pyclashbot.battlepass import check_if_can_collect_bp, collect_bp
from pyclashbot.board_scanner import find_enemy_2
from pyclashbot.card_mastery import (check_if_has_mastery_rewards,
                                     collect_mastery_rewards)
from pyclashbot.chest import check_if_has_chest_unlocking, open_chests
from pyclashbot.client import (check_if_windows_exist, check_quit_key_press,
                               orientate_bot_window, orientate_memu_multi,
                               orientate_window, restart_client)
from pyclashbot.donate import click_donates, getto_donate_page
from pyclashbot.fight import (check_if_past_game_is_win, fight_with_deck_list,
                              leave_end_battle_window, look_for_enemy_troops,
                              start_2v2, wait_for_battle_start)
from pyclashbot.logger import Logger
from pyclashbot.request import (check_if_can_request,
                                request_from_clash_main_menu)
from pyclashbot.state import (check_if_in_a_clan_from_main, check_if_in_battle,
                              check_if_on_clash_main_menu, check_state,
                              open_clash, return_to_clash_main_menu,
                              wait_for_clash_main_menu)
from pyclashbot.upgrade import getto_card_page, upgrade_cards_from_main_2


def post_fight_state(logger, ssids):
    logger.log("STATE=post_fight")
    logger.log("Back on clash main")
    if check_if_past_game_is_win(logger):
        logger.log("Last game was a win")
        logger.add_win()
    else:
        logger.log("Last game was a loss")
        logger.add_loss()
        # switch accounts feature

    ssid = next(ssids)
    log = "Next account is: " + str(ssid)
    logger.log(log)
    state = "clash_main"
    return ssid, state


def fighting_state(logger):
    logger.log("-----STATE=fighting-----")
    fightloops = 0
    while (check_if_in_battle()) and (fightloops < 100):
        check_quit_key_press()
        log = "Plays: " + str(fightloops)
        logger.log(log)
        logger.log("Scanning field.")
        enemy_troop_position = find_enemy_2()
        if enemy_troop_position is not None:
            logger.log(
                f"New enemy position alg found enemy coord to be around {enemy_troop_position[0]},{enemy_troop_position[1]}")
        logger.log("Choosing play.")
        fight_with_deck_list(enemy_troop_position)
        fightloops = fightloops + 1
    logger.log("Battle must be finished")
    time.sleep(10)
    leave_end_battle_window(logger)
    wait_for_clash_main_menu(logger)
    state = "post_fight"
    return state


def start_fight_state(logger):
    logger.log("-----STATE=start_fight-----")
    return_to_clash_main_menu()
    if start_2v2(logger) == "quit":
        # if couldnt find quickmatch button
        logger.log("Had problems finding 2v2 quickmatch button.")
        state = "restart"
    else:
        # if could find the quickmatch button
        if wait_for_battle_start(logger) == "quit":
            # if waiting for battle takes too long
            logger.log(
                "Waited too long for battle start. Restarting")
            state = "restart"
        else:
            # if battle started before wait was too long
            logger.log(
                "Battle has begun. Passing to fighting state")
            state = "fighting"
    return state


def upgrade_state(logger, enable_card_upgrade):
    if not enable_card_upgrade:
        logger.log(
            "Card upgrade is disabled. Passing to card_mastery_collection state.")
        state = "card_mastery_collection"
        return state

    logger.log("-----STATE=upgrade-----")
    # only run upgrade a third of the time because its fucking slow as shit
    # but what can u do yk?
    return_to_clash_main_menu()
    time.sleep(1)
    upgrade_cards_from_main_2(logger)
    time.sleep(1)
    return_to_clash_main_menu()
    logger.log("Finished with upgrading. Passing to card_mastery_collection state")
    state = "card_mastery_collection"
    return state


def card_mastery_collection_state(logger, enable_card_mastery_collection):
    if not enable_card_mastery_collection:
        logger.log(
            "Card_mastery_collection is disabled. Passing to battlepass collection state.")

    logger.log("Getting to card page")
    getto_card_page(logger)
    logger.log("Checking if mastery rewards are available.")
    if check_if_has_mastery_rewards():
        logger.log(
            "Mastery rewards are available. Running mastery collection alg.")
        collect_mastery_rewards(logger)
    logger.log("No mastery rewards are available.")
    logger.log(
        "Done with card mastery collection. Passing to battlepass collection state.")
    state = "battlepass"
    return state


def donate_state(logger, enable_donate):
    if not enable_donate:
        do_upgrade = 1 == random.randint(1, 3)
        if do_upgrade:
            logger.log("Donate is disabled. Passing to upgrade state")
            return "upgrade"
        else:
            logger.log("Donate is disabled. Passing to start_fight state")
            return "start_fight"

    logger.log("-----STATE=donate-----")
    logger.log("Checking if in a clan")
    time.sleep(2)
    do_upgrade = 1 == random.randint(1, 3)
    if check_if_in_a_clan_from_main(logger):
        logger.log("Starting donate alg.")
        time.sleep(2)
        if getto_donate_page(logger) == "quit":
            # if failed to get to clan chat page
            logger.log("Failed to get to clan chat page. Restarting")
            state = "restart"
        else:
            # if got to clan chat page
            logger.log(
                "Successfully got to clan chat page. Starting donate alg")
            click_donates(logger)
            if do_upgrade:
                logger.log("Done with donating. Passing to upgrade state")
                state = "upgrade"
            else:
                logger.log("Done with donating. Passing to start_fight state")
                state = "start_fight"
    else:
        logger.log("You're not in a clan. Skipping donate.")
        if do_upgrade:
            logger.log("Passing to upgrade state")
            state = "upgrade"
        else:
            logger.log("Passing to start_fight state")
            state = "start_fight"
    return state


def request_state(logger, card_to_request, enable_request=True):
    if not enable_request:
        logger.log("Request is disabled. Passing to donate state.")
        return "donate"

    logger.log("-----STATE=request-----")
    logger.log("Trying to get to donate page")
    if getto_donate_page(logger) == "quit":
        # if failed to get to clan chat page
        logger.log("Failed to get to clan chat page. Restarting")
        state = "restart"
    else:
        # if got to clan chat page
        log = "Trying to request " + str(card_to_request) + "."
        logger.log(log)
        if request_from_clash_main_menu(
                card_to_request, logger) == "quit":
            # if request failed
            log = "Failed to request " + str(card_to_request) + "."
            logger.log(log)
        logger.log("Done with requesting. Passing to donate state.")
        return_to_clash_main_menu()
        time.sleep(2)
        state = "donate"
    return state


def clash_main_state(logger, ssid):
    logger.log("-----STATE=clash_main-----")
    # account switch
    logger.log("Logging in to the correct account")
    if switch_accounts_to(logger, ssid) == "quit":
        # if switching accounts fails
        logger.log("Failed to switch accounts. Restarting")
        state = "restart"
    else:
        # if switching accounts works
        logger.log("Successfully switched accounts.")
        # open chests
        if check_if_on_clash_main_menu():
            logger.log(
                "Checking if a chest is being unlocked right now.")
            if not check_if_has_chest_unlocking():
                logger.log(
                    "Found no unlocking symbols. Opening chests.")
                open_chests(logger)
                time.sleep(2)
            logger.log("Checking if can request.")
            if check_if_can_request(logger):
                logger.log("Can request. Passing to request state.")
                state = "request"
            else:
                logger.log(
                    "Cannot request. Skipping request and passing to donate state.")
                state = "donate"
        else:
            logger.log("Not on clash main. Restarting.")
            state = "restart"
    return state


def restart_state(logger):
    logger.log("-----STATE=restart-----")
    logger.log("restart time loop")
    logger.log("Restarting menu client")
    orientate_window()
    time.sleep(0.2)
    orientate_memu_multi()
    time.sleep(0.2)
    orientate_bot_window(logger)
    time.sleep(0.2)
    restart_client(logger)
    if open_clash(logger) == "quit":
        state = "restart"
    else:
        if check_if_on_clash_main_menu():
            state = "clash_main"
        else:
            state = "restart"
    return state


def battlepass_state(logger, enable_battlepass_collection):
    if not enable_battlepass_collection:
        logger.log(
            "Battlepass collection is disabled. Passing to start_fight state.")

    logger.log("-----STATE=battlepass-----")
    logger.log("Handling battlepass rewards")
    if check_if_can_collect_bp():
        # if we can collect rewards
        logger.log("Battlepass rewards are available.")
        collect_bp(logger)
    else:
        logger.log("Battlepass rewards are unavailable. Continuing to a fight.")
    state = "start_fight"
    return state


def initialize_client(logger):
    if not check_if_windows_exist(logger):
        sys.exit()
    orientate_memu_multi()
    time.sleep(0.2)
    orientate_window()
    time.sleep(0.2)
    orientate_bot_window(logger)
    state = check_state(logger)
    if state is None:
        state = "restart"
    return state


def main_loop():
    # user vars
    # these will be specified thru the GUI, but these are the placeholders for
    # now.
    card_to_request = "giant"
    ssids = cycle([1, 2])  # change to which account positions to use
    enable_donate = True
    enable_card_mastery_collection = True
    enable_battlepass_collection = True
    enable_request = True
    enable_card_upgrade = True

    # loop vars
    # *not user vars, do not change*
    logger = Logger()
    ssid = next(ssids)
    state = initialize_client(logger)
    loop_count = 0

    while True:
        # will be true if installed update, needs feature to restart program
        installed_update = auto_update()
        logger.log(f"loop count: {loop_count}")
        if state == "restart":
            state = restart_state(logger)
        if state == "clash_main":
            state = clash_main_state(logger, ssid)
        if state == "request":
            state = request_state(logger, card_to_request, enable_request)
        if state == "donate":
            state = donate_state(logger, enable_donate)
        if state == "upgrade":
            state = upgrade_state(logger, enable_card_upgrade)
        if state == "start_fight":
            state = start_fight_state(logger)
        if state == "fighting":
            state = fighting_state(logger)
        if state == "post_fight":
            ssid, state = post_fight_state(logger, ssids)
        if state == "battlepass":
            state = battlepass_state(logger, enable_battlepass_collection)
        if state == "card_mastery_collection":
            state = card_mastery_collection_state(
                logger, enable_card_mastery_collection)

        loop_count += 1
        time.sleep(0.2)


if __name__ == "__main__":
    main_loop()
