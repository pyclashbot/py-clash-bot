from ast import Str
from cgi import test
from multiprocessing.connection import wait
from re import T
from tabnanny import check
from tracemalloc import start
from PIL import Image
from matplotlib.font_manager import ttfFontProperty
import numpy as np
import matplotlib.pyplot as plt
from pkg_resources import compatible_platforms
import pyautogui
import pygetwindow as gw
import time
import random
import PySimpleGUI as sg   
from pynput import keyboard 
from pynput.keyboard import Key, Listener  
import keyboard

#vars
fights=0
wins=0
losses=0
duration=0.5
fightduration=0.2
loop_count=0
default_board_state=[1]*8

def refresh_screen():
     check_quit_key_press()
     orientate_window(win)
     screenshot = pyautogui.screenshot()
     check_quit_key_press()
     iar = np.array(screenshot)
     return iar
     
def show_image(iar):
     plt.imshow(iar)
     check_quit_key_press()
     plt.show()
     
def orientate_window(win):

     win = gw.getWindowsWithTitle('MEmu')[0]
     '''move to topleft function'''
     check_quit_key_press()
     win.minimize()
     win.restore()
     win.moveTo(0, 0)
     win.resizeTo(460,680)
      
def orientate_memu_multi():

     win2 = gw.getWindowsWithTitle('Multiple Instance Manager')[0]
     check_quit_key_press()
     win2.minimize()
     win2.restore()
     win2.moveTo(0, 0)
     
def open_clash():
     check_quit_key_press()
     print(calculate_time(start_time),"opening clash")
     pyautogui.moveTo(x=60,y=336,duration=duration)
     pyautogui.click()
     wait_for_clash_main_menu()

def check_if_on_memu_main():
     iar = refresh_screen()
     check_quit_key_press()
     
     pix2 = iar[71][142]
     pix3 = iar[77][275]
     

     sentinel = [1] * 3
     sentinel[0] = 5
     sentinel[1] = 18
     sentinel[2] = 35
     check_quit_key_press()
     if compare_pixels(pix2, sentinel) == "diff":
          return 0
     if compare_pixels(pix3, sentinel) == "diff":
          return 0
     return 1
        
def compare_pixels(pix1, pix2):
     check_quit_key_press()
     diff_r = abs(pix1[0] - pix2[0])
     diff_g = abs(pix1[1] - pix2[1])
     diff_b = abs(pix1[2] - pix2[2])
     if (diff_r < 10) and (diff_g < 10) and (diff_b < 10):
          return "same"
     else:
          return "diff"
     check_quit_key_press()
     
def check_if_has_chests():
     has_chests = [1] * 4
     check_quit_key_press()
     iar = refresh_screen()
     slot1_pix = iar[573][102]
     slot2_pix = iar[569][160]
     slot3_pix = iar[562][273]
     slot4_pix = iar[570][343]
     sentinel = [1] * 3
     sentinel[0] = 25 
     sentinel[1] = 98 
     sentinel[2] = 127
     
     if compare_pixels(slot1_pix,sentinel) == "diff":
          has_chests[0] = 1
     else:
          has_chests[0] = 0
     
     if compare_pixels(slot2_pix,sentinel) == "diff":
          has_chests[1] = 1
     else:
          has_chests[1] = 0
     
     if compare_pixels(slot3_pix,sentinel) == "diff":
          has_chests[2] = 1
     else:
          has_chests[2] = 0
     
     if compare_pixels(slot4_pix,sentinel) == "diff":
          has_chests[3] = 1
     else:
          has_chests[3] = 0
     
     check_quit_key_press()
     return has_chests

