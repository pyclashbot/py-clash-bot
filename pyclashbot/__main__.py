import sys

import PySimpleGUI as sg

from pyclashbot.client import (get_next_ssid, orientate_memu,
                               orientate_memu_multi)
from pyclashbot.dependency import setup_ahk, setup_memu
from pyclashbot.gui import show_donate_gui, show_help_gui
from pyclashbot.logger import Logger
from pyclashbot.states import (detect_state, state_clashmain, state_endfight,
                               state_fight, state_request, state_restart,
                               state_startfight, state_upgrade)


# Method to handle ending of the program
def end_loop():
    print("Press ctrl-c to close the program.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        sys.exit()

# Method for reading the attributes of the window


def read_window(window: sg.Window):
    read_result = window.read()
    if read_result is None:
        print("Window not found")
        end_loop()
    return read_result

# Method for the main gui that starts the program


def main_gui():
    out_text = "Matthew Miglio ~October 2022\n\n-------------------------------------------------------------------------------------\nPy-ClashBot can farm gold, chest, and card\nprogress by farming 2v2 matches with random teammates.\n-------------------------------------------------------------------------------------"
    sg.theme('Material2')
    # defining various things that are gonna be in the gui.
    layout = [
        # first text lines
        [sg.Text(out_text)],
        # first checkboxes
        [sg.Text("Select which jobs youd like the bot to do:")],
        [
            sg.Checkbox('Open chests', default=False, key="-Open-Chests-in-"),
            sg.Checkbox('Fight', default=False, key="-Fight-in-"),
            sg.Checkbox('Random Requesting', default=False,
                        key="-Requesting-in-"),
            sg.Checkbox('Upgrade cards', default=False,
                        key="-Upgrade_cards-in-"),

        ],
        # dropdown for amount of accounts
        [sg.Text("-------------------------------------------------------------------------------------\nChoose how many accounts you'd like to simultaneously farm:")],
        [sg.Combo(['1', '2', '3', '4'], key='-SSID_IN-')],
        [sg.Text("-------------------------------------------------------------------------------------")],
        # bottons at bottom
        [sg.Button('Start'), sg.Button('Help'), sg.Button('Donate')]
    ]
    window = sg.Window('PY-ClashBot', layout)

    # run the gui
    while True:
        event, values = read_window(window)

        # if window close or exit button click
        if event in [sg.WIN_CLOSED, 'Exit']:
            break

        # If start button
        if event == 'Start':
            # get job list
            jobs = []
            if values["-Open-Chests-in-"]:
                jobs.append("Open Chests")
            if values["-Fight-in-"]:
                jobs.append("Fight")
            if values["-Requesting-in-"]:
                jobs.append("Request")
            if values["-Upgrade_cards-in-"]:
                jobs.append("Upgrade")

            window.close()
            # run main
            main(jobs=jobs, ssid_total=int(values["-SSID_IN-"]))

        # If donate button
        if event == 'Donate':
            show_donate_gui()

        # if help button
        if event == 'Help':
            show_help_gui()

    window.close()

# main program


def main(jobs, ssid_total):
    # Make logger, initialize SSID as 1
    logger = Logger()
    logger.log()
    ssid = 0

    # Starting with restart state, the bot will pass itself between
    # states as it reads the screen and will ignore jobs not on the joblist
    state = detect_state(logger)
    while True:

        if state == "restart":
            state_restart(logger, launcher_path)
            state = "clashmain"

        if state == "clashmain":
            orientate_memu_multi()
            orientate_memu()
            if state_clashmain(logger=logger, account_number=ssid, jobs=jobs) == "restart":
                state = "restart"
            else:
                state = "startfight"

        if state == "startfight":
            if "Fight" not in jobs:
                state = "upgrade"
            else:
                state = "restart" if state_startfight(
                    logger) == "restart" else "fighting"
        if state == "fighting":
            state = "restart" if state_fight(
                logger) == "restart" else "endfight"
        if state == "endfight":
            state_endfight(logger)
            state = "upgrade"

        if state == "upgrade":
            if "Upgrade" in jobs and state_upgrade(logger) == "restart":
                state = "restart"
            else:
                state = "request"

        if state == "request":
            if "Request" in jobs and state_request(logger) == "restart":
                state = "restart"
            else:
                state = "clashmain"

        # increment SSID to run the next loop with the next account in the cycle
        ssid = get_next_ssid(ssid, ssid_total)


setup_ahk()  # setup autohotkey, install if necessary
launcher_path = setup_memu()  # setup memu, install if necessary
main_gui()
