"""This module contains the main entry point for the py-clash-bot program.
It provides a GUI interface for users to configure and run the bot.
"""

import random
import sys
import webbrowser

import FreeSimpleGUI as sg  # noqa: N813
from FreeSimpleGUI import Window

from pyclashbot.bot.worker import WorkerThread
from pyclashbot.interface import disable_keys, user_config_keys
from pyclashbot.interface.joblist import no_jobs_popup
from pyclashbot.interface.layout import create_window
from pyclashbot.memu.memu_closer import close_everything_memu
from pyclashbot.utils.caching import USER_SETTINGS_CACHE
from pyclashbot.utils.cli_config import arg_parser
from pyclashbot.utils.logger import Logger, initalize_pylogging
from pyclashbot.utils.thread import StoppableThread

initalize_pylogging()


TODO = """
-fix donate image rec (its slow and stupid)
"""


def read_window(
    window: sg.Window,
    timeout: int = 10,
) -> tuple[str, dict[str, str | int]]:
    """Method for reading the attributes of the window
    args:
        window: the window to read
        timeout: the timeout for the  read method

    Returns
    -------
        tuple of the event and the values of the window

    """
    # have a timeout so the output can be updated when no events are happening
    read_result = window.read(timeout=timeout)  # ms
    if read_result is None:
        print("Window not found")
        sys.exit()
    return read_result


def make_job_dictionary(values: dict[str, str | int]) -> dict[str, str | int]:
    """Create a dictionary of job toggles and increments based on the values of the GUI window.

    Args:
    ----
        values: A dictionary of the values of the GUI window.

    Returns:
    -------
        A dictionary of job toggles and increments based on the values of the GUI window.

    """
    random_account_switch_list = make_random_account_switching_dict(
        int(values["account_switching_slider"]),
    )
    print("random_account_switch_list: ", random_account_switch_list)

    jobs_dictionary: dict[str, str | int] = {
        # job toggles
        "open_chests_user_toggle": values["open_chests_user_toggle"],
        "request_user_toggle": values["request_user_toggle"],
        "donate_toggle": values["donate_toggle"],
        "free_donate_toggle": values["free_donate_toggle"],
        "card_mastery_user_toggle": values["card_mastery_user_toggle"],
        "free_offer_user_toggle": values["free_offer_user_toggle"],
        "gold_offer_user_toggle": values["gold_offer_user_toggle"],
        "trophy_road_1v1_battle_user_toggle": values["trophy_road_1v1_user_toggle"],
        "path_of_legends_1v1_battle_user_toggle": values["path_of_legends_1v1_user_toggle"],
        "2v2_battle_user_toggle": values["2v2_user_toggle"],
        "upgrade_user_toggle": values["card_upgrade_user_toggle"],
        "war_user_toggle": values["war_user_toggle"],
        "random_decks_user_toggle": values["random_decks_user_toggle"],
        "deck_number_selection": values["deck_number_selection"],
        "open_bannerbox_user_toggle": values["open_bannerbox_user_toggle"],
        "daily_rewards_user_toggle": values["daily_rewards_user_toggle"],
        "random_plays_user_toggle": values["random_plays_user_toggle"],
        "skip_fight_if_full_chests_user_toggle": values["skip_fight_if_full_chests_user_toggle"],
        "battlepass_collect_user_toggle": values["open_battlepass_user_toggle"],
        "disable_win_track_toggle": values["disable_win_track_toggle"],
        "level_up_chest_user_toggle": values["level_up_chest_user_toggle"],
        "trophy_road_rewards_user_toggle": values["trophy_road_rewards_user_toggle"],
        "magic_items_user_toggle": values["magic_items_user_toggle"],
        # "upgrade_all_cards_user_toggle": values["upgrade_all_cards_user_toggle"],
        "season_shop_buys_user_toggle": values["season_shop_buys_user_toggle"],
        # account switching input info
        "account_switching_toggle": values["account_switching_toggle"],
        "account_switch_count": int(values["account_switching_slider"]),
        # memu settings
        "opengl_toggle": values["opengl_toggle"],
        "directx_toggle": values["directx_toggle"],
    }

    return jobs_dictionary


