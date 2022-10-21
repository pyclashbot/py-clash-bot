import os
import random
import time
from itertools import count
from os.path import dirname, join

import ahk
import numpy
from ahk import AHK

from client import (click, get_next_ssid, orientate_memu, orientate_memu_multi,
                    screenshot, scroll_down, show_image)
from configuration import load_user_config
from fight import leave_end_battle_window
from image_rec import pixel_is_equal
from logger import Logger
from pyclashbot.states import state_request
from request import check_if_in_a_clan, request_random_card_from_clash_main
from states import (state_clashmain, state_endfight, state_fight,
                    state_startfight)

ahk = AHK()
logger = Logger()
user_settings = load_user_config()
launcher_path = user_settings["launcher_path"]


# orientate_memu_multi()
# orientate_memu()
time.sleep(1)

# show_image(screenshot())


# state_fight(logger)

# check_if_end_screen_is_ok_middle()




def battle_end_debug_main():
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



state_request(logger)
