import os
import pyautogui
from matplotlib import pyplot as plt
from PIL import Image
import numpy
import sys
import time

import keyboard
from ahk import AHK


import pygetwindow



ahk = AHK()




#Method to cycle through a list of ints (1 -> 2 -> 3 -> 1 -> 2 -> 3 -> ...)
def get_next_ssid(current_ssid,ssid_total):
    return 0 if (current_ssid + 1) == ssid_total else current_ssid + 1

#Method to return a screenshot of a given region
def screenshot(region=[0,0,500,700]):
    return pyautogui.screenshot(region=region)

#Method for scrolling up faster when interacting with a scrollable menu
def scroll_up_fast():
    origin = pyautogui.position()
    pyautogui.moveTo(x=215, y=300)
    pyautogui.dragTo(x=215, y=350, button='left', duration=0.5)
    pyautogui.moveTo(x=origin[0], y=origin[1])

#Method for scrolling down faster when interacting with a scrollable menu
def scroll_down_fast():
    origin = pyautogui.position()
    pyautogui.moveTo(x=215, y=350)
    pyautogui.dragTo(x=215, y=300, button='left', duration=0.5)
    pyautogui.moveTo(x=origin[0], y=origin[1])

#Method for scrolling down even faster when interacting with a scrollable menu
def scroll_down_super_fast():
    origin = pyautogui.position()
    pyautogui.moveTo(x=215, y=400)
    pyautogui.dragTo(x=215, y=300, button='left', duration=0.2)
    pyautogui.moveTo(x=origin[0], y=origin[1])

#Method for clearing the terminal
def clear_log():
    os.system('cls||clear')
    
#Method for terminating the program upon key press
def check_quit_key_press():
    if keyboard.is_pressed("space"):
        print("Space is held. Quitting the program")
        sys.exit()
    if keyboard.is_pressed("pause"):
        print("Pausing program until pause is held again")
        time.sleep(5)
        pressed = False
        while not (pressed):
            time.sleep(0.05)
            if keyboard.is_pressed("pause"):
                print("Pause held again. Resuming program.")
                time.sleep(3)
                pressed = True

#Method to return the amount of a files in a given directory
def get_file_count(directory) :
    count = 0
    for root_dir, cur_dir, files in os.walk(directory):
        count += len(files)
    #print('file count:', count)
    return count
        
#Method for orientating Memu client
def orientate_memu():
    try:
        window_memu = pygetwindow.getWindowsWithTitle('MEmu')[0]
        window_memu.minimize()
        window_memu.restore()
        time.sleep(0.2)
        try:
            window_memu.moveTo(0, 0)
        except pygetwindow.PyGetWindowException:
            print("Had trouble moving MEmu window.")
        time.sleep(0.2)
        try:
            window_memu.resizeTo(460, 680)
        except pygetwindow.PyGetWindowException:
            print("Had trouble resizing MEmu window")
    except:
        print("Couldnt orientate MEmu")

#Method for orientating the Memu Multi Manager
def orientate_memu_multi():
    try:
        try:
            window_mimm = pygetwindow.getWindowsWithTitle(
                'Multiple Instance Manager')[0]
        except Exception:
            window_mimm = pygetwindow.getWindowsWithTitle('Multi-MEmu')[0]

        window_mimm.minimize()
        window_mimm.restore()
        #window_mimm.moveTo(200, 200)
        time.sleep(0.2)
        window_mimm.moveTo(0, 0)
    except:
        print("Couldnt orientate MIMM")
        
#Method to show a PIL image using matlibplot
def show_image(image):
    plt.imshow(numpy.asarray(image))
    plt.show()

#Method to wait for the user to press spacebar
def pause():
    waiting=True
    clear_log()
    print("Pausing the program. Press spacebar to continue")
    while waiting:
        time.sleep(1)
        if keyboard.is_pressed("space"): 
            print("Space held - Resuming the program")
            waiting=False
     
#Method to compare the equality of two coords
def compare_coords(coord1,coord2):
    return (coord1[0] == coord2[0] and coord1[1] == coord2[1])

#Method for clicking a given coordinate
def click(x,y,duration=1):
    #30 speed = 3 seconds
    speed=duration*10                                                             
    
    #Tolerance for timer comparisons
    tol=0.5
    
    #timer for mouse movement
    start = time.time()
    ahk.mouse_move(x=x, y=y, speed=speed, blocking=False)
    
    while True:
        if ahk.mouse_position == (x, y):
            break
 
        if (time.time() - start) > (speed/10)+tol:                          
            pause()
            start = time.time()
            ahk.mouse_move(x=x, y=y, speed=speed, blocking=False)
            
            
    ahk.click()
    
#Method for scrolling down when interacting with a scrollable menu
def scroll_down():
    origin = pyautogui.position()
    pyautogui.moveTo(x=215, y=350)
    pyautogui.dragTo(x=215, y=300, button='left', duration=1)
    pyautogui.moveTo(x=origin[0], y=origin[1])

