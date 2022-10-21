import random
import time
from ast import Str

import numpy

from card_detection import (get_card_group, get_card_images, get_play_coords,
                            identify_card)
from clashmain import (check_if_in_battle, check_if_on_clash_main_menu,
                       wait_for_clash_main_menu)
from client import click, screenshot
from image_rec import pixel_is_equal


def fight(logger):
    logger.change_status("Starting fight")
    in_battle=True
    plays=0
    
    while in_battle:
        #wait for 6 elixer
        if wait_until_has_6_elixer()=="restart": return "restart"
       
        play_random_card(logger)
        plays+=1
        logger.change_status("Played card. Plays: "+str(plays))
        
        in_battle=check_if_in_battle()
        
        if plays>100: 
            logger.change_status("Made too many plays. Match is probably stuck. Ending match")
            return "restart"
        
        
    logger.change_status("Done fighting.")
        
    
#Method for finishing leaving a battle and returning to the clash royale main menu
def leave_end_battle_window(logger):
    
    #if end screen condition 1 (exit in bottom left)
    if check_if_end_screen_is_exit_bottom_left():
        click(79,625)
        time.sleep(1)
        if wait_for_clash_main_menu(logger)=="restart":return "restart"
        return
    
    #if end screen condition 2 (OK in bottom middle)
    if check_if_end_screen_is_ok_bottom_middle():
        click(206,594)
        time.sleep(1)
        if wait_for_clash_main_menu(logger)=="restart":return "restart"
        return
    
    
    if wait_for_clash_main_menu(logger)=="restart": return 'restart'

#Method to check if the end screen is the one with the OK button in the middle
def check_if_end_screen_is_ok_bottom_middle():
    iar = numpy.asarray(screenshot())
    #(210,589)
    pix_list=[
        iar[591][234],
        iar[595][178],
        iar[588][192],
        iar[591][233],
        
    ]
    color=[ 78, 175 ,255]
    for pix in pix_list:
        #print(pix)
        if not (pixel_is_equal(pix,color,tol=45)):
            return False
    return True





#Method to check if the end screen is the one with the exit button in the bottom left
def check_if_end_screen_is_exit_bottom_left():
    iar = numpy.asarray(screenshot())
    pix_list=[
        iar[638][57],
        iar[640][110],
        iar[622][59],
        iar[621][110],
    ]
    color=[87, 186 ,255]
    for pix in pix_list:
        if not (pixel_is_equal(pix,color,tol=45)):
            return False
    return True




#Method for opening the activity log from the clash royale main menu as to see past game outcomes
def open_activity_log():
    click(x=360, y=99)
    time.sleep(1)

    click(x=255, y=75)
    time.sleep(1)

#Method for reading the actiivty log to check if the previous game was a win or loss
def check_if_past_game_is_win(logger):
    open_activity_log()
    iar = numpy.asarray(screenshot())

    for n in range(40, 130):
        pix = iar[191][n]
        sentinel = [1] * 3
        sentinel[0] = 102
        sentinel[1] = 204
        sentinel[2] = 255
        if pixel_is_equal(pix, sentinel, 10):
            click(20, 507)

            logger.change_status("Last game was a win. Incrementing win counter.")
            logger.add_win()
            return True
    time.sleep(1)
    click(385, 507)
    click(20, 507)
    
    logger.change_status("Last game was a loss. Incrementing loss counter.")
    logger.add_loss()
    return False
    
#Method to see if the bot has 6 expendable elixer in the given moment during a battle
def check_if_has_6_elixer():
    iar=numpy.asarray(screenshot())
    pix_list=[
        #iar[643][258],
        iar[648][272],
        iar[649][257],
    ]
    color=[208,34,214]
    
    
    #print(pix_list)
    
    for pix in pix_list:
        if not(pixel_is_equal(pix,color,tol=45)):
            return False
    return True

#Method to wait untili the bot has 6 expendable elixer
def wait_until_has_6_elixer():
    has_6=check_if_has_6_elixer()
    #logger.change_status("Waiting for 6 elixer")
    loops=0
    while not(has_6):
        loops+=1
        if loops>250:
            print("Waited too long for 6 elixer")
            return "restart"
        time.sleep(0.1)
        has_6=check_if_has_6_elixer()
        if check_if_in_battle()==False:
            return
    
#Method to play a random card
def play_random_card(logger):
    #Select which card we're to play
    n=random.randint(0,3)
    #logger.change_status(str("Selected card: "+str(n)))
    
    #Get an image of this card
    card_image=get_card_images()[n]
    
    #Identify this card
    card_identification = identify_card(card_image)
    if card_identification is None: card_identification = "Unknown"
    #logger.change_status(str("Identified card: "+card_identification))
    
    #Get the card type of this identification
    card_type = get_card_group(card_identification)
    if card_type is None: card_type = "unknown"
    #logger.change_status(str("Card type: "+card_type))
    
    #Get the play coordinates of this card type
    play_coords_list=get_play_coords(card_type)

    #Pick one of theses coords at random
    play_coord = random.choice(play_coords_list)
    
    #Click the card we're playing
    if n==0: click(152,607)
    if n==1: click(222,602)
    if n==2: click(289,606)
    if n==3: click(355,605)
    
    #Click the location we're playing it at
    click(play_coord[0],play_coord[1])
