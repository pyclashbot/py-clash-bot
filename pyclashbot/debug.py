import subprocess
import sys
import time
from itertools import cycle

import pyautogui
import pygetwindow
import pyperclip
import PySimpleGUI as sg

from pyclashbot.__main__ import initialize_client, main_loop, restart_state
from pyclashbot.client import screenshot, show_image
from pyclashbot.launcher import orientate_memu_multi
from pyclashbot.logger import Logger

logger = Logger()
loop_count = 0
ssid=0

# print(launcher_path)

# # jobs = ['Fight', 'Request', 'Donate', 'Upgrade_cards', 'Collect_battlepass_rewards', 'Collect_mastery_rewards']
# main_loop(jobs)

# region=[0,0,2560,1440]
# image=screenshot(region)
# show_image(image)



