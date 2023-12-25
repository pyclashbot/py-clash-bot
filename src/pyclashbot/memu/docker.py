import threading
import time
import pygetwindow as gw

GUI_NAME = "py-clash-bot | dev"
MEMU_CLIENT_NAME = "(pyclashbot-96)"
CLANSPAM_NAME = "(clanspam-11)"

def get_window_pos(name):
    try:
        window = gw.getWindowsWithTitle(name)[0]
        return window.topleft
    except IndexError:
        return None

def move_window(name,x,y):
    try:
        window = gw.getWindowsWithTitle(name)[0]
        window.moveTo(x,y)
    except IndexError:
        return None

def get_window_size(name):
    try:
        window = gw.getWindowsWithTitle(name)[0]
        return window.size
    except IndexError:
        return None


def resize_window(name,w,h):
    try:
        window = gw.getWindowsWithTitle(name)[0]
        window.resizeTo(w,h)
    except IndexError:
        return None


def dock_memu():
    gui_topleft = get_window_pos(GUI_NAME)
    gui_size = get_window_size(GUI_NAME)
    gui_width = gui_size[0]
    gui_topright = (gui_topleft[0]+gui_width,gui_topleft[1])

    gui_topright = (gui_topright[0]-7,gui_topright[1])

    move_window(MEMU_CLIENT_NAME,gui_topright[0],gui_topright[1])


def resize_memu():
    ratio = 0.6326836581709145
    gui_size = get_window_size(GUI_NAME)

    new_height = gui_size[1] - 7

    new_width = int(new_height*ratio)+1

    resize_window(MEMU_CLIENT_NAME,new_width,new_height)


def check_sizing():
    gui_size = get_window_size(GUI_NAME)
    memu_size = get_window_size(MEMU_CLIENT_NAME)

    gui_height = gui_size[1]
    memu_height = memu_size[1]

    # print(gui_height,memu_height)

    value = abs(gui_height - memu_height - 8)

    if value > 2:
        return False
    return True


def check_position():
    gui_topleft = get_window_pos(GUI_NAME)
    gui_size = get_window_size(GUI_NAME)
    gui_width = gui_size[0]
    gui_topright = (gui_topleft[0]+gui_width,gui_topleft[1])

    memu_topleft = get_window_pos(MEMU_CLIENT_NAME)

    memu_topleft = (memu_topleft[0]+7, memu_topleft[1])


    x_diff = abs(gui_topright[0] - memu_topleft[0])
    y_diff = abs(gui_topright[1] - memu_topleft[1])

    if x_diff > 4 or y_diff > 1:
        return False

    return True



def docker_main():
    while 1:
        try:
            if not check_sizing():
                print('[docker] resize...')
                resize_memu()
                continue
            if not check_position():
                print('[docker] Dock...')
                dock_memu()
                continue
            time.sleep(0.33)
        except:
            pass



def start_memu_dock_mode():
    print('Starting memu docking!')
    threading.Thread(target=docker_main).start()




if __name__ == "__main__":
    pass
