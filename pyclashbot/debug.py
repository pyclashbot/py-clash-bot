import os
import random
import sys
import time
import webbrowser
from dataclasses import replace
from os.path import dirname, join
from re import S
from typing import Any

import numpy
import pyautogui
import pygetwindow
import PySimpleGUI as sg
from ahk import AHK
from matplotlib import pyplot as plt
from PIL import Image

from pyclashbot.bot.battlepass_rewards_collection import (
    check_for_battlepass_reward_pixels,
    check_if_has_battlepass_rewards,
    collect_battlepass_rewards,
)
from pyclashbot.bot.card_detection import get_card_images, identify_cards
from pyclashbot.bot.card_mastery_collection import (
    check_if_can_collect_card_mastery_rewards,
    collect_card_mastery_rewards,
    get_to_clash_main_from_card_page,
)
from pyclashbot.bot.clashmain import (
    check_for_friends_logo_on_main,
    check_for_gem_logo_on_main,
    check_for_gold_logo_on_main,
    check_for_war_loot_menu,
    check_if_in_a_clan,
    check_if_in_battle_with_delay,
    check_if_on_clash_main_menu,
    check_if_on_first_card_page,
    check_if_stuck_on_trophy_progression_page,
    check_if_stuck_on_war_final_results_page,
    check_if_unlock_chest_button_exists,
    find_2v2_quick_match_button,
    get_to_account,
    get_to_clan_page,
    get_to_clash_main_from_clan_page,
    handle_war_loot_menu,
    open_chests,
    start_2v2,
    wait_for_battle_start,
)
from pyclashbot.bot.deck import (
    check_if_can_still_scroll_in_card_page,
    check_if_mimimum_scroll_case,
    check_if_pixels_indicate_minimum_scroll_case,
    check_if_pixels_indicate_minimum_scroll_case_with_delay,
    count_scrolls_in_card_page,
    find_card_elixer_icon_in_card_list_in_given_image,
    find_card_level_boost_icon,
    find_use_card_button,
    look_for_card_collection_icon_on_card_page,
    randomize_and_select_deck_2,
)
from pyclashbot.bot.fight import (
    check_if_past_game_is_win,
    check_if_pixels_indicate_win_on_activity_log,
    play_random_card,
)
from pyclashbot.bot.free_offer_collection import (
    check_if_on_shop_page,
    check_if_on_shop_page_with_delay,
    collect_free_offer_from_shop,
    find_free_offer_icon,
)
from pyclashbot.bot.level_up_reward_collection import (
    check_for_level_up_reward_pixels,
    check_if_has_level_up_rewards,
    collect_level_up_rewards,
)
from pyclashbot.bot.request import (
    check_for_request_icon_on_clan_page,
    check_if_can_request,
    look_for_request_button,
    request_random_card_from_clash_main,
)
from pyclashbot.bot.states import (
    state_battlepass_collection,
    state_card_mastery_collection,
    state_clashmain,
    state_endfight,
    state_fight,
    state_free_offer_collection,
    state_level_up_reward_collection,
    state_request,
    state_restart,
    state_startfight,
    state_tree,
    state_upgrade,
    state_war,
)
from pyclashbot.bot.upgrade import (
    check_for_upgradable_cards,
    find_confirm_upgrade_for_gold_button,
    find_first_upgrade_for_gold_button,
    upgrade_current_cards,
)
from pyclashbot.bot.war import (
    check_if_has_a_deck_for_this_war_battle,
    check_if_loading_war_battle,
    click_war_icon,
    fight_war_battle,
    find_battle_icon_on_war_page,
    get_to_war_page_from_main,
    handle_war_attacks,
    make_a_random_deck_for_this_war_battle,
    wait_for_war_battle_loading,
)
from pyclashbot.detection.image_rec import (
    find_references,
    get_first_location,
    pixel_is_equal,
)
from pyclashbot.memu import (
    orientate_terminal,
    screenshot,
    scroll_down,
    scroll_down_super_fast,
)
from pyclashbot.memu.client import (
    click,
    get_file_count,
    make_reference_image_list,
    print_pix_list,
)
from pyclashbot.memu.launcher import start_vm
from pyclashbot.utils import Logger

ahk = AHK()
logger = Logger(console_log=True)


def show_image(image):
    """Method to show a PIL image using matlibplot

    Args:
        image (PIL.Image): Image to show
    """
    plt.imshow(numpy.array(image))
    plt.show()


