import random
import time
from os.path import join

import keyboard
import matplotlib.pyplot as plt
import numpy as np
import pyautogui
import pygetwindow as gw
from PIL import Image

from pyclashbot.logger import Logger
from pyclashbot.image_rec import compare_images

logger = Logger()

try:
    window_memu = gw.getWindowsWithTitle('MEmu')[0]
    window_mimm = gw.getWindowsWithTitle('Multiple Instance Manager')[0]
except (IndexError, KeyError):
    logger.log("MEmu or Multiple Instance Manager not detected!")


def refresh_screen():
    check_quit_key_press()
    orientate_window()
    screenshot = pyautogui.screenshot()
    check_quit_key_press()
    iar = np.array(screenshot)
    return iar


def show_image(iar):
    plt.imshow(iar)
    check_quit_key_press()
    plt.show()


def orientate_window():
    #logger.log("Orientating memu client")
    window_memu = gw.getWindowsWithTitle('MEmu')[0]
    check_quit_key_press()
    window_memu.minimize()
    window_memu.restore()
    time.sleep(2)
    window_memu.moveTo(0, 0)
    window_memu.resizeTo(460, 680)


def orientate_memu_multi():
    check_quit_key_press()
    window_mimm.minimize()
    window_mimm.restore()
    window_mimm.moveTo(200, 200)
    time.sleep(1)
    window_mimm.moveTo(0, 0)


def open_clash(duration):
    orientate_window()
    time.sleep(1)
    check_quit_key_press()
    logger.log("opening clash")
    reference_image = Image.open(
        join("pyclashbot", "reference_images", "clash_logo.png"))
    current_image = refresh_screen()
    coords = compare_images(current_image, reference_image, 0.97)
    if coords is None:
        logger.log("Clash logo wasn't found")
        return
    pyautogui.moveTo(x=coords[1], y=coords[0], duration=duration)
    pyautogui.click()
    # return coords

    wait_for_clash_main_menu(duration)


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
    if compare_pixels(pix2, sentinel, 10) == "diff":
        return False
    if compare_pixels(pix3, sentinel, 10) == "diff":
        return False
    return True


def compare_pixels(pix1, pix2, tol):
    check_quit_key_press()
    diff_r = abs(pix1[0] - pix2[0])
    diff_g = abs(pix1[1] - pix2[1])
    diff_b = abs(pix1[2] - pix2[2])
    if (diff_r < tol) and (diff_g < tol) and (diff_b < tol):
        return "same"
    else:
        return "diff"


def check_if_has_chests():
    has_chests = [0] * 4

    iar = refresh_screen()
    chest1_pix = iar[572][93]
    chest2_pix = iar[566][158]
    chest3_pix = iar[572][277]
    chest4_pix = iar[574][326]

    sentinel = [1] * 3
    sentinel[0] = 34
    sentinel[1] = 122
    sentinel[2] = 173

    if compare_pixels(chest1_pix, sentinel, 40) == "diff":
        has_chests[0] = 1
    if compare_pixels(chest2_pix, sentinel, 40) == "diff":
        has_chests[1] = 1
    if compare_pixels(chest3_pix, sentinel, 40) == "diff":
        has_chests[2] = 1
    if compare_pixels(chest4_pix, sentinel, 40) == "diff":
        has_chests[3] = 1

    check_quit_key_press()
    return has_chests


def open_chests(duration):
    check_quit_key_press()
    n = check_if_has_chests()
    if n[0] == 1:
        logger.log("Chest detected in slot 1")
        pyautogui.moveTo(x=78, y=554, duration=duration)
        pyautogui.click()
        check_quit_key_press()
        time.sleep(1)
        pyautogui.moveTo(x=210, y=455, duration=duration)
        pyautogui.click()
        time.sleep(1)
        pyautogui.click()
        time.sleep(1)
        pyautogui.click(x=20, y=556, clicks=20, interval=0.2, button='left')
        check_quit_key_press()
    if n[1] == 1:
        logger.log("Chest detected in slot 2")
        pyautogui.moveTo(x=162, y=549, duration=duration)
        check_quit_key_press()
        pyautogui.click()
        time.sleep(1)
        pyautogui.moveTo(x=210, y=455, duration=duration)
        time.sleep(1)
        pyautogui.click()
        pyautogui.click()
        time.sleep(1)
        pyautogui.click(x=20, y=556, clicks=20, interval=0.2, button='left')
        check_quit_key_press()
    if n[2] == 1:
        logger.log("Chest detected in slot 3")
        check_quit_key_press()
        pyautogui.moveTo(x=263, y=541, duration=duration)
        pyautogui.click()
        time.sleep(1)
        pyautogui.moveTo(x=210, y=455, duration=duration)
        time.sleep(1)
        pyautogui.click()
        pyautogui.click()
        time.sleep(1)
        pyautogui.click(x=20, y=556, clicks=20, interval=0.2, button='left')
        check_quit_key_press()
    if n[3] == 1:
        logger.log("Chest detected in slot 4")
        pyautogui.moveTo(x=349, y=551, duration=duration)
        check_quit_key_press()
        pyautogui.click()
        time.sleep(1)
        pyautogui.moveTo(x=210, y=455, duration=duration)
        time.sleep(1)
        pyautogui.click()
        pyautogui.click()
        time.sleep(1)
        pyautogui.click(x=20, y=556, clicks=20, interval=0.2, button='left')
        check_quit_key_press()


