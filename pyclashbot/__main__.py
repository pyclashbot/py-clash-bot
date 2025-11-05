"""Main entry point for the py-clash-bot ttkbootstrap interface."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable
from os.path import expandvars, join
from typing import Any

from pyclashbot.bot.worker import WorkerThread
from pyclashbot.interface.enums import PRIMARY_JOB_TOGGLES, UIField
from pyclashbot.interface.ui import PyClashBotUI, no_jobs_popup
from pyclashbot.utils.caching import USER_SETTINGS_CACHE
from pyclashbot.utils.cli_config import arg_parser
from pyclashbot.utils.logger import Logger, initalize_pylogging, log_dir
from pyclashbot.utils.thread import StoppableThread

initalize_pylogging()


def make_job_dictionary(values: dict[str, Any]) -> dict[str, Any]:
    """Create a dictionary of job toggles and increments based on UI values."""

    def as_bool(field: UIField) -> bool:
        return bool(values.get(field.value, False))

    def as_int(field: UIField, default: int) -> int:
        try:
            return int(values.get(field.value, default))
        except (TypeError, ValueError):
            return default

    job_dictionary: dict[str, Any] = {
        UIField.CARD_MASTERY_USER_TOGGLE.value: as_bool(UIField.CARD_MASTERY_USER_TOGGLE),
        UIField.CLASSIC_1V1_USER_TOGGLE.value: as_bool(UIField.CLASSIC_1V1_USER_TOGGLE),
        UIField.CLASSIC_2V2_USER_TOGGLE.value: as_bool(UIField.CLASSIC_2V2_USER_TOGGLE),
        UIField.TROPHY_ROAD_USER_TOGGLE.value: as_bool(UIField.TROPHY_ROAD_USER_TOGGLE),
        UIField.RANDOM_DECKS_USER_TOGGLE.value: as_bool(UIField.RANDOM_DECKS_USER_TOGGLE),
        UIField.DECK_NUMBER_SELECTION.value: as_int(UIField.DECK_NUMBER_SELECTION, 2),
        UIField.CYCLE_DECKS_USER_TOGGLE.value: as_bool(UIField.CYCLE_DECKS_USER_TOGGLE),
        UIField.MAX_DECK_SELECTION.value: as_int(UIField.MAX_DECK_SELECTION, 2),
        UIField.RANDOM_PLAYS_USER_TOGGLE.value: as_bool(UIField.RANDOM_PLAYS_USER_TOGGLE),
        UIField.DISABLE_WIN_TRACK_TOGGLE.value: as_bool(UIField.DISABLE_WIN_TRACK_TOGGLE),
        UIField.RECORD_FIGHTS_TOGGLE.value: as_bool(UIField.RECORD_FIGHTS_TOGGLE),
    }

    job_dictionary["upgrade_user_toggle"] = as_bool(UIField.CARD_UPGRADE_USER_TOGGLE)

    # MEmu render mode
    if values.get(UIField.DIRECTX_TOGGLE.value):
        job_dictionary["memu_render_mode"] = "directx"
    else:
        job_dictionary["memu_render_mode"] = "opengl"

    # BlueStacks render mode selection
    if values.get(UIField.BS_RENDERER_DX.value):
        job_dictionary["bluestacks_render_mode"] = "dx"
    elif values.get(UIField.BS_RENDERER_VK.value):
        job_dictionary["bluestacks_render_mode"] = "vlcn"
    else:
        job_dictionary["bluestacks_render_mode"] = "gl"

    # Emulator selection
    if values.get(UIField.GOOGLE_PLAY_EMULATOR_TOGGLE.value):
        job_dictionary["emulator"] = "Google Play"
    elif values.get(UIField.BLUESTACKS_EMULATOR_TOGGLE.value):
        job_dictionary["emulator"] = "BlueStacks 5"
    else:
        job_dictionary["emulator"] = "MEmu"

    return job_dictionary


def has_no_jobs_selected(job_dict: dict[str, Any]) -> bool:
    """Check if no jobs are selected in the job dictionary."""
    return not any(job_dict.get(field.value, False) for field in PRIMARY_JOB_TOGGLES)


def save_current_settings(values: dict[str, Any]) -> None:
    """Cache the user's current settings."""
    USER_SETTINGS_CACHE.cache_data(values)


