

import random
import sys
import time


import numpy
import pygetwindow
import pyperclip
import PySimpleGUI as sg
from matplotlib import pyplot as plt

from pyclashbot.account import switch_accounts_to
from pyclashbot.auto_update import auto_update
from pyclashbot.battlepass import check_battlepass_state, check_if_can_collect_bp, collect_bp
from pyclashbot.board_scanner import find_enemy_2
from pyclashbot.card_mastery import (check_if_has_mastery_rewards,
                                     collect_mastery_rewards)
from pyclashbot.chest import check_if_has_chest_unlocking, open_chests
from pyclashbot.client import check_quit_key_press, get_next_ssid, handle_clash_main_notifications, orientate_memu
from pyclashbot.donate import click_donates, getto_donate_page
from pyclashbot.fight import (check_if_past_game_is_win, fight_with_deck_list,
                              leave_end_battle_window, start_2v2,
                              wait_for_battle_start)
from pyclashbot.launcher import (  
restart_client)
from pyclashbot.logger import Logger
from pyclashbot.request import (check_if_can_request,
                                request_from_clash_main_menu)
from pyclashbot.state import (check_if_in_a_clan_from_main, check_if_in_battle,
                              check_if_on_clash_main_menu, open_clash,
                              return_to_clash_main_menu,
                              wait_for_clash_main_menu)
from pyclashbot.upgrade import getto_card_page, upgrade_cards_from_main_2



def main_gui():
    out_text=""
    out_text=out_text+"Matthew Miglio ~May 2022\n\n"
    out_text=out_text+"Py-ClashBot can farm gold, chests, card mastery and battlepass\n"
    out_text=out_text+"progress by farming 2v2 matches with random teammates.\n"

    sg.theme('Material2')
    # defining various things that r gonna be in the gui.
    layout = [
        #first text lines
        [sg.Text(out_text)],
        #first checkboxes
        [sg.Text("Select which jobs youd like the bot to do:")],
        [
        sg.Checkbox('Fight',default=False,key="-Fight-in-"),
        sg.Checkbox('Requesting', default=False, key="-Requesting-in-"),
        sg.Checkbox('Donating',default=False,key="-Donating-in-"),
        sg.Checkbox('Upgrade cards',default=False,key="-Upgrade_cards-in-"),
        sg.Checkbox('Battlepass reward collection', default=False, key="-Battlepass_reward_collection-in-"),
        sg.Checkbox('Card mastery collection', default=False, key="-Card_mastery_collection-in-"),
        ],
        #dropdown for amount of accounts
        [sg.Text("Choose how many accounts you'd like to simultaneously farm:")],
        [sg.Combo(['1','2','3', '4'],key='-SSID_IN-')],
        #dropdown for card to request
        [sg.Text("Select the card you'd like to request:")],
        [sg.Combo(['Giant','Archers'],key='-CARD_TO_REQUEST_IN-')],
        #bottons at bottom
        [sg.Button('Start'), sg.Button('Help'), sg.Button('Donate')]
    ]
    window = sg.Window('PY-ClashBot', layout)

    # run the gui
    while True:
        event, values = window.read()

        #if window close or exit button click
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        
        #get job list
        jobs=[]
        if values["-Fight-in-"]:
            jobs.append("Fight")
        if values["-Requesting-in-"]:
            jobs.append("Request")
        if values["-Donating-in-"]:
            jobs.append("Donate")
        if values["-Upgrade_cards-in-"]:
            jobs.append("Upgrade_cards")
        if values["-Battlepass_reward_collection-in-"]:
            jobs.append("Collect_battlepass_rewards")
        if values["-Card_mastery_collection-in-"]:
            jobs.append("Collect_mastery_rewards")

        #get ssid count
        accounts=values["-SSID_IN-"]
        
        #get card_to_request
        card_to_request=values["-CARD_TO_REQUEST_IN-"]



        if event == 'Start':
            #check if vars are filled out before starting
            possible_accounts_choices=["1","2","3","4"]
            if accounts not in possible_accounts_choices:
                print("MISINPUT FOR ACCOUNTS TO FARM VAR")
                window.close()
                main_gui()
                
            possible_request_choices=["Giant","Archers"]
            if card_to_request not in possible_request_choices:
                print("MISINPUT FOR CARD TO REQUEST VAR")
                window.close()
                main_gui()
            
            
            
            window.close()
            main_loop(jobs,accounts,card_to_request)
          
        if event == 'Donate':
            show_donate_gui()

        if event == 'Help':
            show_help_gui()


          
        
    window.close()