def check_if_on_clash_main_menu():
    current_image = pyautogui.screenshot()
    i1 = compare_images(current_image, Image.open(join("pyclashbot", "reference_images","clash_main_menu","clash_main_1.png")), 0.99)
    i2 = compare_images(current_image, Image.open(join("pyclashbot", "reference_images","clash_main_menu","clash_main_2.png")), 0.99)
    i3 = compare_images(current_image, Image.open(join("pyclashbot", "reference_images","clash_main_menu","clash_main_3.png")), 0.99)
    i4 = compare_images(current_image, Image.open(join("pyclashbot", "reference_images","clash_main_menu","clash_main_4.png")), 0.99)
    i5 = compare_images(current_image, Image.open(join("pyclashbot", "reference_images","clash_main_menu","clash_main_5.png")), 0.99)
    
    if i1 is not None:
        return True
    if i2 is not None:
        return True
    if i3 is not None:
        return True
    if i4 is not None:
        return True
    if i5 is not None:
        return True
    return False


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

    if compare_pixels(pix1, sentinel, 10) == "diff":
        return False
    if compare_pixels(pix2, sentinel, 10) == "diff":
        return False
    if compare_pixels(pix3, sentinel, 10) == "diff":
        return False
    check_quit_key_press()
    return True


def request_from_clash_main_menu(duration):
    check_quit_key_press()
    logger.log("Moving to clan chat page")
    pyautogui.moveTo(x=317, y=627, duration=duration)
    pyautogui.click()
    while not check_if_on_clan_chat_page():
        pyautogui.moveTo(x=317, y=627, duration=duration)
        pyautogui.click()
        time.sleep(2)
    logger.log("requesting giant")
    pyautogui.moveTo(x=86, y=564, duration=duration)
    pyautogui.click()
    #scroll till find card
    time.sleep(2)
    while check_for_request_card() is None:
        pyautogui.scroll(-90, x=0, y=0)
        time.sleep(3)
        check_quit_key_press()
    #click card
    coords = check_for_request_card()
    pyautogui.moveTo(x=coords[1], y=coords[0], duration=duration)
    pyautogui.click()
    time.sleep(2)
    #click request
    coords = look_for_request_button()
    pyautogui.moveTo(x=coords[1], y=coords[0], duration=duration)
    pyautogui.click()
    time.sleep(2)
    return_to_clash_main_menu(duration)


def check_for_request_card():
    current_image = pyautogui.screenshot()
    i1 = compare_images(current_image, Image.open(join("pyclashbot", "reference_images","request_page_card_logos","giant_1.png")), 0.99)
    i2 = compare_images(current_image, Image.open(join("pyclashbot", "reference_images","request_page_card_logos","giant_2.png")), 0.99)
    i3 = compare_images(current_image, Image.open(join("pyclashbot", "reference_images","request_page_card_logos","giant_3.png")), 0.99)
    i4 = compare_images(current_image, Image.open(join("pyclashbot", "reference_images","request_page_card_logos","giant_4.png")), 0.99)
    i5 = compare_images(current_image, Image.open(join("pyclashbot", "reference_images","request_page_card_logos","giant_5.png")), 0.99)
    i6 = compare_images(current_image, Image.open(join("pyclashbot", "reference_images","request_page_card_logos","giant_6.png")), 0.99)
    i7 = compare_images(current_image, Image.open(join("pyclashbot", "reference_images","request_page_card_logos","giant_7.png")), 0.99)
    i8 = compare_images(current_image, Image.open(join("pyclashbot", "reference_images","request_page_card_logos","giant_8.png")), 0.99)

    if i1 is not None:
        return i1
    if i2 is not None:
        return i2
    if i3 is not None:
        return i3
    if i4 is not None:
        return i4
    if i5 is not None:
        return i5
    if i6 is not None:
        return i6
    if i7 is not None:
        return i7
    if i8 is not None:
        return i8
    return None
    

def look_for_request_button():
    current_image = pyautogui.screenshot()
    i1 = compare_images(current_image, Image.open(join("pyclashbot", "reference_images","request_page_card_logos","req_logo_1.png")), 0.99)
    i2 = compare_images(current_image, Image.open(join("pyclashbot", "reference_images","request_page_card_logos","req_logo_2.png")), 0.99)
    i3 = compare_images(current_image, Image.open(join("pyclashbot", "reference_images","request_page_card_logos","req_logo_3.png")), 0.99)
    i4 = compare_images(current_image, Image.open(join("pyclashbot", "reference_images","request_page_card_logos","req_logo_4.png")), 0.99)
    i5 = compare_images(current_image, Image.open(join("pyclashbot", "reference_images","request_page_card_logos","req_logo_5.png")), 0.99)
    
    if i1 is not None:
        return i1
    if i2 is not None:
        return i2
    if i3 is not None:
        return i3
    if i4 is not None:
        return i4
    if i5 is not None:
        return i5
    return None


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

    if compare_pixels(pix1, sentinel, 10) == "diff":
        return False
    if compare_pixels(pix2, sentinel, 10) == "diff":
        return False
    if compare_pixels(pix3, sentinel, 10) == "diff":
        return False
    check_quit_key_press()
    return True


def return_to_clash_main_menu(duration):
    check_quit_key_press()
    logger.log("Returning to clash main menu")
    pyautogui.moveTo(x=180, y=625, duration=duration)
    pyautogui.click()
    check_quit_key_press()


def start_2v2(duration):
    check_quit_key_press()
    logger.log("Navigating to 2v2 match")
    pyautogui.moveTo(x=280, y=440, duration=duration)
    pyautogui.click()
    time.sleep(2)
    pyautogui.scroll(-10, x=0, y=0)
    time.sleep(3)
    pyautogui.moveTo(x=300, y=300, duration=duration)
    pyautogui.click()
    check_quit_key_press()


def start_1v1_ranked(duration):
    check_quit_key_press()
    logger.log("Navigating to 1v1 ranked match")
    pyautogui.moveTo(x=140, y=440, duration=duration)
    pyautogui.click()
    wait_for_battle_start()
    check_quit_key_press()


