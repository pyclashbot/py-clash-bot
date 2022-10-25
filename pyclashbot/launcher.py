import subprocess
import time

import pygetwindow

from pyclashbot.clashmain import wait_for_clash_main_menu
from pyclashbot.client import (check_quit_key_press, click, orientate_memu,
                               orientate_memu_multi, orientate_terminal,
                               screenshot)
from pyclashbot.dependency import setup_memu
from pyclashbot.image_rec import (check_for_location, find_references,
                                  get_first_location)

launcher_path = setup_memu()  # setup memu, install if necessary

#Method for restarting Memu and MeMU Multi Manager, opening clash, and waiting for the clash main menu to appear.
def restart_and_open_clash(logger):
    #If Memu is running, close it
    if len (pygetwindow.getWindowsWithTitle("MEmu")) != 0: close_memu()

    #If MeMU Multi Manager is running, close it
    if len (pygetwindow.getWindowsWithTitle("Multiple Instance Manager")) != 0: close_memu_multi()

    orientate_terminal()
    
    #Open the Memu Multi Manager
    logger.change_status("Opening MEmu launcher")
    subprocess.Popen(launcher_path)

    #WAIT 10 SECONDS
    for n in range(10):
        logger.change_status(f"Giving Memu Multi time to load: {str(n)}")
        time.sleep(1)


    #Orientate the Memu Multi Manager
    orientate_memu_multi()
    time.sleep(3)

    #Start Memu Client
    logger.change_status("Starting Memu client instance")
    click(556,141)
    time.sleep(3)
    check_quit_key_press()

    #orientate memu client
    orientate_memu()
    time.sleep(3)

    #Wait for Memu Client loading screen
    if wait_for_memu_loading_screen(logger): restart_and_open_clash(logger)
    time.sleep(3)




    #Skip Memu ads
    if find_clash_app_logo() is None: skip_ads(logger)
    time.sleep(3)

    #Wait for clash logo to appear
    if wait_for_clash_logo_to_appear(logger)=="restart":
        logger.change_status("Waited too long for clash logo to appear. Restarting")
        restart_and_open_clash(logger)
    time.sleep(3)

    #Click the clash logo
    logo_coords=find_clash_app_logo()
    if logo_coords is not None:
        click(logo_coords[1],logo_coords[0])

    #Wait for the clash main menu to appear
    if wait_for_clash_main_menu(logger) == "restart":
        restart_and_open_clash(logger)
    time.sleep(3)

#Method to wait for memu loading background to disappear
def wait_for_memu_loading_screen(logger):
    logger.change_status("Waiting for Memu Client to load")
    waiting=True
    n=0
    loops=0
    while waiting:
        loops+=1
        if loops>20:
            logger.change_status("Waited too long for memu client to load, restarting")
            return "restart"
        n=n+1
        time.sleep(1)
        logger.change_status(f"Waiting for memu Client to load: {str(n)}")
        waiting=check_for_memu_loading_background()
    time.sleep(3)
    logger.change_status("Done waiting for Memu Client to load.")
    time.sleep(3)

#Method for skipping the memu ads that popip up when you start memu
def skip_ads(logger):
    logger.change_status("Skipping ads")
    for _ in range(4):
        click(445,600)
        time.sleep(1)
    time.sleep(3)

#Method for waiting for memu to finish loading and display the memu home menu
def wait_for_clash_logo_to_appear(logger):
    n=0
    waiting=True
    loops=0
    while waiting:
        loops+=1
        if loops>35:
            logger.change_status("Waited too long for clash logo to appear, restarting")
            return "restart"
        n=n+1
        time.sleep(1)
        logger.change_status(f"Waiting for clash logo to appaer: {str(n)}")

        logo_coords=find_clash_app_logo()

        if logo_coords is not None: waiting = False

#Method to check if memu loading background is present in the given moment
def check_for_memu_loading_background():
    check_quit_key_press()
    current_image = screenshot()
    reference_folder = "memu_loading_background"
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
        "5.png",
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.99
    )

    return check_for_location(locations)

#Method to find the coordinates of the clash app logo on the menu home screen
def find_clash_app_logo():
    current_image = screenshot()
    reference_folder = "logo"
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
        
        
        
    ]


    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.99
    )

    return get_first_location(locations)

#Method to close memu
def close_memu():
    try:
        window=pygetwindow.getWindowsWithTitle("(MEmu)")[0]
        window.close()
        print("Closed Memu")
        time.sleep(3)
    except:
        print("Couldnt close Memu using title (MEmu)")

    try:
        window=pygetwindow.getWindowsWithTitle("(MEmu1)")[0]
        window.close()
        print("Closed Memu")
        time.sleep(3)
    except:
        print("Couldnt close Memu using title (MEmu1)")

#Method to close memu multi
def close_memu_multi():
    try:
        window=pygetwindow.getWindowsWithTitle("Multiple Instance Manager")[0]
        window.close()
        print("Closed Memu Multi")
        time.sleep(3)
    except:
        print("Couldnt close Memu Multi")