def main_loop(jobs,accounts,card_to_request):
    logger = Logger()
    ssid_total=accounts
    current_ssid = 0
    state = "restart"
    loop_count = 0

    while True:
        if state=="restart":
            restart_state(logger)
            time.sleep(5)
            state="clash_main"
        
        if state=="clash_main":
            if clash_main_state(logger, current_ssid)=="restart": state="restart"
            else: state="start_fight"
            
        if state=="start_fight":
            if "Fight" in jobs:
                logger.log("Doing fights")
                if start_fight_state(logger)=="restart":state= "restart"
                else: state="fighting"
            else:
                logger.log("Skipping fights. Moving to request.")
                state="request"
                
        if state=="fighting":
            fighting_state(logger)
            state="post_fight"
               
        if state=="post_fight":
            if post_fight_state(logger)=="in battle":
                logger.log("Moved to post fight too soon. Passing it back to fighting state.")
                state="fighting"
            else:
                state="request"
                
        if state=="request":
            if "Request" in jobs:
                logger.log("Doing request.")
                if request_state(logger, card_to_request)=="restart":state="restart"
                else:state="donate"
            else:
                logger.log("Skipping request")
                state="donate"
            
        if state=="donate":
            if "Donate" in jobs:
                logger.log("Doing donate.")
                if donate_state(logger)=="restart": state="restart"
                else: state="upgrade"
            else:
                logger.log("Skipping donate.")
                state="upgrade"
                
        if state=="upgrade":
            if "Upgrade" in jobs:
                logger.log("Doing upgrade")
                if upgrade_state(logger)== "restart": state="restart"
                else: state="card_mastery_collection"
            else:
                logger.log("Skipping upgrade")
                state="card_mastery_collection"
                
        if state=="card_mastery_collection":
            if "Collect_mastery_rewards" in jobs:
                logger.log("Doing card mastery collection")
                if card_mastery_collection_state(logger)=="restart":state = "restart"
                else: state="battlepass_collection"
            else:
                logger.log("Skipping card mastery collection")
                state="battlepass_collection"
            
        if state=="battlepass_collection":
            if "Collect_battlepass_rewards" in jobs:
                logger.log("Doing collect battlepass rewards.")
                if battlepass_state(logger)=="restart":state="restart"
                else: state="clash_main"
            else:
                logger.log("Skipping collect battlepass rewards.")
                state="clash_main"
            

        current_ssid=get_next_ssid(current_ssid,ssid_total)
        loop_count = loop_count +1
        logger.log(f"Main is running loop: {loop_count}")
        
        
        
