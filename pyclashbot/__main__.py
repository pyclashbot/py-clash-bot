"""Main entry point for the py-clash-bot ttkbootstrap interface."""

from __future__ import annotations

import os
from os.path import expandvars, join
from typing import Any, Callable, Optional

from pyclashbot.bot.worker import WorkerThread
from pyclashbot.interface.ui import PyClashBotUI, no_jobs_popup
from pyclashbot.utils.caching import USER_SETTINGS_CACHE
from pyclashbot.utils.cli_config import arg_parser
from pyclashbot.utils.logger import Logger, initalize_pylogging, log_dir
from pyclashbot.utils.thread import StoppableThread

initalize_pylogging()


def make_job_dictionary(values: dict[str, Any]) -> dict[str, Any]:
    """Create a dictionary of job toggles and increments based on UI values."""
    job_dictionary: dict[str, Any] = {
        "card_mastery_user_toggle": bool(values.get("card_mastery_user_toggle", False)),
        "classic_1v1_user_toggle": bool(values.get("classic_1v1_user_toggle", False)),
        "classic_2v2_user_toggle": bool(values.get("classic_2v2_user_toggle", False)),
        "trophy_road_user_toggle": bool(values.get("trophy_road_user_toggle", False)),
        "upgrade_user_toggle": bool(values.get("card_upgrade_user_toggle", False)),
        "random_decks_user_toggle": bool(values.get("random_decks_user_toggle", False)),
        "deck_number_selection": values.get("deck_number_selection", 2),
        "cycle_decks_user_toggle": bool(values.get("cycle_decks_user_toggle", False)),
        "max_deck_selection": values.get("max_deck_selection", 2),
        "random_plays_user_toggle": bool(values.get("random_plays_user_toggle", False)),
        "disable_win_track_toggle": bool(values.get("disable_win_track_toggle", False)),
        "record_fights_toggle": bool(values.get("record_fights_toggle", False)),
    }

    # MEmu render mode
    if values.get("directx_toggle"):
        job_dictionary["memu_render_mode"] = "directx"
    else:
        job_dictionary["memu_render_mode"] = "opengl"

    # BlueStacks render mode selection
    if values.get("bs_renderer_dx"):
        job_dictionary["bluestacks_render_mode"] = "dx"
    elif values.get("bs_renderer_vk"):
        job_dictionary["bluestacks_render_mode"] = "vlcn"
    else:
        job_dictionary["bluestacks_render_mode"] = "gl"

    # Emulator selection
    if values.get("google_play_emulator_toggle"):
        job_dictionary["emulator"] = "Google Play"
    elif values.get("bluestacks_emulator_toggle"):
        job_dictionary["emulator"] = "BlueStacks 5"
    else:
        job_dictionary["emulator"] = "MEmu"

    return job_dictionary


def has_no_jobs_selected(job_dict: dict[str, Any]) -> bool:
    """Check if no jobs are selected in the job dictionary."""
    job_keys = [
        "card_mastery_user_toggle",
        "classic_1v1_user_toggle",
        "classic_2v2_user_toggle",
        "trophy_road_user_toggle",
        "upgrade_user_toggle",
    ]
    return not any(job_dict.get(key, False) for key in job_keys)


def save_current_settings(values: dict[str, Any]) -> None:
    """Cache the user's current settings."""
    USER_SETTINGS_CACHE.cache_data(values)


def load_settings(settings: Optional[dict[str, Any]], ui: PyClashBotUI) -> Optional[dict[str, Any]]:
    """Load settings into the UI from CLI args or cached data."""
    loaded = settings
    if not loaded and USER_SETTINGS_CACHE.exists():
        loaded = USER_SETTINGS_CACHE.load_data()
    if loaded:
        ui.set_all_values(loaded)
    return loaded


def start_button_event(logger: Logger, ui: PyClashBotUI, values: dict[str, Any]) -> Optional[WorkerThread]:
    """Start the worker thread with the current configuration."""
    job_dictionary = make_job_dictionary(values)

    if has_no_jobs_selected(job_dictionary):
        no_jobs_popup()
        logger.log("No jobs are selected!")
        return None

    logger.log("Start Button Event")
    logger.change_status("Starting the bot!")
    save_current_settings(values)
    logger.log_job_dictionary(job_dictionary)

    ui.set_running_state(True)
    ui.notebook.select(ui.stats_tab)

    thread = WorkerThread(logger, job_dictionary)
    thread.start()
    return thread


def stop_button_event(logger: Logger, ui: PyClashBotUI, thread: StoppableThread) -> None:
    """Stop the worker thread."""
    logger.change_status("Stopping")
    ui.stop_btn.configure(state="disabled")
    thread.shutdown(kill=False)


def update_layout(ui: PyClashBotUI, logger: Logger) -> None:
    """Update UI widgets from the logger's statistics."""
    stats = logger.get_stats()
    ui.update_stats(stats)
    status_text = logger.current_status
    if stats and "current_status" in stats:
        status_text = str(stats["current_status"])
    ui.set_status(status_text)
    ui.append_log(status_text)