def open_chests():
     check_quit_key_press()
     n = check_if_has_chests()
     if n[0] == 1:
          print(calculate_time(start_time),"Chest detected in slot 1")
          pyautogui.moveTo(x=78,y=554,duration=duration)
          pyautogui.click()
          check_quit_key_press()
          time.sleep(1)
          pyautogui.moveTo(x=208,y=455,duration=duration)
          pyautogui.click()
          time.sleep(1)
          pyautogui.click(x=20, y=556, clicks=20, interval=0.2, button='left')
          check_quit_key_press()
     if n[1] == 1:
          print(calculate_time(start_time),"Chest detected in slot 2")
          pyautogui.moveTo(x=162,y=549,duration=duration)
          check_quit_key_press()
          pyautogui.click()
          time.sleep(1)
          pyautogui.moveTo(x=208,y=455,duration=duration)
          pyautogui.click()
          time.sleep(1)
          pyautogui.click(x=20, y=556, clicks=20, interval=0.2, button='left')
          check_quit_key_press()
     if n[2] == 1:
          print(calculate_time(start_time),"Chest detected in slot 3")
          check_quit_key_press()
          pyautogui.moveTo(x=263,y=541,duration=duration)
          pyautogui.click()
          time.sleep(1)
          pyautogui.moveTo(x=208,y=455,duration=duration)
          pyautogui.click()
          time.sleep(1)
          pyautogui.click(x=20, y=556, clicks=20, interval=0.2, button='left')
          check_quit_key_press()
     if n[3] == 1:
          print(calculate_time(start_time),"Chest detected in slot 4")
          pyautogui.moveTo(x=349,y=551,duration=duration)
          check_quit_key_press()
          pyautogui.click()
          time.sleep(1)
          pyautogui.moveTo(x=208,y=455,duration=duration)
          pyautogui.click()
          time.sleep(1)
          pyautogui.click(x=20, y=556, clicks=20, interval=0.2, button='left')
          check_quit_key_press()
          
def check_if_on_clash_main_menu():
     check_quit_key_press()
     iar = refresh_screen()
     pix1 = iar[94][385]
     pix2 = iar[95][403]
     pix3 = iar[106][396]
     sentinel = [1] * 3
     sentinel[0] = 9 
     sentinel[1] = 52 
     sentinel[2] = 73
     

     
     if compare_pixels(pix1,sentinel) == "diff":
          return 0
     if compare_pixels(pix2,sentinel) == "diff":
          return 0
     if compare_pixels(pix3,sentinel) == "diff":
          return 0
     check_quit_key_press()
     return 1
     
def check_if_can_request():
     iar = refresh_screen()
     pix1 = iar[612][326]
     pix2 = iar[606][334]
     pix3 = iar[608][326]
     sentinel = [1] * 3
     sentinel[0] = 49 
     sentinel[1] = 186 
     sentinel[2] = 71
     check_quit_key_press()

     
     if compare_pixels(pix1, sentinel) == "diff":
          return 0
     if compare_pixels(pix2, sentinel) == "diff":
          return 0
     if compare_pixels(pix3, sentinel) == "diff":
          return 0
     check_quit_key_press()
     return 1
     
def request_from_clash_main_menu():
     check_quit_key_press()
     print(calculate_time(start_time),"Moving to clan chat page")
     pyautogui.moveTo(x=317,y=627,duration=duration)
     pyautogui.click()
     while check_if_on_clan_chat_page() == 0:
          pyautogui.moveTo(x=317,y=627,duration=duration)
          pyautogui.click()
          time.sleep(2)
     print(calculate_time(start_time),"requesting giant")
     pyautogui.moveTo(x=86,y=564,duration=duration)
     pyautogui.click()
     time.sleep(1)
     check_quit_key_press()
     pyautogui.scroll(-20, x=0, y=0)
     time.sleep(3)
     check_quit_key_press()
     pyautogui.scroll(-20, x=0, y=0)
     time.sleep(3)
     pyautogui.scroll(-20, x=0, y=0)
     check_quit_key_press()
     time.sleep(3)
     pyautogui.scroll(-20, x=0, y=0)
     time.sleep(3)
     pyautogui.scroll(-20, x=0, y=0)
     time.sleep(3)
     check_quit_key_press()
     pyautogui.moveTo(x=340,y=250,duration=duration)
     pyautogui.click()
     pyautogui.moveTo(x=330,y=520,duration=duration)
     pyautogui.click()
     time.sleep(3)
     check_quit_key_press()
     return_to_clash_main_menu()
          
def check_if_on_clan_chat_page():
     check_quit_key_press()
     iar = refresh_screen()
     pix1 = iar[573][109]
     pix2 = iar[573][116]
     pix3 = iar[573][121]
     sentinel = [1] * 3
     sentinel[0] = 255 
     sentinel[1] = 188 
     sentinel[2] = 42
     
     if compare_pixels(pix1,sentinel) == "diff":
          return 0
     if compare_pixels(pix2,sentinel) == "diff":
          return 0
     if compare_pixels(pix3,sentinel) == "diff":
          return 0
     check_quit_key_press()
     return 1
     
