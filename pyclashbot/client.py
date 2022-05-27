import sys
import time

import keyboard
import matplotlib.pyplot as plt
import numpy
import pyautogui
import pygetwindow

from pyclashbot.image_rec import find_references, get_first_location, pixel_is_equal


def show_image(iar):
    plt.imshow(iar)
    check_quit_key_press()
    plt.show()


def check_for_windows(logger):
    try:
        pygetwindow.getWindowsWithTitle('MEmu')[0]
        pygetwindow.getWindowsWithTitle('Multiple Instance Manager')[0]
    except (IndexError, KeyError):
        logger.log("MEmu or Multiple Instance Manager not detected!")
        return False
    return True


def check_if_windows_exist(logger):
    if pygetwindow.getWindowsWithTitle('MEmu') == []:
        logger.log("MEmu window not found")
        return False
    if pygetwindow.getWindowsWithTitle('Multiple Instance Manager') == []:
        logger.log("MMIM window not found")
        return False
    return True


def check_if_on_memu_main():
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
        "6.png",

    ]
    locations = find_references(
        screenshot=refresh_screen(),
        folder="memu_main",
        names=references,
        tolerance=0.97
    )
    return get_first_location(locations)


def wait_for_memu_main(logger):
    loops = 0
    while check_if_on_memu_main() is False:
        orientate_bot_window()
        time.sleep(0.2)
        loops = loops + 1
        log = "Waiting for memu main:" + str(loops)
        logger.log(log)
        time.sleep(1)
        if loops > 20:
            logger.log("Waited too long for memu start")
            return "quit"
    time.sleep(5)


def orientate_window():
    # logger.log("Orientating memu client")
    window_memu = pygetwindow.getWindowsWithTitle('MEmu')[0]
    check_quit_key_press()
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


def orientate_memu_multi():
    check_quit_key_press()
    window_mimm = pygetwindow.getWindowsWithTitle(
        'Multiple Instance Manager')[0]
    window_mimm.minimize()
    window_mimm.restore()
    window_mimm.moveTo(200, 200)
    time.sleep(0.2)
    window_mimm.moveTo(0, 0)


def refresh_screen():
    check_quit_key_press()
    orientate_window()
    screenshot = pyautogui.screenshot(region=(0, 0, 500, 700))
    check_quit_key_press()
    iar = numpy.array(screenshot)
    return iar


def orientate_bot_window(logger):
    terminal_window=get_terminal_window(logger)
    if terminal_window is None:
        logger.log("Unable to orientate terminal menu.")
        return
    terminal_window.minimize()
    terminal_window.restore()
    terminal_window.moveTo(200, 200)
    time.sleep(0.2)
    terminal_window.moveTo(730, 0)
    
    


def get_terminal_window(logger):
    # window_terminal = pygetwindow.getWindowsWithTitle(
    #     [title for title in pygetwindow.getAllTitles() if title.startswith('py-clash')][0])[0]
    list=pygetwindow.getAllTitles()
    n=len(list)
    while n!=0:
        n=n-1
        #print(list[n])
        if list[n].startswith("py-clash"): 
            return pygetwindow.getWindowsWithTitle(list[n])
    return None
    
    


def screenshot(region=(0, 0, 500, 700)):
    if region is None:
        return pyautogui.screenshot()
    else:
        return pyautogui.screenshot(region=region)


def restart_client(logger):
    check_quit_key_press()
    logger.log("closing client")
    time.sleep(1)
    click(x=540, y=140)
    time.sleep(1)
    check_quit_key_press()
    logger.log("opening client")
    click(x=540, y=140)
    time.sleep(3)
    if wait_for_memu_main(logger) == "quit":
        return "quit"
    logger.log("skipping ads")
    orientate_window()
    time.sleep(1)
    click(x=440, y=600, clicks=5, interval=1)


def scroll_down():
    origin = pyautogui.position()
    pyautogui.moveTo(x=215, y=350)
    pyautogui.dragTo(x=215, y=300, button='left', duration=1)
    pyautogui.moveTo(x=origin[0], y=origin[1])


def scroll_up():
    origin = pyautogui.position()
    pyautogui.moveTo(x=215, y=300)
    pyautogui.dragTo(x=215, y=350, button='left', duration=1)
    pyautogui.moveTo(x=origin[0], y=origin[1])


def scroll_down_fast():
    origin = pyautogui.position()
    pyautogui.moveTo(x=215, y=350)
    pyautogui.dragTo(x=215, y=300, button='left', duration=0.5)
    pyautogui.moveTo(x=origin[0], y=origin[1])


def scroll_down_super_fast():
    origin = pyautogui.position()
    pyautogui.moveTo(x=215, y=400)
    pyautogui.dragTo(x=215, y=300, button='left', duration=0.2)
    pyautogui.moveTo(x=origin[0], y=origin[1])


def scroll_up_fast():
    origin = pyautogui.position()
    pyautogui.moveTo(x=215, y=300)
    pyautogui.dragTo(x=215, y=350, button='left', duration=0.5)
    pyautogui.moveTo(x=origin[0], y=origin[1])


def click(x, y, clicks=1, interval=0.0):
    original_pos = pyautogui.position()
    loops = 0
    while loops < clicks:
        check_quit_key_press()
        pyautogui.click(x=x, y=y)
        pyautogui.moveTo(original_pos[0], original_pos[1])
        loops = loops + 1
        time.sleep(interval)


def check_quit_key_press():
    if keyboard.is_pressed("space"):
        print("space is pressed. Quitting the program")
        sys.exit()
