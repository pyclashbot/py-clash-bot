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
from pyclashbot.battlepass_rewards_collection import check_for_battlepass_reward_pixels, check_if_has_battlepass_rewards, collect_battlepass_rewards
from pyclashbot.clashmain import check_if_in_battle, check_if_in_battle_with_delay, check_if_on_clash_main_menu, check_if_unlock_chest_button_exists
from pyclashbot.client import orientate_memu, orientate_memu_multi, screenshot, show_image
from pyclashbot.launcher import check_for_memu_loading_background, wait_for_memu_loading_screen



from pyclashbot.level_up_reward_collection import (
    check_for_level_up_reward_pixels,
    check_if_has_level_up_rewards,
    collect_level_up_rewards,
)
from pyclashbot.logger import Logger
from pyclashbot.upgrade import find_confirm_upgrade_for_gold_button, find_first_upgrade_for_gold_button
from pyclashbot.war import check_if_has_a_deck_for_this_war_battle, check_if_on_war_page, click_war_icon, get_to_war_page_from_main, find_battle_icon_on_war_page, handle_war_attacks


ahk = AHK()
logger = Logger()
# user_settings = load_user_config()
# launcher_path = user_settings["launcher_path"]


# orientate_memu_multi()
# orientate_memu()


# show_image(screenshot())



# get_to_war_page_from_main()

# print(check_if_on_war_page())

while True:
    print(check_for_memu_loading_background())