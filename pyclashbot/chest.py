from ast import Str
import pyautogui
import time

from pyclashbot.client import check_quit_key_press, click, screenshot
from pyclashbot.image_rec import find_references


def check_if_unlock_chest_button_exists():
    current_image = screenshot()
    reference_folder = "unlock_chest_button"
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
        "6.png",
        "7.png",
        "8.png",
        "9.png",
        "10.png",
        "11.png",
        
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.90
    )

    for location in locations:
        if location is not None:
            return True
    return False


def look_for_clock():
    current_image = screenshot(region=(35, 490, 360, 40))
    reference_folder = "unlocking_chest_images"
    references = [
        "chest_unlocking_1.png",
        "chest_unlocking_2.png",
        "chest_unlocking_3.png",
        "chest_unlocking_4.png",
        "chest_unlocking_5.png",
        "e1.png",
        "e2.png",
        "e3.png",
        "e4.png",
        "e5.png",
        "e6.png",
        "e7.png",
        "e8.png",
        "e9.png",
        "e10.png",
        "e11.png",
        "e12.png",
        "e13.png",
        "e14.png",
        "e15.png",
        "e16.png",
        "e17.png",
        "e18.png",
        "e19.png",
        "e20.png",
        "e21.png",
        "e22.png",
        "e23.png",
        "e24.png",
        "e25.png",
        "e26.png",
        "e27.png",
        "e28.png",
        "e29.png",
        "e30.png",
        "e31.png",
        "e32.png",
        "e33.png",
        "e34.png",
        "e35.png",
        "e36.png",
        "e37.png",
        "e38.png",
        "e39.png",
        "e40.png",
        "e41.png",
        "e42.png",
        "e43.png",
        "e44.png",
        "e45.png",
        "e46.png",
        "e47.png",
        "e48.png",
        "e49.png",
        "e50.png",
        "e51.png",
        "e52.png",
        "e53.png",
        "e54.png",
        "e55.png",
        "e56.png",
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97
    )

    for location in locations:
        if location is not None:
            # found a location
            return True
    return False


def check_if_has_chest_unlocking():
    n = 10
    while n != 0:
        if look_for_clock():
            return True
        else:
            n = n - 1
            time.sleep(0.2)

#method to handle the chest unlocking in any state
def open_chests(logger):
    #unlock coord (210, 455)
    #chest 1 coord (78, 554)
    #chest 2 coord (162,549)
    #chest 3 coord (263,541)
    #chest 4 coord (349 551)
    #dead space coord (20, 556)
    #check_if_unlock_chest_button_exists()
    
    chest_coord_list=[[78, 554],[162,549],[263,541],[349,551]]
    
    chest_index=0
    for chest_coord in chest_coord_list:
        chest_index=chest_index+1
        
        #click chest
        click(chest_coord[0],chest_coord[1])
        time.sleep(1)
        
        if check_if_unlock_chest_button_exists():
            print("Found unlock in chest", chest_index)
            time.sleep(0.5)
            
            logger.log(str("Unlocking chest " + str(chest_index)))
            time.sleep(0.5)
            click(210, 465)
            
        else:
            logger.log("Handling possibility of rewards screen")
            click(20,556,clicks=20,interval=0.1)
            time.sleep(3)
    
        
        #close chest menu
        click(20,556)
        time.sleep(0.33)
