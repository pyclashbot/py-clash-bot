import subprocess
import sys
import time
from itertools import cycle

import pyautogui
import pygetwindow
import pyperclip
import PySimpleGUI as sg
from pyclashbot.__main__ import battlepass_state, card_mastery_collection_state, donate_state, request_state, upgrade_state
from pyclashbot.battlepass import check_battlepass_state, check_if_can_collect_bp
from pyclashbot.card_mastery import collect_mastery_rewards

from pyclashbot.client import click, orientate_memu, screenshot, show_image
from pyclashbot.launcher import orientate_bot_window, orientate_memu_multi
from pyclashbot.logger import Logger
from pyclashbot.state import check_if_on_clash_main_menu, find_clash_app_logo
from pyclashbot.upgrade import upgrade_cards_from_main

logger = Logger()
loop_count = 0
ssid=0

# print(launcher_path)

# # jobs = ['Fight', 'Request', 'Donate', 'Upgrade_cards', 'Collect_battlepass_rewards', 'Collect_mastery_rewards']
# main_loop(jobs)

# region=[0,0,2560,1440]
# image=screenshot(region)
# show_image(image)

# orientate_memu_multi()
# orientate_memu()




# orientate_memu()

print(check_if_on_clash_main_menu())