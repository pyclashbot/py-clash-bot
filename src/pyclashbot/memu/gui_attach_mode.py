import win32gui
import time
import threading

GUI_NAME = "py-clash-bot | dev"
MEMU_CLIENT_NAME = "(pyclashbot-96)"

# Define a threading.Event to signal when to stop the threads
stop_threads = threading.Event()


def get_window_position(window_name):
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd:
        rect = win32gui.GetWindowRect(hwnd)
        x, y = rect[0], rect[1]
        return x, y
    else:
        return None


def move_window(window_name, new_x, new_y):
    hwnd = win32gui.FindWindow(None, window_name)
    w, h = get_window_size(window_name)
    if hwnd:
        win32gui.MoveWindow(hwnd, new_x, new_y, w, h, True)
        return True
    else:
        return False


def resize_window(window_name, new_width, new_height):
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd:
        win32gui.MoveWindow(hwnd, 0, 0, new_width, new_height, True)
        return True
    else:
        return False


def get_window_size(window_name):
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd:
        rect = win32gui.GetWindowRect(hwnd)
        width, height = rect[2] - rect[0], rect[3] - rect[1]
        return width, height
    else:
        return None


def attach_memu_to_gui():
    # get pos of gui
    pos = get_window_position(GUI_NAME)

    # get width of gui
    width, height = get_window_size(GUI_NAME)

    # calculate topright coord of gui
    rightmost_x = pos[0] + width - 7

    move_window(MEMU_CLIENT_NAME, rightmost_x, pos[1])


def make_new_memu_res(height):
    ratio = 0.6326836581709145

    width = int(height * ratio)

    return width, height


def resize_memu_based_on_gui():
    # gui size
    width, height = get_window_size(GUI_NAME)

    # make new memu res
    new_width, new_height = make_new_memu_res(height)

    # subtract 5 from new_height
    new_height -= 5

    # resize memu
    resize_window(MEMU_CLIENT_NAME, new_width, new_height)


def check_memu_windows_orientation():
    gui_pos = get_window_position(GUI_NAME)
    gui_size = get_window_size(GUI_NAME)
    memu_pos = get_window_position(MEMU_CLIENT_NAME)

    #calculate topright of gui
    topright = (gui_pos[0] + gui_size[0], gui_pos[1])

    #calculate topleft of memu
    topleft = (memu_pos[0], memu_pos[1])

    #if either axis is off by more than 10, return False
    if abs(topright[0] - topleft[0]) > 10 or abs(topright[1] - topleft[1]) > 10:
        return False

    return True


def memu_attach_mode():
    current_pos = None
    while not stop_threads.is_set():
        try:
            if current_pos is None:
                current_pos = get_window_position(GUI_NAME)

            if current_pos != get_window_position(GUI_NAME):
                current_pos = get_window_position(GUI_NAME)
                resize_memu_based_on_gui()
                attach_memu_to_gui()
                time.sleep(0.1)
        except:
            pass

def start_memu_attach_mode():
    print('Starting memu attach mode!')
    threading.Thread(target=memu_attach_mode).start()




if __name__ == "__main__":
    start_memu_attach_mode()
