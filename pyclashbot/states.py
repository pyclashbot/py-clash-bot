

import time

from pyclashbot.clashmain import (check_if_in_battle, get_to_account,
                                  handle_card_mastery_notification,
                                  open_chests, start_2v2,
                                  wait_for_battle_start,
                                  wait_for_clash_main_menu)
from pyclashbot.client import clear_log, click, orientate_memu, orientate_memu_multi, orientate_terminal
from pyclashbot.fight import (check_if_end_screen_is_exit_bottom_left,
                              check_if_end_screen_is_ok_bottom_middle,
                              check_if_past_game_is_win, fight,
                              leave_end_battle_window)
from pyclashbot.launcher import restart_and_open_clash
from pyclashbot.logger import Logger
from pyclashbot.request import (check_if_on_clan_page,
                                get_to_clash_main_from_request_page,
                                request_random_card_from_clash_main)
from pyclashbot.upgrade import (check_if_on_first_card_page, get_to_card_page,
                                get_to_clash_main_from_card_page,
                                randomize_and_select_deck_2,
                                upgrade_current_cards)


# Method for detecting the state of the client in a given moment
def detect_state(logger):  # sourcery skip: extract-duplicate-method
    # if we're on clan page get back to clash main and return
    if check_if_on_clan_page():
        if get_to_clash_main_from_request_page(logger) == "restart":
            return "restart"
        time.sleep(1)
        return "clashmain"

    # if we're on card page get back to clash main and return
    if check_if_on_first_card_page():
        if get_to_clash_main_from_card_page(logger) == "restart":
            return "restart"
        time.sleep(1)
        return "clashmain"

    # if we're in battle return fighting
    if check_if_in_battle():
        return "fighting"

    # if we're on end fight screen condition 1 (exit in bottom left)
    if check_if_end_screen_is_exit_bottom_left():
        click(79, 625)
        time.sleep(1)
        if wait_for_clash_main_menu(logger) == "restart":
            return "restart"
        return "clashmain"

    # if we're on end fight screen condition 2 (OK in bottom middle)
    if check_if_end_screen_is_ok_bottom_middle():
        click(206, 594)
        time.sleep(1)
        if wait_for_clash_main_menu(logger) == "restart":
            return "restart"
        return "clashmain"

    # if none of these conditions are met return "restart"
    return "restart"


def state_tree(jobs: list[str], logger: Logger, ssid: int, state: str) -> str:
    if state == "clashmain":
        orientate_memu_multi()
        orientate_memu()
        orientate_terminal()
        return "restart" if state_clashmain(logger=logger, account_number=ssid, jobs=jobs) == "restart" else "startfight"

    elif state == "startfight":
        if "Fight" not in jobs:
            return "upgrade"
        else:
            return "restart" if state_startfight(logger) == "restart" else "fighting"

    elif state == "fighting":
        return "restart" if state_fight(logger) == "restart" else "endfight"

    elif state == "endfight":
        state_endfight(logger)
        return "upgrade"

    elif state == "upgrade":
        return "restart" if "Upgrade" in jobs and state_upgrade(logger) == "restart" else "request"

    elif state == "request":
        return "restart" if "Request" in jobs and state_request(logger) == "restart" else "clashmain"

    elif state == "restart":
        state_restart(logger)
        return "clashmain"

    return state


# Method for the restart state of the program


def state_restart(logger):
    # Restart state restarts Memu and MeMU Multi Manager, opens clash, and waits for the clash main menu to appear.
    # clear_log()
    logger.change_status("Restarting")

    if restart_and_open_clash(logger) == "restart":
        restart_and_open_clash(logger)

# Method for the clash royale main menu state of the program


def state_clashmain(logger, account_number, jobs):
    # Clashmain state gets to the correct account of the current state then opens their chests

    logger.change_status("On clash main")

    # Get to correct account
    if get_to_account(logger, account_number) == "restart":
        return "restart"

    time.sleep(3)

    # Open chests
    if "Open Chests" in jobs:
        open_chests(logger)
    time.sleep(3)

# Method for the starting of a fight state of the program


def state_startfight(logger):
    # Begins on clash main, ends in the beginning of a fight

    logger.change_status("Starting a fight")

    # make a random deck
    randomize_and_select_deck_2(logger)

    # Start 2v2 quickmatch
    if start_2v2(logger) == "restart":
        return "restart"

    # Wait for battle to start
    if wait_for_battle_start(logger) == "restart":
        return "restart"

# Method for the state of the program when fighting


def state_fight(logger):
    # Method that plays cards with certain logic until the fight is over then returns to the clash royale main screen

    logger.change_status("Fighting")
    logger.add_fight()

    if fight(logger) == "restart":
        return "restart"

    if leave_end_battle_window(logger) == "restart":
        return 'restart'

# Method for the state of the program after a fight


def state_endfight(logger):
    # Checks if the last battle was a win or loss then adds this to the logger tally
    # Starts and ends on the clash royale main menu

    logger.change_status("Post fight")

    check_if_past_game_is_win(logger)

# Method for the state of the program when upgrading cards


def state_upgrade(logger):
    # Starts on the clash royale main menu and ends on the clash royale main menu

    logger.change_status("Upgrading cards")

    handle_card_mastery_notification()

    # Get to card page
    if get_to_card_page(logger) == "restart":
        return "restart"

    # Upgrade user cards
    upgrade_current_cards(logger)

    # return to clash main
    if get_to_clash_main_from_card_page(logger) == "restart":
        return "restart"

# Method for the state of the program when requesting cards


def state_request(logger):
    # Request method goes to clan page, requests a random card if request is available, then returns to the clash royale main menu
    clear_log()
    logger.change_status("Requesting card")

    time.sleep(1)
    handle_card_mastery_notification()
    time.sleep(1)

    if request_random_card_from_clash_main(logger) == "restart":
        return "restart"
