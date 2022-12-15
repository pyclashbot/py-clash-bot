import ctypes
import os
import sys
import tkinter.messagebox


def check_if_program_is_running_in_admin():
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


if not check_if_program_is_running_in_admin():
    tkinter.messagebox.showinfo(
        "CRITICAL ERROR",
        "This program MUST be running in administrator mode!\n\nClose the running program and restart it as administrator.",
    )
    sys.exit()
