"""Main entry point for the py-clash-bot ttkbootstrap interface."""

from __future__ import annotations

import locale
import logging
import multiprocessing as mp
import shlex
from multiprocessing import Queue
from os.path import expandvars, join
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable
    from multiprocessing.synchronize import Event

_original_setlocale = locale.setlocale
_LocaleError = locale.Error


# Parameter name must match the stdlib's (callers may pass locale= by keyword);
# it shadows the locale module inside the body, hence the module-level aliases.
def _setlocale_safe(category: int, locale: str | Iterable[str | None] | None = None) -> str:
    """Fallback to the C locale if the requested locale is unsupported."""
    try:
        return _original_setlocale(category, locale)
    except _LocaleError:
        return _original_setlocale(category, "C")


# Deliberate monkeypatch; ty rejects reassigning a module-level function even with
# a matching signature, so suppress rather than launder the type.
locale.setlocale = _setlocale_safe  # ty: ignore[invalid-assignment]

try:
    # Force a portable locale so ttkbootstrap does not raise unsupported locale errors on non-English systems.
    locale.setlocale(locale.LC_ALL, "C")
except locale.Error:
    # If even the C locale is unavailable, continue with the default to avoid crashing on import.
    pass

from pyclashbot.bot.worker import WorkerProcess
from pyclashbot.emulators import EmulatorType
from pyclashbot.emulators.adb import AdbController
from pyclashbot.emulators.adb_base import validate_device_serial
from pyclashbot.emulators.bluestacks import BlueStacksEmulatorController
from pyclashbot.emulators.google_play import GooglePlayEmulatorController
from pyclashbot.interface.enums import UIField, has_start_ready_job
from pyclashbot.interface.ui import PyClashBotUI, no_jobs_popup
from pyclashbot.utils.caching import USER_SETTINGS_CACHE
from pyclashbot.utils.cli_config import arg_parser
from pyclashbot.utils.discord_rpc import DiscordRPCManager
from pyclashbot.utils.logger import Logger, initialize_pylogging, log_dir, log_name
from pyclashbot.utils.open_folder import open_folder
from pyclashbot.utils.platform import is_macos
from pyclashbot.utils.subprocess import run as run_command

initialize_pylogging()


def migrate_clan_job_settings(values: dict[str, Any]) -> None:
    """Map legacy clan settings to per-action toggles."""
    clan_actions = (
        UIField.CLAN_DONATE_USER_TOGGLE,
        UIField.CLAN_CLAIM_GIFTS_USER_TOGGLE,
        UIField.CLAN_REQUEST_CARDS_USER_TOGGLE,
    )
    if values.get(UIField.CLAN_CHAT_USER_TOGGLE.value) and not any(values.get(field.value) for field in clan_actions):
        for field in clan_actions:
            values[field.value] = True


_CLAN_ACTION_TOGGLES = (
    UIField.CLAN_DONATE_USER_TOGGLE,
    UIField.CLAN_CLAIM_GIFTS_USER_TOGGLE,
    UIField.CLAN_REQUEST_CARDS_USER_TOGGLE,
)


