"""This module contains the main entry point for the py-clash-bot program.
It provides a GUI interface for users to configure and run the bot.
"""

import sys
import webbrowser

import FreeSimpleGUI as sg  # noqa: N813
from FreeSimpleGUI import Window

from pyclashbot.bot.worker import WorkerThread
from pyclashbot.interface import disable_keys, user_config_keys
from pyclashbot.interface.layout import create_window, no_jobs_popup
from pyclashbot.utils.caching import USER_SETTINGS_CACHE
from pyclashbot.utils.cli_config import arg_parser
from pyclashbot.utils.logger import Logger, initalize_pylogging
from pyclashbot.utils.thread import StoppableThread

initalize_pylogging()


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
    """Create a dictionary of job toggles and increments based on the values of the GUI window."""
    jobs_dictionary: dict[str, str | int] = {
        "card_mastery_user_toggle": values["card_mastery_user_toggle"],
        "classic_1v1_user_toggle": values["classic_1v1_user_toggle"],
        "classic_2v2_user_toggle": values["classic_2v2_user_toggle"],
        "trophy_road_user_toggle": values["trophy_road_user_toggle"],
        "upgrade_user_toggle": values["card_upgrade_user_toggle"],
        "random_decks_user_toggle": values["random_decks_user_toggle"],
        "deck_number_selection": values["deck_number_selection"],
        "cycle_decks_user_toggle": values["cycle_decks_user_toggle"],
        "max_deck_selection": values["max_deck_selection"],
        "random_plays_user_toggle": values["random_plays_user_toggle"],
        "disable_win_track_toggle": values["disable_win_track_toggle"],
        "record_fights_toggle": values.get("record_fights_toggle", False),
    }

    # Set render mode based on toggle
    if values.get("directx_toggle"):
        jobs_dictionary["memu_render_mode"] = "directx"
    else:
        jobs_dictionary["memu_render_mode"] = "opengl"

    # BlueStacks render mode selection
    if values.get("bs_renderer_dx"):
        jobs_dictionary["bluestacks_render_mode"] = "dx"
    elif values.get("bs_renderer_vk"):
        jobs_dictionary["bluestacks_render_mode"] = "vlcn"
    else:
        jobs_dictionary["bluestacks_render_mode"] = "gl"

    # Set emulator based on toggle
    if values.get("google_play_emulator_toggle"):
        jobs_dictionary["emulator"] = "Google Play"
    elif values.get("bluestacks_emulator_toggle"):
        jobs_dictionary["emulator"] = "BlueStacks 5"
    else:
        jobs_dictionary["emulator"] = "MEmu"

    return jobs_dictionary


def has_no_jobs_selected(job_dict) -> bool:
    """Check if no jobs are selected in the job dictionary."""
    job_keys = [
        "card_mastery_user_toggle",
        "classic_1v1_user_toggle",
        "classic_2v2_user_toggle",
        "trophy_road_user_toggle",
        "upgrade_user_toggle",
    ]
    return not any(job_dict.get(key, False) for key in job_keys)


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


def start_button_event(logger: Logger, window: Window, values) -> WorkerThread | None:
    """Start the main bot thread with the given configuration."""
    job_dictionary = make_job_dictionary(values)

    if has_no_jobs_selected(job_dictionary):
        no_jobs_popup()
        logger.log("No jobs are selected!")
        return None

    logger.log("Start Button Event")
    logger.change_status(status="Starting the bot!")
    save_current_settings(values)
    logger.log_job_dictionary(job_dictionary)

    # Disable UI controls
    for key in disable_keys:
        if key in window.key_dict:
            element = window[key]
            if element is not None:
                element.update(disabled=True)

    # Start worker thread
    thread = WorkerThread(logger, job_dictionary)
    thread.start()

    # Update UI state
    stop_button = window["Stop"]
    if stop_button is not None:
        stop_button.update(disabled=False)

    main_tabs = window["-MAIN_TABS-"]
    if main_tabs is not None:
        main_tabs.Widget.select(2)  # Focus stats tab

    return thread


def stop_button_event(logger: Logger, window, thread: StoppableThread) -> None:
    """Stop the main bot thread."""
    logger.change_status(status="Stopping")
    stop_button = window["Stop"]
    if stop_button is not None:
        stop_button.update(disabled=True)
    thread.shutdown(kill=False)


