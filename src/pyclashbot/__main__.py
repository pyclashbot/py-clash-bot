import sys
import webbrowser

import PySimpleGUI as sg


from pyclashbot.bot.states import state_tree
from pyclashbot.bot.worker import WorkerThread
from pyclashbot.interface import disable_keys, user_config_keys
from pyclashbot.interface.joblist import no_jobs_popup
from pyclashbot.interface.layout import create_window
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


def make_job_dictionary(values: dict[str, str | int]) -> dict[str, str | int]:
    jobs_dictionary: dict[str, str | int] = {
        # job toggles
        "open_chests_user_toggle": values["open_chests_user_toggle"],
        "request_user_toggle": values["request_user_toggle"],
        "card_mastery_user_toggle": values["card_mastery_user_toggle"],
        "free_offer_user_toggle": values["free_offer_user_toggle"],
        "1v1_battle_user_toggle": values["1v1_user_toggle"],
        "2v2_battle_user_toggle": values["2v2_user_toggle"],
        "upgrade_user_toggle": values["card_upgrade_user_toggle"],
        "war_user_toggle": values["war_user_toggle"],
        "random_decks_user_toggle": values["random_decks_user_toggle"],
        # job increments
        "card_upgrade_increment_user_input": values[
            "card_upgrade_increment_user_input"
        ],
        "free_offer_collection_increment_user_input": values[
            "free_offer_collection_increment_user_input"
        ],
        "request_increment_user_input": values["request_increment_user_input"],
        "card_mastery_collect_increment_user_input": values[
            "card_mastery_collect_increment_user_input"
        ],
        "open_chests_increment_user_input": values["open_chests_increment_user_input"],
        "deck_randomization_increment_user_input": values[
            "deck_randomization_increment_user_input"
        ],
    }
    return jobs_dictionary


def check_for_invalid_job_increment_input(job_dictionary):
    items = job_dictionary.items()

    for key, value in items:
        # if its a bool then its a good type input
        if isinstance(value, bool):
            continue

        # if its an int, then its a good type input
        if isinstance(value, int):
            continue

        # if it includes chars that aren't numbers, then its a bad type input
        if value == "":
            return key

        for char in value:
            if char not in "1234567890":
                return key

    return False


def check_for_no_jobs_in_job_dictionary(job_dict):
    for i in job_dict.items():
        if i[1]:
            return False

    return True


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
    print("Cached settings")
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


def show_invalid_job_increment_input_popup(key) -> None:
    key_to_job_dict: dict[str, str] = {
        "card_upgrade_increment_user_input": "Card Upgrade Increment",
        "free_offer_collection_increment_user_input": "Free Offer Collection Increment",
        "request_increment_user_input": "Request Increment",
        "card_mastery_collect_increment_user_input": "Card Mastery Collect Increment",
        "open_chests_increment_user_input": "Open Chests Increment",
        "deck_randomization_increment_user_input": "Randomize Deck Increment",
    }

    key_string = key_to_job_dict[key]
    sg.popup(
        f"Invalid job increment input for key: {key_string}",
        title="Invalid Job Increment Input",
    )


def start_button_event(logger: Logger, window, values) -> WorkerThread | None:
    """method for starting the main bot thread
    args:
        logger, the logger object for for stats storage and printing
        window, the gui window
        values: dictionary of the values of the window
    returns:
        None
    """

    # make job dictionary
    job_dictionary: dict[str, str | int] = make_job_dictionary(values)

    if job_increment_input_check := check_for_invalid_job_increment_input(
        job_dictionary
    ):
        logger.log("Job increment inputs are invalid")
        logger.log(f"Offensive increment input for key: [{job_increment_input_check}]")
        show_invalid_job_increment_input_popup(job_increment_input_check)
        logger.log("invalid job increment input")
        return None

    # handle no jobs selected
    if check_for_no_jobs_in_job_dictionary(job_dictionary):
        no_jobs_popup()
        logger.log("No jobs are selected!")
        return None

    logger.change_status(status="Start Button Event")
    save_current_settings(values)

    logger.log_job_dictionary(job_dictionary)

    for key in disable_keys:
        window[key].update(disabled=True)

    # setup the main thread and start it

    args = job_dictionary
    # args: tuple[list[str], int] = (jobs, acc_count)
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
    thread.shutdown(kill=False)  # send the shutdown flag to the thread


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
    jobs_dictionary = {
        # job list
        "open_chests_user_toggle": True,
        "request_user_toggle": True,
        "card_mastery_user_toggle": True,
        "free_offer_user_toggle": True,
        "1v1_battle_user_toggle": True,
        "2v2_battle_user_toggle": True,
        "upgrade_user_toggle": True,
        "war_user_toggle": True,
        "random_decks_user_toggle": True,
        # job incremenets
        "card_upgrade_increment_user_input": "1",
        "free_offer_collection_increment_user_input": "1",
        "request_increment_user_input": "1",
        "card_mastery_collect_increment_user_input": "1",
        "deck_randomization_increment_user_input": "1",
        "open_chests_increment_user_input": "1",
    }

    while 1:
        # code to run
        state = state_tree(
            vm_index,
            logger,
            state,
            jobs_dictionary,
        )

        if state == "restart":
            for _ in range(10):
                print("Failure")
            break


def debug() -> None:
    pass


if __name__ == "__main__":
    # debug()
    # dummy_bot()
    main_gui()

    # logger = Logger()
    # logger.add_1v1_fight()
    # logger.add_chest_unlock_attempt()
    # logger.check_if_can_open_chests('11')
