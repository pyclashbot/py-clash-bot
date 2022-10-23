import sys

import PySimpleGUI as sg

from pyclashbot.client import (get_next_ssid, orientate_memu,
                               orientate_memu_multi, orientate_terminal)
from pyclashbot.gui import show_donate_gui, show_help_gui
from pyclashbot.logger import Logger
from pyclashbot.states import (detect_state, state_clashmain, state_endfight,
                               state_fight, state_request, state_restart,
                               state_startfight, state_upgrade)
from pyclashbot.thread import StoppableThread


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
        [sg.Combo(['1', '2', '3', '4'], key='-SSID_IN-', default_value='1')],
        [sg.Text("-------------------------------------------------------------------------------------")],
        # bottons at bottom
        [sg.Button('Start'), sg.Button('Stop', disabled=True), sg.Button('Help'), sg.Button('Donate')],
        [sg.Output(size=(88,20), font=("Consolas 10"))]
    ]
    window = sg.Window('Py-ClashBot', layout)
    

    thread = None
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
            if not jobs:
                print("At least one job must be selected")
                continue
            # disable the start button after it is pressed
            window["Start"].update(disabled=True)
            # prepare arguments for main thread
            args = (jobs, int(values["-SSID_IN-"]))
            # create thread
            thread = MainLoopThread(args)
            # start thread
            thread.start()
            # enable the stop button after the thread is started
            window["Stop"].update(disabled=False)

        elif event == "Stop" and thread is not None:
            # disable the stop button after it is pressed
            window["Stop"].update(disabled=True)
            # send the shutdown flag to the thread
            thread.shutdown_flag.set()
            # wait for the thread to close
            thread.join()
            # enable the start button after the thread is stopped
            window["Start"].update(disabled=False)


        elif event == 'Donate':
            show_donate_gui()

        elif event == 'Help':
            show_help_gui()

    window.close()

# main program
class MainLoopThread(StoppableThread):
    def __init__(self, args, kwargs=None):
        super().__init__(args, kwargs)

    def run(self):
        print(f"Thread #{self.ident} started")
        
        jobs, ssid_total = self.args

        logger = Logger()
        logger.log()
        ssid = 0

        # Starting with restart state, the bot will pass itself between
        # states as it reads the screen and will ignore jobs not on the joblist
        state = detect_state(logger)
        while not self.shutdown_flag.is_set():
            if state == "restart":
                state_restart(logger)
                state = "clashmain"

            elif state == "clashmain":
                orientate_memu_multi()
                orientate_memu()
                orientate_terminal()
                if state_clashmain(logger=logger, account_number=ssid, jobs=jobs) == "restart":
                    state = "restart"
                else:
                    state = "startfight"

            elif state == "startfight":
                if "Fight" not in jobs:
                    state = "upgrade"
                else:
                    state = "restart" if state_startfight(
                        logger) == "restart" else "fighting"
            elif state == "fighting":
                state = "restart" if state_fight(
                    logger) == "restart" else "endfight"
            elif state == "endfight":
                state_endfight(logger)
                state = "upgrade"

            elif state == "upgrade":
                if "Upgrade" in jobs and state_upgrade(logger) == "restart":
                    state = "restart"
                else:
                    state = "request"

            elif state == "request":
                if "Request" in jobs and state_request(logger) == "restart":
                    state = "restart"
                else:
                    state = "clashmain"

            # increment SSID to run the next loop with the next account in the cycle
            ssid = get_next_ssid(ssid, ssid_total)

        print(f"Thread #{self.ident} stopped") # doesnt print for some reason


main_gui()