def wait_for_battle_start():
    logger.log("Waiting for battle start")
    n = 1
    n1 = 0
    check_quit_key_press()
    while n == 1:
        n1 += 1
        if check_if_in_battle():
            n = 0
        time.sleep(1)
        if n1 > 90:
            logger.log("Waited longer than 90 sec for a fight")
            break
        refresh_screen()
    check_quit_key_press()


def fight_in_2v2():
    check_quit_key_press()
    card_coord = random_card_coord_picker()
    placement_coord = look_for_enemy_troops()
    if placement_coord is None:
        print("picking random coord")
        placement_coord = random_placement_coord_maker()
    else:
        print("picking coord: ",placement_coord)
        placement_coord[1] = placement_coord[1] + 30
    #pick card
    pyautogui.click(x=card_coord[0], y=card_coord[1], clicks=1, interval=0, button='left')
    #place card
    pyautogui.click(x=placement_coord[0], y=placement_coord[1], clicks=1, interval=0, button='left')
    

def random_placement_coord_maker():
    check_quit_key_press()
    n = random.randint(1, 6)
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
    n = random.randint(1, 4)
    coords = [1] * 2
    if n == 1:
        # logger.log("randomly selected card 1")
        coords[0] = 146
        coords[1] = 588
    if n == 2:
        # logger.log("randomly selected card 2")
        coords[0] = 206
        coords[1] = 590
    if n == 3:
        # logger.log("randomly selected card 3")
        coords[0] = 278
        coords[1] = 590
    if n == 4:
        # logger.log("randomly selected card 4")
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

    if compare_pixels(pix1, sentinel, 10) == "diff":
        return False
    if compare_pixels(pix2, sentinel, 10) == "diff":
        return False
    if compare_pixels(pix3, sentinel, 10) == "diff":
        return False
    check_quit_key_press()
    return True


def leave_end_battle_window(duration):
    check_quit_key_press()
    logger.log("battle is over. return to clash main menu")
    pyautogui.moveTo(x=81, y=630, duration=duration)
    pyautogui.click()
    time.sleep(5)
    check_quit_key_press()


def refresh_clan_tab(duration):
    check_quit_key_press()
    pyautogui.moveTo(x=300, y=630, duration=duration)
    pyautogui.click()
    return_to_clash_main_menu(duration)
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
    if compare_pixels(pix1, sentinel, 10) == "diff":
        return False
    if compare_pixels(pix3, sentinel, 10) == "diff":
        return False
    check_quit_key_press()
    return True


def find_donates():
    logger.log("searching screen for donate buttons")
    current_image = pyautogui.screenshot()
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "donate", "donate_button_1.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "donate", "donate_button_1.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "donate", "donate_button_2.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "donate", "donate_button_2.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "donate", "donate_button_3.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "donate", "donate_button_3.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "donate", "donate_button_4.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "donate", "donate_button_4.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "donate", "donate_button_5.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "donate", "donate_button_5.png")), 0.97)
    print("Found none this go-around")
    return [500, 50]
 

def click_donates(duration):
    logger.log("clicking the donate buttons if there are any available")
    check_quit_key_press()
    n = 0
    while n < 3:
        coords = find_donates()
        if coords is not None:
            pyautogui.moveTo(x=coords[1], y=coords[0], duration=duration)
            pyautogui.click(x=coords[1], y=coords[0],
                            clicks=5, interval=0.2, button='left')

            if check_if_more_donates():
                pyautogui.moveTo(x=50, y=170, duration=duration)
                pyautogui.click()
                time.sleep(2)

            pyautogui.moveTo(x=coords[1], y=coords[0], duration=duration)
            pyautogui.click(x=coords[1], y=coords[0],
                            clicks=5, interval=0.2, button='left')
        n += 1
    pyautogui.moveTo(x=393, y=525, duration=duration)
    pyautogui.click()
    check_quit_key_press()
    return_to_clash_main_menu(duration)


def getto_donate_page(duration):
    check_quit_key_press()
    logger.log("Moving to clan chat page")
    pyautogui.moveTo(x=317, y=627, duration=duration)
    pyautogui.click()
    while not check_if_on_clan_chat_page():
        pyautogui.moveTo(x=317, y=627, duration=duration)
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

    more_donates_exists = True
    if compare_pixels(pix1, sentinel, 10) == "diff":
        more_donates_exists = False
    if compare_pixels(pix2, sentinel, 10) == "diff":
        more_donates_exists = False
    if compare_pixels(pix3, sentinel, 10) == "diff":
        more_donates_exists = False
    check_quit_key_press()
    return more_donates_exists


def check_quit_key_press():
    if keyboard.is_pressed("space"):
        logger.log("space is pressed. Quitting the program")
        quit()


def restart_client(duration):
    check_quit_key_press()
    logger.log("closing client")
    pyautogui.moveTo(x=540, y=140, duration=duration)
    pyautogui.click()
    time.sleep(2)
    check_quit_key_press()
    logger.log("opening client")
    pyautogui.moveTo(x=540, y=140, duration=duration)
    pyautogui.click()
    time.sleep(5)
    check_quit_key_press()
    time.sleep(5)
    check_quit_key_press()
    time.sleep(5)
    logger.log("skipping ads")
    orientate_window()
    time.sleep(1)
    pyautogui.moveTo(x=440, y=600, duration=duration)
    time.sleep(1)
    pyautogui.click()
    time.sleep(1)
    pyautogui.click()
    time.sleep(1)
    pyautogui.click()
    time.sleep(1)
    open_clash(duration)


def wait_for_clash_main_menu(duration):
    n = 0
    while not check_if_on_clash_main_menu():

        check_quit_key_press()
        time.sleep(3)
        logger.log(f"Waiting for clash main menu/{n}")
        n = n+1
        if n > 20:
            logger.log("Waiting longer than a minute for clash main menu")
            break
        pyautogui.moveTo(x=50, y=190, duration=duration)
        pyautogui.moveTo(x=10, y=170, duration=duration)
        pyautogui.click()


