import pygetwindow as gw
import time
import threading

GOOGLE_PLAY_PROCESS_NAME = "Google Play Games on PC Emulator"  # window title keyword
GUI_PROCESS_NAME = "py-clash-bot |"  # your app's window title


def find_window(title_keyword):
    windows = gw.getWindowsWithTitle(title_keyword)
    return windows[0] if windows else None


def get_gui_pos():
    win = find_window(GUI_PROCESS_NAME)
    return (win.left, win.top) if win else (0, 0)


def get_google_play_pos():
    win = find_window(GOOGLE_PLAY_PROCESS_NAME)
    return (win.left, win.top) if win else (0, 0)


def get_gui_dims():
    win = find_window(GUI_PROCESS_NAME)
    return (win.width, win.height) if win else (0, 0)


def get_google_play_dims():
    win = find_window(GOOGLE_PLAY_PROCESS_NAME)
    return (win.width, win.height) if win else (0, 0)


def move_google_play(x, y):
    win = find_window(GOOGLE_PLAY_PROCESS_NAME)
    if win:
        win.moveTo(x, y)


def dock():
    gui_pos = get_gui_pos()
    gui_dims = get_gui_dims()
    if gui_pos == (0, 0) or gui_dims == (0, 0):
        print("GUI window not found.")
        return

    new_x = gui_pos[0] + gui_dims[0]  # dock to the right
    new_y = gui_pos[1]
    move_google_play(new_x, new_y)


def is_docked(threshold=3):
    gui_pos = get_gui_pos()
    google_pos = get_google_play_pos()
    gui_dims = get_gui_dims()

    expected_x = gui_pos[0] + gui_dims[0]
    expected_y = gui_pos[1]

    dx = abs(google_pos[0] - expected_x)
    dy = abs(google_pos[1] - expected_y)
    return dx <= threshold and dy <= threshold


def dock_loop():
    while True:
        if not is_docked():
            dock()
        time.sleep(1)


def start_dock_thread():
    t = threading.Thread(target=dock_loop, daemon=True)
    t.start()
    return t

