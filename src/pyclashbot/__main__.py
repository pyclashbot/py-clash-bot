import sys
import webbrowser
from os import path
from typing import LiteralString

import PySimpleGUI as sg


from pyclashbot.bot.worker import WorkerThread
from pyclashbot.interface import disable_keys, main_layout, user_config_keys
from pyclashbot.utils.caching import (
    cache_user_settings,
    check_user_settings,
    read_user_settings,
)
from pyclashbot.utils.logger import Logger
from pyclashbot.utils.thread import PausableThread, StoppableThread


def read_window(
    window: sg.Window, timeout: int = 10
) -> tuple[str, dict[str, str | int]]:
    """Method for reading the attributes of the window
    args:
        window: the window to read
        timeout: the timeout for the read method

    returns:
        tuple of the event and the values of the window

    """

    # have a timeout so the output can be updated when no events are happening
    read_result = window.read(timeout=timeout)  # ms
    if read_result is None:
        print("Window not found")
        sys.exit()
    return read_result


def read_job_list(values: dict[str, str | int]) -> list[str]:
    """method for unpacking the job list from the user's input in the gui
    args:
        values: dictionary of the values of the window
    returns:
        list of jobs as str[]
    """
    # unpacking gui vars into a list of jobs as strings
    jobs = []

    if values["-Open-Chests-in-"]:
        jobs.append("Open Chests")

    if values["-Requesting-in-"]:
        jobs.append("Request")

    if values["-Card-Mastery-Collection-in-"]:
        jobs.append("card mastery collection")

    if values["-Free-Offer-Collection-in-"]:
        jobs.append("free offer collection")

    if values["1v1_battle_in"]:
        jobs.append("1v1 battle")
    if values["2v2_battle_in"]:
        jobs.append("2v2 battle")

    if values["card_upgrading_in"]:
        jobs.append("upgrade")

    if values["war_checkbox_in"]:
        jobs.append("war")
    return jobs


def save_current_settings(values) -> None:
    """method for caching the user's current settings
    args:
        values: dictionary of the values of the window
    returns:
        None
    """
    # read the currently selected values for each key in user_coinfig_keys
    user_settings = {key: values[key] for key in user_config_keys if key in values}
    # cache the user settings
    cache_user_settings(user_settings)


def load_last_settings(window) -> None:
    """method for accessing chacned user settings and updating the gui
    args:
        window,the gui window
    returns:
        None
    """
    # if user settings file exists, load the cached settings
    if check_user_settings():
        read_window(window)  # read the window to edit the layout
        user_settings = read_user_settings()
        if user_settings is not None:
            for key in user_config_keys:
                if key in user_settings:
                    window[key].update(user_settings[key])
        window.refresh()  # refresh the window to update the layout


def no_jobs_popup() -> None:
    # Define the layout of the GUI
    layout = [
        [
            sg.Text(
                "You must select at least one job!",
                size=(25, 2),
                justification="center",
            )
        ],
        [sg.Button("Exit", size=(10, 1), pad=((150, 0), 3))],
    ]

    # Create the window
    window = sg.Window("Critical Error!", layout)

    # Event loop to process events and get user input
    while True:
        event, *_ = window.read()  # type: ignore

        # Exit the program if the "Exit" button is clicked or window is closed
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break

    # Close the window
    window.close()


def start_button_event(logger: Logger, window, values) -> WorkerThread | None:
    """method for starting the main bot thread
    args:
        logger, the logger object for for stats storage and printing
        window, the gui window
        values: dictionary of the values of the window
    returns:
        None
    """
    logger.change_status(status="Start Button Event")

    # get job list from gui
    jobs = read_job_list(values)

    # check if at least one job is selected
    if len(jobs) == 0:
        logger.change_status(status="At least one job must be selected")
        no_jobs_popup()
        return None

    for key in disable_keys:
        window[key].update(disabled=True)

    # setup the main thread and start it
    acc_count = int(values["-SSID_IN-"])
    args: tuple[list[str], int] = (jobs, acc_count)
    thread = WorkerThread(logger, args)
    thread.start()

    # enable the stop button after the thread is started
    window["Stop"].update(disabled=False)
    window["-Pause-Resume-Button-"].update(text="Pause")
    window["-Pause-Resume-Button-"].update(disabled=False)

    return thread


