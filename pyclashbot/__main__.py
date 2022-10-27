import sys

import PySimpleGUI as sg

from pyclashbot.client import get_next_ssid
from pyclashbot.gui import show_donate_gui, show_help_gui
from pyclashbot.logger import Logger
from pyclashbot.states import detect_state, state_tree
from pyclashbot.thread import StoppableThread


# Method for reading the attributes of the window
def read_window(window: sg.Window):
    read_result = window.read()
    if read_result is None:
        print("Window not found")
        sys.exit()
    return read_result


def start_button_event(window, values):
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
        return None
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
    return thread


def stop_button_event(window, thread):
    # disable the stop button after it is pressed
    window["Stop"].update(disabled=True)
    # send the shutdown flag to the thread
    thread.shutdown_flag.set()
    # wait for the thread to close
    thread.join()
    # enable the start button after the thread is stopped
    window["Start"].update(disabled=False)


def main_gui():
    # Method for the main gui that starts the program
    out_text = "Matthew Miglio ~October 2022\n\n-------------------------------------------------------------------------------------\nPy-ClashBot can farm gold, chest, and card\nprogress by farming 2v2 matches with random teammates.\n-------------------------------------------------------------------------------------"
    sg.theme('Material2')
    # defining various things that are gonna be in the gui.
    layout = [
        # first text lines
        [sg.Text(out_text)],
        # first checkboxes
        [sg.Text("Select which jobs youd like the bot to do:")],
        [
            sg.Checkbox('Open chests', default=True, key="-Open-Chests-in-"),
            sg.Checkbox('Fight', default=True, key="-Fight-in-"),
            sg.Checkbox('Random Requesting', default=True,
                        key="-Requesting-in-"),
            sg.Checkbox('Upgrade cards', default=True,
                        key="-Upgrade_cards-in-"),

        ],
        # dropdown for amount of accounts
        [sg.Text("-------------------------------------------------------------------------------------\nChoose how many accounts you'd like to simultaneously farm:")],
        [sg.Combo(['1', '2', '3', '4'], key='-SSID_IN-', default_value='1')],
        [sg.Text("-------------------------------------------------------------------------------------")],
        # bottons at bottom
        [sg.Button('Start'), sg.Button('Stop', disabled=True),
         sg.Button('Help'), sg.Button('Donate')],
        [sg.Output(size=(88, 20), font=("Consolas 10"))]
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
            thread = start_button_event(window, values)

        elif event == 'Stop' and thread is not None:
            stop_button_event(window, thread)

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
            # perform a state decision based on the current state and get the
            # next state
            state = state_tree(jobs, logger, ssid, state)
            # increment SSID to run the next loop with the next account in the
            # cycle
            ssid = get_next_ssid(ssid, ssid_total)

        print(f"Thread #{self.ident} stopped")


main_gui()
