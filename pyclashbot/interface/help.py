import PySimpleGUI as sg

from pyclashbot.interface.theme import THEME

sg.theme(THEME)


def show_help_gui():
    # Method for the secondary popup help gui for when the help button is
    # pressed

    out_text = """Py-ClashBot is a bot that can be used to automate the process of playing
Clash Royale. It can be used to farm gold, upgrade cards, and much more.

To start, select the jobs you want to run, set the number of accounts to use, and click start.

To stop the bot, click the stop button.

Click the 'Issues?' link to report any issues you may have with the bot."""

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
