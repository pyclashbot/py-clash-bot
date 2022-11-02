import sys
from typing import Union

import PySimpleGUI as sg

from pyclashbot.client import get_next_ssid
from pyclashbot.gui import show_donate_gui, show_help_gui
from pyclashbot.logger import Logger
from pyclashbot.states import detect_state, state_tree
from pyclashbot.thread import StoppableThread


def read_window(window: sg.Window):
    # Method for reading the attributes of the window
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
    if values["-Random-Decks-in-"]:
        jobs.append("Randomize Deck")
    if values["-Card-Mastery-Collection-in-"]:
        jobs.append("card mastery collection")
    elif not jobs:
        print("At least one job must be selected")
        return None

    # get amount of accounts
    acc_count = int(values["-SSID_IN-"])

    # prepare arguments for main thread
    args = (jobs, acc_count)

    # disable the start button after it is pressed
    window["Start"].update(disabled=True)

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
    sg.theme("Material2")
    # defining various things that are gonna be in the gui.
    layout = [
        # first text lines
        [sg.Text(out_text)],
        # first checkboxes
        [sg.Text("Select which jobs youd like the bot to do:")],
        [
            sg.Checkbox("Open chests", default=True, key="-Open-Chests-in-"),
            sg.Checkbox("Fight", default=True, key="-Fight-in-"),
            sg.Checkbox("Random Requesting", default=True, key="-Requesting-in-"),
            sg.Checkbox("Upgrade cards", default=True, key="-Upgrade_cards-in-"),
            sg.Checkbox("Random decks", default=True, key="-Random-Decks-in-"),
            sg.Checkbox(
                "Card Mastery Collection",
                default=True,
                key="-Card-Mastery-Collection-in-",
            ),
        ],
        # dropdown for amount of accounts
        [
            sg.Text(
                "-------------------------------------------------------------------------------------\nChoose how many accounts you'd like to simultaneously farm:"
            )
        ],
        [sg.Combo(["1", "2", "3", "4"], key="-SSID_IN-", default_value="1")],
        [
            sg.Text(
                "-------------------------------------------------------------------------------------"
            )
        ],
        # bottons at bottom
        [
            sg.Button("Start"),
            sg.Button("Stop", disabled=True),
            sg.Button("Help"),
            sg.Button("Donate"),
        ],
        [sg.Output(size=(88, 20), font=("Consolas 10"))],
    ]
    window = sg.Window("Py-ClashBot", layout)

    thread: Union[MainLoopThread, None] = None
    # run the gui
    while True:
        event, values = read_window(window)

        # if window close or exit button click
        if event in [sg.WIN_CLOSED, "Exit"]:
            break

        # If start button
        if event == "Start":
            thread = start_button_event(window, values)

        elif event == "Stop" and thread is not None:
            stop_button_event(window, thread)

        elif event == "Donate":
            show_donate_gui()

        elif event == "Help":
            show_help_gui()

    # shut down the thread if it is still running
    if thread is not None:
        thread.shutdown_flag.set()
        # wait for the thread to close
        thread.join()

    window.close()


class MainLoopThread(StoppableThread):
    def __init__(self, args, kwargs=None):
        super().__init__(args, kwargs)

    def run(self):
        # parse thread args
        jobs, ssid_total = self.args

        logger = Logger()
        logger.log()
        ssid = 0

        # detect initial state
        state = detect_state(logger)
        while not self.shutdown_flag.is_set():
            # enter state tree
            state = state_tree(jobs, logger, ssid, state)
            # get next account ssid
            ssid = get_next_ssid(ssid, ssid_total)


if __name__ == "__main__":
    main_gui()