def show_donate_gui():
    sg.theme('Material2')
    layout = [
        [sg.Text('Paypal donate link: \n\nhttps://www.paypal.com/donate/?business=YE72ZEB3KWGVY&no_recurring=0&item_name=Support+my+projects%21&currency_code=USD'),
         sg.Text(size=(15, 1), key='-OUTPUT-')],

        [sg.Button('Exit'), sg.Button('Copy link to clipboard')]
        # https://www.paypal.com/donate/?business=YE72ZEB3KWGVY&no_recurring=0&item_name=Support+my+projects%21&currency_code=USD
    ]
    window = sg.Window('Donate', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break

        if event == "Copy link to clipboard":
            pyperclip.copy(
                'https://www.paypal.com/donate/?business=YE72ZEB3KWGVY&no_recurring=0&item_name=Support+my+projects%21&currency_code=USD')

    window.close()


def show_help_gui():
    #help menu text
    out_text=""
    out_text=out_text+"Make sure to check out the website @https://matthewmiglio.github.io/py-clash-bot/?utm_source=github.com\nor the github @https://github.com/matthewmiglio/py-clash-bot\n\n"
    out_text=out_text+"To emulate the game, Download and install MEmu.\n"
    out_text=out_text+"It is reccomended to install the emulator in Enligsh mode.\n\n"
    out_text=out_text+"Using the Multiple Instance Manager, set the instance, display and appearance settings of your instance to match that in the Readme.\n"
    out_text=out_text+"Then start the emulator and install Clash Royale with the Google Play Store.\n\n"
    out_text=out_text+"It is reccomended to play Clash Royale in English mode.\n"

    sg.theme('Material2')
    layout = [
        [sg.Text(out_text)],
        [sg.Button('Exit')],
        ]
    window = sg.Window('PY-TarkBot', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
    window.close()


        

def post_fight_state(logger):
    if check_if_in_battle():
        return "in battle"
    logger.log("STATE=post_fight")
    logger.log("Back on clash main")
    if check_if_past_game_is_win(logger):
        logger.log("Last game was a win")
        logger.add_win()
    else:
        logger.log("Last game was a loss")
        logger.add_loss()


def fighting_state(logger):
    logger.log("-----STATE=fighting-----")
    time.sleep(7)
    fightloops = 0
    while (check_if_in_battle()) and (fightloops < 100):
        check_quit_key_press()
        log = "Plays: " + str(fightloops)
        logger.log(log)
        logger.log("Scanning field.")
        enemy_troop_position = find_enemy_2()
        if enemy_troop_position is not None:
            logger.log(
                f"New enemy position alg found enemy coord to be around {enemy_troop_position[0]},{enemy_troop_position[1]}")
        logger.log("Choosing play.")
        fight_with_deck_list(enemy_troop_position)
        fightloops = fightloops + 1
    logger.log("Battle must be finished")
    time.sleep(10)
    leave_end_battle_window(logger)
    wait_for_clash_main_menu(logger)
    state = "post_fight"
    return state


def start_fight_state(logger):
    logger.log("-----STATE=start_fight-----")
    return_to_clash_main_menu()
    if start_2v2(logger) == "quit":
        # if couldnt find quickmatch button
        logger.log("Had problems finding 2v2 quickmatch button.")
        state = "restart"
    else:
        # if could find the quickmatch button
        if wait_for_battle_start(logger) == "quit":
            # if waiting for battle takes too long
            logger.log(
                "Waited too long for battle start. Restarting")
            state = "restart"
        else:
            # if battle started before wait was too long
            logger.log(
                "Battle has begun. Passing to fighting state")
            state = "fighting"
    return state


def upgrade_state(logger):
    logger.log("-----STATE=upgrade-----")
    # only run upgrade a third of the time because its fucking slow as shit
    # but what can u do yk?
    return_to_clash_main_menu()
    time.sleep(1)
    upgrade_cards_from_main_2(logger)
    time.sleep(1)
    return_to_clash_main_menu()
    logger.log("Finished with upgrading. Passing to card_mastery_collection state")
    state = "card_mastery_collection"
    return state


def card_mastery_collection_state(logger):
    logger.log("Getting to card page")
    getto_card_page(logger)
    logger.log("Checking if mastery rewards are available.")
    if check_if_has_mastery_rewards():
        logger.log(
            "Mastery rewards are available. Running mastery collection alg.")
        collect_mastery_rewards(logger)
    logger.log("No mastery rewards are available.")
    logger.log(
        "Done with card mastery collection. Passing to battlepass collection state.")
    state = "battlepass"
    return state


def donate_state(logger):
    logger.log("-----STATE=donate-----")
    logger.log("Checking if in a clan")
    time.sleep(2)
    do_upgrade = 1 == random.randint(1, 3)
    if check_if_in_a_clan_from_main(logger):
        logger.log("Starting donate alg.")
        time.sleep(2)
        if getto_donate_page(logger) == "quit":
            # if failed to get to clan chat page
            logger.log("Failed to get to clan chat page. Restarting")
            state = "restart"
        else:
            # if got to clan chat page
            logger.log(
                "Successfully got to clan chat page. Starting donate alg")
            click_donates(logger)
            if do_upgrade:
                logger.log("Done with donating. Passing to upgrade state")
                state = "upgrade"
            else:
                logger.log("Done with donating. Passing to start_fight state")
                state = "start_fight"
    else:
        logger.log("You're not in a clan. Skipping donate.")
        if do_upgrade:
            logger.log("Passing to upgrade state")
            state = "upgrade"
        else:
            logger.log("Passing to start_fight state")
            state = "start_fight"
    return state


def request_state(logger, card_to_request):
    logger.log("State=REQUEST")


    logger.log("-----STATE=request-----")
    logger.log("Trying to get to donate page")
    if getto_donate_page(logger) == "quit":
        # if failed to get to clan chat page
        logger.log("Failed to get to clan chat page. Restarting")
        state = "restart"
    else:
        # if got to clan chat page
        log = "Trying to request " + str(card_to_request) + "."
        logger.log(log)
        if request_from_clash_main_menu(
                card_to_request, logger) == "quit":
            # if request failed
            log = "Failed to request " + str(card_to_request) + "."
            logger.log(log)
        logger.log("Done with requesting. Passing to donate state.")
        return_to_clash_main_menu()
        time.sleep(2)
        state = "donate"
    return state


def clash_main_state(logger, ssid):
    logger.log("-----STATE=clash_main-----")
    
    #handle dumb popups        
    logger.log("Handling clash main notifications.")
    handle_clash_main_notifications()
    
    # account switch
    logger.log("Logging in to the correct account")
    if switch_accounts_to(logger, ssid) == "quit":
        # if switching accounts fails
        logger.log("Failed to switch accounts. Restarting")
        return "restart"
    else:
        # if switching accounts works
        logger.log("Successfully switched accounts.")
        # open chests
        if check_if_on_clash_main_menu():
            logger.log(
                "Checking if a chest is being unlocked right now.")
            if not check_if_has_chest_unlocking():
                logger.log(
                    "Found no unlocking symbols. Opening chests.")
                open_chests(logger)
                time.sleep(2)
    

def restart_state(logger):
    logger.log("-----STATE=restart-----")

    restart_client(logger)
    if open_clash(logger) == "quit":
        state = "restart"
    else:
        if check_if_on_clash_main_menu():
            state = "clash_main"
        else:
            state = "restart"
    return state


def battlepass_state(logger):
    logger.log("-----STATE=battlepass-----")
    logger.log("Handling battlepass rewards")
    if check_if_can_collect_bp():
        # if we can collect rewards
        logger.log("Battlepass rewards are available.")
        collect_bp(logger)
    else:
        logger.log("Battlepass rewards are unavailable. Continuing to a fight.")
    state = "start_fight"
    return state








def end_loop():
    print("Press ctrl-c to close the program.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        sys.exit()


if __name__ == "__main__":
    # try:
    #     main_gui()
    # finally:
    #     end_loop()
    
    main_gui()
