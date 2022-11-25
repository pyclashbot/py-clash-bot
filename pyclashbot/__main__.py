import sys
import webbrowser
from queue import Queue

import PySimpleGUI as sg

from pyclashbot.bot import detect_state, state_tree
from pyclashbot.interface import (
    disable_keys,
    main_layout,
    show_help_gui,
    user_config_keys,
)
from pyclashbot.utils import (
    Logger,
    StoppableThread,
    cache_user_settings,
    read_user_settings,
)
from pyclashbot.utils.caching import check_user_settings


def read_window(
    window: sg.Window, timeout: int = 10
) -> tuple[str, dict[str, str | int]]:
    # Method for reading the attributes of the window
    # have a timeout so the output can be updated when no events are happening
    read_result = window.read(timeout=timeout)  # ms
    if read_result is None:
        print("Window not found")
        sys.exit()
    return read_result


def read_job_list(values: dict[str, str | int]) -> list[str]:
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
    if values["-Free-Offer-Collection-in-"]:
        jobs.append("free offer collection")
    
    return jobs


def save_current_settings(values):
    # read the currently selected values for each key in user_coinfig_keys
    user_settings = {key: values[key] for key in user_config_keys if key in values}
    # cache the user settings
    cache_user_settings(user_settings)


def load_last_settings(window):
    if check_user_settings():
        read_window(window)  # read the window to edit the layout
        user_settings = read_user_settings()
        if user_settings is not None:
            for key in user_config_keys:
                if key in user_settings:
                    window[key].update(user_settings[key])
        window.refresh()  # refresh the window to update the layout


def start_button_event(logger: Logger, window, values):
    logger.change_status("Starting")

    for key in disable_keys:
        window[key].update(disabled=True)

    jobs = read_job_list(values)

    # check if at least one job is selected
    if len(jobs) == 0:
        logger.change_status("At least one job must be selected")
        return None

    # setup thread and start it
    acc_count = int(values["-SSID_IN-"])
    args = (jobs, acc_count)
    thread = WorkerThread(logger, args)
    thread.start()

    # enable the stop button after the thread is started
    window["Stop"].update(disabled=False)

    return thread


def stop_button_event(logger: Logger, window, thread):
    logger.change_status("Stopping")
    window["Stop"].update(disabled=True)
    shutdown_thread(thread)  # send the shutdown flag to the thread


def shutdown_thread(thread, join=False):
    if thread is not None:
        thread.shutdown_flag.set()
        if join:
            # wait for the thread to close
            thread.join()  # this will block the gui


def update_layout(window: sg.Window, logger: Logger):
    window["time_since_start"].update(logger.calc_time_since_start())  # type: ignore
    # update the statistics in the gui
    if not logger.queue.empty():
        # read the statistics from the logger
        for stat, val in logger.queue.get().items():
            window[stat].update(val)  # type: ignore


def main_gui():
    console_log = True  # enable/disable console logging

    window = sg.Window("Py-ClashBot", main_layout)

    load_last_settings(window)

    # track worker thread, communication queue and logger
    thread: WorkerThread | None = None
    statistics_q: Queue[dict[str, str | int]] = Queue()
    logger = Logger(statistics_q, console_log=console_log, timed=False)

    # run the gui
    while True:
        event, values = read_window(window, timeout=10)

        if event in [sg.WIN_CLOSED, "Exit"]:
            # shut down the thread if it is still running
            shutdown_thread(thread)
            break

        if event == "Start":
            # reset the logger and communication queue for a new thread
            statistics_q = Queue()
            logger = Logger(statistics_q, console_log=console_log)
            thread = start_button_event(logger, window, values)

        elif event == "Stop" and thread is not None:
            stop_button_event(logger, window, thread)

        elif event in user_config_keys:
            save_current_settings(values)

        elif event == "Donate":
            webbrowser.open(
                "https://www.paypal.com/donate/"
                + "?business=YE72ZEB3KWGVY"
                + "&no_recurring=0"
                + "&item_name=Support+my+projects%21"
                + "&currency_code=USD"
            )

        elif event == "Help":
            show_help_gui()

        elif event == "issues-link":
            webbrowser.open(
                "https://github.com/matthewmiglio/py-clash-bot/issues/new/choose"
            )

        # handle when thread is finished
        if thread is not None and not thread.is_alive():
            # enable the start button and configuration after the thread is stopped
            for key in disable_keys:
                window[key].update(disabled=False)
            if thread.logger.errored:
                window["Stop"].update(disabled=True)
            else:
                # reset the communication queue and logger
                statistics_q = Queue()
                logger = Logger(statistics_q, console_log=console_log, timed=False)
                thread = None

        update_layout(window, logger)

    # shut down the thread if it is still running
    shutdown_thread(thread, join=True)

    window.close()


class WorkerThread(StoppableThread):
    def __init__(self, logger: Logger, args, kwargs=None):
        super().__init__(args, kwargs)
        self.logger = logger

    def run(self):
        try:
            jobs, ssid_max = self.args  # parse thread args
            ssid = 0  # start ssid at 0
            state = detect_state(self.logger)

            # loop until shutdown flag is set
            while not self.shutdown_flag.is_set():
                # perform state transition
                (state, ssid) = state_tree(jobs, self.logger, ssid_max, ssid, state)
        except Exception as e:  # pylint: disable=broad-except
            # we don't want the thread to crash the interface so we catch all exceptions and log
            # raise e
            self.logger.error(str(e))


if __name__ == "__main__":
    main_gui()
