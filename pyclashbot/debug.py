import random
import time
from dataclasses import replace
from os.path import dirname, join
from re import S

import numpy
import pyautogui
import pygetwindow
from ahk import AHK
from matplotlib import pyplot as plt
from PIL import Image

from pyclashbot.card_detection import (
    get_card_group,
    get_card_images,
    identify_cards,
    make_reference_image_list,
)
from pyclashbot.card_mastery_collection import collect_card_mastery_rewards
from pyclashbot.clashmain import (
    check_for_blue_background_on_main,
    check_for_friends_logo_on_main,
    check_for_gem_logo_on_main,
    check_for_gold_logo_on_main,
    check_if_on_clash_main_menu,
    find_2v2_quick_match_button,
    find_and_click_2v2_quickmatch_button,
    get_to_account,
    get_to_card_page,
    start_2v2,
    wait_for_clash_main_menu,
)
from pyclashbot.client import (
    click,
    get_file_count,
    get_next_ssid,
    orientate_memu,
    orientate_memu_multi,
    screenshot,
    scroll_down,
    scroll_down_fast,
    scroll_down_super_fast,
    scroll_up_fast,
    scroll_up_super_fast,
    show_image,
)
from pyclashbot.configuration import load_user_config
from pyclashbot.deck import check_if_can_still_scroll, find_use_card_button
from pyclashbot.fight import (
    check_if_has_6_elixer,
    fight,
    leave_end_battle_window,
    pick_a_lane,
    wait_until_has_6_elixer,
)
from pyclashbot.image_rec import find_references, get_first_location, pixel_is_equal
from pyclashbot.launcher import (
    close_memu,
    close_memu_multi,
    find_clash_app_logo,
    restart_and_open_clash,
)
from pyclashbot.logger import Logger
from pyclashbot.request import check_if_in_a_clan, count_maximum_request_scrolls, request_random_card_from_clash_main
from pyclashbot.states import (
    state_clashmain,
    state_endfight,
    state_fight,
    state_request,
    state_startfight,
    state_upgrade,
)
from pyclashbot.upgrade import upgrade_current_cards

ahk = AHK()
logger = Logger()
# user_settings = load_user_config()
# launcher_path = user_settings["launcher_path"]


# orientate_memu_multi()
# orientate_memu()


# show_image(screenshot())


def battle_debug_main():
    # Make logger, get launcherpath from %appdata/pyclashbot/config.json,
    # initialize SSID as 1
    logger = Logger()
    ssid = 0
    jobs = ["Fight"]
    ssid_total = 2

    # Starting with restart state, the bot will pass itself between
    # states as it reads the screen and will ignore jobs not on the joblist
    state = "clashmain"
    while True:
        if state == "clashmain":
            orientate_memu_multi()
            orientate_memu()
            if (
                state_clashmain(logger=logger, account_number=ssid, jobs=jobs)
                == "restart"
            ):
                state = "restart"
            else:
                state = "startfight"

        if state == "startfight":
            if "Fight" not in jobs:
                state = "upgrade"
            else:
                state = (
                    "restart" if state_startfight(logger) == "restart" else "fighting"
                )
        if state == "fighting":
            state = "restart" if state_fight(logger) == "restart" else "endfight"
        if state == "endfight":
            state_endfight(logger)
            state = "clashmain"

        # increment SSID to run the next loop with the next account in the
        # cycle
        ssid = get_next_ssid(ssid, ssid_total)


def card_detection_debug():
    n = 0
    while True:
        n += 1
        print(n, "----------------------")
        print(identify_cards())


def request_debug():
    # starts on clash main and ends on clash main
    # should request if you can, should do nothing if you cant
    state_request(logger)


collect_card_mastery_rewards(logger)