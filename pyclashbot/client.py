import time

import keyboard
import numpy
import pyautogui
import pygetwindow

from pyclashbot.image_rec import pixel_is_equal


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
    iar = refresh_screen()
    check_quit_key_press()

    pix2 = iar[71][142]
    pix3 = iar[77][275]

    sentinel = [1] * 3
    sentinel[0] = 5
    sentinel[1] = 18
    sentinel[2] = 35
    check_quit_key_press()
    if not pixel_is_equal(pix2, sentinel, 10):
        return False
    if not pixel_is_equal(pix3, sentinel, 10):
        return False
    return True


def wait_for_memu_main(logger):
    loops = 0
    while check_if_on_memu_main() is False:
        loops = loops+1
        log = "Waiting for memu main:"+str(loops)
        logger.log(log)
        time.sleep(1)
        if loops > 20:
            logger.log("Waited too long for memu start")
            return "quit"


def orientate_window():
    #logger.log("Orientating memu client")
    window_memu = pygetwindow.getWindowsWithTitle('MEmu')[0]
    check_quit_key_press()
    window_memu.minimize()
    window_memu.restore()
    time.sleep(0.2)
    window_memu.moveTo(0, 0)
    time.sleep(0.2)
    window_memu.resizeTo(460, 680)


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
    screenshot = pyautogui.screenshot()
    check_quit_key_press()
    iar = numpy.array(screenshot)
    return iar


def screenshot(region=None):
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


def click(x, y, clicks=1, interval=0.1):
    original_pos = pyautogui.position()
    loops = 0
    while loops < clicks:
        check_quit_key_press()
        pyautogui.click(x=x, y=y)
        pyautogui.moveTo(original_pos[0], original_pos[1])
        loops = loops+1
        time.sleep(interval)


def check_quit_key_press():
    if keyboard.is_pressed("space"):
        print("space is pressed. Quitting the program")
        quit()
