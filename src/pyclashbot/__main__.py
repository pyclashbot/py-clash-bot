import sys
import webbrowser

import PySimpleGUI as sg
from pyclashbot.bot.request_state import check_if_can_request_3, check_if_can_request_wrapper

from pyclashbot.bot.states import state_tree
from pyclashbot.bot.worker import WorkerThread
from pyclashbot.interface import disable_keys, user_config_keys
from pyclashbot.interface.joblist import no_jobs_popup
from pyclashbot.interface.layout import create_window
from pyclashbot.memu.client import screenshot
from pyclashbot.utils.caching import (
    cache_user_settings,
    check_user_settings,
    read_user_settings,
)
from pyclashbot.utils.logger import Logger, initalize_pylogging
from pyclashbot.utils.thread import PausableThread, StoppableThread

initalize_pylogging()


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
        jobs.append("open Chests")

    if values["-Requesting-in-"]:
        jobs.append("request")

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
    for _ in range(3):
        logger.log(f"JOB LIST IS: {jobs}")

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


def handle_thread_finished(
    window: sg.Window, thread: WorkerThread | None, logger: Logger
):
    """method for handling when the worker thread is finished"""
    # enable the start button and configuration after the thread is stopped
    if thread is not None and not thread.is_alive():
        for key in disable_keys:
            window[key].update(disabled=False)
        if thread.logger.errored:
            window["Stop"].update(disabled=True)
            window["-Pause-Resume-Button-"].update(disabled=True)
        else:
            # reset the logger
            logger = Logger(timed=False)
            thread = None
    return thread, logger


def main_gui() -> None:
    """method for displaying the main gui"""
    # create gui window
    window = create_window()

    # load the last cached settings
    load_last_settings(window=window)

    # track worker thread and logger
    thread: WorkerThread | None = None
    logger = Logger(timed=False)

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
            logger = Logger(timed=True)
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
        elif event == "bug-report":
            webbrowser.open(
                "https://github.com/matthewmiglio/py-clash-bot/issues/new/choose"
            )

        # on Help button event, open the help gui
        elif event == "discord":
            webbrowser.open("https://discord.gg/eXdVuHuaZv")

            # handle when thread is finished

        update_layout(window, logger)

    # shut down the thread if it is still running
    window.close()
    if thread is not None:
        thread.shutdown(kill=True)
        thread.join()


def dummy_bot():
    vm_index = 1
    logger = Logger()
    state = "open_chests"
    joblist: list[str] = [
        # "Open Chests",
        # "upgrade",
        # "request",
        # "free offer collection",
        "1v1 battle",
        # "2v2 battle",
        # "card mastery collection",
        # "war",
    ]

    while 1:
        # code to run
        state = state_tree(
            vm_index,
            logger,
            state,
            joblist,
        )

        if state == "restart":
            for _ in range(10):
                print("Failure")
            break


def debug():
    # screenshot(1)
    # check_if_can_request_3(1)
    print(check_if_can_request_wrapper(1))


if __name__ == "__main__":
    # dummy_bot()
    # main_gui()
    debug()