def return_to_clash_main_menu():
     check_quit_key_press()
     print(calculate_time(start_time),"Returning to clash main menu")
     pyautogui.moveTo(x=180,y=625,duration=duration)
     pyautogui.click()
     check_quit_key_press()
     
def start_2v2():
     check_quit_key_press()
     print(calculate_time(start_time),"Navigating to 2v2 match")
     pyautogui.moveTo(x=280,y=440,duration=duration)
     pyautogui.click() 
     time.sleep(2) 
     pyautogui.scroll(-10, x=0, y=0)
     time.sleep(3)
     pyautogui.moveTo(x=300,y=300,duration=duration)
     pyautogui.click() 
     check_quit_key_press()
     
def start_1v1_ranked():
     check_quit_key_press()
     print(calculate_time(start_time),"Navigating to 1v1 ranked match")
     pyautogui.moveTo(x=140,y=440,duration=duration)
     pyautogui.click() 
     wait_for_battle_start()
     check_quit_key_press()

def wait_for_battle_start():
     print(calculate_time(start_time),"Waiting for battle start")
     n = 1
     n1 = 0
     check_quit_key_press()
     while n == 1: 
          n1 = n1 + 1
          if check_if_in_battle() == 1:
               n = 0
          time.sleep(1)
          if n1 > 90:
               print("Waited longer than 90 sec for a fight")
               break
          refresh_screen()
     check_quit_key_press()
          
def fight_in_2v2():
     check_quit_key_press()
     time.sleep(3)
     card_pick = random_card_coord_picker()
     card_placement = random_placement_coord_maker()
     pyautogui.moveTo(x=card_pick[0],y=card_pick[1],duration=fightduration)
     pyautogui.click()
     pyautogui.moveTo(x=card_placement[0],y=card_placement[1],duration=fightduration)
     pyautogui.click()
     check_quit_key_press()
       
def random_placement_coord_maker():
     check_quit_key_press()
     n = random.randint(1 ,6)
     coords = [1] * 2
     if n == 0:
          coords[0] = 55
          coords[1] = 333
     if n == 1:
          coords[0] = 55
          coords[1] = 333
     if n == 2:
          coords[0] = 73
          coords[1] = 439
     if n == 3:
          coords[0] = 177
          coords[1] = 502
     if n == 4:
          coords[0] = 240
          coords[1] = 515
     if n == 5:
          coords[0] = 346
          coords[1] = 429
     if n == 6:
          coords[0] = 364
          coords[1] = 343 
     check_quit_key_press()
     return coords
     
def random_card_coord_picker():
     check_quit_key_press()
     n = random.randint(1,4)
     coords = [1] * 2
     if n == 1:
          #print(calculate_time(start_time),"randomly selected card 1")
          coords[0] = 146
          coords[1] = 588
     if n == 2:
          #print(calculate_time(start_time),"randomly selected card 2")
          coords[0] = 206
          coords[1] = 590
     if n == 3:
          #print(calculate_time(start_time),"randomly selected card 3")
          coords[0] = 278
          coords[1] = 590
     if n == 4:
          #print(calculate_time(start_time),"randomly selected card 4")
          coords[0] = 343
          coords[1] = 588
     check_quit_key_press()
     
     return coords

def check_if_in_battle():
     check_quit_key_press()
     iar = refresh_screen()
     pix1 = iar[551][56]
     pix2 = iar[549][78]
     pix3 = iar[567][73]
     sentinel = [1] * 3
     sentinel[0] = 255 
     sentinel[1] = 255 
     sentinel[2] = 255


     if compare_pixels(pix1,sentinel) == "diff":
          return 0
     if compare_pixels(pix2,sentinel) == "diff":
          return 0
     if compare_pixels(pix3,sentinel) == "diff":
          return 0
     check_quit_key_press()
     return 1

def leave_end_battle_window():
     check_quit_key_press()
     print(calculate_time(start_time),"battle is over. return to clash main menu")
     pyautogui.moveTo(x=81,y=630,duration=duration)
     pyautogui.click()
     time.sleep(5)
     check_quit_key_press()

def calculate_time(start_time):
     check_quit_key_press()
     output_time = time.time()-start_time
     output_time = int(output_time)
     check_quit_key_press()
     
     time_str = str(convert_int_to_time(output_time))
     wins_str = str(wins)+"W"
     losses_str = str(losses)+"L"
     gap_str = "|"
     output_string = time_str+gap_str+wins_str+gap_str+losses_str+": "
     
     return output_string

