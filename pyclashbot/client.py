import sys
import time
from os.path import dirname, join

import keyboard
import numpy
import pyautogui
import pygetwindow
from matplotlib import pyplot as plt
from PIL import Image

from pyclashbot.image_rec import (check_for_location, find_references,
                                  get_first_location)


def check_if_windows_exist(logger):
    try:
        pygetwindow.getWindowsWithTitle('MEmu')[0]
        pygetwindow.getWindowsWithTitle('Multiple Instance Manager')[0]
    except (IndexError, KeyError):
        logger.log("MEmu or Multiple Instance Manager not detected!")
        logger.log(
            "Ensure both MEmu and Multi Instance Manager are open and running before starting the program.")
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
        orientate_bot_window(logger)
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
    #window_mimm.moveTo(200, 200)
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
    terminal_window = get_terminal_window()
    if terminal_window is None:
        logger.log("Unable to orientate terminal menu.")
        return
    terminal_window.minimize()
    terminal_window.restore()
    terminal_window.moveTo(200, 200)
    time.sleep(0.2)
    terminal_window.moveTo(730, 0)


def get_terminal_window():
    terminal_titles = [title for title in pygetwindow.getAllTitles(
    ) if title.startswith('py-clash-bot v')]
    if len(terminal_titles) > 0:
        terminal_windows = pygetwindow.getWindowsWithTitle(
            terminal_titles.pop())
        if len(terminal_windows) > 0:
            return terminal_windows.pop()
    return None


def screenshot(region=(0, 0, 500, 700)):
    if region is None:
        return pyautogui.screenshot()
    else:
        return pyautogui.screenshot(region=region)


def get_image(folder, name):
    top_level = dirname(__file__)
    reference_folder = join(top_level, "reference_images")
    return Image.open(join(reference_folder, folder, name))


def draw_picture(coords):
    # make black image and open up white_pix image for pasting
    black_image = get_image(name="draw_background.png", folder="draw_images")
    white_pix = get_image(name="white_pix.png", folder="draw_images")

    image = screenshot(region=[0, 0, 700, 700])
    image.paste(black_image)
    image.paste(im=get_image(name="board_outline_image.png",
                folder="draw_images"), box=(0, 0))

    # for each coord, paste a white pixel at each coord
    size = len(coords)

    print(size)
    print("-------")

    size = size - 1
    while size > 0:
        # print(size)

        image.paste(white_pix, coords[size])
        size = size - 1

    iar = numpy.asarray(image)
    plt.imshow(iar)
    plt.show()


def get_avg_coord(coord_list):
    # handle null params
    if (coord_list == []) or (coord_list is None):
        return
    if len(coord_list) == 0:
        return

    # vars
    x_total = 0
    y_total = 0
    coord_total = 0

    # loop
    size = len(coord_list)
    index = size - 1
    while index > -1:
        current_coord = coord_list[index]
        x_total = x_total + current_coord[0]
        y_total = y_total + current_coord[1]
        coord_total = coord_total + 1

        index = index - 1

    # calc average
    avg_x = int(x_total / coord_total)
    avg_y = int(y_total / coord_total)

    return [avg_x, avg_y]


def restart_client(logger):
    time.sleep(1)
    # close client
    logger.log("Closing client")
    orientate_memu_multi()
    time.sleep(1)
    click(541, 133)
    time.sleep(3)
    # open client
    logger.log("Opening client")
    click(541, 133)
    time.sleep(3)
    # wait for client
    logger.log("Waiting for client")
    orientate_window()
    time.sleep(3)
    loading = True
    loading_loops = 0
    while (loading) and (loading_loops < 20):
        loading_loops = loading_loops + 1
        logger.log(f"Waiting for memu to load:{loading_loops}")
        loading = check_for_memu_loading_background()
        time.sleep(1)
    logger.log("Done waiting for memu to load.")
    time.sleep(5)
    # skip ads
    logger.log("Skipping ads")
    click(440, 600, clicks=7, interval=1)


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
