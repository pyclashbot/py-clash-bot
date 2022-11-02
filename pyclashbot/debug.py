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
from pyclashbot.battlepass_rewards_collection import check_for_battlepass_reward_pixels, check_if_has_battlepass_rewards
from pyclashbot.client import screenshot, show_image



from pyclashbot.level_up_reward_collection import (
    check_for_level_up_reward_pixels,
    check_if_has_level_up_rewards,
    collect_level_up_rewards,
)
from pyclashbot.logger import Logger


ahk = AHK()
logger = Logger()
# user_settings = load_user_config()
# launcher_path = user_settings["launcher_path"]


# orientate_memu_multi()
# orientate_memu()


# show_image(screenshot())

while True:
    print(check_if_has_battlepass_rewards())