def check_if_past_game_is_win(duration):
    check_quit_key_press()
    open_activity_log(duration)
    iar = refresh_screen()

    n = 40
    while n < 130:
        pix = iar[191][n]
        sentinel = [1] * 3
        sentinel[0] = 102
        sentinel[1] = 204
        sentinel[2] = 255
        if compare_pixels(pix, sentinel, 10) == "same":
            return True
        n = n+1
    time.sleep(1)
    pyautogui.moveTo(x=385, y=507, duration=duration)
    pyautogui.click(x=385, y=507, clicks=1, interval=0.2, button='left')
    return False


def open_activity_log(duration):
    check_quit_key_press()
    pyautogui.moveTo(x=360, y=99, duration=duration)
    pyautogui.click()
    time.sleep(1)
    check_quit_key_press()
    pyautogui.moveTo(x=255, y=75, duration=duration)
    pyautogui.click()
    time.sleep(1)
    check_quit_key_press()


def check_if_windows_exist():
    if gw.getWindowsWithTitle('MEmu') == []:
        logger.log("MEmu window not found")
        return False
    if gw.getWindowsWithTitle('Multiple Instance Manager') == []:
        logger.log("MMIM window not found")
        return False
    return True


def look_for_enemy_troops():
    current_image = refresh_screen()
    i=[0,0]*59
    
    i[0] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_10.png")), 0.97)
    i[1] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "1_1.png")), 0.97)
    i[2] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "1_2.png")), 0.97)
    i[3] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "1_3.png")), 0.97)
    i[4] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "1_4.png")), 0.97)
    i[5] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "2_1.png")), 0.97)
    i[6] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "2_3.png")), 0.97)
    i[7] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "2_2.png")), 0.97)
    i[8] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "3_1.png")), 0.97)
    i[9] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "3_2.png")), 0.97)
    i[10] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "3_3.png")), 0.97)
    i[11] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "3_4.png")), 0.97)
    i[12] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "3_5.png")), 0.97)
    i[13] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "5_1.png")), 0.97)
    i[14] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "5_2.png")), 0.97)
    i[15] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "5_3.png")), 0.97)
    i[16] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "5_4.png")), 0.97)
    i[17] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "6_1.png")), 0.97)
    i[18] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "6_2.png")), 0.97)
    i[19] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "6_3.png")), 0.97)
    i[20] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "6_4.png")), 0.97)
    i[21] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "7_1.png")), 0.97)
    i[22] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "7_2.png")), 0.97)
    i[23] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "7_3.png")), 0.97)
    i[24] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "7_4.png")), 0.97)
    i[25] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "7_5.png")), 0.97)
    i[26] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "8_1.png")), 0.97)
    i[27] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "8_2.png")), 0.97)
    i[28] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "8_3.png")), 0.97)
    i[29] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "8_4.png")), 0.97)
    i[30] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "9_1.png")), 0.97)
    i[31] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "9_2.png")), 0.97)
    i[32] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "9_3.png")), 0.97)
    i[33] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "9_4.png")), 0.97)
    i[34] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "10_1.png")), 0.97)
    i[35] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "10_2.png")), 0.97)
    i[36] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "10_3.png")), 0.97)
    i[37] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "10_4.png")), 0.97)
    i[38] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "11_1.png")), 0.97)
    i[39] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "11_2.png")), 0.97)
    i[40] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "11_3.png")), 0.97)
    i[41] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "11_4.png")), 0.97)
    i[42] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "11_5.png")), 0.97)
    i[43] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "12_1.png")), 0.97)
    i[44] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "12_2.png")), 0.97)
    i[45] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "12_3.png")), 0.97)
    i[46] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "12_4.png")), 0.97)
    i[47] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "12_5.png")), 0.97)
    i[48] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "12_6.png")), 0.97)
    i[49] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "13_2.png")), 0.97)
    i[50] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "13_3.png")), 0.97)
    i[51] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_2.png")), 0.97)
    i[52] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_3.png")), 0.97)
    i[53] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_4.png")), 0.97)
    i[54] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_5.png")), 0.97)
    i[55] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_6.png")), 0.97)
    i[56] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_7.png")), 0.97)
    i[57] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_8.png")), 0.97)
    i[58] = compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_9.png")), 0.97)
    
    n = 0
    while n < 59:
        if i[n] is not None:
            return_coords = [i[n][1],i[n][0]]
            return return_coords
        n=n+1
    return None


