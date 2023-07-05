import sys

import PySimpleGUI as sg

from interface.theme import THEME

sg.theme(THEME)


def show_clash_royale_setup_gui():
    # a method to notify the user that clashroayle is not installed or setup

    out_text = """Clash Royale is not installed or setup.
Please install Clash Royale, finish the in-game tutorial
and login before using this bot."""

    _layout = [
        [sg.Text(out_text)],
    ]
    _window = sg.Window("Clash Royale Not Setup!", _layout)
    while True:
        read = _window.read()
        if read is None:
            break
        _event, _ = read
        if _event in [sg.WIN_CLOSED]:
            break
    _window.close()
    sys.exit(0)
