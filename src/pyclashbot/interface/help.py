import PySimpleGUI as sg

from interface.theme import THEME

sg.theme(THEME)


def show_help_gui():
    # Method for the secondary popup help gui for when the help button is
    # pressed

    out_text = """No help text yet"""

    _layout = [
        [sg.Text(out_text)],
        [sg.Button("Exit")],
    ]
    _window = sg.Window("Help", _layout)
    while True:
        read = _window.read()
        if read is None:
            break
        _event, _ = read
        if _event in [sg.WIN_CLOSED, "Exit"]:
            break
    _window.close()
