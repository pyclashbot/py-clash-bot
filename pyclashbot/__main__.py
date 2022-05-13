import random
import time
from os.path import join

import cv2
import keyboard
import matplotlib.pyplot as plt
import numpy as np
import pyautogui
import pygetwindow as gw
from PIL import Image

from pyclashbot.logger import Logger

logger = Logger()

try:
    window_memu = gw.getWindowsWithTitle('MEmu')[0]
    window_mimm = gw.getWindowsWithTitle('Multiple Instance Manager')[0]
except IndexError:
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
    logger.log("Orientating memu client")
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
    reference_image = Image.open(
        join("pyclashbot", "reference_images", "clash_main.png"))
    current_image = refresh_screen()

    # reference_image.show()
    # plt.imshow(current_image)
    # plt.show()

    if compare_images(current_image, reference_image, 0.9) is None:
        return False
    return True


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
    pyautogui.moveTo(x=340, y=250, duration=duration)
    pyautogui.click()
    pyautogui.moveTo(x=330, y=520, duration=duration)
    pyautogui.click()
    time.sleep(3)
    check_quit_key_press()
    return_to_clash_main_menu(duration)


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


def fight_in_2v2(fight_duration):
    check_quit_key_press()
    time.sleep(3)
    card_pick = random_card_coord_picker()
    card_placement = look_for_enemy_troops()
    if card_placement is None:
        print("Found nothing giving random coord")
        card_placement = random_placement_coord_maker()
        y_coord = card_placement[1]
    else:
        print("Placing card on where I found a troop")
        y_coord = min(card_placement[1] - 30, 0)

    pyautogui.moveTo(x=card_pick[0], y=card_pick[1], duration=fight_duration)
    pyautogui.click()
    pyautogui.moveTo(
        x=card_placement[0], y=y_coord, duration=fight_duration)
    pyautogui.click()
    check_quit_key_press()


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
    logger.log("searching screen for green donate buttons")

    reference_image = Image.open(
        join("pyclashbot", "reference_images", "donate_button.png"))
    reference_image2 = Image.open(
        join("pyclashbot", "reference_images", "donate_button2.png"))
    current_image = refresh_screen()

    coords = compare_images(current_image, reference_image, 0.96)
    coords2 = compare_images(current_image, reference_image2, 0.96)
    if (coords is None) and (coords2 is None):
        print("No donate buttons found on this page.")
        return [500, 50]
    if coords is not None:
        return coords
    if coords2 is not None:
        return coords2


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
    # orientate_window()
    time.sleep(5)
    check_quit_key_press()
    time.sleep(5)
    logger.log("skipping ads")
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


def compare_images(image, template, threshold=0.8):
    """detects pixel location of a template in an image
    Args:
        image (Image): image to find template within
        template (Image): template image to match to
        threshold (float, optional): matching threshold. defaults to 0.8
    Returns:
        tuple[(int,int)] or None: a tuple of pixel location (x,y)
    """

    # show template
    # template.show()

    # Convert image to np.array
    image = np.array(image)
    template = np.array(template)

    # Convert image colors
    img_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_RGB2GRAY)

    # Perform match operations.
    res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    # Store the coordinates of matched area in a numpy array
    loc = np.where(res >= threshold)  # type: ignore

    if len(loc[0]) != 1:
        return None

    return (loc[0][0], loc[1][0])


def look_for_enemy_troops():
    current_image = refresh_screen()
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "10_1.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "10_1.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "11_1.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "11_1.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "11_2.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "11_2.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "11_3.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "11_3.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "11_4.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "11_4.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "11_5.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "11_5.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "12_1.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "12_1.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "12_2.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "12_2.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "12_3.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "12_3.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "12_4.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "12_4.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "12_5.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "12_5.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "12_6.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "12_6.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "13_1.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "13_1.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "13_2.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "13_2.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "13_3.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "13_3.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "13_4.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "13_4.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "13_5.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "13_5.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_1.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_1.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_2.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_2.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_3.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_3.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_4.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_4.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_5.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_5.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_6.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_6.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_7.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_7.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_8.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_8.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_9.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_9.png")), 0.97)
    if compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_10.png")), 0.97) is not None:
        return compare_images(current_image, Image.open(join("pyclashbot", "reference_images", "ENEMY_TROOP_IMAGES", "14_10.png")), 0.97)

    return None


def main_loop():
    # vars
    fights = 0
    duration = 0.5
    fight_duration = 0.2
    loop_count = 0

    if not check_if_windows_exist():
        return

    while True:
        time.sleep(1)
        logger.log(f"loop count: {loop_count}")
        loop_count += 1
        iar = refresh_screen()
        plt.imshow(iar)

        # plt.show()
        orientate_memu_multi()
        time.sleep(1)
        restart_client(duration)
        orientate_window()
        if check_if_on_clash_main_menu():
            logger.log("We're on the main menu")
            time.sleep(1)
            logger.log("Handling chests")
            time.sleep(1)
            open_chests(duration)
            time.sleep(3)
            logger.log("Checking if can request")
            time.sleep(1)
            if check_if_can_request():
                logger.log("Can request. Requesting giant")
                time.sleep(1)
                request_from_clash_main_menu(duration)
            else:
                logger.log("Request is unavailable")
            logger.log("Checking if can donate")
            time.sleep(1)
            getto_donate_page(duration)
            click_donates(duration)
        else:
            logger.log("not on clash main menu")
        logger.log("Handled chests and requests. Gonna start a battle")
        time.sleep(1)
        start_2v2(duration)
        logger.add_fight()
        wait_for_battle_start()
        fightloops = 0
        while not check_if_exit_battle_button_exists():
            fightloops = fightloops + 1
            logger.log(f"fightloop: {fightloops}")
            fight_in_2v2(fight_duration)
            if fightloops > 100:
                break
        leave_end_battle_window(duration)
        time.sleep(5)
        if check_if_past_game_is_win(duration):
            logger.log("Last game was a win")
            logger.add_win()
        else:
            logger.log("Last gane was a loss")
            logger.add_loss()


if __name__ == "__main__":
    main_loop()