def check_deck():
    #get to deck tab
    pyautogui.moveTo(x=115, y=634, duration=1)
    pyautogui.click()
    time.sleep(2)
    pyautogui.moveTo(x=90, y=110, duration=1)
    pyautogui.click()
    time.sleep(2)
    #screenshot deck region
    deck_image = pyautogui.screenshot()
    
    #check for all cards
    comparisons = ["empty"]*8
    
    #archer_queen
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archer_queen_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archer_queen_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archer_queen_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archer_queen_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archer_queen_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found archer queen in deck")
            comparisons = add_card_to_deck(comparisons,"archer_queen")
    #barb_barrel
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barb_barrel_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barb_barrel_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barb_barrel_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barb_barrel_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barb_barrel_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found barb_barrel in deck")
            comparisons = add_card_to_deck(comparisons,"barb_barrel")
    #goblin_gang
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_gang_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_gang_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_gang_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_gang_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_gang_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found goblin_gang in deck")
            comparisons = add_card_to_deck(comparisons,"goblin_gang")
    #mother_witch
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mother_witch_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mother_witch_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mother_witch_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mother_witch_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mother_witch_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found mother_witch in deck")
            comparisons = add_card_to_deck(comparisons,"mother_witch")
    #royal_ghost
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_ghost_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_ghost_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_ghost_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_ghost_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_ghost_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found royal_ghost in deck")
            comparisons = add_card_to_deck(comparisons,"royal_ghost")
    #tesla
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tesla_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tesla_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tesla_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tesla_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tesla_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found tesla in deck")
            comparisons = add_card_to_deck(comparisons,"tesla")
    #valk
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "valk_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "valk_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "valk_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "valk_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "valk_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found valk in deck")
            comparisons = add_card_to_deck(comparisons,"valk")
    #battle_ram
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "battle_ram_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "battle_ram_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "battle_ram_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "battle_ram_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "battle_ram_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found battle_ram in deck")
            comparisons = add_card_to_deck(comparisons,"battle_ram")
    #e_wiz
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_wiz_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_wiz_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_wiz_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_wiz_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_wiz_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found e_wiz in deck")
            comparisons = add_card_to_deck(comparisons,"e_wiz")
    #fire_spirit
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fire_spirit_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fire_spirit_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fire_spirit_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fire_spirit_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fire_spirit_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found fire_spirit in deck")
            comparisons = add_card_to_deck(comparisons,"fire_spirit")
    #fireball
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fireball_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fireball_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fireball_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fireball_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fireball_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found fireball in deck")
            comparisons = add_card_to_deck(comparisons,"fireball")
    #firecracker
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "firecracker_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "firecracker_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "firecracker_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "firecracker_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "firecracker_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found firecracker in deck")
            comparisons = add_card_to_deck(comparisons,"firecracker")
    #hog
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "hog_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "hog_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "hog_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "hog_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "hog_1.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found hog in deck")
            comparisons = add_card_to_deck(comparisons,"hog")
    #dark_knight
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dark_knight_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dark_knight_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dark_knight_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dark_knight_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dark_knight_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found dark_knight in deck")
            comparisons = add_card_to_deck(comparisons,"dark_knight")
    #royal_recruits
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_recruits_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_recruits_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_recruits_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_recruits_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_recruits_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found royal_recruits in deck")
            comparisons = add_card_to_deck(comparisons,"royal_recruits")
    #witch
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "witch_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "witch_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "witch_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "witch_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "witch_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found witch in deck")
            comparisons = add_card_to_deck(comparisons,"witch")
    #mega_knight
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barb_barrel_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_knight_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_knight_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_knight_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_knight_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found mega_knight in deck")
            comparisons = add_card_to_deck(comparisons,"mega_knight")
    #mini_pekka
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barb_barrel_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mini_pekka_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mini_pekka_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mini_pekka_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mini_pekka_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found mini_pekka in deck")
            comparisons = add_card_to_deck(comparisons,"mini_pekka")
    #mirror
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mirror_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mirror_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mirror_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mirror_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mirror_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found mirror in deck")
            comparisons = add_card_to_deck(comparisons,"mirror")
    #ram_rider
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ram_rider_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ram_rider_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ram_rider_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ram_rider_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ram_rider_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found ram_rider in deck")
            comparisons = add_card_to_deck(comparisons,"ram_rider")
    #poison
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "poison_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "poison_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "poison_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "poison_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "poison_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found poison in deck")
            comparisons = add_card_to_deck(comparisons,"poison")
    #pekka
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "pekka_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "pekka_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "pekka_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "pekka_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "pekka_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found pekka in deck")
            comparisons = add_card_to_deck(comparisons,"pekka")
    #night_witch
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "night_witch_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "night_witch_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "night_witch_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "night_witch_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found night_witch in deck")
            comparisons = add_card_to_deck(comparisons,"night_witch")
    #musketeer
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "musketeer_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "musketeer_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "musketeer_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "musketeer_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "musketeer_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "musketeer_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "musketeer_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "musketeer_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "musketeer_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "musketeer_5.png")), 0.97) is not None:
            n = 1
            
            
            
        if n == 1:
            logger.log("Found musketeer in deck")
            comparisons = add_card_to_deck(comparisons,"musketeer")
    #bandit
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_13.png")), 0.97) is not None:
            n = 1 
        if n == 1:
            logger.log("Found bandit in deck")
            comparisons = add_card_to_deck(comparisons,"bandit")  
    #ice_spirit
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_spirit_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_spirit_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_spirit_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_spirit_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_spirit_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found ice_spirit in deck")
            comparisons = add_card_to_deck(comparisons,"ice_spirit")
    #ice_golem
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_golem_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_golem_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_golem_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_golem_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_golem_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found ice_golem in deck")
            comparisons = add_card_to_deck(comparisons,"ice_golem")
    #heal_spirit
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "heal_spirit_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "heal_spirit_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "heal_spirit_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "heal_spirit_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "heal_spirit_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found heal_spirit in deck")
            comparisons = add_card_to_deck(comparisons,"heal_spirit")
    #e_spirit
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_spirit_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_spirit_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_spirit_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_spirit_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_spirit_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found e_spirit in deck")
            comparisons = add_card_to_deck(comparisons,"e_spirit")
    #bomber
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomber_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomber_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomber_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomber_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomber_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found bomber in deck")
            comparisons = add_card_to_deck(comparisons,"bomber")
    #spear_goblins
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "spear_goblins_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "spear_goblins_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "spear_goblins_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "spear_goblins_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "spear_goblins_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found spear_goblins in deck")
            comparisons = add_card_to_deck(comparisons,"spear_goblins")
    #skeletons
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeletons_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeletons_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeletons_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeletons_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeletons_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found skeletons in deck")
            comparisons = add_card_to_deck(comparisons,"skeletons")
    #goblins
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblins_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblins_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblins_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblins_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblins_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblins_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblins_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblins_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblins_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblins_10.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found goblins in deck")
            comparisons = add_card_to_deck(comparisons,"goblins")
    #bats
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_9.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found bats in deck")
            comparisons = add_card_to_deck(comparisons,"bats")
    #archers
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archers_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archers_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archers_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archers_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archers_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found archers in deck")
            comparisons = add_card_to_deck(comparisons,"archers")
    #rage
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rage_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rage_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rage_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rage_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rage_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found rage in deck")
            comparisons = add_card_to_deck(comparisons,"rage")
    #minions
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minions_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minions_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minions_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minions_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minions_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found minions in deck")
            comparisons = add_card_to_deck(comparisons,"minions")
    #snowball
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "snowball_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "snowball_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "snowball_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "snowball_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "snowball_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found snowball in deck")
            comparisons = add_card_to_deck(comparisons,"snowball")
    #zap
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "zap_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "zap_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "zap_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "zap_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "zap_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found zap in deck")
            comparisons = add_card_to_deck(comparisons,"zap")
    #wall_breaker
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wall_breaker_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wall_breaker_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wall_breaker_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wall_breaker_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wall_breaker_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found wall_breaker in deck")
            comparisons = add_card_to_deck(comparisons,"wall_breaker")
    #knight
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "knight_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "knight_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "knight_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "knight_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "knight_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found knight in deck")
            comparisons = add_card_to_deck(comparisons,"knight")
    #log
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "log_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "log_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "log_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "log_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "log_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found log in deck")
            comparisons = add_card_to_deck(comparisons,"log")
    #fisherman
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fisherman_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fisherman_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fisherman_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fisherman_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fisherman_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found fisherman in deck")
            comparisons = add_card_to_deck(comparisons,"fisherman")
    #skeleton_army
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_army_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_army_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_army_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_army_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_army_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found skeleton_army in deck")
            comparisons = add_card_to_deck(comparisons,"skeleton_army")
    #princess
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "princess_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "princess_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "princess_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "princess_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "princess_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found princess in deck")
            comparisons = add_card_to_deck(comparisons,"princess")
    #miner
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "miner_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "miner_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "miner_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "miner_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "miner_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found miner in deck")
            comparisons = add_card_to_deck(comparisons,"miner")
    #skeleton_barrel
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_barrel_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_barrel_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_barrel_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_barrel_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_barrel_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found skeleton_barrel in deck")
            comparisons = add_card_to_deck(comparisons,"skeleton_barrel")
    #ice_wizard
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_wizard_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_wizard_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_wizard_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_wizard_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_wizard_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found ice_wizard in deck")
            comparisons = add_card_to_deck(comparisons,"ice_wizard")
    #mega_minion
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_minion_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_minion_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_minion_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_minion_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_minion_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found mega_minion in deck")
            comparisons = add_card_to_deck(comparisons,"mega_minion")
    #guards
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "guards_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "guards_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "guards_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "guards_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "guards_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "guards_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "guards_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "guards_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "guards_9.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found guards in deck")
            comparisons = add_card_to_deck(comparisons,"guards")
    #tombstone
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tombstone_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tombstone_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tombstone_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tombstone_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tombstone_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found tombstone in deck")
            comparisons = add_card_to_deck(comparisons,"tombstone")
    #arrows
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "arrows_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "arrows_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "arrows_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "arrows_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "arrows_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found arrows in deck")
            comparisons = add_card_to_deck(comparisons,"arrows")
    #elixer_golem
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elixer_golem_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elixer_golem_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elixer_golem_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elixer_golem_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elixer_golem_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found elixer_golem in deck")
            comparisons = add_card_to_deck(comparisons,"elixer_golem")
    #dart_goblin
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dart_goblin_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dart_goblin_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dart_goblin_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dart_goblin_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dart_goblin_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dart_goblin_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dart_goblin_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dart_goblin_8.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found dart_goblin in deck")
            comparisons = add_card_to_deck(comparisons,"dart_goblin")
    #cannon
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_8.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found cannon in deck")
            comparisons = add_card_to_deck(comparisons,"cannon")
    #inferno_dragon
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_dragon_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_dragon_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_dragon_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_dragon_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_dragon_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found inferno_dragon in deck")
            comparisons = add_card_to_deck(comparisons,"inferno_dragon")
    #tornado
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tornado_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tornado_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tornado_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tornado_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tornado_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found tornado in deck")
            comparisons = add_card_to_deck(comparisons,"tornado")
    #goblin_barrel
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_barrel_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_barrel_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_barrel_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_barrel_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_barrel_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found goblin_barrel in deck")
            comparisons = add_card_to_deck(comparisons,"goblin_barrel")
    #clone
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "clone_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "clone_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "clone_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "clone_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "clone_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found clone in deck")
            comparisons = add_card_to_deck(comparisons,"clone")
    #earthquake
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "earthquake_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "earthquake_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "earthquake_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "earthquake_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "earthquake_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found earthquake in deck")
            comparisons = add_card_to_deck(comparisons,"earthquake")
    #royal_delivery
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_delivery_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_delivery_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_delivery_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_delivery_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_delivery_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found royal_delivery in deck")
            comparisons = add_card_to_deck(comparisons,"royal_delivery")
    #baby_dragon
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "baby_dragon_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "baby_dragon_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "baby_dragon_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "baby_dragon_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "baby_dragon_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found baby_dragon in deck")
            comparisons = add_card_to_deck(comparisons,"baby_dragon")
    #lumberjack
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lumberjack_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lumberjack_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lumberjack_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lumberjack_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lumberjack_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            logger.log("Found lumberjack in deck")
            comparisons = add_card_to_deck(comparisons,"lumberjack")
    
    
    
    
    
    time.sleep(2)
    pyautogui.moveTo(x=245, y=640, duration=1)
    pyautogui.click()
    time.sleep(2)
    return comparisons
    
    
