from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox
from typing import TYPE_CHECKING

import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, LEFT, READONLY, YES, X
from ttkbootstrap.tooltip import ToolTip

from pyclashbot.emulators import EmulatorType, get_available_emulators
from pyclashbot.interface.config import (
    BLUESTACKS_SETTINGS,
    GOOGLE_PLAY_SETTINGS,
    JOBS,
    MEMU_SETTINGS,
    ComboConfig,
)
from pyclashbot.interface.enums import (
    BATTLE_STAT_FIELDS,
    BATTLE_STAT_LABELS,
    BOT_STAT_FIELDS,
    BOT_STAT_LABELS,
    COLLECTION_STAT_FIELDS,
    COLLECTION_STAT_LABELS,
    BotStatField,
    DerivedStatField,
    StatField,
    UIField,
)
from pyclashbot.interface.widgets import DualRingGauge

if TYPE_CHECKING:
    from collections.abc import Callable


def no_jobs_popup() -> None:
    messagebox.showerror("Critical Error!", "You must select at least one job!")


class PyClashBotUI(ttk.Window):
    DEFAULT_THEME = "darkly"

    def __init__(self) -> None:
        super().__init__(themename=self.DEFAULT_THEME)
        self.title("py-clash-bot")
        self.geometry("490x500")
        self.resizable(False, False)

        self._style = ttk.Style()
        current_theme = self._style.theme_use()
        if not current_theme:
            current_theme = self.DEFAULT_THEME
        self.theme_var = ttk.StringVar(value=current_theme)
        self._config_callback: Callable[[dict[str, object]], None] | None = None
        self._open_recordings_callback: Callable[[], None] | None = None
        self._open_logs_callback: Callable[[], None] | None = None
        self._config_widgets: dict[str, tk.Widget] = {}
        self._theme_labels: list[tk.Widget] = []
        self._traces: list[tuple[tk.Variable, str]] = []
        self._suspend_traces = 0

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_tabs()
        self._build_bottom_row()
        self._refresh_theme_colours()

    def register_config_callback(self, callback: Callable[[dict[str, object]], None]) -> None:
        self._config_callback = callback

    def register_open_recordings_callback(self, callback: Callable[[], None]) -> None:
        self._open_recordings_callback = callback

    def register_open_logs_callback(self, callback: Callable[[], None]) -> None:
        self._open_logs_callback = callback

    def get_all_values(self) -> dict[str, object]:
        values: dict[str, object] = {}
        for field, var in self.jobs_vars.items():
            values[field.value] = bool(var.get())

        values[UIField.DECK_NUMBER_SELECTION.value] = self._safe_int(self.deck_var.get(), fallback=2)
        values[UIField.CYCLE_DECKS_USER_TOGGLE.value] = bool(self.jobs_vars[UIField.CYCLE_DECKS_USER_TOGGLE].get())
        values[UIField.MAX_DECK_SELECTION.value] = self._safe_int(self.max_deck_var.get(), fallback=2)
        values[UIField.RECORD_FIGHTS_TOGGLE.value] = bool(self.record_var.get())

        emulator_choice = self.emulator_var.get()
        values[UIField.MEMU_EMULATOR_TOGGLE.value] = emulator_choice == EmulatorType.MEMU
        values[UIField.GOOGLE_PLAY_EMULATOR_TOGGLE.value] = emulator_choice == EmulatorType.GOOGLE_PLAY
        values[UIField.BLUESTACKS_EMULATOR_TOGGLE.value] = emulator_choice == EmulatorType.BLUESTACKS
        values[UIField.ADB_TOGGLE.value] = emulator_choice == EmulatorType.ADB

        memu_render = self.memu_render_var.get()
        values[UIField.DIRECTX_TOGGLE.value] = memu_render == "DirectX"
        values[UIField.OPENGL_TOGGLE.value] = memu_render == "OpenGL"

        bs_render = self.bs_render_var.get()
        values[UIField.BS_RENDERER_DX.value] = bs_render == "DirectX"
        values[UIField.BS_RENDERER_GL.value] = bs_render == "OpenGL"
        values[UIField.BS_RENDERER_VK.value] = bs_render == "Vulkan"

        for field, var in self.gp_vars.items():
            values[field.value] = var.get()

        values[UIField.ADB_SERIAL.value] = self.adb_serial_var.get()

        values[UIField.THEME_NAME.value] = self.theme_var.get() or self.DEFAULT_THEME
        return values

    def set_all_values(self, values: dict[str, object]) -> None:
        theme_value: str | None = None
        self._suspend_traces += 1
        try:
            for field, var in self.jobs_vars.items():
                if field.value in values:
                    var.set(bool(values[field.value]))

            if UIField.DECK_NUMBER_SELECTION.value in values:
                self.deck_var.set(str(values[UIField.DECK_NUMBER_SELECTION.value]))
            if UIField.MAX_DECK_SELECTION.value in values:
                self.max_deck_var.set(str(values[UIField.MAX_DECK_SELECTION.value]))
            if UIField.RECORD_FIGHTS_TOGGLE.value in values:
                self.record_var.set(bool(values[UIField.RECORD_FIGHTS_TOGGLE.value]))

            if UIField.THEME_NAME.value in values:
                theme_value = str(values[UIField.THEME_NAME.value])

            # Determine saved emulator choice
            if values.get(UIField.GOOGLE_PLAY_EMULATOR_TOGGLE.value):
                saved_emulator = EmulatorType.GOOGLE_PLAY
            elif values.get(UIField.BLUESTACKS_EMULATOR_TOGGLE.value):
                saved_emulator = EmulatorType.BLUESTACKS
            elif values.get(UIField.ADB_TOGGLE.value):
                saved_emulator = EmulatorType.ADB
            else:
                saved_emulator = EmulatorType.MEMU

            # Use saved choice if available on this platform, otherwise fallback
            available = get_available_emulators()
            if saved_emulator in available:
                self.emulator_var.set(saved_emulator)
            elif available:
                self.emulator_var.set(available[0])

            if values.get(UIField.DIRECTX_TOGGLE.value):
                self.memu_render_var.set("DirectX")
            elif values.get(UIField.OPENGL_TOGGLE.value):
                self.memu_render_var.set("OpenGL")

            if values.get(UIField.BS_RENDERER_VK.value):
                self.bs_render_var.set("Vulkan")
            elif values.get(UIField.BS_RENDERER_DX.value):
                self.bs_render_var.set("DirectX")
            elif values.get(UIField.BS_RENDERER_GL.value):
                self.bs_render_var.set("OpenGL")

            for field, var in self.gp_vars.items():
                config = next((c for c in GOOGLE_PLAY_SETTINGS if c.key == field), None)
                if field.value in values and values[field.value] is not None:
                    var.set(str(values[field.value]))
                elif config:
                    var.set(str(config.default))

            if UIField.ADB_SERIAL.value in values:
                self.adb_serial_var.set(str(values[UIField.ADB_SERIAL.value]))

            self._update_google_play_comboboxes()

        finally:
            self._suspend_traces -= 1

        if theme_value is not None:
            self._apply_theme(theme_value)

        self._show_current_emulator_settings()

    def set_running_state(self, running: bool) -> None:
        start_state = tk.DISABLED if running else tk.NORMAL
        stop_state = tk.NORMAL if running else tk.DISABLED
        self.start_btn.configure(state=start_state)
        self.stop_btn.configure(state=stop_state)

        for key, widget in self._config_widgets.items():
            if widget in {self.stop_btn, self.start_btn}:
                continue
            try:
                if isinstance(widget, ttk.Combobox):
                    if key == "emulator_combobox":
                        widget.configure(state=tk.DISABLED if running else READONLY)
                    elif widget is self.adb_serial_combo:
                        widget.configure(state=tk.DISABLED if running else tk.NORMAL)
                    else:
                        widget.configure(state=tk.DISABLED if running else READONLY)
                elif isinstance(widget, ttk.Spinbox):
                    widget.configure(state=tk.DISABLED if running else READONLY)
                elif isinstance(widget, ttk.Radiobutton) and key in [
                    UIField.DIRECTX_TOGGLE.value,
                    UIField.OPENGL_TOGGLE.value,
                    UIField.BS_RENDERER_DX.value,
                    UIField.BS_RENDERER_GL.value,
                    UIField.BS_RENDERER_VK.value,
                ]:
                    widget.configure(state=tk.DISABLED if running else tk.NORMAL)
                elif widget in [
                    self.adb_connect_btn,
                    self.adb_refresh_btn,
                    self.adb_restart_btn,
                    self.adb_set_size_btn,
                    self.adb_reset_size_btn,
                ]:
                    widget.configure(state=tk.DISABLED if running else tk.NORMAL)
                elif isinstance(widget, ttk.Checkbutton):
                    widget.configure(state=tk.DISABLED if running else tk.NORMAL)
                elif isinstance(widget, ttk.Button):
                    widget.configure(state=tk.DISABLED if running else tk.NORMAL)

            except tk.TclError:
                continue
        if running:
            self._hide_action_button()

    def show_action_button(self, text: str, callback: Callable[[], None]) -> None:
        self._action_callback = callback
        self.action_btn.configure(text=text)
        self.stop_btn.grid_remove()
        self.action_btn.grid()

    def hide_action_button(self) -> None:
        self._hide_action_button()

    def append_log(self, message: str) -> None:
        self.event_log.configure(state="normal")
        self.event_log.delete("1.0", "end")
        self.event_log.insert("end", message)
        self.event_log.configure(state="disabled")
        self.event_log.see("end")

    def set_status(self, text: str) -> None:
        self._status_text = text

    def update_stats(self, stats: dict[str, object] | None) -> None:
        if not stats:
            return

        def as_string(field: StatField, default: str = "0") -> str:
            value = stats.get(field.value, default)
            return str(value)

        def as_int(field: StatField) -> int:
            value = stats.get(field.value)
            try:
                return int(value)
            except (TypeError, ValueError):
                return 0

        for field, var in self.stat_labels.items():
            var.set(as_string(field))

        runtime = stats.get(BotStatField.TIME_SINCE_START.value)
        if runtime is not None:
            self.bot_labels[BotStatField.TIME_SINCE_START].set(str(runtime))
        failures = stats.get(BotStatField.RESTARTS_AFTER_FAILURE.value)
        if failures is not None:
            self.bot_labels[BotStatField.RESTARTS_AFTER_FAILURE].set(str(failures))

        winrate_raw = stats.get(DerivedStatField.WINRATE.value)
        wins = as_int(StatField.WINS)
        losses = as_int(StatField.LOSSES)
        parsed_winrate = self._parse_winrate_value(winrate_raw)
        winrate = parsed_winrate if parsed_winrate is not None else self._calculate_winrate_percentage(wins, losses)
        gauge_fg = getattr(self._style.colors, "success", "#2ecc71") if hasattr(self._style, "colors") else "#2ecc71"
        self.win_gauge.animate_to(winrate, fg_colour=gauge_fg, text_colour=self._label_foreground())

        # Update win streak stats
        current_streak = stats.get(DerivedStatField.CURRENT_WIN_STREAK.value, 0)
        best_streak = stats.get(DerivedStatField.BEST_WIN_STREAK.value, 0)
        if hasattr(self, "current_streak_var"):
            self.current_streak_var.set(str(current_streak))
        if hasattr(self, "best_streak_var"):
            self.best_streak_var.set(str(best_streak))

    def _build_tabs(self) -> None:
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 6))

        self.jobs_tab = ttk.Frame(self.notebook)
        self.emulator_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)
        self.misc_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.jobs_tab, text="Jobs")
        self.notebook.add(self.emulator_tab, text="Emulator")
        self.notebook.add(self.stats_tab, text="Stats")
        self.notebook.add(self.misc_tab, text="Misc")

        self._create_jobs_tab()
        self._create_emulator_tab()
        self._create_stats_tab()
        self._create_misc_tab()

    def _build_bottom_row(self) -> None:
        bottom = ttk.Frame(self)
        bottom.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        bottom.columnconfigure(0, weight=1)

        log_container = ttk.Frame(bottom)
        log_container.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        log_container.columnconfigure(0, weight=1)
        self.event_log = tk.Text(log_container, height=1, wrap="none")
        self.event_log.grid(row=0, column=0, sticky="ew")
        self.event_log.configure(state="disabled")
        self._status_text = "Idle"

        self.start_btn = tk.Button(bottom, text="Start", bg="green", fg="white", width=10)
        self.start_btn.grid(row=0, column=1, sticky="e", padx=(0, 6))
        self._register_config_widget("Start", self.start_btn)

        self.stop_btn = tk.Button(bottom, text="Stop", bg="red", fg="white", width=10, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=2, sticky="e")
        self._register_config_widget("Stop", self.stop_btn)

        self.action_btn = ttk.Button(bottom, text="Retry")
        self.action_btn.grid(row=0, column=2, sticky="e")
        self.action_btn.grid_remove()
        self._action_callback: Callable[[], None] | None = None
        self.action_btn.configure(command=self._on_action_pressed)

    def _create_jobs_tab(self) -> None:
        frame = ttk.Labelframe(self.jobs_tab, text="Jobs", padding=10)
        frame.pack(padx=10, pady=10, anchor="n", fill="x")

        frame.columnconfigure(1, weight=1)

        job_defaults = {job.key: job.default for job in JOBS}
        jobs_by_key = {job.key: job for job in JOBS}
        self.jobs_vars: dict[UIField, ttk.BooleanVar] = {}

        checkbox_width = 25

        def add_job_checkbox(
            field: UIField,
            text: str,
            row_index: int,
            bootstyle: str,
        ) -> None:
            var = ttk.BooleanVar(value=job_defaults.get(field, False))
            checkbox = ttk.Checkbutton(
                frame,
                text=text,
                variable=var,
                bootstyle=bootstyle,
                command=self._notify_config_change,
                width=checkbox_width,
            )
            checkbox.grid(row=row_index, column=0, sticky="w", pady=2)
            self.jobs_vars[field] = var
            self._trace_variable(var)
            self._register_config_widget(field.value, checkbox)

        primary_bootstyle = "warning-outline-toolbutton"
        secondary_bootstyle = "info-outline-toolbutton"

        add_job_checkbox(
            UIField.CLASSIC_1V1_USER_TOGGLE,
            "⚔️ Classic 1v1 battles",
            0,
            primary_bootstyle,
        )
        add_job_checkbox(
            UIField.CLASSIC_2V2_USER_TOGGLE,
            "👥 Classic 2v2 battles",
            1,
            primary_bootstyle,
        )
        add_job_checkbox(
            UIField.TROPHY_ROAD_USER_TOGGLE,
            "🏆 Trophy Road battles",
            2,
            primary_bootstyle,
        )

        random_job = jobs_by_key[UIField.RANDOM_DECKS_USER_TOGGLE]
        deck_config: ComboConfig = random_job.extras[UIField.DECK_NUMBER_SELECTION]
        self.jobs_vars[UIField.RANDOM_DECKS_USER_TOGGLE] = ttk.BooleanVar(value=random_job.default)
        random_checkbox = ttk.Checkbutton(
            frame,
            text="🎲 Randomize Deck",
            variable=self.jobs_vars[UIField.RANDOM_DECKS_USER_TOGGLE],
            bootstyle=secondary_bootstyle,
            command=self._notify_config_change,
            width=checkbox_width,
        )
        random_checkbox.grid(row=3, column=0, sticky="w", pady=2)
        self._trace_variable(self.jobs_vars[UIField.RANDOM_DECKS_USER_TOGGLE])
        self._register_config_widget(UIField.RANDOM_DECKS_USER_TOGGLE.value, random_checkbox)

        deck_info = ttk.Label(frame, text="ⓘ", bootstyle="info")
        deck_info.grid(row=3, column=2, sticky="e", padx=(0, 2))
        ToolTip(deck_info, "Deck Number to use for Randomization")
        self.deck_var = ttk.StringVar(value=str(deck_config.default))
        self.deck_spin = ttk.Spinbox(
            frame,
            from_=min(deck_config.values),
            to=max(deck_config.values),
            width=6,
            textvariable=self.deck_var,
            command=self._notify_config_change,
            state=READONLY,
        )
        self.deck_spin.grid(row=3, column=3, sticky="e")
        self._trace_variable(self.deck_var)
        self._register_config_widget(UIField.DECK_NUMBER_SELECTION.value, self.deck_spin)

        cycle_job = jobs_by_key[UIField.CYCLE_DECKS_USER_TOGGLE]
        max_config: ComboConfig = cycle_job.extras[UIField.MAX_DECK_SELECTION]
        self.jobs_vars[UIField.CYCLE_DECKS_USER_TOGGLE] = ttk.BooleanVar(value=cycle_job.default)
        cycle_checkbox = ttk.Checkbutton(
            frame,
            text="♻️ Cycle decks",
            variable=self.jobs_vars[UIField.CYCLE_DECKS_USER_TOGGLE],
            bootstyle=secondary_bootstyle,
            command=self._notify_config_change,
            width=checkbox_width,
        )
        cycle_checkbox.grid(row=4, column=0, sticky="w", pady=2)
        self._trace_variable(self.jobs_vars[UIField.CYCLE_DECKS_USER_TOGGLE])
        self._register_config_widget(UIField.CYCLE_DECKS_USER_TOGGLE.value, cycle_checkbox)

        max_deck_info = ttk.Label(frame, text="ⓘ", bootstyle="info")
        max_deck_info.grid(row=4, column=2, sticky="e", padx=(0, 2))
        ToolTip(max_deck_info, "Number of decks to cycle through")
        self.max_deck_var = ttk.StringVar(value=str(max_config.default))
        self.max_deck_spin = ttk.Spinbox(
            frame,
            from_=min(max_config.values),
            to=max(max_config.values),
            width=6,
            textvariable=self.max_deck_var,
            command=self._notify_config_change,
            state=READONLY,
        )
        self.max_deck_spin.grid(row=4, column=3, sticky="e")
        self._trace_variable(self.max_deck_var)
        self._register_config_widget(UIField.MAX_DECK_SELECTION.value, self.max_deck_spin)

        add_job_checkbox(UIField.RANDOM_PLAYS_USER_TOGGLE, "❔ Random plays", 5, secondary_bootstyle)
        add_job_checkbox(UIField.DISABLE_WIN_TRACK_TOGGLE, "⏭️ Skip win/loss check", 6, secondary_bootstyle)
        add_job_checkbox(UIField.CARD_MASTERY_USER_TOGGLE, "🎯 Card Masteries", 7, secondary_bootstyle)
        add_job_checkbox(UIField.CARD_UPGRADE_USER_TOGGLE, "⬆️ Upgrade Cards", 8, secondary_bootstyle)

    def _create_emulator_tab(self) -> None:
        # Main container frame for the tab
        container = ttk.Frame(self.emulator_tab, padding=10)
        container.pack(fill=BOTH, expand=YES)

        # Emulator Selection Dropdown
        selection_frame = ttk.Frame(container)
        selection_frame.pack(fill=X, pady=(0, 10))
        ttk.Label(selection_frame, text="Select Emulator:").pack(side=LEFT, padx=(0, 5))

        available_emulators = get_available_emulators()
        default_emulator = available_emulators[0] if available_emulators else EmulatorType.ADB
        self.emulator_var = ttk.StringVar(value=default_emulator)
        self.emulator_combo = ttk.Combobox(
            selection_frame,
            textvariable=self.emulator_var,
            values=available_emulators,
            state=READONLY,
            width=20,
        )
        self.emulator_combo.pack(side=LEFT, fill=X, expand=True)
        self.emulator_combo.bind("<<ComboboxSelected>>", self._on_emulator_changed)
        # Register the combobox itself for state management
        self._register_config_widget("emulator_combobox", self.emulator_combo)

        # Frame to hold the currently selected emulator's settings
        self.settings_container = ttk.Frame(container)
        self.settings_container.pack(fill=BOTH, expand=YES)

        # Create the individual settings frames but don't pack them yet
        self.google_play_frame = ttk.Frame(self.settings_container)
        self.memu_frame = ttk.Frame(self.settings_container)
        self.bluestacks_frame = ttk.Frame(self.settings_container)
        self.adb_frame = ttk.Frame(self.settings_container)

        # Store frames in a dictionary for easy access
        self.emulator_settings_frames = {
            EmulatorType.MEMU: self.memu_frame,
            EmulatorType.GOOGLE_PLAY: self.google_play_frame,
            EmulatorType.BLUESTACKS: self.bluestacks_frame,
            EmulatorType.ADB: self.adb_frame,
        }

        # Populate the settings frames
        self.gp_vars: dict[UIField, ttk.StringVar] = {}
        self._create_google_play_settings(self.google_play_frame)
        self._create_memu_settings(self.memu_frame)
        self._create_bluestacks_settings(self.bluestacks_frame)
        self._create_adb_tab(self.adb_frame)

        # Show the initial settings based on the default value
        self._show_current_emulator_settings()

    def _create_google_play_settings(self, parent_frame: ttk.Frame) -> None:
        frame = ttk.Labelframe(parent_frame, text="Google Play Options", padding=10)
        frame.pack(fill="x", padx=5, pady=5)

        left_keys = GOOGLE_PLAY_SETTINGS[:4]
        right_keys = GOOGLE_PLAY_SETTINGS[4:]

        for row, config in enumerate(left_keys):
            self._add_google_play_row(frame, row, 0, config)

        for row, config in enumerate(right_keys):
            self._add_google_play_row(frame, row, 3, config)

    def _create_memu_settings(self, parent_frame: ttk.Frame) -> None:
        frame = ttk.Labelframe(parent_frame, text="Render Mode", padding=10)
        frame.pack(fill="x", padx=5, pady=5)

        self.memu_render_var = ttk.StringVar(value="DirectX")
        for config in MEMU_SETTINGS:
            text = "DirectX" if config.key == UIField.DIRECTX_TOGGLE else "OpenGL"
            rb = ttk.Radiobutton(
                frame,
                text=text,
                variable=self.memu_render_var,
                value=text,
                command=self._notify_config_change,
            )
            rb.pack(anchor="w")
            self._register_config_widget(config.key.value, rb)

    def _create_bluestacks_settings(self, parent_frame: ttk.Frame) -> None:
        frame = ttk.Labelframe(parent_frame, text="Render Mode", padding=10)
        frame.pack(fill="x", padx=5, pady=5)

        self.bs_render_var = ttk.StringVar(value="DirectX")
        for config in BLUESTACKS_SETTINGS:
            if config.key == UIField.BS_RENDERER_DX:
                value = "DirectX"
            elif config.key == UIField.BS_RENDERER_VK:
                value = "Vulkan"
            else:
                value = "OpenGL"
            rb = ttk.Radiobutton(
                frame,
                text=value,
                variable=self.bs_render_var,
                value=value,
                command=self._notify_config_change,
            )
            rb.pack(anchor="w")
            self._register_config_widget(config.key.value, rb)

    def _create_adb_tab(self, parent_frame: ttk.Frame) -> None:
        """Create the widgets for the ADB Device settings tab."""
        frame = ttk.Labelframe(parent_frame, text="Device Settings", padding=10)
        frame.pack(fill="x", padx=5, pady=5)

        # --- Row 1: Serial Input ---
        row1 = ttk.Frame(frame)
        row1.pack(fill="x", pady=(0, 5))
        row1.columnconfigure(1, weight=1)

        ttk.Label(row1, text="Device Serial:").grid(row=0, column=0, padx=(0, 5), sticky="w")

        self.adb_serial_var = ttk.StringVar(value="")
        self.adb_serial_combo = ttk.Combobox(
            row1,
            textvariable=self.adb_serial_var,
            state=tk.NORMAL,
        )
        self.adb_serial_combo.grid(row=0, column=1, padx=5, sticky="ew")
        self._register_config_widget(UIField.ADB_SERIAL.value, self.adb_serial_combo)
        self._trace_variable(self.adb_serial_var)

        # --- Row 2: Connect/Refresh Buttons ---
        row_buttons_connect = ttk.Frame(frame)
        row_buttons_connect.pack(fill="x", pady=(0, 8))
        row_buttons_connect.columnconfigure(0, weight=1)
        row_buttons_connect.columnconfigure(1, weight=1)

        self.adb_connect_btn = ttk.Button(row_buttons_connect, text="Connect", style="success.TButton")
        self.adb_connect_btn.grid(row=0, column=0, padx=(0, 3), sticky="ew")
        self._register_config_widget("adb_connect_btn", self.adb_connect_btn)

        self.adb_refresh_btn = ttk.Button(row_buttons_connect, text="Refresh")
        self.adb_refresh_btn.grid(row=0, column=1, padx=(3, 0), sticky="ew")
        self._register_config_widget("adb_refresh_btn", self.adb_refresh_btn)

        # --- Row 3: Action Buttons (Stacked Vertically) ---
        row_buttons_action = ttk.Frame(frame)
        row_buttons_action.pack(fill="x")

        self.adb_restart_btn = ttk.Button(row_buttons_action, text="Restart ADB")
        self.adb_restart_btn.pack(fill=X, pady=(0, 3))
        self._register_config_widget("adb_restart_btn", self.adb_restart_btn)

        self.adb_set_size_btn = ttk.Button(row_buttons_action, text="Set Size & Density")
        self.adb_set_size_btn.pack(fill=X, pady=3)
        self._register_config_widget("adb_set_size_btn", self.adb_set_size_btn)

        self.adb_reset_size_btn = ttk.Button(row_buttons_action, text="Reset Size & Density")
        self.adb_reset_size_btn.pack(fill=X, pady=(3, 0))
        self._register_config_widget("adb_reset_size_btn", self.adb_reset_size_btn)

        ToolTip(self.adb_set_size_btn, "Sets screen to 419x633 and density to 160")
        ToolTip(self.adb_reset_size_btn, "Resets screen size and density to device defaults")

    def _create_stats_tab(self) -> None:
        container = ttk.Frame(self.stats_tab, padding=10)
        container.pack(fill=BOTH, expand=YES)
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)
        left = ttk.Frame(container)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        gauge_frame = ttk.Labelframe(left, text="Win Rate", padding=10)
        gauge_frame.pack(fill=X)
        self.win_gauge = DualRingGauge(gauge_frame, diameter=120, thickness=12, text_color="#00aaff")
        self.win_gauge.pack(anchor="center")

        battle_frame = ttk.Labelframe(left, text="Battle Stats", padding=10)
        battle_frame.pack(fill=BOTH, expand=YES, pady=(8, 0))
        self.stat_labels: dict[StatField, ttk.StringVar] = {}
        for row, field in enumerate(BATTLE_STAT_FIELDS):
            title = BATTLE_STAT_LABELS[field]
            label = ttk.Label(battle_frame, text=title)
            label.grid(row=row, column=0, sticky="w")
            self._theme_labels.append(label)
            var = ttk.StringVar(value="0")
            ttk.Label(battle_frame, textvariable=var, foreground="#00aaff").grid(row=row, column=1, sticky="e")
            self.stat_labels[field] = var

        # Add win streak stats
        ttk.Separator(battle_frame, orient="horizontal").grid(
            row=len(BATTLE_STAT_FIELDS), column=0, columnspan=2, sticky="ew", pady=(8, 4)
        )
        streak_row = len(BATTLE_STAT_FIELDS) + 1
        ttk.Label(battle_frame, text="Current Streak:").grid(row=streak_row, column=0, sticky="w")
        self.current_streak_var = ttk.StringVar(value="0")
        ttk.Label(battle_frame, textvariable=self.current_streak_var, foreground="#00aaff").grid(
            row=streak_row, column=1, sticky="e"
        )
        ttk.Label(battle_frame, text="Best Streak:").grid(row=streak_row + 1, column=0, sticky="w")
        self.best_streak_var = ttk.StringVar(value="0")
        ttk.Label(battle_frame, textvariable=self.best_streak_var, foreground="#00aaff").grid(
            row=streak_row + 1, column=1, sticky="e"
        )

        right = ttk.Frame(container)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        collection_frame = ttk.Labelframe(right, text="Collection Stats", padding=10)
        collection_frame.pack(fill=X)
        for row, field in enumerate(COLLECTION_STAT_FIELDS):
            title = COLLECTION_STAT_LABELS[field]
            label = ttk.Label(collection_frame, text=title)
            label.grid(row=row, column=0, sticky="w")
            self._theme_labels.append(label)
            var = ttk.StringVar(value="0")
            ttk.Label(collection_frame, textvariable=var, foreground="#00aaff").grid(row=row, column=1, sticky="e")
            self.stat_labels[field] = var

        bot_frame = ttk.Labelframe(right, text="Bot Stats", padding=10)
        bot_frame.pack(fill=BOTH, expand=YES, pady=(8, 0))
        self.bot_labels = {
            BotStatField.RESTARTS_AFTER_FAILURE: ttk.StringVar(value="0"),
            BotStatField.TIME_SINCE_START: ttk.StringVar(value="00:00:00"),
        }
        for row, field in enumerate(BOT_STAT_FIELDS):
            title = BOT_STAT_LABELS[field]
            label = ttk.Label(bot_frame, text=title)
            label.grid(row=row, column=0, sticky="w")
            self._theme_labels.append(label)
            ttk.Label(
                bot_frame,
                textvariable=self.bot_labels[field],
                foreground="#00aaff",
            ).grid(row=row, column=1, sticky="e")

    def _create_misc_tab(self) -> None:
        appearance = ttk.Labelframe(self.misc_tab, text="Appearance", padding=10)
        appearance.pack(padx=10, pady=10, anchor="n", fill="x")

        ttk.Label(appearance, text="Select Theme:").pack(anchor="w", pady=(0, 4))
        self.theme_combo = ttk.Combobox(
            appearance,
            values=self._style.theme_names(),
            width=25,
            state=READONLY,
            textvariable=self.theme_var,
        )
        self.theme_combo.pack(anchor="w")
        self.theme_combo.bind("<<ComboboxSelected>>", self._on_theme_change)
        self._trace_variable(self.theme_var)
        self._register_config_widget(UIField.THEME_NAME.value, self.theme_combo)

        ttk.Separator(self.misc_tab, orient="horizontal").pack(fill="x", padx=10, pady=(6, 0))
        data_frame = ttk.Labelframe(self.misc_tab, text="Data Settings", padding=10)
        data_frame.pack(fill="x", padx=10, pady=10)

        self.record_var = ttk.BooleanVar()
        record_checkbox = ttk.Checkbutton(
            data_frame,
            text="Record fights",
            variable=self.record_var,
            bootstyle="round-toggle",
            command=self._notify_config_change,
        )
        record_checkbox.pack(anchor="w")
        self._trace_variable(self.record_var)
        self._register_config_widget(UIField.RECORD_FIGHTS_TOGGLE.value, record_checkbox)

        self.open_recordings_btn = ttk.Button(
            data_frame,
            text="Open Recordings Folder",
            command=self._on_open_recordings_clicked,
        )
        self.open_recordings_btn.pack(fill="x", pady=(6, 0))

        self.open_logs_btn = ttk.Button(
            data_frame,
            text="Open Logs Folder",
            command=self._on_open_logs_clicked,
        )
        self.open_logs_btn.pack(fill="x", pady=(6, 0))

        ttk.Separator(self.misc_tab, orient="horizontal").pack(fill="x", padx=10, pady=(6, 0))
        display_frame = ttk.Labelframe(self.misc_tab, text="Display Settings", padding=10)
        display_frame.pack(fill="x", padx=10, pady=10)

    def _register_config_widget(self, key: str, widget: tk.Widget) -> None:
        self._config_widgets[key] = widget

    def _notify_config_change(self, *_: object) -> None:
        if self._suspend_traces > 0 or self._config_callback is None:
            return
        self.after_idle(lambda: self._config_callback(self.get_all_values()))

    def _trace_variable(self, var: tk.Variable) -> None:
        trace_id = var.trace_add("write", self._notify_config_change)
        self._traces.append((var, trace_id))

    def _add_google_play_row(
        self,
        frame: ttk.Labelframe,
        row: int,
        column_offset: int,
        config: ComboConfig,
    ) -> None:
        ttk.Label(frame, text=config.label).grid(row=row, column=column_offset, sticky="w", padx=5, pady=2)
        var = ttk.StringVar(value=str(config.default))
        combo = ttk.Combobox(
            frame,
            values=[str(option) for option in config.values],
            width=12,
            state=READONLY,
            textvariable=var,
        )
        combo.grid(row=row, column=column_offset + 1, sticky="w")
        combo.bind("<<ComboboxSelected>>", self._notify_config_change_event)
        field = config.key
        self.gp_vars[field] = var
        self._trace_variable(var)
        self._register_config_widget(field.value, combo)

    def _notify_config_change_event(self, _event: object) -> None:
        self._notify_config_change()

    def _update_google_play_comboboxes(self) -> None:
        for field, var in self.gp_vars.items():
            widget = self._config_widgets.get(field.value)
            if not widget:
                continue
            values = [str(option) for option in widget.cget("values")]
            if var.get() not in values and values:
                var.set(values[0])

    def _apply_theme(self, theme_name: str, skip_variable_update: bool = False) -> None:
        available = tuple(self._style.theme_names())
        selected = theme_name if theme_name in available else self.DEFAULT_THEME
        if selected not in available and available:
            selected = available[0]
        if not skip_variable_update or self.theme_var.get() != selected:
            self._suspend_traces += 1
            try:
                self.theme_var.set(selected)
            finally:
                self._suspend_traces -= 1
        self._style.theme_use(selected)
        self._refresh_theme_colours()

    def _label_foreground(self) -> str:
        try:
            colour = self._style.lookup("TLabel", "foreground")
            return colour or "#202020"
        except tk.TclError:
            return "#202020"

    def _refresh_theme_colours(self) -> None:
        foreground = self._label_foreground()
        for label in self._theme_labels:
            try:
                label.configure(foreground=foreground)
            except tk.TclError:
                continue
        gauge_fg = getattr(self._style.colors, "success", "#2ecc71")
        gauge_bg = getattr(self._style.colors, "danger", "#e74c3c")
        self.win_gauge.set_colours(gauge_fg, gauge_bg, foreground)

    def _on_theme_change(self, _event: object | None = None) -> None:
        self._apply_theme(self.theme_var.get(), skip_variable_update=True)
        self._notify_config_change()

    def _on_emulator_changed(self, _event: object = None) -> None:
        self._show_current_emulator_settings()
        self._notify_config_change()

    def _show_current_emulator_settings(self) -> None:
        """Hides all emulator settings frames and shows the one selected in the combobox."""
        selected_emulator = self.emulator_var.get()

        # Hide all frames first
        for frame in self.emulator_settings_frames.values():
            frame.pack_forget()

        # Show the selected frame
        frame_to_show = self.emulator_settings_frames.get(selected_emulator)
        if frame_to_show:
            frame_to_show.pack(fill=BOTH, expand=YES)

    def _hide_action_button(self) -> None:
        self.action_btn.grid_remove()
        self.stop_btn.grid()

    def _on_action_pressed(self) -> None:
        if self._action_callback:
            self._action_callback()
        self._hide_action_button()

    def _on_open_recordings_clicked(self) -> None:
        if self._open_recordings_callback:
            self._open_recordings_callback()

    def _on_open_logs_clicked(self) -> None:
        if self._open_logs_callback:
            self._open_logs_callback()

    @staticmethod
    def _safe_int(value: object, fallback: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return fallback

    @staticmethod
    def _parse_winrate_value(raw: object) -> float | None:
        if isinstance(raw, str):
            stripped = raw.strip()
            if stripped.endswith("%"):
                stripped = stripped[:-1]
            try:
                return float(stripped)
            except ValueError:
                return None
        if isinstance(raw, int | float):
            return float(raw)
        return None

    @staticmethod
    def _calculate_winrate_percentage(wins: int, losses: int) -> float:
        total = wins + losses
        if total <= 0:
            return 0.0
        return wins / total * 100
