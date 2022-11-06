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

from pyclashbot.battlepass_rewards_collection import (
    check_for_battlepass_reward_pixels, check_if_has_battlepass_rewards,
    collect_battlepass_rewards)
from pyclashbot.clashmain import (check_if_in_a_clan, check_if_in_battle,
                                  check_if_in_battle_with_delay,
                                  check_if_on_clash_main_menu,
                                  check_if_unlock_chest_button_exists,
                                  open_chests)
from pyclashbot.client import (orientate_memu, 
                               orientate_terminal, screenshot, scroll_down,
                               scroll_down_super_fast, show_image)
from pyclashbot.deck import (check_if_mimimum_scroll_case,
                             count_scrolls_in_card_page,
                             look_for_card_collection_icon_on_card_page,
                             randomize_current_deck)
from pyclashbot.level_up_reward_collection import (
    check_for_level_up_reward_pixels, check_if_has_level_up_rewards,
    collect_level_up_rewards)
from pyclashbot.logger import Logger
from pyclashbot.request import (check_if_can_request,
                                request_random_card_from_clash_main)
from pyclashbot.upgrade import (find_confirm_upgrade_for_gold_button,
                                find_first_upgrade_for_gold_button)
from pyclashbot.war import (check_if_has_a_deck_for_this_war_battle,
                            check_if_on_war_page, click_war_icon,
                            fight_war_battle, find_battle_icon_on_war_page,
                            get_to_war_page_from_main, handle_war_attacks)

ahk = AHK()
logger = Logger(console_log=True)


def gui_debug():
    from pyclashbot.layout import disable_keys, layout, show_help_gui
    

    
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

    window = sg.Window("Py-ClashBot", layout)

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
                "https://www.paypal.com/donate/?business=YE72ZEB3KWGVY&no_recurring=0&item_name=Support+my+projects%21&currency_code=USD"
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






gui_debug()
