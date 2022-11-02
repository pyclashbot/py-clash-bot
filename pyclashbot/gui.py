import sys

import pyperclip
import PySimpleGUI as sg


def show_help_gui():
    # Method for the secondary popup help gui for when the help button is
    # pressed

    out_text = (
        ""
        + "Make sure to check out the website @https://matthewmiglio.github.io/py-clash-bot/?utm_source=github.com\nor the github @https://github.com/matthewmiglio/py-clash-bot\n\n"
    )

    out_text += "To emulate the game, Download and install MEmu.\n"
    out_text += "It is reccomended to install the emulator in Enligsh mode.\n\n"
    out_text += "Using the Multiple Instance Manager, set the instance, display and appearance settings of your instance to match that in the Readme.\n"

    out_text += "Then start the emulator and install Clash Royale with the Google Play Store.\n\n"

    out_text += "It is reccomended to play Clash Royale in English mode.\n"

    sg.theme("Material2")
    layout = [
        [sg.Text(out_text)],
        [sg.Button("Exit")],
    ]
    window = sg.Window("PY-TarkBot", layout)
    while True:
        event, values = read_window(window)
        if event in [sg.WIN_CLOSED, "Exit"]:
            break
    window.close()


def show_donate_gui():
    # Method for the secondary popup donate gui for when the donate button is
    # pressed
    sg.theme("Material2")
    layout = [
        [
            sg.Text(
                "Paypal donate link: \n\nhttps://www.paypal.com/donate/?business=YE72ZEB3KWGVY&no_recurring=0&item_name=Support+my+projects%21&currency_code=USD"
            ),
            sg.Text(size=(15, 1), key="-OUTPUT-"),
        ],
        [sg.Button("Exit"), sg.Button("Copy link to clipboard")]
        # https://www.paypal.com/donate/?business=YE72ZEB3KWGVY&no_recurring=0&item_name=Support+my+projects%21&currency_code=USD
    ]
    window = sg.Window("Donate", layout)
    while True:
        event, values = read_window(window)
        if event in [sg.WIN_CLOSED, "Exit"]:
            break

        if event == "Copy link to clipboard":
            pyperclip.copy(
                "https://www.paypal.com/donate/?business=YE72ZEB3KWGVY&no_recurring=0&item_name=Support+my+projects%21&currency_code=USD"
            )

    window.close()


def read_window(window: sg.Window):
    # Method for reading the attributes of the window

    read_result = window.read()
    if read_result is None:
        print("Window not found")
        end_loop()
    return read_result


def end_loop():
    # Method to handle ending of the program

    print("Press ctrl-c to close the program.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        sys.exit()