def refresh_clan_tab():
     check_quit_key_press()
     pyautogui.moveTo(x=300,y=630,duration=duration)
     pyautogui.click()
     return_to_clash_main_menu()
     time.sleep(3)
     check_quit_key_press()

def check_if_exit_battle_button_exists():
     check_quit_key_press()
     iar = refresh_screen()
     pix1 = iar[634][52]
     pix3 = iar[640][107]
     sentinel = [1] * 3
     sentinel[0] = 76 
     sentinel[1] = 174 
     sentinel[2] = 255
     if compare_pixels(pix1, sentinel) == "diff":
          return 0
     if compare_pixels(pix3, sentinel) == "diff":
          return 0
     check_quit_key_press()
     return 1
     
def find_donates():
     print(calculate_time(start_time),"searching screen for green donate buttons")
     iar = refresh_screen()
     check_quit_key_press()
     sentinel = [1] * 3
     sentinel[0] = 106 
     sentinel[1] = 235 
     sentinel[2] = 118

     n = 110
     coords = [1]*2
     while n < 510:
          if compare_pixels(iar[n][286],sentinel) == "same":
               coords[0] = 286
               coords[1] = n
               print(calculate_time(start_time),"found a donate button")
               return coords
          n = n+1
     while n < 510:
          if compare_pixels(iar[n][343],sentinel) == "same":
               coords[0] = 286
               coords[1] = n
               print(calculate_time(start_time),"found a donate button")
               return coords
     while n < 510:
          if compare_pixels(iar[n][284],sentinel) == "same":
               coords[0] = 286
               coords[1] = n
               print(calculate_time(start_time),"found a donate button")
               return coords
          n = n+1
     print(calculate_time(start_time),"Searched entire boundary without finding donate button")
     check_quit_key_press()
     
def click_donates():
     print(calculate_time(start_time),"clicking the donate buttons if there are any available")
     check_quit_key_press()
     n = 0
     while n < 3:
          coords = [1]*2
          if find_donates() == None:
               coords[0] = 385
               coords[1] = 507
          else:
               coords = find_donates()
          pyautogui.moveTo(x=coords[0],y=coords[1],duration=duration)
          pyautogui.click(x=coords[0], y=coords[1], clicks=5, interval=0.2, button='left')  
          pyautogui.moveTo(x=385,y=507,duration=duration)
          pyautogui.click(x=385, y=507, clicks=1, interval=0.2, button='left')  
          
          if check_if_more_donates() == 1:
               pyautogui.moveTo(x=50,y=170,duration=duration)
               pyautogui.click()  
          
          pyautogui.moveTo(x=coords[0],y=coords[1],duration=duration)
          pyautogui.click(x=coords[0], y=coords[1], clicks=5, interval=0.2, button='left')  
          pyautogui.moveTo(x=385,y=507,duration=duration)
          pyautogui.click(x=385, y=507, clicks=1, interval=0.2, button='left') 
          
          n=n+1
     pyautogui.moveTo(x=393,y=525,duration=duration)
     pyautogui.click() 
     check_quit_key_press()
     return_to_clash_main_menu()
   
def getto_donate_page():
     check_quit_key_press()
     print(calculate_time(start_time),"Moving to clan chat page")
     pyautogui.moveTo(x=317,y=627,duration=duration)
     pyautogui.click()
     while check_if_on_clan_chat_page() == 0:
          pyautogui.moveTo(x=317,y=627,duration=duration)
          pyautogui.click()
          time.sleep(2)
     check_quit_key_press()
 
def check_if_more_donates():
     check_quit_key_press()
     iar = refresh_screen()
     pix1 = iar[186][34]
     pix2 = iar[177][32]
     pix3 = iar[163][61]
     sentinel = [1] * 3
     sentinel[0] = 214 
     sentinel[1] = 234 
     sentinel[2] = 244

     more_donates_exists = 1
     if compare_pixels(pix1,sentinel) == "diff":
          more_donates_exists = 0
     if compare_pixels(pix2,sentinel) == "diff":
          more_donates_exists = 0
     if compare_pixels(pix3,sentinel) == "diff":
          more_donates_exists = 0
     check_quit_key_press()
     return more_donates_exists