def add_card_to_deck(deck_list,card):
    if deck_list[0]=="empty":
        deck_list[0]=card
        return deck_list
    if deck_list[1]=="empty":
        deck_list[1]=card
        return deck_list
    if deck_list[2]=="empty":
        deck_list[2]=card
        return deck_list
    if deck_list[3]=="empty":
        deck_list[3]=card
        return deck_list
    if deck_list[4]=="empty":
        deck_list[4]=card
        return deck_list
    if deck_list[5]=="empty":
        deck_list[5]=card
        return deck_list
    if deck_list[6]=="empty":
        deck_list[6]=card
        return deck_list
    if deck_list[7]=="empty":
        deck_list[7]=card
        return deck_list
    return deck_list


def check_for_card_in_hand(card):
    hand_screenshot = pyautogui.screenshot()
    if card == "mega_knight":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "mega_knight.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "firecracker":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "firecracker.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "hog":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "hog.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "mini_pekka":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "mini_pekka.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "fire_spirit":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "fire_spirit.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "ram_rider":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "ram_rider.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "valk":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "valk.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "musketeer":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "musketeer.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "archer_queen":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "archer_queen.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "goblin_gang":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "goblin_gang.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "battle_ram":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "battle_ram.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "e_wiz":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "e_wiz.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "dark_knight":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "dark_knight.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "bandit":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "bandit.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "royal_ghost":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "royal_ghost.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "pekka":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "pekka.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "poison":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "poison.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "fireball":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "fireball.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "barb_barrel":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "barb_barrel.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "tesla":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "tesla.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "royal_recruits":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "royal_recruits.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "witch":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "witch.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "mother_witch":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "mother_witch.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    if card == "night_witch":
        coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "night_witch.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1],coords_reverse[0]]
    
      