def gui_debug():
    from pyclashbot.interface import disable_keys, main_layout, show_help_gui

    sg.theme("SystemDefaultForReal")
    # some sample statistics
    statistics: dict[str, Any] = {
        "wins": 1,
        "losses": 2,
        "fights": 3,
        "requests": 4,
        "restarts": 5,
        "chests_unlocked": 6,
        "cards_played": 7,
        "cards_upgraded": 8,
        "account_switches": 9,
        "card_mastery_reward_collections": 10,
        "battlepass_rewards_collections": 11,
        "level_up_chest_collections": 12,
        "war_battles_fought": 13,
        "current_status": "Starting",
    }

    window = sg.Window("Py-ClashBot", main_layout)

    running = False

    while True:
        event, values = window.read(timeout=100)  # type: ignore
        if event == sg.WIN_CLOSED:
            break
        elif event == "Start":
            window["current_status"].update("Starting")  # type: ignore
            for key in disable_keys:
                window[key].update(disabled=True)
            running = True
            window["Stop"].update(disabled=False)

        elif event == "Stop":
            window["current_status"].update("Stopping")  # type: ignore
            running = False
            for key in disable_keys:
                window[key].update(disabled=False)
            window["Stop"].update(disabled=True)

        elif event == "Help":
            show_help_gui()

        elif event == "Donate":
            webbrowser.open(
                "https://www.paypal.com/donate/"
                + "?business=YE72ZEB3KWGVY"
                + "&no_recurring=0"
                + "&item_name=Support+my+projects%21"
                + "&currency_code=USD"
            )

        elif event == "issues-link":
            webbrowser.open(
                "https://github.com/matthewmiglio/py-clash-bot/issues/new/choose"
            )

        if running:
            orientate_terminal()
            # change some of the statistics
            statistics["wins"] += 1
            statistics["losses"] += 1
            statistics["fights"] += 1
            statistics["war_battles_fought"] += 1
            statistics["requests"] += 1

        # update the statistics
        window["wins"].update(statistics["wins"])
        window["losses"].update(statistics["losses"])
        window["fights"].update(statistics["fights"])
        window["war_battles_fought"].update(statistics["war_battles_fought"])
        window["requests"].update(statistics["requests"])

        time.sleep(1)


def memu_debug(logger):
    logger.change_status("Starting memu debug")
    start_vm(logger)


def reference_image_debug():
    path = dirname(__file__)[:-3]
    path = join(path, "detection", "reference_images")
    print(path)


def main_debug():
    # print(check_if_on_clash_main_menu())
    # open_chests(logger)
    # collect_battlepass_rewards(logger)
    # collect_card_mastery_rewards(logger)
    # print(check_if_stuck_on_trophy_progression_page())
    # print(check_if_on_first_card_page())
    # get_to_account(logger, 0)
    # start_2v2(logger)
    # print(check_if_in_a_clan(logger))
    # randomize_and_select_deck_2(logger)
    # request_random_card_from_clash_main(logger)
    # print(check_if_has_level_up_rewards())
    # collect_level_up_rewards(logger)
    # handle_war_attacks(logger)
    # upgrade_current_cards(logger)
    # print(check_if_in_battle_with_delay())
    pass


def fight_debug():
    while True:
        if not check_if_on_clash_main_menu():
            print("youre not on main dude.")
            return

        randomize_and_select_deck_2(logger)
        time.sleep(1)

        if not check_if_on_clash_main_menu():
            print("youre not on main dude.")
            return

        time.sleep(1)
        start_2v2(logger)
        wait_for_battle_start(logger)
        if state_fight(logger) == "restart":
            return


def randomize_deck_debug():
    while True:
        if not check_if_on_clash_main_menu():
            print("youre not on main dude.")
            return
        if randomize_and_select_deck_2(logger) == "restart":
            return
        get_to_clash_main_from_card_page(logger)


def find_random_card_debug():
    region_list = [
        [50, 130, 81, 71],
        [131, 130, 81, 71],
        [212, 130, 81, 71],
        [293, 130, 81, 71],
        [50, 275, 81, 71],
        [50, 346, 81, 71],
        [50, 417, 81, 71],
        [50, 488, 81, 71],
        [131, 275, 81, 71],
        [131, 346, 81, 71],
        [131, 417, 81, 71],
        [131, 488, 81, 71],
        [212, 275, 81, 71],
        [212, 346, 81, 71],
        [212, 417, 81, 71],
        [212, 488, 81, 71],
        [293, 275, 81, 71],
        [293, 346, 81, 71],
        [293, 417, 81, 71],
        [293, 488, 81, 71],
    ]
    for region in region_list:
        show_image(screenshot(region=region))
        coord = find_card_elixer_icon_in_card_list_in_given_image(screenshot(region))
        if coord is not None:
            print("found elixer icon in region: ", region)


def card_detection_debug():
    while True:
        print(identify_cards())


def debug_state_tree(logger, ssid_max, jobs, ssid, state):

    if state == "clashmain":

        state = state_clashmain(
            logger=logger, ssid_max=ssid_max, account_number=ssid, jobs=jobs
        )

        # Increment account number, loop back to 0 if it's ssid_max
        ssid = ssid + 1 if ssid < ssid_max else 0

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
        state = (
            state_free_offer_collection(logger)
            if "free offer collection" in jobs
            else "clashmain"
        )

    return (state, ssid)


def do_debug_state_tree():
    state_restart(logger)
    jobs = [
        "Open Chests",
        "Fight",
        "Request",
        "Upgrade",
        "Randomize Deck",
        "card mastery collection",
        "level up reward collection",
        "battlepass reward collection",
        "war",
    ]
    ssid = 0
    state = "clashmain"
    while True:
        state, ssid = debug_state_tree(
            jobs=jobs, logger=logger, ssid_max=3, ssid=ssid, state=state
        )


# show_image(screenshot())

# memu_debug(logger)