def check_quit_key_press():
     if keyboard.is_pressed("space"):
          print(calculate_time(start_time),"space is pressed. Quitting the program")
          quit()
   
def restart_client():
     check_quit_key_press()
     print(calculate_time(start_time),"closing client")
     pyautogui.moveTo(x=540,y=140,duration=duration)
     pyautogui.click()
     time.sleep(2)
     check_quit_key_press()
     print(calculate_time(start_time),"opening client")
     pyautogui.moveTo(x=540,y=140,duration=duration)
     pyautogui.click()
     time.sleep(5)
     check_quit_key_press()
     orientate_window(win)
     time.sleep(5)
     check_quit_key_press()
     print(calculate_time(start_time),"skipping ads")
     pyautogui.moveTo(x=440,y=600,duration=duration)
     pyautogui.click()
     time.sleep(1)
     check_quit_key_press()
     pyautogui.click()
     time.sleep(1)
     check_quit_key_press()
     pyautogui.click()
     time.sleep(3)
     check_quit_key_press()
     open_clash()
     
def wait_for_clash_main_menu():
     n = 0
     while check_if_on_clash_main_menu() == 0:
          
          check_quit_key_press()
          time.sleep(3)
          print(calculate_time(start_time),"Waiting for clash main menu/",n)
          n=n+1
          if n > 20:
               print("Waiting longer than a minute for clash main menu")
               break
          pyautogui.moveTo(x=50,y=190,duration=duration)
          pyautogui.moveTo(x=10,y=170,duration=duration)
          pyautogui.click() 

