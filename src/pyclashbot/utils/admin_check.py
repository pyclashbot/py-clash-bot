"""Checks if the program is running in administrator mode."""
import ctypes
import sys
import tkinter.messagebox


def check_if_program_is_running_in_admin():
    """Checks if the program is running in administrator mode."""
    return ctypes.windll.shell32.IsUserAnAdmin() != 0


def admin_check():
    if not check_if_program_is_running_in_admin():
        tkinter.messagebox.showinfo(
            "CRITICAL ERROR",
            "This program MUST be running in administrator mode!\n\n"
            "Close the running program and restart it as administrator.",
        )
        sys.exit()