def exit_button_event(thread: Optional[StoppableThread]) -> None:
    if thread is not None:
        thread.shutdown(kill=True)


def handle_thread_finished(
    ui: PyClashBotUI,
    thread: Optional[WorkerThread],
    logger: Logger,
) -> tuple[Optional[WorkerThread], Logger]:
    if thread is not None and not thread.is_alive():
        ui.set_running_state(False)
        if getattr(thread.logger, "errored", False):
            logger = thread.logger
        else:
            logger = Logger(timed=False)
            thread = None
    return thread, logger


def open_recordings_folder() -> None:
    folder_path = join(expandvars("%localappdata%"), "programs", "py-clash-bot", "recordings")
    os.makedirs(folder_path, exist_ok=True)
    try:
        os.startfile(folder_path)
    except AttributeError:
        # Non-Windows fallback
        import subprocess

        subprocess.Popen(["xdg-open", folder_path])


def open_logs_folder() -> None:
    folder_path = log_dir
    os.makedirs(folder_path, exist_ok=True)
    try:
        os.startfile(folder_path)
    except AttributeError:
        import subprocess

        subprocess.Popen(["xdg-open", folder_path])

class BotApplication:
    """Main application class for the ttkbootstrap GUI."""

    def __init__(self, settings: Optional[dict[str, Any]] = None) -> None:
        self.ui = PyClashBotUI()
        self.ui.start_btn.configure(command=self._on_start)
        self.ui.stop_btn.configure(command=self._on_stop)
        self.ui.register_config_callback(self._on_config_change)
        self.ui.register_open_recordings_callback(self._on_open_recordings_clicked)
        self.ui.register_open_logs_callback(self._on_open_logs_clicked)
        self.ui.protocol("WM_DELETE_WINDOW", self._on_close)

        self.thread: Optional[WorkerThread] = None
        self.logger = Logger(timed=False)
        self._closing = False
        self._suppress_persist = True
        self.current_values = self.ui.get_all_values()

        loaded = load_settings(settings, self.ui)
        if loaded:
            self.current_values = self.ui.get_all_values()
        self._suppress_persist = False

        self.ui.set_running_state(False)
        self._poll()

    def _on_start(self) -> None:
        if self.thread is not None and self.thread.is_alive():
            return
        values = self.ui.get_all_values()
        new_logger = Logger(timed=True)
        thread = start_button_event(new_logger, self.ui, values)
        if thread is not None:
            self.logger = new_logger
            self.thread = thread
            self.current_values = values.copy()
        else:
            self.ui.set_running_state(False)

    def _on_stop(self) -> None:
        if self.thread is not None:
            stop_button_event(self.logger, self.ui, self.thread)

    def _on_config_change(self, values: dict[str, Any]) -> None:
        changed = {key for key, value in values.items() if self.current_values.get(key) != value}
        if values.get("random_decks_user_toggle") and values.get("cycle_decks_user_toggle"):
            if "random_decks_user_toggle" in changed:
                self.ui.set_all_values({"cycle_decks_user_toggle": False})
                values["cycle_decks_user_toggle"] = False
            elif "cycle_decks_user_toggle" in changed:
                self.ui.set_all_values({"random_decks_user_toggle": False})
                values["random_decks_user_toggle"] = False
            else:
                self.ui.set_all_values({"cycle_decks_user_toggle": False})
                values["cycle_decks_user_toggle"] = False
        self.current_values = values.copy()
        if not self._suppress_persist:
            save_current_settings(values)

    def _dispatch_action(self) -> None:
        callback: Optional[Callable[[], None]] = getattr(self.logger, "action_callback", None)
        if callable(callback):
            try:
                callback()
            except Exception as exc:  # noqa: BLE001
                self.logger.log(f"Error executing action callback: {exc}")
        if hasattr(self.logger, "action_needed"):
            self.logger.action_needed = False
            self.logger.action_callback = None
            self.logger.action_text = "Continue"
        self.ui.hide_action_button()

    def _poll(self) -> None:
        if self._closing:
            return
        self.thread, self.logger = handle_thread_finished(self.ui, self.thread, self.logger)
        update_layout(self.ui, self.logger)
        if hasattr(self.logger, "action_needed") and self.logger.action_needed:
            action_text = getattr(self.logger, "action_text", "Continue")
            self.ui.show_action_button(action_text, self._dispatch_action)
        else:
            self.ui.hide_action_button()
        self.ui.after(100, self._poll)

    def _on_open_recordings_clicked(self) -> None:
        open_recordings_folder()

    def _on_open_logs_clicked(self) -> None:
        open_logs_folder()

    def _on_close(self) -> None:
        self._closing = True
        exit_button_event(self.thread)
        self.ui.destroy()

    def run(self, start_on_run: bool = False) -> None:
        if start_on_run:
            self.ui.after(200, self._on_start)
        self.ui.mainloop()

def main_gui(start_on_run: bool = False, settings: Optional[dict[str, Any]] = None) -> None:
    app = BotApplication(settings)
    app.run(start_on_run)


if __name__ == "__main__":
    cli_args = arg_parser()
    main_gui(start_on_run=cli_args.start)