def update_layout(window: sg.Window, logger: Logger) -> None:
    """Update the GUI window with current stats and time."""
    time_element = window["time_since_start"]
    if time_element is not None:
        time_element.update(logger.calc_time_since_start())

    stats = logger.get_stats()
    if stats:
        for stat, val in stats.items():
            element = window[stat]
            if element is not None:
                element.update(val)

    # Handle action button visibility and text
    action_button = window["action_button"]
    if action_button is not None:
        if hasattr(logger, "action_needed") and logger.action_needed:
            action_text = getattr(logger, "action_text", "Continue")
            action_button.update(text=action_text, visible=True)
        else:
            action_button.update(visible=False)


def exit_button_event(thread) -> None:
    """Shut down the thread if it is still running."""
    if thread is not None:
        thread.shutdown(kill=True)


def handle_thread_finished(
    window: sg.Window,
    thread: WorkerThread | None,
    logger: Logger,
):
    """Handle cleanup when the worker thread is finished."""
    if thread is not None and not thread.is_alive():
        # Re-enable UI controls
        for key in disable_keys:
            element = window[key]
            if element is not None:
                element.update(disabled=False)

        if thread.logger.errored:
            stop_button = window["Stop"]
            if stop_button is not None:
                stop_button.update(disabled=True)
        else:
            logger = Logger(timed=False)
            thread = None
    return thread, logger


class BotApplication:
    """Main application class for the PyClashBot GUI."""

    def __init__(self, settings: dict[str, str] | None = None):
        self.window = create_window()
        self.thread: WorkerThread | None = None
        self.logger = Logger(timed=False)
        load_settings(settings, self.window)

    def handle_start_event(self, values):
        """Handle the start button event."""
        self.logger = Logger(timed=True)
        self.thread = start_button_event(self.logger, self.window, values)

    def handle_stop_event(self):
        """Handle the stop button event."""
        if self.thread is not None:
            stop_button_event(self.logger, self.window, self.thread)

    def handle_settings_change(self, values):
        """Handle settings changes."""
        save_current_settings(values)

    def handle_external_links(self, event):
        """Handle opening external links."""
        if event == "bug-report":
            webbrowser.open("https://github.com/pyclashbot/py-clash-bot/issues/new/choose")
        elif event == "discord":
            webbrowser.open("https://discord.gg/eXdVuHuaZv")

    def handle_action_button(self):
        """Handle action button click - call the logger's callback function"""
        if hasattr(self.logger, "action_callback") and self.logger.action_callback:
            try:
                # Call the callback function
                self.logger.action_callback()
            except Exception as e:
                print(f"Error calling action callback: {e}")
                self.logger.log(f"Error executing action callback: {e}")

        # Clear action state after executing
        if hasattr(self.logger, "action_needed"):
            self.logger.action_needed = False
            self.logger.action_callback = None

    def cleanup(self):
        """Clean up resources when closing."""
        self.window.close()
        if self.thread is not None:
            self.thread.shutdown(kill=True)
            self.thread.join()

    def run(self, start_on_run=False) -> None:
        """Run the main GUI event loop."""
        while True:
            event, values = read_window(self.window, timeout=10)

            if start_on_run:
                event = "Start"
                start_on_run = False

            if event in [sg.WIN_CLOSED, "Exit"]:
                exit_button_event(self.thread)
                break
            elif event == "Start":
                self.handle_start_event(values)
            elif event == "Stop":
                self.handle_stop_event()
            elif event == "random_decks_user_toggle":
                if values["random_decks_user_toggle"]:
                    self.window["cycle_decks_user_toggle"].update(False)
                self.handle_settings_change(values)
            elif event == "cycle_decks_user_toggle":
                if values["cycle_decks_user_toggle"]:
                    self.window["random_decks_user_toggle"].update(False)
                self.handle_settings_change(values)
            elif event in user_config_keys:
                self.handle_settings_change(values)
            elif event in ["bug-report", "discord"]:
                self.handle_external_links(event)
            elif event == "action_button":
                self.handle_action_button()

            # Handle thread completion cleanup
            self.thread, self.logger = handle_thread_finished(self.window, self.thread, self.logger)

            update_layout(self.window, self.logger)

        self.cleanup()


def main_gui(start_on_run=False, settings: None | dict[str, str] = None) -> None:
    """Main entry point for the GUI application."""
    app = BotApplication(settings)
    app.run(start_on_run)


if __name__ == "__main__":
    cli_args = arg_parser()
    main_gui(start_on_run=cli_args.start)
