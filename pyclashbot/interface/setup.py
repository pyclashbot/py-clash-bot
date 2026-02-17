import sys
import tkinter as tk
from tkinter import messagebox
from pyclashbot.interface.i18n import tr


def show_clash_royale_setup_gui() -> None:
    """Notify the user that Clash Royale must be installed and configured."""
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        tr("Clash Royale Not Setup!"),
        tr("Clash Royale is not installed or setup.\nPlease install Clash Royale, finish the in-game tutorial,\nand log in before using this bot."),
    )
    root.destroy()
    sys.exit(0)
