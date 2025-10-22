import sys
import tkinter as tk
from tkinter import messagebox


def show_clash_royale_setup_gui() -> None:
    """Notify the user that Clash Royale must be installed and configured."""
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Clash Royale Not Setup!",
        "Clash Royale is not installed or setup.\n"
        "Please install Clash Royale, finish the in-game tutorial,\n"
        "and log in before using this bot.",
    )
    root.destroy()
    sys.exit(0)
