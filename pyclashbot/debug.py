import os
import random
import time
from itertools import count
from os.path import dirname, join

import ahk
import numpy
import pyautogui
from ahk import AHK
from matplotlib import pyplot as plt
from PIL import Image

from client import (click, get_next_ssid, orientate_memu, orientate_memu_multi,
                    screenshot, scroll_down, show_image)
from configuration import load_user_config
from fight import fight, leave_end_battle_window
from image_rec import pixel_is_equal
from logger import Logger
from request import check_if_in_a_clan, request_random_card_from_clash_main
from states import (state_clashmain, state_endfight, state_fight,
                    state_request, state_startfight, state_upgrade)
from upgrade import check_if_pixel_indicates_upgrade, upgrade_current_cards

ahk = AHK()
logger = Logger()
user_settings = load_user_config()
launcher_path = user_settings["launcher_path"]


# orientate_memu_multi()
# orientate_memu()
# time.sleep(1)

# show_image(screenshot())



def battle_debug_main():
    #Make logger, get launcherpath from %appdata/pyclashbot/config.json, initialize SSID as 1
    logger = Logger()
    ssid=0
    jobs=["Fight"]
    ssid_total=2
    
    #Starting with restart state, the bot will pass itself between
    #states as it reads the screen and will ignore jobs not on the joblist
    state="clashmain"
    while True:
        if state=="clashmain": 
            orientate_memu_multi()
            orientate_memu()
            if state_clashmain(logger=logger,account_number=ssid,jobs=jobs)=="restart": state="restart"
            else: state="startfight"
        
        if state=="startfight": 
            if "Fight" not in jobs: state="upgrade"
            else:
                if state_startfight(logger)=="restart": state="restart"
                else: state="fighting"
        
        if state=="fighting":
            if state_fight(logger)=="restart": state="restart"
            else: state="endfight"
        
        if state=="endfight": 
            state_endfight(logger)
            state="clashmain"
        
       
    
        #increment SSID to run the next loop with the next account in the cycle
        ssid = get_next_ssid(ssid, ssid_total)


def upgrade_card_coords_debug():
    card_coord_list=[
        [86,278],
        [174,278],
        [260,278],
        [328,278],
        [86,400],
        [174,400],
        [260,400],
        [328,400]
    ]
    #make list of coords of where the upgrade button will possibly appear for each 8 cards
    upgrade_button_coords=[
        [51,338],
        [136,338],
        [280,341],
        [303,337],
        [53,464],
        [133,464],
        [281,465],
        [303,466],
    ]
    for n in range(8):
        card_coord=card_coord_list[n]
        upgrade_coord=upgrade_button_coords[n]
        
        print("Moving to card number", n+1)
        pyautogui.moveTo(card_coord[0],card_coord[1],duration=1)
        time.sleep(1)
        pyautogui.click()
        time.sleep(1)
        pyautogui.moveTo(upgrade_coord[0],upgrade_coord[1],duration=1)
        time.sleep(1)
        print(check_if_pixel_indicates_upgrade(numpy.asarray(screenshot())[upgrade_coord[1]][upgrade_coord[0]]))






    
fight(logger)
