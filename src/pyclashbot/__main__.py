import random
import sys
import webbrowser
import time
import PySimpleGUI as sg
import pickle
import os
from pyclashbot.bot.worker import WorkerThread
from pyclashbot.interface.layout2 import make_window, user_config_keys, make_job_dict
from pyclashbot.memu.launcher import close_everything_memu, get_vms
from pyclashbot.utils.caching import USER_SETTINGS_CACHE
from pyclashbot.utils.cli_config import arg_parser
from pyclashbot.utils.logger import Logger, initalize_pylogging
from pyclashbot.utils.thread import StoppableThread
from PySimpleGUI import Window
from pyclashbot.memu.memu_closer import close_memuc_processes

initalize_pylogging()

# Define the configuration file path
config_dir = os.path.join(os.getenv("APPDATA"), "py-clash-bot")
config_file_path = os.path.join(config_dir, "config.pkl")

# Create the directory if it doesn't exist
if not os.path.exists(config_dir):
    os.makedirs(config_dir)


def save_configuration(values, keys_to_store, file_path):
    """Method to save the configuration to a file."""
    print("saving configuration")
    print('values',values)
    print('keys_to_store')
    for key in keys_to_store:
        print('\t',key)
    print('file_path',file_path)
    config = {}
    for key in keys_to_store:
        config[key] = values[key]
    with open(file_path, "wb") as file:
        pickle.dump(config, file)
    print(f"Configuration saved to {file_path}")


def load_configuration(window, file_path):
    """Method to load the configuration from a file and update the window.
    If the file does not exist, create an empty configuration file.
    """
    print("loading configuration")
    if os.path.exists(file_path):
        with open(file_path, "rb") as file:
            config = pickle.load(file)
        for key, value in config.items():
            print(key, value)
            if key in window.AllKeysDict:
                window[key].update(value)
        print(f"Configuration loaded from {file_path}")
    else:
        print(f"No configuration file found at {file_path}. Creating a new one.")
        # Create an empty configuration file
        with open(file_path, "wb") as file:
            pickle.dump({}, file)
        print(f"Empty configuration file created at {file_path}")


def save_current_settings(values):
    """Method to save the current settings to the configuration file."""
    save_configuration(values, user_config_keys, config_file_path)


def read_window(
    window: sg.Window, timeout: int = 10
) -> tuple[str, dict[str, str | int]]:
    """Method for reading the attributes of the window
    args:
        window: the window to read
        timeout: the timeout for the  read method

    returns:
        tuple of the event and the values of the window

    """

    # have a timeout so the output can be updated when no events are happening
    read_result = window.read(timeout=timeout)  # ms
    if read_result is None:
        print("Window not found")
        sys.exit()
    return read_result


def start_button_event(logger, window: Window, values) -> WorkerThread | None:
    # print window layout
    window["Stats"].select()
    logger.start_time = time.time()

    # make job dictionary
    job_dictionary: dict[str, str | int] = make_job_dict(values)

    logger.log("Start Button Event")
    logger.change_status(None, status="Starting the bot!")

    # close existing memuc processes
    close_memuc_processes()

    # setup the main thread and start it
    print("Starting main thread")
    thread_args = job_dictionary

    vm_indicies = get_vms(logger, 2)

    print(job_dictionary)

    close_everything_memu()

    if job_dictionary[1]["bot_toggle"] is True:
        vm_index = vm_indicies[0]
        logger.set_bot_vm_index(vm_index, 1)
        logger.add_vm_index(vm_index)
        logger.set_bot_account_order(job_dictionary[1]["account_order_1"], 1)
        thread_args = job_dictionary[1]
        thread = WorkerThread(logger, vm_index, thread_args)
        print("Initialized bot workerthread #1")
        thread.start()

    if job_dictionary[2]["bot_toggle"] is True:
        vm_index = vm_indicies[1]
        logger.set_bot_vm_index(vm_index, 2)
        logger.add_vm_index(vm_index)
        logger.set_bot_account_order(job_dictionary[2]["account_order_2"], 2)
        thread_args = job_dictionary[2]
        thread = WorkerThread(logger, vm_index, thread_args)
        print("Initialized bot workerthread #2")
        thread.start()

    # enable the stop button after the thread is started
    window["Stop"].update(disabled=False)


def stop_button_event(logger: Logger, window, thread: StoppableThread) -> None:
    """method for stopping the main bot thread
    args:
        logger, the logger object for for stats storage and printing
        window, the gui window
        thread: the main bot thread
    returns:
        None
    """
    logger.change_status(vm_index, status="Stopping")
    window["Stop"].update(disabled=True)
    thread.shutdown(kill=False)  # send the shutdown flag to the thread


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
            # update current status key to that of the correct display key
            window[stat].update(val)  # type: ignore


def exit_button_event(thread) -> None:
    """
    Method for handling the exit button event. Shuts down the thread if it is still running.

    Args:
        thread: The thread to be shut down.

    Returns:
        None
    """
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
        else:
            # reset the logger
            logger = Logger(timed=False)
            thread = None
    return thread, logger


def main_gui(start_on_run=False, settings: None | dict[str, str] = None) -> None:
    """method for displaying the main gui"""

    # create gui window
    window = make_window()

    # load the last cached settings
    load_configuration(window, config_file_path)

    # track worker thread and logger
    thread: WorkerThread | None = None
    logger = Logger(timed=True)

    # run the gui
    while True:
        event, values = read_window(window, timeout=10)

        if event != '__TIMEOUT__':
            print(event)

        if start_on_run:
            event = "Start"
            start_on_run = False

        # on exit event, kill any existing thread
        if event in [sg.WIN_CLOSED, "Exit"]:
            # shut down the thread if it is still running
            exit_button_event(thread)
            break

        # on start event, start the thread
        if event == "Start" or event == "start_key":
            start_button_event(logger, window, values)
            save_configuration(values, user_config_keys, config_file_path)

        # on stop event, stop the thread
        elif event == "Stop" and thread is not None:
            stop_button_event(logger, window, thread)


        # on Donate button event, open the donation link in browser
        elif event == "bug-report":
            webbrowser.open(
                "https://github.com/pyclashbot/py-clash-bot/issues/new/choose"
            )

        elif event == "upload-log":
            if logger is not None:
                url = logger.upload_log()
                if url is not None:
                    webbrowser.open(url)

        # refresh emulator button
        elif event == "refresh_emualtor_key":
            print("Deprecated")

        # donate event
        elif event in ("donate", "donate"):
            urls = {
                "https://github.com/sponsors/matthewmiglio?o=sd&sc=t",
                "https://www.paypal.com/donate/"
                "?business=YE72ZEB3KWGVY"
                "&no_recurring=0"
                "&item_name=Support+my+projects%21"
                "&currency_code=USD",
            }
            webbrowser.open(random.choice(list(urls)))

        # on Help button event, open the help gui
        elif event == "discord":
            webbrowser.open("https://discord.gg/eXdVuHuaZv")

        update_layout(window, logger)

    # shut down the thread if it is still running
    window.close()
    if thread is not None:
        thread.shutdown(kill=True)
        thread.join()


if __name__ == "__main__":
    cli_args = arg_parser()
    main_gui(start_on_run=cli_args.start)
