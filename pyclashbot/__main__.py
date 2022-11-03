from queue import LifoQueue, Queue
import sys
import time
from typing import Union, Any

import PySimpleGUI as sg

from pyclashbot.gui import show_donate_gui, show_help_gui
from pyclashbot.logger import Logger
from pyclashbot.states import detect_state, state_tree
from pyclashbot.thread import StoppableThread
from pyclashbot.layout import layout, disable_keys


def read_window(window: sg.Window):
    # Method for reading the attributes of the window
    # have a timeout so the output can be updated when no events are happening
    read_result = window.read(timeout=100)  # ms
    if read_result is None:
        print("Window not found")
        sys.exit()
    return read_result


def read_job_list(values: dict[str, Any]) -> list[str]:
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
    if values["-Level-Up-Reward-Collection-in-"]:
        jobs.append("level up reward collection")
    if values["-Battlepass-Reward-Collection-in-"]:
        jobs.append("battlepass reward collection")
    if values["-War-Participation-in-"]:
        jobs.append("war")

    return jobs


def start_button_event(logger: Logger, window, values):
    # get job list
    jobs = read_job_list(values)

    # check if at least one job is selected
    if len(jobs) == 0:
        print("At least one job must be selected")
        return None

    # get amount of accounts
    acc_count = int(values["-SSID_IN-"])

    # prepare arguments for main thread
    args = (jobs, acc_count)

    # disable the start button and configuration after the thread is started
    for key in disable_keys:
        window[key].update(disabled=True)

    # create thread
    thread = MainLoopThread(logger, args)
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
    # enable the start button and configuration after the thread is stopped
    for key in disable_keys:
        window[key].update(disabled=False)


def main_gui():
    # Method for the main gui that starts the program

    # defining various things that are gonna be in the gui.

    window = sg.Window("Py-ClashBot", layout)

    thread: Union[MainLoopThread, None] = None
    statistics_q = LifoQueue()
    logger = Logger(statistics_q, console_log=True)
    # run the gui
    while True:
        event: str
        values: dict

        event, values = read_window(window)

        # if window close or exit button click
        if event in [sg.WIN_CLOSED, "Exit"]:
            break

        # If start button
        if event == "Start":
            logger.change_status("Starting")
            thread = start_button_event(logger, window, values)

        elif event == "Stop" and thread is not None:
            logger.change_status("Stopping")
            stop_button_event(window, thread)
            statistics_q = Queue()
            logger = Logger(
                statistics_q, console_log=True
            )  # reset the logger after thread has been stopped

        elif event == "Donate":
            show_donate_gui()

        elif event == "Help":
            show_help_gui()

        # update the statistics in the gui
        if not statistics_q.empty():
            # read the statistics from the logger
            statistics = statistics_q.get()

            for stat in statistics:
                window[stat].update(statistics[stat])

    # shut down the thread if it is still running
    if thread is not None:
        thread.shutdown_flag.set()
        # wait for the thread to close
        thread.join()

    window.close()


class MainLoopThread(StoppableThread):
    def __init__(self, logger: Logger, args, kwargs=None):
        super().__init__(args, kwargs)
        self.logger = logger

    def run(self):
        # parse thread args
        jobs, ssid_max = self.args

        # start ssid at 0
        ssid = 0

        # detect initial state
        state = detect_state(self.logger)

        # loop until shutdown flag is set
        while not self.shutdown_flag.is_set():
            # perform state transition
            (state, ssid) = state_tree(jobs, self.logger, ssid_max, ssid, state)


if __name__ == "__main__":
    main_gui()