def make_random_account_switching_dict(count):
    old_list = []
    for i in range(count):
        old_list.append(i)

    new_list = []
    while len(new_list) < len(old_list):
        random_choice = random.choice(old_list)
        if random_choice not in new_list:
            new_list.append(random_choice)

    return new_list


def check_for_invalid_job_increment_input(job_dictionary):
    """Check if the job increments in the job dictionary are valid.

    Args:
    ----
        job_dictionary: A dictionary containing job information.

    Returns:
    -------
        False if all job increments are valid, otherwise
        returns the key of the invalid job increment.

    """
    items = job_dictionary.items()

    for key, value in items:
        if key == "random_account_switch_list":
            continue

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
    """Check if there are no jobs in the job dictionary.

    Args:
    ----
        job_dict: A dictionary containing job information.

    Returns:
    -------
        True if there are no jobs in the dictionary, False otherwise.

    """
    for i in job_dict.items():
        if i[1]:
            return False

    return True


def save_current_settings(values) -> None:
    """Method for caching the user's current settings
    args:
        values: dictionary of the values of the window
    returns:
        None
    """
    # read the currently selected values for each key in user_coinfig_keys
    user_settings = {key: values[key] for key in user_config_keys if key in values}
    # cache the user settings
    print("Cached settings")
    USER_SETTINGS_CACHE.cache_data(user_settings)


def load_settings(settings: None | dict[str, str], window: sg.Window) -> None:
    """Method for loading settings to the gui
    args:
        settings: dictionary of the settings to load
        window: the gui window
    """
    if not settings and USER_SETTINGS_CACHE.exists():
        read_window(window)  # read the window to edit the layout
        user_settings = USER_SETTINGS_CACHE.load_data()
        if user_settings is not None:
            settings = user_settings

    if settings is not None:
        for key in user_config_keys:
            if key in settings:
                if key in list(window.key_dict.keys()):
                    window[key].update(settings[key])  # type: ignore  # noqa: PGH003
                else:
                    print(f"This key {key} appears in saved settings, but not the active window.")
        window.refresh()


def show_invalid_job_increment_input_popup(key) -> None:
    """Display a popup message indicating that the job increment input is invalid.

    Args:
    ----
        key: A string representing the key of the job increment input.

    Returns:
    -------
        None

    """
    # A dictionary mapping the job increment input keys to their corresponding job names.
    key_to_job_dict: dict[str, str] = {
        "card_upgrade_increment_user_input": "Card Upgrade Increment",
        "shop_buy_increment_user_input": "Shop Purchase Increment",
        "request_increment_user_input": "Request Increment",
        "donate_increment_user_input": "Donate Increment",
        "daily_reward_increment_user_input": "Daily Reward Increment",
        "card_mastery_collect_increment_user_input": "Card Mastery Collect Increment",
        "open_chests_increment_user_input": "Open Chests Increment",
        "deck_randomization_increment_user_input": "Randomize Deck Increment",
        "war_attack_increment_user_input": "War Attack Increment",
        "battlepass_collect_increment_user_input": "battlepass_collect_increment_user_input",
        "account_switching_increment_user_input": "Account Switching Increment",
    }

    # Get the job name corresponding to the given key.
    key_string = key_to_job_dict[key]

    # Display a popup message indicating that the job increment input is invalid.
    sg.popup(
        f"Invalid job increment input for key: {key_string}",
        title="Invalid Job Increment Input",
    )


