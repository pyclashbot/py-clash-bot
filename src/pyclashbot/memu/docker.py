import threading
import time
import pygetwindow as gw

GUI_NAME = "py-clash-bot | dev"
MEMU_CLIENT_NAME = "(pyclashbot-96"


def docker_main():
    def get_clashbot_windows():
        good_titles = []
        titles = gw.getAllTitles()
        for title in titles:
            if MEMU_CLIENT_NAME in title:
                good_titles.append(title)

        return good_titles

    def get_gui_name():
        titles = gw.getAllTitles()
        for title in titles:
            if GUI_NAME in title:
                return title
        return None

    def get_pos(window_name):
        window = gw.getWindowsWithTitle(window_name)[0]
        pos= window.topleft
        pos = (pos[0], pos[1])
        return pos

    def get_size(window_name):
        window = gw.getWindowsWithTitle(window_name)[0]
        w,h= window.size
        return (w,h)

    def resize_window(name,h):
        #get the current position
        good_ratio = 1.56
        new_width = int(h/good_ratio)

        #get the window's current size
        diff_buffer = 3
        current_width,current_height = get_size(name)
        diff = abs(current_width-new_width) + abs(current_height-h)
        if diff < diff_buffer:
            return

        try:
            window = gw.getWindowsWithTitle(name)[0]
            window.resizeTo(new_width,h)
            print('Resized window:',name)
        except IndexError:
            return None

    def calc_toplefts(gui_name,vm_names):
        buffer = 0

        vm_window_coords = []

        gui_width,gui_height = get_size(gui_name)
        gui_pos = get_pos(gui_name)
        current_x_coord = gui_pos[0] + gui_width + buffer - 9
        for vm_name in vm_names:
            this_coord = (current_x_coord,gui_pos[1])
            vm_window_coords.append(this_coord)
            this_vm_size = get_size(vm_name)
            current_x_coord+= this_vm_size[0] + buffer

        return vm_window_coords

    def move_window(name,x,y):
        #get the current position of the window
        diff_buffer = 3
        pos = get_pos(name)
        diff = abs(pos[0]-x) + abs(pos[1]-y)
        if diff < diff_buffer:
            return

        try:
            window = gw.getWindowsWithTitle(name)[0]
            window.moveTo(x,y)
            print('Moved window:',name)
        except IndexError:
            return None

    while 1:
        vm_windows = get_clashbot_windows()
        gui_window = get_gui_name()

        #get gui size
        _,gui_h = get_size(gui_window)

        #resize every clashbot window to the same height as the gui
        for clashbot_window in vm_windows:
            resize_window(clashbot_window,gui_h)

        #calc new coords for vm windows
        new_coords = calc_toplefts(gui_window,vm_windows)
        for i,coord in enumerate(new_coords):
            vm_name = vm_windows[i]
            move_window(vm_name,coord[0],coord[1])

        time.sleep(0.05)




def start_memu_dock_mode():
    print("Starting memu docking!")
    threading.Thread(target=docker_main).start()


if __name__ == "__main__":
    start_memu_dock_mode()

