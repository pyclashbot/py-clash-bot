

import time

import pyautogui

from pyclashbot.__main__ import battlepass_state, card_mastery_collection_state, clash_main_state, donate_state, fighting_state, post_fight_state, request_state, restart_state, start_fight_state, upgrade_state
from pyclashbot.client import check_quit_key_press, orientate_memu, screenshot, show_image
from pyclashbot.configuration import load_user_config
from pyclashbot.fight import find_2v2_quick_match_button, find_and_click_2v2_quickmatch_button, start_2v2
from pyclashbot.launcher import orientate_memu_multi
from pyclashbot.logger import Logger
from pyclashbot.request import check_if_can_request
from pyclashbot.state import check_if_in_battle, check_if_on_trophy_progession_rewards_page, wait_for_clash_main_menu
from pyclashbot.upgrade import look_for_upgrade_button, upgrade_cards_from_main_2, upgrade_given_card


user_settings = load_user_config()
launcher_path = user_settings["launcher_path"]
accounts=2
logger = Logger()
ssid_total = accounts

current_ssid = 0


# show_image(screenshot())


# orientate_memu_multi()
# orientate_memu()




##############DONE FIXING
# restart_state(logger,launcher_path)
# clash_main_state(logger, current_ssid)
# upgrade_state(logger)
# request_state(logger)



##############STILL UNCHECKED
# donate_state(logger)
# card_mastery_collection_state(logger)
# battlepass_state(logger)





# start_fight_state(logger)



start_fight_state(logger)
fighting_state(logger)



