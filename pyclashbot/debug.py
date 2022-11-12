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
    check_if_unlock_chest_button_exists,
    find_2v2_quick_match_button,
    get_to_account,
    get_to_clan_page,
    get_to_clash_main_from_clan_page,
    handle_gold_rush_event,
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
    find_use_card_button,
    look_for_card_collection_icon_on_card_page,
    randomize_and_select_deck_2,
)
from pyclashbot.bot.level_up_reward_collection import (
    check_for_level_up_reward_pixels,
    check_if_has_level_up_rewards,
    collect_level_up_rewards,
)
from pyclashbot.bot.request import (
    check_if_can_request,
    look_for_request_button,
    request_random_card_from_clash_main,
)
from pyclashbot.bot.states import state_fight
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
from pyclashbot.memu.client import click, get_file_count, make_reference_image_list
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


# show_image(screenshot())


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
    if not check_if_on_clash_main_menu():
        print("youre not on main dude.")
        return
    start_2v2(logger)
    wait_for_battle_start(logger)
    state_fight(logger)


looping = True
while looping:
    if randomize_and_select_deck_2(logger) == "restart":
        looping = False
    time.sleep(5)


# main_debug()