def fight_with_deck_list(deck_list):
#turrets
    #if tesla in deck and in hand
    if (check_if_card_in_deck(deck_list,"tesla"))and(check_for_card_in_hand("tesla") is not None):
        logger.log("Decided to play tesla")
        card_coords = check_for_card_in_hand("tesla")
        placement_coords = [212,385]
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
#melee tanks
     #if bandit in deck and bandit in hand
    if (check_if_card_in_deck(deck_list,"bandit"))and(check_for_card_in_hand("bandit") is not None):
        logger.log("Decided to play bandit")
        card_coords = check_for_card_in_hand("bandit")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1]=placement_coords[1]+45
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    #if dark_knight in deck and dark_knight in hand
    if (check_if_card_in_deck(deck_list,"dark_knight"))and(check_for_card_in_hand("dark_knight") is not None):
        logger.log("Decided to play dark_knight")
        card_coords = check_for_card_in_hand("dark_knight")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    #if fire_spirit in deck and fire_spirit in hand
    if (check_if_card_in_deck(deck_list,"fire_spirit"))and(check_for_card_in_hand("fire_spirit") is not None):
        logger.log("Decided to play fire_spirit")
        card_coords = check_for_card_in_hand("fire_spirit")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1]=placement_coords[1]+30
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    #if mega_knight in deck and mega_knight in hand
    if (check_if_card_in_deck(deck_list,"mega_knight"))and(check_for_card_in_hand("mega_knight") is not None):
        logger.log("Decided to play mega_knight")
        card_coords = check_for_card_in_hand("mega_knight")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1] + 30
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    #if mini_pekka in deck and mini_pekka in hand
    if (check_if_card_in_deck(deck_list,"mini_pekka"))and(check_for_card_in_hand("mini_pekka") is not None):
        logger.log("Decided to play mini_pekka")
        card_coords = check_for_card_in_hand("mini_pekka")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    #if pekka in deck and pekka in hand
    if (check_if_card_in_deck(deck_list,"pekka"))and(check_for_card_in_hand("pekka") is not None):
        logger.log("Decided to play pekka")
        card_coords = check_for_card_in_hand("pekka")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    #if royal_ghost in deck and royal_ghost in hand
    if (check_if_card_in_deck(deck_list,"royal_ghost"))and(check_for_card_in_hand("royal_ghost") is not None):
        logger.log("Decided to play royal_ghost")
        card_coords = check_for_card_in_hand("royal_ghost")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    #if royal_recruits in deck and in hand
    if (check_if_card_in_deck(deck_list,"royal_recruits"))and(check_for_card_in_hand("royal_recruits") is not None):
        logger.log("Decided to play royal_recruits")
        card_coords = check_for_card_in_hand("royal_recruits")
        placement_coords = [215,390]
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    #if valk in deck and valk in hand
    if (check_if_card_in_deck(deck_list,"valk"))and(check_for_card_in_hand("valk") is not None):
        logger.log("Decided to play valk")
        card_coords = check_for_card_in_hand("valk")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    #if barb_barrel in deck and in hand
    if (check_if_card_in_deck(deck_list,"barb_barrel"))and(check_for_card_in_hand("barb_barrel") is not None)and(look_for_enemy_troops() is not None):
        logger.log("Decided to play barb_barrel")
        card_coords = check_for_card_in_hand("barb_barrel")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1]=placement_coords[1]+30
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
#ranged
    #if e_wiz in deck and e_wiz in hand
    if (check_if_card_in_deck(deck_list,"e_wiz"))and(check_for_card_in_hand("e_wiz") is not None):
        logger.log("Decided to play e_wiz")
        card_coords = check_for_card_in_hand("e_wiz")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1]=placement_coords[1]+25
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    #if firecracker in deck and firecracker in hand
    if (check_if_card_in_deck(deck_list,"firecracker"))and(check_for_card_in_hand("firecracker") is not None):
        logger.log("Decided to play firecracker")
        card_coords = check_for_card_in_hand("firecracker")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1]=placement_coords[1]+65
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    #if goblin_gang in deck and goblin_gang in hand
    if (check_if_card_in_deck(deck_list,"goblin_gang"))and(check_for_card_in_hand("goblin_gang") is not None):
        logger.log("Decided to play goblin_gang")
        card_coords = check_for_card_in_hand("goblin_gang")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1]=placement_coords[1]+35
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    #if mother_witch in deck and in hand
    if (check_if_card_in_deck(deck_list,"mother_witch"))and(check_for_card_in_hand("mother_witch") is not None):
        logger.log("Decided to play mother_witch")
        card_coords = check_for_card_in_hand("mother_witch")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1]=placement_coords[1]+65
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    #if musketeer in deck and musketeer in hand
    if (check_if_card_in_deck(deck_list,"musketeer"))and(check_for_card_in_hand("musketeer") is not None):
        logger.log("Decided to play musketeer")
        card_coords = check_for_card_in_hand("musketeer")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1]=placement_coords[1]+65
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    #if night_witch in deck and in hand
    if (check_if_card_in_deck(deck_list,"night_witch"))and(check_for_card_in_hand("night_witch") is not None):
        logger.log("Decided to play night_witch")
        card_coords = check_for_card_in_hand("night_witch")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1]=placement_coords[1]+65
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    #if witch in deck and in hand
    if (check_if_card_in_deck(deck_list,"witch"))and(check_for_card_in_hand("witch") is not None):
        logger.log("Decided to play witch")
        card_coords = check_for_card_in_hand("witch")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1]=placement_coords[1]+65
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    #if archer_queen in deck and archer_queen in hand
    if (check_if_card_in_deck(deck_list,"archer_queen"))and(check_for_card_in_hand("archer_queen") is not None):
        logger.log("Decided to play archer_queen")
        card_coords = check_for_card_in_hand("archer_queen")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1]=placement_coords[1]+65
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
#spells
    #if fireball in deck and in hand
    if (check_if_card_in_deck(deck_list,"fireball"))and(check_for_card_in_hand("fireball") is not None):
        logger.log("Decided to play fireball")
        card_coords = check_for_card_in_hand("fireball")
        n99 = random.randint(1, 2)
        if n99 == 1:
            placement_coords = [97,203]
        if n99 == 2:
            placement_coords = [320,208]
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    #if poison in deck and in hand
    if (check_if_card_in_deck(deck_list,"poison"))and(check_for_card_in_hand("poison") is not None):
        logger.log("Decided to play poison")
        card_coords = check_for_card_in_hand("poison")
        n99 = random.randint(1, 2)
        if n99 == 1:
            placement_coords = [97,203]
        if n99 == 2:
            placement_coords = [320,208]
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
#hogs
    #if battle_ram in deck and battle_ram in hand
    if (check_if_card_in_deck(deck_list,"battle_ram"))and(check_for_card_in_hand("battle_ram") is not None):
        logger.log("Decided to play archer_queen")
        card_coords = check_for_card_in_hand("archer_queen")
        placement_coords = random_placement_coord_maker()
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return    
    #if hog in deck and hog in hand
    if (check_if_card_in_deck(deck_list,"hog"))and(check_for_card_in_hand("hog") is not None):
        logger.log("Decided to play hog")
        card_coords = check_for_card_in_hand("hog")
        placement_coords = random_placement_coord_maker()
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    #if ram_rider in deck and ram_rider in hand
    if (check_if_card_in_deck(deck_list,"ram_rider"))and(check_for_card_in_hand("ram_rider") is not None):
        logger.log("Decided to play ram_rider")
        card_coords = check_for_card_in_hand("ram_rider")
        placement_coords = random_placement_coord_maker()
        #click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        #click placement
        pyautogui.moveTo(x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    
    
    logger.log("No moves found. Waiting")
    time.sleep(3)
    check_quit_key_press()


def check_if_card_in_deck(deck_list,card):
    n = 0
    while n < 8:
        if deck_list[n] == card:
            return True
        n=n+1
    return False    
    


def main_loop():
    # vars
    fights = 0
    duration = 0.5
    fight_duration = 0.2
    loop_count = 0
    deck = ["witch","fire_spirit","mother_witch","hog","valk","firecracker","bandit","musketeer"]

    if not check_if_windows_exist():
        return

    while True:
        time.sleep(1)
        logger.log(f"loop count: {loop_count}")
        loop_count += 1
        iar = refresh_screen()
        plt.imshow(iar)

        #plt.show()


        
        print(check_deck())

        # while 1 == 1:
        #     fight_with_deck_list(deck)

        

       
        # orientate_memu_multi()
        # time.sleep(1)
        # restart_client(duration)
        # orientate_window()
        # if check_if_on_clash_main_menu():
        #     logger.log("We're on the main menu")
        #     time.sleep(1)
        #     logger.log("Handling chests")
        #     time.sleep(1)
        #     open_chests(duration)
        #     time.sleep(3)
        #     logger.log("Checking if can request")
        #     time.sleep(1)
        #     if check_if_can_request():
        #         logger.log("Can request. Requesting giant")
        #         time.sleep(1)
        #         request_from_clash_main_menu(duration)
        #     else:
        #         logger.log("Request is unavailable")
        #     logger.log("Checking if can donate")
        #     time.sleep(1)
        #     getto_donate_page(duration)
        #     click_donates(duration)
        # else:
        #     logger.log("not on clash main menu")
        
        # #check deck
        # deck = check_deck()
        # time.sleep(2)
        
        # logger.log("Handled chests, requests, and deck. Gonna start a battle")
        # time.sleep(1)
        # start_2v2(duration)
        # logger.add_fight()
        # wait_for_battle_start()
        # fightloops = 0
        # while not check_if_exit_battle_button_exists():
        #     fightloops = fightloops + 1
        #     logger.log(f"fightloop: {fightloops}")
        #     fight_with_deck_list(deck)
        #     if fightloops > 100:
        #         break
        # leave_end_battle_window(duration)
        # time.sleep(5)
        # if check_if_past_game_is_win(duration):
        #     logger.log("Last game was a win")
        #     logger.add_win()
        # else:
        #     logger.log("Last gane was a loss")
        #     logger.add_loss()


if __name__ == "__main__":
    main_loop()