def convert_int_to_time(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
      
    return "%d:%02d:%02d" % (hour, minutes, seconds)

def check_if_past_game_is_win():
     check_quit_key_press()
     open_activity_log()
     iar = refresh_screen()
     
     n=40
     while n < 130:
          pix = iar[191][n]
          sentinel = [1] * 3
          sentinel[0] = 102 
          sentinel[1] = 204 
          sentinel[2] = 255
          if compare_pixels(pix,sentinel) == "same":
               return 1
          n=n+1
     time.sleep(1)
     pyautogui.moveTo(x=385,y=507,duration=duration)
     pyautogui.click(x=385, y=507, clicks=1, interval=0.2, button='left') 
     return 0
          
def open_activity_log():
     check_quit_key_press()
     pyautogui.moveTo(x=360,y=99,duration=duration)
     pyautogui.click()
     time.sleep(1)
     check_quit_key_press()
     pyautogui.moveTo(x=255,y=75,duration=duration)
     pyautogui.click()
     time.sleep(1)
     check_quit_key_press()
     
def check_if_windows_exist():
     if gw.getWindowsWithTitle('MEmu') == []:
          print("MEmu window not found")
          exit()
     if gw.getWindowsWithTitle('Multiple Instance Manager') == []:
          print("MMIM window not found")
          exit()
     return 1

def capture_board_state():
     check_quit_key_press()
     check_locations = [1] * 8
     iar = refresh_screen()
     check_locations[0] = iar[209][71]
     check_locations[1] = iar[211][95]
     check_locations[2] = iar[212][141]
     check_locations[3] = iar[213][188]
     check_locations[4] = iar[215][270]
     check_locations[5] = iar[222][276]
     check_locations[6] = iar[223][322]
     check_locations[7] = iar[218][354]
     return check_locations

def choose_placement_based_on_board_state(default_board_state):
     default_board_state = default_board_state
     current_board_state = capture_board_state()
     n3 = 0
     choice = 1
     coords = [1]*2
     rand = random.randint(1 ,3)
     while n3 < 8:
          pix1 = default_board_state[n3]
          pix2 = current_board_state[n3]
          if compare_pixels(pix1,pix2)=="diff":
               choice = n3
               print("Found difference in position: "+str(n3)+"Identifying it as an enemy troop")
     if choice == 1:
          if rand == 1:
               coords[0]=170
               coords[1]=503
          if rand == 2:
               coords[0]=170
               coords[1]=430
          if rand == 3:
               coords[0]=170
               coords[1]=317
     if choice == 2:
          if rand == 1:
               coords[0]=170
               coords[1]=503
          if rand == 2:
               coords[0]=170
               coords[1]=430
          if rand == 3:
               coords[0]=170
               coords[1]=317
     if choice == 3:
          if rand == 1:
               coords[0]=170
               coords[1]=503
          if rand == 2:
               coords[0]=170
               coords[1]=430
          if rand == 3:
               coords[0]=170
               coords[1]=317
     if choice == 4:
          if rand == 1:
               coords[0]=170
               coords[1]=503
          if rand == 2:
               coords[0]=170
               coords[1]=430
          if rand == 3:
               coords[0]=170
               coords[1]=317
     if choice == 5:
          if rand == 1:
               coords[0]=249
               coords[1]=513
          if rand == 2:
               coords[0]=252
               coords[1]=431
          if rand == 3:
               coords[0]=244
               coords[1]=332
     if choice == 6:
          if rand == 1:
               coords[0]=249
               coords[1]=513
          if rand == 2:
               coords[0]=252
               coords[1]=431
          if rand == 3:
               coords[0]=244
               coords[1]=332
     if choice == 7:
          if rand == 1:
               coords[0]=249
               coords[1]=513
          if rand == 2:
               coords[0]=252
               coords[1]=431
          if rand == 3:
               coords[0]=244
               coords[1]=332
     if choice == 8:
          if rand == 1:
               coords[0]=249
               coords[1]=513
          if rand == 2:
               coords[0]=252
               coords[1]=431
          if rand == 3:
               coords[0]=244
               coords[1]=332
     
     return coords
               
def set_default_board_state():
     pix1=[1]*3
     pix1[0] = 30
     pix1[1] = 121
     pix1[2] = 8
     
     pix2=[1]*3
     pix2[0] = 181
     pix2[1] = 166
     pix2[2] = 156
     
     pix3=[1]*3
     pix3[0] = 193
     pix3[1] = 188
     pix3[2] = 167
     
     pix4=[1]*3
     pix4[0] = 194
     pix4[1] = 189
     pix4[2] = 165
     
     pix5=[1]*3
     pix5[0] = 219
     pix5[1] = 211
     pix5[2] = 186
     
     pix6=[1]*3
     pix6[0] = 228
     pix6[1] = 221
     pix6[2] = 196
     
     pix7=[1]*3
     pix7[0] = 194
     pix7[1] = 188
     pix7[2] = 169
     
     pix8=[1]*3
     pix8[0] = 181
     pix8[1] = 173
     pix8[2] = 157
     while n4 < 8:
          
          n4=n4+1
     
     
     

check_if_windows_exist()
win = gw.getWindowsWithTitle('MEmu')[0]
win2 = gw.getWindowsWithTitle('Multiple Instance Manager')[0]

start_time = time.time()
while True:
     time.sleep(2)
     print(calculate_time(start_time),"loop count: ",loop_count)
     loop_count+=1 
     iar = refresh_screen()
     plt.imshow(iar)
     
     #plt.show()
    
     
     orientate_memu_multi()
     time.sleep(1)
     orientate_window(win)
     restart_client()
     if check_if_on_clash_main_menu() == 1:
          print(calculate_time(start_time),"We're on the main menu")
          time.sleep(1)
          print(calculate_time(start_time),"Handling chests")
          time.sleep(1)                                                        
          open_chests()
          time.sleep(3)
          print (calculate_time(start_time),"Checking if can request")
          time.sleep(1)
          if check_if_can_request() == 1:
               print(calculate_time(start_time),"Can request. Requesting giant")
               time.sleep(1)
               request_from_clash_main_menu()
          else:
               print(calculate_time(start_time),"Request is unavailable")
          print(calculate_time(start_time),"Checking if can donate")
          time.sleep(1)
          getto_donate_page()
          click_donates()
     else:
          print(calculate_time(start_time),"not on clash main menu")
     print(calculate_time(start_time),"Handled chests and requests. Gonna start a battle")
     time.sleep(1)
     start_2v2()
     fights = fights + 1
     wait_for_battle_start()
     fightloops = 0
     default_board_state = capture_board_state()
     while check_if_exit_battle_button_exists() == 0:
          fightloops = fightloops + 1
          print(calculate_time(start_time),"fightloop: ",fightloops)
          fight_in_2v2()
          if fightloops > 100:
               break
     leave_end_battle_window()
     time.sleep(5)
     if check_if_past_game_is_win() == 1:
          print(calculate_time(start_time),"Last game was a win")
          wins=wins+1
     else:
          print(calculate_time(start_time),"Last gane was a loss")
          losses=losses+1
          


     
     
     
    
     

     

     
          
     

     
     
     
          
     
     
     
     
     
     

     
          
     