def make_job_dictionary(values: dict[str, Any]) -> dict[str, Any]:
    """Create a dictionary of job toggles and increments based on UI values."""
    migrate_clan_job_settings(values)

    def as_bool(field: UIField) -> bool:
        return bool(values.get(field.value, False))

    def as_int(field: UIField, default: int) -> int:
        try:
            return int(values.get(field.value, default))
        except (TypeError, ValueError):
            return default

    job_dictionary: dict[str, Any] = {
        UIField.CARD_MASTERY_USER_TOGGLE.value: as_bool(UIField.CARD_MASTERY_USER_TOGGLE),
        UIField.SHOP_DAILY_OFFER_USER_TOGGLE.value: as_bool(UIField.SHOP_DAILY_OFFER_USER_TOGGLE),
        UIField.CLASSIC_1V1_USER_TOGGLE.value: as_bool(UIField.CLASSIC_1V1_USER_TOGGLE),
        UIField.CLASSIC_2V2_USER_TOGGLE.value: as_bool(UIField.CLASSIC_2V2_USER_TOGGLE),
        UIField.TROPHY_ROAD_USER_TOGGLE.value: as_bool(UIField.TROPHY_ROAD_USER_TOGGLE),
        UIField.RANDOM_DECKS_USER_TOGGLE.value: as_bool(UIField.RANDOM_DECKS_USER_TOGGLE),
        UIField.DECK_NUMBER_SELECTION.value: as_int(UIField.DECK_NUMBER_SELECTION, 2),
        UIField.CYCLE_DECKS_USER_TOGGLE.value: as_bool(UIField.CYCLE_DECKS_USER_TOGGLE),
        UIField.MAX_DECK_SELECTION.value: as_int(UIField.MAX_DECK_SELECTION, 2),
        UIField.SWITCH_ACCOUNTS_USER_TOGGLE.value: as_bool(UIField.SWITCH_ACCOUNTS_USER_TOGGLE),
        UIField.MAX_ACCOUNT_SELECTION.value: as_int(UIField.MAX_ACCOUNT_SELECTION, 2),
        UIField.CLAN_DONATE_USER_TOGGLE.value: as_bool(UIField.CLAN_DONATE_USER_TOGGLE),
        UIField.CLAN_CLAIM_GIFTS_USER_TOGGLE.value: as_bool(UIField.CLAN_CLAIM_GIFTS_USER_TOGGLE),
        UIField.CLAN_REQUEST_CARDS_USER_TOGGLE.value: as_bool(UIField.CLAN_REQUEST_CARDS_USER_TOGGLE),
        UIField.CLAN_CHAT_USER_TOGGLE.value: any(as_bool(field) for field in _CLAN_ACTION_TOGGLES),
        UIField.WAR_USER_TOGGLE.value: as_bool(UIField.WAR_USER_TOGGLE),
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
    elif values.get(UIField.BS_RENDERER_GL.value):
        job_dictionary["bluestacks_render_mode"] = "gl"
    else:
        # Default: Vulkan on macOS, OpenGL on Windows
        job_dictionary["bluestacks_render_mode"] = "vlcn" if is_macos() else "gl"

    # Emulator selection
    if values.get(UIField.GOOGLE_PLAY_EMULATOR_TOGGLE.value):
        job_dictionary["emulator"] = EmulatorType.GOOGLE_PLAY
    elif values.get(UIField.BLUESTACKS_EMULATOR_TOGGLE.value):
        job_dictionary["emulator"] = EmulatorType.BLUESTACKS
    elif values.get(UIField.ADB_TOGGLE.value):
        job_dictionary["emulator"] = EmulatorType.ADB
    else:
        job_dictionary["emulator"] = EmulatorType.MEMU

    adb_serial = values.get(UIField.ADB_SERIAL.value)
    job_dictionary[UIField.ADB_SERIAL.value] = adb_serial.strip() if adb_serial else None

    gp_serial = values.get(UIField.GP_DEVICE_SERIAL.value)
    job_dictionary[UIField.GP_DEVICE_SERIAL.value] = gp_serial.strip() if gp_serial else None

    bs_serial = values.get(UIField.BS_DEVICE_SERIAL.value)
    job_dictionary[UIField.BS_DEVICE_SERIAL.value] = bs_serial.strip() if bs_serial else None

    return job_dictionary


def has_no_jobs_selected(job_dict: dict[str, Any]) -> bool:
    """Check if no start-ready jobs are selected."""
    return not has_start_ready_job(job_dict)


def save_current_settings(values: dict[str, Any]) -> None:
    """Cache the user's current settings."""
    USER_SETTINGS_CACHE.cache_data(values)


def load_settings(settings: dict[str, Any] | None, ui: PyClashBotUI) -> dict[str, Any] | None:
    """Load settings into the UI from CLI args or cached data."""
    loaded = settings
    if not loaded and USER_SETTINGS_CACHE.exists():
        loaded = USER_SETTINGS_CACHE.load_data()
    if loaded:
        migrate_clan_job_settings(loaded)
        ui.set_all_values(loaded)
    return loaded


def start_button_event(
    logger: Logger,
    ui: PyClashBotUI,
    values: dict[str, Any],
    stats_queue: Queue,
    shutdown_event: Event,
) -> WorkerProcess | None:
    """Start the worker process with the current configuration."""
    job_dictionary = make_job_dictionary(values)

    if has_no_jobs_selected(job_dictionary):
        no_jobs_popup()
        logger.log("No jobs are selected!")
        return None

    # ADB - serial required
    if job_dictionary.get("emulator") == EmulatorType.ADB:
        device_serial = job_dictionary.get(UIField.ADB_SERIAL.value)
        if not device_serial or not AdbController.is_device_connected(device_serial):
            logger.change_status(f"Start cancelled: ADB device '{device_serial}' not connected.")
            return None

    # Google Play - serial optional; validate format only, worker boots and connects.
    if job_dictionary.get("emulator") == EmulatorType.GOOGLE_PLAY:
        device_serial = job_dictionary.get(UIField.GP_DEVICE_SERIAL.value)
        if device_serial and not validate_device_serial(device_serial):
            logger.change_status(f"Start cancelled: invalid device serial '{device_serial}'.")
            return None

    # BlueStacks - serial optional; validate format only, worker boots and connects.
    if job_dictionary.get("emulator") == EmulatorType.BLUESTACKS:
        device_serial = job_dictionary.get(UIField.BS_DEVICE_SERIAL.value)
        if device_serial and not validate_device_serial(device_serial):
            logger.change_status(f"Start cancelled: invalid device serial '{device_serial}'.")
            return None

    logger.log("Start Button Event")
    logger.change_status("Starting the bot!")
    save_current_settings(values)
    logger.log_job_dictionary(job_dictionary)

    ui.notebook.select(ui.stats_tab)

    process = WorkerProcess(job_dictionary, stats_queue, shutdown_event, log_name)
    process.start()
    return process


def stop_button_event(logger: Logger, shutdown_event: Event) -> None:
    """Signal the worker process to stop gracefully."""
    logger.change_status("Stopping")
    shutdown_event.set()


def update_layout(
    ui: PyClashBotUI,
    logger: Logger,
    stats: dict[str, Any] | None = None,
) -> None:
    """Update UI widgets from the logger's statistics."""
    if stats is None:
        stats = logger.get_stats()
    if stats is None:
        return
    ui.update_stats(stats)
    status_text = logger.current_status
    if "current_status" in stats:
        status_text = str(stats["current_status"])
    ui.set_status(status_text)
    if ui.get_button_state() == "idle" and not ui.can_start():
        return
    ui.append_log(status_text)


def exit_button_event(process: WorkerProcess | None, shutdown_event: Event | None) -> None:
    """Force stop the worker process on application exit."""
    if shutdown_event is not None:
        shutdown_event.set()
    if process is not None and process.is_alive():
        process.terminate()
        process.join(timeout=1)
        if process.is_alive():
            process.kill()


def handle_process_finished(
    ui: PyClashBotUI,
    process: WorkerProcess | None,
    logger: Logger,
) -> tuple[WorkerProcess | None, Logger]:
    """Check if the worker process has finished and reset UI state if so."""
    if process is not None and not process.is_alive():
        ui.set_button_state("idle")
        logger = Logger(timed=False)
        logger.change_status("Idle")
        process = None
    return process, logger


def open_recordings_folder() -> None:
    folder_path = join(expandvars("%localappdata%"), "programs", "py-clash-bot", "recordings")
    open_folder(folder_path)


def open_logs_folder() -> None:
    folder_path = log_dir
    open_folder(folder_path)


class BotApplication:
    """Main application class for the ttkbootstrap GUI."""

    def __init__(self, settings: dict[str, Any] | None = None) -> None:
        self.ui = PyClashBotUI()
        self.ui.main_btn.configure(command=self._on_main_button)
        self.ui.register_config_callback(self._on_config_change)
        self.ui.register_open_logs_callback(self._on_open_logs_clicked)
        self.ui.protocol("WM_DELETE_WINDOW", self._on_close)
        self.ui.adb_refresh_btn.configure(command=self._on_adb_refresh)
        self.ui.adb_connect_btn.configure(command=self._on_adb_connect)
        self.ui.adb_restart_btn.configure(command=self._on_adb_restart)
        self.ui.adb_set_size_btn.configure(command=self._on_adb_set_size)
        self.ui.adb_reset_size_btn.configure(command=self._on_adb_reset_size)
        # Auto-refresh device lists when dropdown opens
        self.ui.gp_device_serial_combo.configure(postcommand=self._refresh_gp_devices)
        self.ui.bs_device_serial_combo.configure(postcommand=self._refresh_bs_devices)

        # Multiprocessing primitives
        self.process: WorkerProcess | None = None
        self.stats_queue: Queue | None = None
        self.shutdown_event: Event | None = None
        self.last_stats: dict[str, Any] = {}

        self.logger = Logger(timed=False)
        self.discord_rpc = DiscordRPCManager()
        self.discord_rpc_enabled = False
        self._closing = False
        self._suppress_persist = True
        self.current_values = self.ui.get_all_values()

        loaded = load_settings(settings, self.ui)
        if loaded:
            self.current_values = self.ui.get_all_values()
            self.discord_rpc_enabled = bool(self.current_values.get(UIField.DISCORD_RPC_TOGGLE.value, False))
        self._suppress_persist = False

        self.ui.set_button_state("idle")
        self._poll()

    def _on_main_button(self) -> None:
        """Handle the unified Start/Stop/Force Stop button."""
        state = self.ui.get_button_state()
        if state == "idle":
            self._on_start()
        elif state == "running":
            self._on_stop()
        elif state == "stopping":
            self._on_force_stop()

    def _on_start(self) -> None:
        if self.process is not None and self.process.is_alive():
            return
        values = self.ui.get_all_values()

        # Create fresh multiprocessing primitives for each run
        self.stats_queue = mp.Queue(maxsize=100)
        self.shutdown_event = mp.Event()
        self.last_stats = {}

        new_logger = Logger(timed=True)
        process = start_button_event(new_logger, self.ui, values, self.stats_queue, self.shutdown_event)
        if process is not None:
            self.logger = new_logger
            self.process = process
            self.current_values = values.copy()
            if self.discord_rpc_enabled:
                self.discord_rpc.enable()
            self.ui.set_button_state("running")
        else:
            self.ui.set_button_state("idle")

    def _on_stop(self) -> None:
        if self.shutdown_event is not None:
            stop_button_event(self.logger, self.shutdown_event)
            # Change to Force Stop button in case graceful shutdown takes too long
            self.ui.set_button_state("stopping")

    def _on_force_stop(self) -> None:
        """Force kill the worker process using SIGTERM/SIGKILL."""
        if self.process is not None and self.process.is_alive():
            self.logger.change_status("Force stopping bot...")
            self.process.terminate()  # SIGTERM
            self.process.join(timeout=1)
            if self.process.is_alive():
                self.process.kill()  # SIGKILL
            self._snapshot_session_stats()
            self.process = None
            self.logger.change_status("Idle")
            self.ui.set_button_state("idle")

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
        self.discord_rpc_enabled = bool(values.get(UIField.DISCORD_RPC_TOGGLE.value, False))
        if not self._suppress_persist:
            save_current_settings(values)

    def _snapshot_session_stats(self) -> None:
        """Freeze the current session stats for display while idle."""
        # Counters live in the worker and arrive via the stats queue. The UI
        # logger's change_status() can rebuild logger.stats from zeroed instance
        # fields, so prefer the latest queue snapshot and only borrow runtime
        # from get_stats().
        frozen = dict(self.last_stats) if self.last_stats else {}
        live_stats = self.logger.get_stats()
        if live_stats:
            if not frozen:
                frozen = dict(live_stats)
            else:
                frozen["time_since_start"] = live_stats["time_since_start"]
        if frozen:
            self.last_stats = frozen

    def _get_display_stats(self) -> dict[str, Any] | None:
        """Return stats for the UI: frozen session totals when idle, live stats while running."""
        if self.process is None and self.last_stats:
            stats = self.last_stats.copy()
            stats["current_status"] = self.logger.current_status
            return stats
        return self.logger.get_stats()

    def _update_ui_from_stats(self) -> None:
        update_layout(self.ui, self.logger, self._get_display_stats())

    def _poll(self) -> None:
        if self._closing:
            return

        # Read all available stats from the queue
        if self.stats_queue is not None:
            try:
                while True:
                    stats = self.stats_queue.get_nowait()
                    if self.process is not None:
                        self.last_stats = stats
                        # Update local logger with stats from worker process
                        if "current_status" in stats:
                            self.logger.current_status = stats["current_status"]
                        if self.logger.stats is not None:
                            self.logger.stats.update(stats)
            except Exception:
                pass  # Queue empty

        if self.process is not None and not self.process.is_alive():
            self._snapshot_session_stats()

        self.process, self.logger = handle_process_finished(self.ui, self.process, self.logger)
        self._update_ui_from_stats()
        self.discord_rpc.sync(self.discord_rpc_enabled, self._get_display_stats())
        self.ui.after(100, self._poll)

    def _on_open_logs_clicked(self) -> None:
        open_logs_folder()

    def _on_close(self) -> None:
        self._closing = True
        exit_button_event(self.process, self.shutdown_event)
        self.discord_rpc.disable()
        self.ui.destroy()

    def _run_adb_command(self, serial: str, command: str):
        """Helper to run a single ADB command and log the output."""
        if not serial:
            self.logger.change_status("Please select a device serial first.")
            return

        if not validate_device_serial(serial):
            self.logger.change_status(f"Invalid device serial format: {serial}")
            return

        argv = ["adb", "-s", serial, *shlex.split(command)]
        self.logger.change_status(f"Running ADB command: {' '.join(argv)}")
        try:
            result = run_command(argv, timeout=10)
            if result.returncode == 0:
                self.logger.change_status(f"Success: {result.stdout.strip() if result.stdout else '(No output)'}")
            else:
                self.logger.change_status(f"Error: {result.stderr.strip() if result.stderr else '(No error message)'}")
        except FileNotFoundError:
            self.logger.change_status("ADB command not found. Is ADB installed and in your PATH?")
        except Exception as e:
            self.logger.change_status(f"Failed to execute ADB command: {e}")

    def _on_adb_refresh(self) -> None:
        self.logger.change_status("Refreshing ADB devices list...")
        try:
            devices = AdbController.discover_devices()
            self.ui.adb_serial_combo.configure(values=devices)
            if devices:
                current_selection = self.ui.adb_serial_var.get()
                if current_selection not in devices:
                    self.ui.adb_serial_var.set(devices[0])
                self.logger.change_status(f"Found devices: {', '.join(devices)}")
            else:
                self.ui.adb_serial_var.set("")
                self.logger.change_status("No ADB devices found.")
        except Exception as e:
            self.logger.change_status(f"Error refreshing ADB devices: {e}")

    def _refresh_device_dropdown(self, combo_widget, controller_class, emulator_name: str) -> None:
        """Refresh device list for a dropdown (called on open)."""
        try:
            devices = controller_class.discover_devices()
            combo_widget.configure(values=["", *devices])  # Empty option for default
            if not devices:
                self.logger.change_status(f"No ADB devices found for {emulator_name}")
        except Exception:
            logging.exception(f"Failed to refresh {emulator_name} device list")
            self.logger.change_status(f"Failed to discover devices for {emulator_name}")

    def _refresh_gp_devices(self) -> None:
        """Refresh device list for Google Play dropdown (called on open)."""
        self._refresh_device_dropdown(self.ui.gp_device_serial_combo, GooglePlayEmulatorController, "Google Play")

    def _refresh_bs_devices(self) -> None:
        """Refresh device list for BlueStacks dropdown (called on open)."""
        self._refresh_device_dropdown(self.ui.bs_device_serial_combo, BlueStacksEmulatorController, "BlueStacks")

    def _on_adb_connect(self) -> None:
        device_address = self.ui.adb_serial_var.get()
        if not device_address:
            self.logger.change_status("Device address/serial cannot be empty.")
            return

        self.logger.change_status(f"Attempting to connect to {device_address}...")
        self.ui.update_idletasks()

        try:
            if AdbController.connect_device(self.logger, device_address):
                self.logger.change_status(f"Successfully connected/verified {device_address}!")
                # Refresh device list to confirm connection status in list
                self._on_adb_refresh()  # Call refresh to update list and potentially selection
                # Re-set the variable just in case refresh changed it due to new device order
                self.ui.adb_serial_var.set(device_address)
            else:
                # connect_device logs failure reason
                pass  # Logger status already set by connect_device
        except Exception as e:
            self.logger.change_status(f"Error during ADB connect: {e}")

    def _on_adb_restart(self) -> None:
        AdbController.restart_adb(self.logger)

    def _on_adb_set_size(self) -> None:
        serial = self.ui.adb_serial_var.get()
        width, height, density = 419, 633, 160
        self.logger.change_status(f"Setting size to {width}x{height} and density to {density} for {serial}...")
        self._run_adb_command(serial, f"shell wm size {width}x{height}")
        self._run_adb_command(serial, f"shell wm density {density}")

    def _on_adb_reset_size(self) -> None:
        serial = self.ui.adb_serial_var.get()
        self.logger.change_status(f"Resetting size and density for {serial}...")
        self._run_adb_command(serial, "shell wm size reset")
        self._run_adb_command(serial, "shell wm density reset")

    def run(self, start_on_run: bool = False) -> None:
        if start_on_run:
            self.ui.after(200, self._on_start)
        self.ui.mainloop()


def main_gui(start_on_run: bool = False, settings: dict[str, Any] | None = None) -> None:
    app = BotApplication(settings)
    app.run(start_on_run)


if __name__ == "__main__":
    from multiprocessing import freeze_support, set_start_method

    freeze_support()
    try:
        set_start_method("spawn")
    except RuntimeError:
        pass  # Already set
    cli_args = arg_parser()
    main_gui(start_on_run=cli_args.start)
