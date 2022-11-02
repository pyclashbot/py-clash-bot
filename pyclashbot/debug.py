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
    check_for_memu_loading_background,
    close_memu,
    close_memu_multi,
    find_clash_app_logo,
    restart_and_open_clash,
    wait_for_memu_loading_screen,
)
from pyclashbot.level_up_reward_collection import check_for_level_up_reward_pixels, check_if_has_level_up_rewards, collect_level_up_rewards
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
from pyclashbot.upgrade import check_for_final_upgrade_button, check_for_upgradable_cards, check_if_card_is_upgradable, find_confirm_upgrade_for_gold_button, find_first_upgrade_for_gold_button, upgrade_current_cards

ahk = AHK()
logger = Logger()
# user_settings = load_user_config()
# launcher_path = user_settings["launcher_path"]


# orientate_memu_multi()
# orientate_memu()


# show_image(screenshot())




print(check_for_memu_loading_background())