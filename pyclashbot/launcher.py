
import subprocess
from pyclashbot.client import check_quit_key_press, click, orientate_memu, screenshot
from pyclashbot.image_rec import check_for_location, find_references, get_first_location
from pyclashbot.state import check_state
import pygetwindow
import time
import pyautogui
import numpy



def initialize_client(logger):
    #orientate windows
    orientate_memu_multi()
    time.sleep(0.2)
    orientate_memu()
    time.sleep(0.2)
    orientate_bot_window(logger)
    
    #check the state
    state = check_state(logger)
    if state is None:
        state = "restart"
    return state


def close_all_windows():
    windows = pygetwindow.getWindowsWithTitle('MEMu')
    windows += pygetwindow.getWindowsWithTitle('Multiple Instance Manager')
    windows += pygetwindow.getWindowsWithTitle('Multi-MEmu')
    for window in windows:
        if window is not None:
            window.close()


def check_if_windows_exist(logger):
    try:
        # try to get memu
        pygetwindow.getWindowsWithTitle('MEmu')[0]
    except:
        # if i cant find memu i always return false
        logger.log(
            "MEmu not found. Make sure MEmu and Multiple Instance Manager are both open before running the program.")
        return False
    try:
        # try to get MIM with normal name
        pygetwindow.getWindowsWithTitle('Multiple Instance Manager')[0]
    except:
        # if that didnt work try to get MIM with other name.
        try:
            pygetwindow.getWindowsWithTitle('Multi-MEmu')[0]
        except:
            # if that didnt work either then there is no MIM so return false
            logger.log(
                "Multi-Instance Manager not found. Make sure MEmu and Multiple Instance Manager are both open before running the program.")
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


def orientate_memu_multi():
    check_quit_key_press()

    try:
        window_mimm = pygetwindow.getWindowsWithTitle(
            'Multiple Instance Manager')[0]
    except:
        window_mimm = pygetwindow.getWindowsWithTitle('Multi-MEmu')[0]

    window_mimm.minimize()
    window_mimm.restore()
    #window_mimm.moveTo(200, 200)
    time.sleep(0.2)
    window_mimm.moveTo(0, 0)


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


def restart_client(logger):
    logger.log("Restarting everything.")
    logger.log("Closing any existing windows.")
    #get windows
    memu_windows = pygetwindow.getWindowsWithTitle("(MEmu)")
    memu_multi_windows = pygetwindow.getWindowsWithTitle("Multiple Instance Manager")
    
    #close everything
    if len (memu_windows) != 0:
        logger.log("Closing MEmu client.")
        memu_windows[0].close()
    
    if len (memu_multi_windows) != 0:
        logger.log("Closing MEmu launcher.")
        memu_multi_windows[0].close()
    
    #open launcher
    logger.log("Opening MEmu launcher")
    path=r"D:\Program Files\Microvirt\MEmu\MEmuConsole.exe"
    subprocess.Popen(path)
    time.sleep(3)
    
    #orientate launcher
    orientate_memu_multi()
    time.sleep(3)
    
    #click start
    click(556,141)
    time.sleep(3)
    
    #orientate memu client
    orientate_memu()
    
    # wait for client
    logger.log("Waiting for client")
    orientate_memu()
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
    time.sleep(3)
    




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