def start_button_event(logger: Logger, window: Window, values) -> WorkerThread | None:
    """Method for starting the main bot thread
    args:
        logger, the logger object for for stats storage and printing
        window, the gui window
        values: dictionary of the values of the window
    returns:
        None
    """
    # print window layout
    window["Stats"].select()

    # make job dictionary
    job_dictionary: dict[str, str | int] = make_job_dictionary(values)

    if job_increment_input_check := check_for_invalid_job_increment_input(
        job_dictionary,
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

    logger.log("Start Button Event")
    logger.change_status(status="Starting the bot!")
    save_current_settings(values)

    logger.log_job_dictionary(job_dictionary)

    for key in disable_keys:
        if key in list(window.key_dict.keys()):
            window[key].update(disabled=True)

    # close existing memuc processes
    print("Closing everything memu related...")
    close_everything_memu()

    # setup the main thread and start it
    print("Starting main thread")
    thread_args = job_dictionary
    # args: tuple[list[str], int] = (jobs, acc_count)
    thread = WorkerThread(logger, thread_args)
    thread.start()

    # enable the stop button after the thread is started
    window["Stop"].update(disabled=False)

    return thread


def stop_button_event(logger: Logger, window, thread: StoppableThread) -> None:
    """Method for stopping the main bot thread
    args:
        logger, the logger object for for stats storage and printing
        window, the gui window
        thread: the main bot thread
    returns:
        None
    """
    logger.change_status(status="Stopping")
    window["Stop"].update(disabled=True)
    thread.shutdown(kill=False)  # send the shutdown flag to the thread


def update_layout(window: sg.Window, logger: Logger) -> None:
    """Method for updaing the values in the gui's window
    args:
        window, the gui window
        logger, the logger object for for stats storage and printing
    returns:
        None
    """
    window["time_since_start"].update(logger.calc_time_since_start())  # type: ignore  # noqa: PGH003
    # update the statistics in the gui
    stats = logger.get_stats()
    if stats is not None:
        for stat, val in stats.items():
            window[stat].update(val)  # type: ignore  # noqa: PGH003


def exit_button_event(thread) -> None:
    """Method for handling the exit button event. Shuts down the thread if it is still running.

    Args:
    ----
        thread: The thread to be shut down.

    Returns:
    -------
        None

    """
    if thread is not None:
        thread.shutdown(kill=True)


def handle_thread_finished(
    window: sg.Window,
    thread: WorkerThread | None,
    logger: Logger,
):
    """Method for handling when the worker thread is finished"""
    # enable the start button and configuration after the thread is stopped
    if thread is not None and not thread.is_alive():
        for key in disable_keys:
            window[key].update(disabled=False)
        if thread.logger.errored:
            window["Stop"].update(disabled=True)
        else:
            # reset the logger
            logger = Logger(timed=False)
            thread = None
    return thread, logger


def main_gui(start_on_run=False, settings: None | dict[str, str] = None) -> None:
    """Method for displaying the main gui"""
    # create gui window
    window = create_window()

    # load the last cached settings
    load_settings(settings, window)

    # track worker thread and logger
    thread: WorkerThread | None = None
    logger = Logger(timed=False)

    # run the gui
    while True:
        event, values = read_window(window, timeout=10)
        if start_on_run:
            event = "Start"
            start_on_run = False

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

        elif event == "-Collapse-Button-":
            window["-Collapse-Button-"].update(
                text="Expand" if window["-tab-group-"].visible else "Collapse",
            )
            window["-tab-group-"].update(visible=not window["-tab-group-"].visible)

        # upon changing any user settings, save the current settings
        elif event in user_config_keys:
            save_current_settings(values)

        # on Donate button event, open the donation link in browser
        elif event == "bug-report":
            webbrowser.open(
                "https://github.com/pyclashbot/py-clash-bot/issues/new/choose",
            )

        elif event == "upload-log":
            if logger is not None:
                url = logger.upload_log()
                if url is not None:
                    webbrowser.open(url)

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


if __name__ == "__main__":
    cli_args = arg_parser()
    main_gui(start_on_run=cli_args.start)
