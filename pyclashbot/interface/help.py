import tkinter as tk
from tkinter import messagebox


def show_help_gui() -> None:
    """Display a simple help message."""
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Help", "No help text yet")
    root.destroy()
