import random
import time
from itertools import cycle

from pyclashbot.account import switch_accounts_to
from pyclashbot.card import fight_with_deck_list
from pyclashbot.chest import check_if_has_chest_unlocking, open_chests
from pyclashbot.client import (check_if_windows_exist, check_quit_key_press,
                               orientate_memu_multi, orientate_window,
                               restart_client)
from pyclashbot.donate import click_donates, getto_donate_page
from pyclashbot.fight import (check_if_past_game_is_win,
                              leave_end_battle_window, look_for_enemy_troops,
                              start_2v2, wait_for_battle_start)
from pyclashbot.logger import Logger
from pyclashbot.request import (check_if_can_request,
                                request_from_clash_main_menu)
from pyclashbot.state import (check_if_in_battle, check_if_on_clash_main_menu,
                              check_state, open_clash,
                              return_to_clash_main_menu,
                              wait_for_clash_main_menu)
from pyclashbot.upgrade import upgrade_cards_from_main

logger = Logger()


def post_fight_state(ssids):
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
    log = "Next account was random chosen and is account: " + str(ssid)
    logger.log(log)
    state = "clash_main"
    return state


def fight_state(fight_type):
    logger.log("-----STATE=start_fight-----")
    state = "restart"
    return_to_clash_main_menu()
    if fight_type == "1v1":
        logger.log("I cant do 1v1s yet. Restarting")
        state = "restart"
    if fight_type == "2v2":
        logger.log("Starting a 2v2 match.")
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


def upgrade_state():
    logger.log("-----STATE=upgrade-----")
    # only run upgrade a third of the time because its fucking slow as shit but what can u do yk?
    return_to_clash_main_menu()
    time.sleep(1)
    upgrade_cards_from_main(logger)
    time.sleep(1)
    return_to_clash_main_menu()
    logger.log("Finished with upgrading. Passing to start fight state")
    state = "start_fight"
    return state


def donate_state():
    logger.log("-----STATE=donate-----")
    if getto_donate_page(logger) == "quit":
        # if failed to get to clan chat page
        logger.log("Failed to get to clan chat page. Restarting")
        state = "restart"
    else:
        # if got to clan chat page
        logger.log(
            "Successfully got to clan chat page. Starting donate alg")
        click_donates(logger)
        n = random.randint(1, 3)
        if n == 1:
            logger.log("Done with donating. Passing to upgrade state")
            state = "upgrade"
        else:
            logger.log(
                "Done with donating. Passing to start_fight state")
            state = "start_fight"
    return state


def request_state(card_to_request):
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
        else:
            # if request works
            log = "Successfully requested " + \
                str(card_to_request) + "."
            logger.log(log)
        logger.log("Done with requesting. Passing to donate state.")
        return_to_clash_main_menu()
        time.sleep(2)
        state = "donate"
    return state


def clash_main_state(ssid):
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


def restart_state():
    logger.log("-----STATE=restart-----")
    logger.log("restart time loop")
    logger.log("Restarting menu client")
    restart_client(logger)
    if open_clash(logger) == "quit":
        state = "restart"
    else:
        if check_if_on_clash_main_menu():
            state = "clash_main"
        else:
            state = "restart"
    return state


def main_loop():
    # user vars (these will be specified thru the GUI, but these are the
    # placeholders for now.)
    total_accounts = 2
    deck = ""
    fight_type = "2v2"
    card_to_request = "archers"
    cards_to_not_donate = ["card_1", "card_2", "card_3"]
    ssids = cycle([1, 2, 3]) # change to which account positions to use
    ssid = next(ssids)
    # vars
    loop_count = 0
    if not check_if_windows_exist(logger):
        return
    orientate_memu_multi()
    time.sleep(0.2)
    orientate_window()
    state = check_state(logger)
    if state is None:
        state = "restart"

    # region=[45,500,8,8]
    # folder=r"C:\Users\Matt\Desktop\inc_pics"
    # take_many_screenshots(duration=9, frequency=30, name="e", region=region,folder=folder)
    # print("done")
    # time.sleep(30)

    while True:
        time.sleep(0.2)
        logger.log(f"loop count: {loop_count}")
        loop_count += 1

        # show_image(refresh_screen())

        if state == "restart":
            state = restart_state()
        if state == "clash_main":
            state = clash_main_state(ssid)
        if state == "request":
            state = request_state(card_to_request)
        if state == "donate":
            state = donate_state()
        if state == "upgrade":
            state = upgrade_state()
        if state == "start_fight":
            state = fight_state(fight_type)
        if state == "fighting":
            logger.log("-----STATE=fighting-----")
            fightloops = 0
            while (check_if_in_battle()) and (fightloops < 100):
                check_quit_key_press()
                log = "Plays: " + str(fightloops)
                logger.log(log)
                logger.log("Scanning field.")
                enemy_troop_position = look_for_enemy_troops()
                logger.log("Choosing play.")
                fight_with_deck_list(enemy_troop_position)
                fightloops = fightloops + 1
            logger.log("Battle must be finished")
            time.sleep(10)
            leave_end_battle_window(logger)
            wait_for_clash_main_menu(logger)
            state = "post_fight"
        if state == "post_fight":
            post_fight_state(ssids)


if __name__ == "__main__":
    main_loop()