def load_settings(settings: dict[str, Any] | None, ui: PyClashBotUI) -> dict[str, Any] | None:
    """Load settings into the UI from CLI args or cached data."""
    loaded = settings
    if not loaded and USER_SETTINGS_CACHE.exists():
        loaded = USER_SETTINGS_CACHE.load_data()
    if loaded:
        ui.set_all_values(loaded)
    return loaded


def start_button_event(logger: Logger, ui: PyClashBotUI, values: dict[str, Any]) -> WorkerThread | None:
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


def exit_button_event(thread: StoppableThread | None) -> None:
    if thread is not None:
        thread.shutdown(kill=True)


def handle_thread_finished(
    ui: PyClashBotUI,
    thread: WorkerThread | None,
    logger: Logger,
) -> tuple[WorkerThread | None, Logger]:
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

    def __init__(self, settings: dict[str, Any] | None = None) -> None:
        self.ui = PyClashBotUI()
        self.ui.register_start_callback(self._on_start)
        self.ui.register_stop_callback(self._on_stop)
        self.ui.register_config_callback(self._on_config_change)
        self.ui.register_open_recordings_callback(self._on_open_recordings_clicked)
        self.ui.register_open_logs_callback(self._on_open_logs_clicked)
        self.ui.register_switch_to_web_ui_callback(self._on_switch_to_web_ui)
        self.ui.protocol("WM_DELETE_WINDOW", self._on_close)

        self.thread: WorkerThread | None = None
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
        random_toggle = UIField.RANDOM_DECKS_USER_TOGGLE.value
        cycle_toggle = UIField.CYCLE_DECKS_USER_TOGGLE.value
        if values.get(random_toggle) and values.get(cycle_toggle):
            if random_toggle in changed:
                self.ui.set_all_values({cycle_toggle: False})
                values[cycle_toggle] = False
            elif cycle_toggle in changed:
                self.ui.set_all_values({random_toggle: False})
                values[random_toggle] = False
            else:
                self.ui.set_all_values({cycle_toggle: False})
                values[cycle_toggle] = False
        self.current_values = values.copy()
        if not self._suppress_persist:
            save_current_settings(values)

    def _dispatch_action(self) -> None:
        callback: Callable[[], None] | None = getattr(self.logger, "action_callback", None)
        if callable(callback):
            try:
                callback()
            except Exception as exc:
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

    def _on_switch_to_web_ui(self) -> None:
        """Switch to web UI: save settings, close tkinter UI, and spawn webview UI process."""
        # Save current settings first
        values = self.ui.get_all_values()
        values["ui_mode"] = "web"
        save_current_settings(values)

        # Stop any running thread
        if self.thread is not None:
            exit_button_event(self.thread)

        # Launch webview UI in a separate process to avoid GUI mainloop conflicts
        try:
            subprocess.Popen([sys.executable, "-m", "pyclashbot.web_main"], close_fds=False)
        except Exception:
            # Fallback: run in-process if subprocess fails
            from pyclashbot.interface.webview_app import run_webview

            run_webview()

        # Close the tkinter window
        self._closing = True
        try:
            self.ui.quit()
        except Exception:
            pass
        self.ui.destroy()

    def _on_close(self) -> None:
        self._closing = True
        exit_button_event(self.thread)
        self.ui.destroy()

    def run(self, start_on_run: bool = False) -> None:
        if start_on_run:
            self.ui.after(200, self._on_start)
        self.ui.mainloop()


def main_gui(start_on_run: bool = False, settings: dict[str, Any] | None = None) -> None:
    app = BotApplication(settings)
    app.run(start_on_run)


if __name__ == "__main__":
    cli_args = arg_parser()

    # Determine UI mode: CLI argument > cached setting > default (web)
    ui_mode = cli_args.ui
    if ui_mode is None:
        # Check cached settings
        if USER_SETTINGS_CACHE.exists():
            cached_settings = USER_SETTINGS_CACHE.load_data()
            ui_mode = cached_settings.get("ui_mode", "web")
        else:
            ui_mode = "web"

    # Launch appropriate UI
    if ui_mode == "regular":
        main_gui(start_on_run=cli_args.start)
    else:
        # Default to web UI
        from pyclashbot.interface.webview_app import run_webview

        run_webview()
