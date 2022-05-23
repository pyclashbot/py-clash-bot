import random
import time

import matplotlib.pyplot as plt

from pyclashbot.account import switch_accounts_to
from pyclashbot.card import fight_with_deck_list
from pyclashbot.chest import check_if_has_chest_unlocking, look_for_clock, open_chests
from pyclashbot.client import (check_if_windows_exist, check_quit_key_press,
                               orientate_memu_multi, orientate_window,
                               refresh_screen, restart_client)
from pyclashbot.donate import click_donates, getto_donate_page
from pyclashbot.fight import (check_if_past_game_is_win,
                              leave_end_battle_window, look_for_enemy_troops,
                              start_2v2, wait_for_battle_start)
from pyclashbot.logger import Logger
from pyclashbot.mass_screenshot import take_screenshots
from pyclashbot.request import (check_if_can_request,
                                request_from_clash_main_menu)
from pyclashbot.state import (
    check_if_in_battle,
    check_if_on_clash_main_menu,
    check_state,
    open_clash,
    return_to_clash_main_menu,
    wait_for_clash_main_menu)

logger = Logger()


def show_image(iar):
    plt.imshow(iar)
    check_quit_key_press()
    plt.show()


def main_loop():
    # user vars (these will be specified thru the GUI, but these are the
    # placeholders for now.)
    deck = ""
    fight_type = "2v2"
    card_to_request = "goblin_cage"
    cards_to_not_donate = ["card_1", "card_2", "card_3"]
    ssid = random.randint(1, 2)
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
    while True:
        time.sleep(0.2)
        logger.log(f"loop count: {loop_count}")
        loop_count += 1
        iar = refresh_screen()                    
        plt.imshow(iar)

        #plt.show()
        print()

        
        
        if state == "restart":
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
        if state == "clash_main":
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
                    logger.log("Checking if a chest is being unlocked right now.")
                    if not check_if_has_chest_unlocking():
                        logger.log("Found no unlocking symbols. Opening chests.")
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
        if state == "request":
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
        if state == "donate":
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
                logger.log("Done with donating. Passing to start_fight state")
                state = "start_fight"
        if state == "start_fight":
            logger.log("-----STATE=start_fight-----")
            if fight_type == "1v1":
                logger.log("I cant do 1v1s yet. Restarting")
                state = "restart"
            if fight_type == "2v2":
                logger.log("Starting a 2v2 match.")
                if start_2v2(logger) == "quit":
                    #if couldnt find quickmatch button
                    logger.log("Had problems finding 2v2 quickmatch button.")
                    state = "restart"
                else:
                    #if could find the quickmatch button
                    if wait_for_battle_start(logger) == "quit":
                        # if waiting for battle takes too long
                        logger.log("Waited too long for battle start. Restarting")
                        state = "restart"
                    else:
                        # if battle started before wait was too long
                        logger.log("Battle has begun. Passing to fighting state")
                        state = "fighting"
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
            logger.log("STATE=post_fight")
            logger.log("Back on clash main")
            if check_if_past_game_is_win(logger):
                logger.log("Last game was a win")
                logger.add_win()
            else:
                logger.log("Last game was a loss")
                logger.add_loss()
            # switch accounts feature
            ssid = random.randint(1, 3)
            log = "Next account was random chosen and is account: " + str(ssid)
            logger.log(log)
            state = "clash_main"


if __name__ == "__main__":
    main_loop()