def stop_button_event(logger: Logger, window, thread: StoppableThread) -> None:
    """method for stopping the main bot thread
    args:
        logger, the logger object for for stats storage and printing
        window, the gui window
        thread: the main bot thread
    returns:
        None
    """
    logger.change_status(status="Stopping")
    window["Stop"].update(disabled=True)
    window["-Pause-Resume-Button-"].update(text="Pause")
    window["-Pause-Resume-Button-"].update(disabled=True)
    thread.shutdown()  # send the shutdown flag to the thread


def pause_resume_button_event(logger: Logger, window, thread: PausableThread) -> None:
    """method for temporarily stopping the main bot thread
    args:
        logger, the logger object for for stats storage and printing
        window, the gui window
        thread: the main bot thread
    returns:
        None
    """
    if thread.toggle_pause():
        logger.change_status(status="Pausing")
        window["-Pause-Resume-Button-"].update(text="Resume")
    else:
        logger.change_status(status="Resuming")
        window["-Pause-Resume-Button-"].update(text="Pause")


def update_layout(window: sg.Window, logger: Logger) -> None:
    """method for updaing the values in the gui's window
    args:
        window, the gui window
        logger, the logger object for for stats storage and printing
    returns:
        None
    """
    window["time_since_start"].update(logger.calc_time_since_start())  # type: ignore
    # update the statistics in the gui
    stats = logger.get_stats()
    if stats is not None:
        for stat, val in stats.items():
            window[stat].update(val)  # type: ignore


def exit_button_event(thread) -> None:
    # shut down the thread if it is still running
    if thread is not None:
        thread.shutdown(kill=True)


def main_gui() -> None:
    """method for displaying the main gui"""
    console_log = True  # enable/disable console logging

    icon_path = "pixel-pycb.ico"
    if not path.isfile(path=icon_path):
        icon_path: LiteralString = path.join("..\\..\\assets\\", icon_path)

    # create gui window
    window = sg.Window(title="Py-ClashBot", layout=main_layout, icon=icon_path)

    # load the last cached settings
    load_last_settings(window=window)

    # track worker thread and logger
    thread: WorkerThread | None = None
    logger = Logger(console_log=console_log, timed=True)

    # run the gui
    while True:
        event, values = read_window(window, timeout=10)

        # on exit event, kill any existing thread
        if event in [sg.WIN_CLOSED, "Exit"]:
            # shut down the thread if it is still running
            exit_button_event(thread)
            break

        # on start event, start the thread
        if event == "Start":
            thread = start_button_event(logger, window, values)

        # on stop event, stop the thread
        elif event == "Stop" and thread is not None:
            stop_button_event(logger, window, thread)

        # on pause/resume event, pause/resume the thread
        elif event == "-Pause-Resume-Button-" and thread is not None:
            pause_resume_button_event(logger, window, thread)

        # upon changing any user settings, save the current settings
        elif event in user_config_keys:
            save_current_settings(values)

        # on Donate button event, open the donation link in browser
        elif event == "Donate":
            webbrowser.open(
                "https://www.paypal.com/donate/"
                + "?business=YE72ZEB3KWGVY"
                + "&no_recurring=0"
                + "&item_name=Support+my+projects%21"
                + "&currency_code=USD"
            )

        # on Help button event, open the help gui
        elif event == "Help":
            print("Help button event")

        # on issues button event, open the github issues link in browser
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
                window["-Pause-Resume-Button-"].update(disabled=True)
            else:
                # reset the logger
                logger = Logger(console_log=console_log, timed=False)
                thread = None

        update_layout(window, logger)

    # shut down the thread if it is still running
    if thread is not None:
        thread.shutdown(kill=True)
        thread.join()

    window.close()


# def dummy_bot() -> None:
#     logger = Logger()
#     vm_index: int = check_for_vm(logger)
#     jobs: list[str] = [
#         "Open Chests",
#         "upgrade",
#         "request",
#         "free offer collection",
#         "1v1 battle",
#         "card_mastery",
#         "account_switch",
#     ]
#     state = "start"
#     account_switch_order: list[int] = [0]
#     account_index_to_switch_to: int = account_switch_order[0]

#     while 1:
#         state, account_index_to_switch_to = state_tree(
#             vm_index,
#             logger,
#             state,
#             jobs,
#             account_index_to_switch_to,
#             account_switch_order,
#         )
#         print(f"state = {state}")


if __name__ == "__main__":
    # dummy_bot()
    main_gui()
    # debug()
