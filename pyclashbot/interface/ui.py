# ttkbootstrap-based user interface for py-clash-bot. -nosh

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional

import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, LEFT, READONLY, X, YES

from pyclashbot.interface.config import (
    BLUESTACKS_SETTINGS,
    GOOGLE_PLAY_SETTINGS,
    JOBS,
    MEMU_SETTINGS,
    ComboConfig,
)


def no_jobs_popup() -> None:
    messagebox.showerror("Critical Error!", "You must select at least one job!") # Display an error message when no jobs are selected.


class DualRingGauge(tk.Canvas):

    def __init__(
        self,
        master,
        diameter: int = 120,
        thickness: int = 12,
        start_angle: float = -90,
        fg: str = "#2ecc71",
        bg: str = "#e74c3c",
        text_color: str = "#ffffff",
        **kwargs,
    ):
        size = diameter + thickness + 4
        super().__init__(master, width=size, height=size, highlightthickness=0, **kwargs)
        self.diameter = diameter
        self.thickness = thickness
        self.start_angle = start_angle
        self.foreground_colour = fg
        self.background_colour = bg
        self.text_colour = text_color
        self._value = 0.0
        self._arc_fg = None
        self._arc_bg = None
        self._text = None
        self._draw_static()
        self._draw_dynamic(0, "0%")

    def _bbox(self) -> tuple[int, int, int, int]:
        padding = self.thickness // 2 + 4
        return (padding, padding, padding + self.diameter, padding + self.diameter)

    def _draw_static(self) -> None:
        bbox = self._bbox()
        if self._arc_bg:
            self.delete(self._arc_bg)
        self._arc_bg = self.create_arc(
            *bbox,
            start=0,
            extent=359.9,
            style="arc",
            width=self.thickness,
            outline=self.background_colour,
        )
        centre = self.winfo_reqwidth() // 2
        if self._text:
            self.delete(self._text)
        self._text = self.create_text(
            centre,
            centre,
            text="0%",
            fill=self.text_colour,
            font=("-size", 16, "-weight", "bold"),
        )

    def _draw_dynamic(
        self,
        percent: float,
        label: str,
        fg_colour: Optional[str] = None,
        text_colour: Optional[str] = None,
    ) -> None:
        percent = max(0, min(100, float(percent)))
        bbox = self._bbox()
        extent = percent / 100 * 360
        outline = fg_colour or self.foreground_colour
        if self._arc_fg:
            self.delete(self._arc_fg)
        self._arc_fg = self.create_arc(
            *bbox,
            start=self.start_angle,
            extent=extent,
            style="arc",
            width=self.thickness,
            outline=outline,
        )
        self.itemconfig(self._text, text=label, fill=text_colour or self.text_colour)
        self._value = percent

    def animate_to(
        self,
        target_percent: float,
        label_format: str = "{:.0f}%",
        fg_colour: Optional[str] = None,
        text_colour: Optional[str] = None,
        duration_ms: int = 400,
    ) -> None:
        start = self._value
        target = max(0, min(100, float(target_percent)))
        steps = max(1, duration_ms // 10)
        delta = (target - start) / steps
        frame = 0

        def step() -> None:
            nonlocal frame, start
            start += delta
            frame += 1
            final_frame = frame >= steps
            current = target if final_frame else start
            self._draw_dynamic(current, label_format.format(current), fg_colour, text_colour)
            if not final_frame:
                self.after(10, step)

        step()

    def set_colours(self, fg: str, bg: str, text: str) -> None:
        """Update the colours used by the gauge."""
        self.foreground_colour = fg
        self.background_colour = bg
        self.text_colour = text
        self._draw_static()
        self._draw_dynamic(self._value, f"{self._value:.0f}%", fg, text)

class PyClashBotUI(ttk.Window): # main window

    DEFAULT_THEME = "darkly"

    def __init__(self) -> None:
        super().__init__(themename=self.DEFAULT_THEME)
        self.title("py-clash-bot")
        self.geometry("460x500")
        self.resizable(False, False)

        self._style = ttk.Style()
        current_theme = self._style.theme_use()
        if not current_theme:
            current_theme = self.DEFAULT_THEME
        self.theme_var = ttk.StringVar(value=current_theme)
        self._config_callback: Optional[Callable[[dict[str, object]], None]] = None
        self._open_recordings_callback: Optional[Callable[[], None]] = None
        self._open_logs_callback: Optional[Callable[[], None]] = None
        self._config_widgets: dict[str, tk.Widget] = {}
        self._theme_labels: list[tk.Widget] = []
        self._traces: list[tuple[tk.Variable, str]] = []
        self._suspend_traces = 0

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_tabs()
        self._build_bottom_row()
        self._refresh_theme_colours()

    def register_config_callback(self, callback: Callable[[dict[str, object]], None]) -> None: # Call *callback* whenever a configuration control changes.
        self._config_callback = callback

    def register_open_recordings_callback(self, callback: Callable[[], None]) -> None:
        """Register the callback for opening the recordings folder."""
        self._open_recordings_callback = callback

    def register_open_logs_callback(self, callback: Callable[[], None]) -> None:
        """Register the callback for opening the logs folder."""
        self._open_logs_callback = callback
    def get_all_values(self) -> dict[str, object]: # Return current UI values using legacy configuration keys.
        values: dict[str, object] = {}
        for key, var in self.jobs_vars.items():
            values[key] = bool(var.get())

        values["deck_number_selection"] = self._safe_int(self.deck_var.get(), fallback=2)
        values["cycle_decks_user_toggle"] = bool(self.jobs_vars["cycle_decks_user_toggle"].get())
        values["max_deck_selection"] = self._safe_int(self.max_deck_var.get(), fallback=2)
        values["record_fights_toggle"] = bool(self.record_var.get())

        emulator_choice = self.emulator_var.get()
        values["memu_emulator_toggle"] = emulator_choice == "MEmu"
        values["google_play_emulator_toggle"] = emulator_choice == "Google Play"
        values["bluestacks_emulator_toggle"] = emulator_choice == "BlueStacks 5"

        memu_render = self.memu_render_var.get()
        values["directx_toggle"] = memu_render == "DirectX"
        values["opengl_toggle"] = memu_render == "OpenGL"

        bs_render = self.bs_render_var.get()
        values["bs_renderer_dx"] = bs_render == "DirectX"
        values["bs_renderer_gl"] = bs_render == "OpenGL"
        values["bs_renderer_vk"] = bs_render == "Vulkan"

        for key, var in self.gp_vars.items():
            values[key] = var.get()
        values["theme_name"] = self.theme_var.get() or self.DEFAULT_THEME
        return values

    def set_all_values(self, values: dict[str, object]) -> None: # Apply a collection of previously saved configuration values.
        theme_value: Optional[str] = None
        self._suspend_traces += 1
        try:
            for key, var in self.jobs_vars.items():
                if key in values:
                    var.set(bool(values[key]))

            if "deck_number_selection" in values:
                self.deck_var.set(str(values["deck_number_selection"]))
            if "max_deck_selection" in values:
                self.max_deck_var.set(str(values["max_deck_selection"]))
            if "record_fights_toggle" in values:
                self.record_var.set(bool(values["record_fights_toggle"]))

            if "theme_name" in values:
                theme_value = str(values["theme_name"])

            if values.get("google_play_emulator_toggle"):
                self.emulator_var.set("Google Play")
            elif values.get("bluestacks_emulator_toggle"):
                self.emulator_var.set("BlueStacks 5")
            else:
                self.emulator_var.set("MEmu")

            if values.get("directx_toggle"):
                self.memu_render_var.set("DirectX")
            elif values.get("opengl_toggle"):
                self.memu_render_var.set("OpenGL")

            if values.get("bs_renderer_vk"):
                self.bs_render_var.set("Vulkan")
            elif values.get("bs_renderer_dx"):
                self.bs_render_var.set("DirectX")
            elif values.get("bs_renderer_gl"):
                self.bs_render_var.set("OpenGL")

            for key, var in self.gp_vars.items():
                if key in values and values[key]:
                    var.set(str(values[key]))

            self._update_google_play_comboboxes()
            self._show_emulator_settings()
        finally:
            self._suspend_traces -= 1
        if theme_value is not None:
            self._apply_theme(theme_value)

    def set_running_state(self, running: bool) -> None:
        start_state = tk.DISABLED if running else tk.NORMAL
        stop_state = tk.NORMAL if running else tk.DISABLED
        self.start_btn.configure(state=start_state)
        self.stop_btn.configure(state=stop_state)

        for widget in self._config_widgets.values():
            if widget in {self.stop_btn, self.start_btn}:
                continue
            try:
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
    def update_stats(self, stats: Optional[dict[str, object]]) -> None:
        if not stats:
            return

        def as_string(key: str, default: str = "0") -> str:
            value = stats.get(key, default)
            return str(value)

        def as_int(key: str) -> int:
            value = stats.get(key)
            try:
                return int(value)
            except (TypeError, ValueError):
                return 0

        for key in (
            "wins",
            "losses",
            "cards_played",
            "classic_1v1_fights",
            "classic_2v2_fights",
            "trophy_road_1v1_fights",
            "card_randomizations",
            "card_cycles",
            "card_mastery_reward_collections",
            "upgrades",
            "war_chest_collects",
        ):
            if key in self.stat_labels:
                self.stat_labels[key].set(as_string(key))

        runtime = stats.get("time_since_start")
        if runtime is not None:
            self.bot_labels["time_since_start"].set(str(runtime))
        failures = stats.get("restarts_after_failure")
        if failures is not None:
            self.bot_labels["restarts_after_failure"].set(str(failures))

        winrate_raw = stats.get("winrate")
        wins = as_int("wins")
        losses = as_int("losses")
        winrate = self._extract_winrate(winrate_raw, wins, losses)
        gauge_fg = getattr(self._style.colors, "success", "#2ecc71") if hasattr(self._style, "colors") else "#2ecc71"
        self.win_gauge.animate_to(winrate, fg_colour=gauge_fg, text_colour=self._label_foreground())
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
        self._action_callback: Optional[Callable[[], None]] = None
        self.action_btn.configure(command=self._on_action_pressed)
    def _create_jobs_tab(self) -> None:
        frame = ttk.Labelframe(self.jobs_tab, text="Jobs", padding=10)
        frame.pack(padx=10, pady=10, anchor="n", fill="x")

        job_defaults = {job.key: job.default for job in JOBS}
        self.jobs_vars: dict[str, ttk.BooleanVar] = {}

        def add_job_checkbox(key: str, text: str, row_index: int, bootstyle: str) -> None:
            var = ttk.BooleanVar(value=job_defaults.get(key, False))
            checkbox = ttk.Checkbutton(
                frame,
                text=text,
                variable=var,
                bootstyle=bootstyle,
                command=self._notify_config_change,
            )
            checkbox.grid(row=row_index, column=0, sticky="w", pady=2)
            self.jobs_vars[key] = var
            self._trace_variable(var)
            self._register_config_widget(key, checkbox)

        primary_bootstyle = "warning-outline-toolbutton"
        secondary_bootstyle = "info-outline-toolbutton"
        add_job_checkbox("classic_1v1_user_toggle", "Classic 1v1 battles", 0, primary_bootstyle)
        add_job_checkbox("classic_2v2_user_toggle", "Classic 2v2 battles", 1, primary_bootstyle)
        add_job_checkbox("trophy_road_user_toggle", "Trophy Road battles", 2, primary_bootstyle)

        random_job = next(job for job in JOBS if job.key == "random_decks_user_toggle")
        deck_config: ComboConfig = random_job.extras["deck_number_selection"]
        self.jobs_vars["random_decks_user_toggle"] = ttk.BooleanVar(value=random_job.default)
        random_checkbox = ttk.Checkbutton(
            frame,
            text="Random decks",
            variable=self.jobs_vars["random_decks_user_toggle"],
            bootstyle=secondary_bootstyle,
            command=self._notify_config_change,
        )
        random_checkbox.grid(row=3, column=0, sticky="w", pady=2)
        self._trace_variable(self.jobs_vars["random_decks_user_toggle"])
        self._register_config_widget("random_decks_user_toggle", random_checkbox)

        ttk.Label(frame, text="Deck #").grid(row=3, column=1, padx=(20, 6), sticky="e")
        self.deck_var = ttk.StringVar(value=str(deck_config.default))
        self.deck_spin = ttk.Spinbox(
            frame,
            from_=min(deck_config.values),
            to=max(deck_config.values),
            width=6,
            textvariable=self.deck_var,
            command=self._notify_config_change,
        )
        self.deck_spin.grid(row=3, column=2, sticky="w")
        self._trace_variable(self.deck_var)
        self._register_config_widget("deck_number_selection", self.deck_spin)

        cycle_job = next(job for job in JOBS if job.key == "cycle_decks_user_toggle")
        max_config: ComboConfig = cycle_job.extras["max_deck_selection"]
        self.jobs_vars["cycle_decks_user_toggle"] = ttk.BooleanVar(value=cycle_job.default)
        cycle_checkbox = ttk.Checkbutton(
            frame,
            text="Cycle decks",
            variable=self.jobs_vars["cycle_decks_user_toggle"],
            bootstyle=secondary_bootstyle,
            command=self._notify_config_change,
        )
        cycle_checkbox.grid(row=4, column=0, sticky="w", pady=2)
        self._trace_variable(self.jobs_vars["cycle_decks_user_toggle"])
        self._register_config_widget("cycle_decks_user_toggle", cycle_checkbox)

        ttk.Label(frame, text="Decks to Cycle:").grid(row=4, column=1, padx=(20, 6), sticky="e")
        self.max_deck_var = ttk.StringVar(value=str(max_config.default))
        self.max_deck_spin = ttk.Spinbox(
            frame,
            from_=min(max_config.values),
            to=max(max_config.values),
            width=6,
            textvariable=self.max_deck_var,
            command=self._notify_config_change,
        )
        self.max_deck_spin.grid(row=4, column=2, sticky="w")
        self._trace_variable(self.max_deck_var)
        self._register_config_widget("max_deck_selection", self.max_deck_spin)

        add_job_checkbox("random_plays_user_toggle", "Random plays", 5, secondary_bootstyle)
        add_job_checkbox("disable_win_track_toggle", "Skip win/loss check", 6, secondary_bootstyle)
        add_job_checkbox("card_mastery_user_toggle", "Card Masteries", 7, secondary_bootstyle)
        add_job_checkbox("card_upgrade_user_toggle", "Upgrade Cards", 8, secondary_bootstyle)
    def _create_emulator_tab(self) -> None:
        outer = ttk.Labelframe(self.emulator_tab, text="Emulator Type", padding=10)
        outer.pack(padx=10, pady=10, anchor="n", fill="x")

        self.emulator_var = ttk.StringVar(value="MEmu")
        choices = [
            ("MEmu", "memu_emulator_toggle"),
            ("Google Play", "google_play_emulator_toggle"),
            ("BlueStacks 5", "bluestacks_emulator_toggle"),
        ]

        radio_row = ttk.Frame(outer)
        radio_row.pack(anchor="w")
        for text, key in choices:
            rb = ttk.Radiobutton(
                radio_row,
                text=text,
                variable=self.emulator_var,
                value=text,
                command=self._on_emulator_changed,
            )
            rb.pack(side=LEFT, padx=(0, 12))
            self._register_config_widget(key, rb)

        self.sub_notebook = ttk.Notebook(outer)
        self.sub_notebook.pack(fill="x", pady=8)

        self.google_play_frame = ttk.Frame(self.sub_notebook)
        self.memu_frame = ttk.Frame(self.sub_notebook)
        self.bluestacks_frame = ttk.Frame(self.sub_notebook)

        self.sub_notebook.add(self.google_play_frame, text="Google Play Settings")
        self.sub_notebook.add(self.memu_frame, text="MEmu Settings")
        self.sub_notebook.add(self.bluestacks_frame, text="BlueStacks Settings")

        self.gp_vars: dict[str, ttk.StringVar] = {}
        self._create_google_play_settings()
        self._create_memu_settings()
        self._create_bluestacks_settings()
        self._show_emulator_settings()

    def _create_google_play_settings(self) -> None:
        frame = ttk.Labelframe(self.google_play_frame, text="Google Play Options", padding=10)
        frame.pack(fill="x", padx=5, pady=5)

        left_keys = GOOGLE_PLAY_SETTINGS[:4]
        right_keys = GOOGLE_PLAY_SETTINGS[4:]

        for row, config in enumerate(left_keys):
            self._add_google_play_row(frame, row, 0, config)

        for row, config in enumerate(right_keys):
            self._add_google_play_row(frame, row, 3, config)

    def _create_memu_settings(self) -> None:
        frame = ttk.Labelframe(self.memu_frame, text="Render Mode", padding=10)
        frame.pack(fill="x", padx=5, pady=5)

        self.memu_render_var = ttk.StringVar(value="DirectX")
        for config in MEMU_SETTINGS:
            text = "DirectX" if "directx" in config.key else "OpenGL"
            rb = ttk.Radiobutton(
                frame,
                text=text,
                variable=self.memu_render_var,
                value=text,
                command=self._notify_config_change,
            )
            rb.pack(anchor="w")
            self._register_config_widget(config.key, rb)

    def _create_bluestacks_settings(self) -> None:
        frame = ttk.Labelframe(self.bluestacks_frame, text="Render Mode", padding=10)
        frame.pack(fill="x", padx=5, pady=5)

        self.bs_render_var = ttk.StringVar(value="DirectX")
        for config in BLUESTACKS_SETTINGS:
            if "dx" in config.key:
                value = "DirectX"
            elif "vk" in config.key:
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
            self._register_config_widget(config.key, rb)
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
        battle_fields = [
            ("wins", "Win"),
            ("losses", "Loss"),
            ("cards_played", "Moves"),
            ("classic_1v1_fights", "Classic 1v1s"),
            ("classic_2v2_fights", "Classic 2v2s"),
            ("trophy_road_1v1_fights", "Trophy Road 1v1s"),
            ("card_randomizations", "Decks Randomized"),
            ("card_cycles", "Decks Cycled"),
        ]
        self.stat_labels: dict[str, ttk.StringVar] = {}
        for row, (key, title) in enumerate(battle_fields):
            label = ttk.Label(battle_frame, text=title)
            label.grid(row=row, column=0, sticky="w")
            self._theme_labels.append(label)
            var = ttk.StringVar(value="0")
            ttk.Label(battle_frame, textvariable=var, foreground="#00aaff").grid(row=row, column=1, sticky="e")
            self.stat_labels[key] = var

        right = ttk.Frame(container)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        collection_frame = ttk.Labelframe(right, text="Collection Stats", padding=10)
        collection_frame.pack(fill=X)
        for row, (key, title) in enumerate(
            [
                ("card_mastery_reward_collections", "Masteries"),
                ("upgrades", "Upgrades"),
                ("war_chest_collects", "War Chests"),
            ]
        ):
            label = ttk.Label(collection_frame, text=title)
            label.grid(row=row, column=0, sticky="w")
            self._theme_labels.append(label)
            var = ttk.StringVar(value="0")
            ttk.Label(collection_frame, textvariable=var, foreground="#00aaff").grid(row=row, column=1, sticky="e")
            self.stat_labels[key] = var

        bot_frame = ttk.Labelframe(right, text="Bot Stats", padding=10)
        bot_frame.pack(fill=BOTH, expand=YES, pady=(8, 0))
        self.bot_labels = {
            "restarts_after_failure": ttk.StringVar(value="0"),
            "time_since_start": ttk.StringVar(value="00:00:00"),
        }
        label_failures = ttk.Label(bot_frame, text="Bot Failures")
        label_failures.grid(row=0, column=0, sticky="w")
        self._theme_labels.append(label_failures)
        ttk.Label(bot_frame, textvariable=self.bot_labels["restarts_after_failure"], foreground="#00aaff").grid(
            row=0, column=1, sticky="e"
        )
        label_runtime = ttk.Label(bot_frame, text="Runtime")
        label_runtime.grid(row=1, column=0, sticky="w")
        self._theme_labels.append(label_runtime)
        ttk.Label(bot_frame, textvariable=self.bot_labels["time_since_start"], foreground="#00aaff").grid(
            row=1, column=1, sticky="e"
        )

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
        self._register_config_widget("theme_name", self.theme_combo)

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
        self._register_config_widget("record_fights_toggle", record_checkbox)

        self.open_recordings_btn = ttk.Button(
            data_frame,
            text="Open Recordings Folder",
            command=self._on_open_recordings_clicked,
        )
        self.open_recordings_btn.pack(anchor="w", pady=(6, 0))

        self.open_logs_btn = ttk.Button(
            data_frame,
            text="Open Logs Folder",
            command=self._on_open_logs_clicked,
        )
        self.open_logs_btn.pack(anchor="w", pady=(6, 0))

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
        combo.bind("<<ComboboxSelected>>", self._notify_config_change)
        self.gp_vars[config.key] = var
        self._trace_variable(var)
        self._register_config_widget(config.key, combo)

    def _update_google_play_comboboxes(self) -> None:
        for key, var in self.gp_vars.items():
            widget = self._config_widgets.get(key)
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
        colour = self._style.lookup("TLabel", "foreground")
        return colour or "#202020"

    def _refresh_theme_colours(self) -> None:
        foreground = self._label_foreground()
        for label in self._theme_labels:
            try:
                label.configure(foreground=foreground)
            except tk.TclError:
                continue
        gauge_fg = getattr(self._style.colors, "success", "#2ecc71") if hasattr(self._style, "colors") else "#2ecc71"
        gauge_bg = getattr(self._style.colors, "danger", "#e74c3c") if hasattr(self._style, "colors") else "#e74c3c"
        self.win_gauge.set_colours(gauge_fg, gauge_bg, foreground)

    def _on_theme_change(self, _event: object) -> None:
        self._apply_theme(self.theme_var.get(), skip_variable_update=True)
        self._notify_config_change()

    def _on_emulator_changed(self) -> None:
        self._show_emulator_settings()
        self._notify_config_change()

    def _show_emulator_settings(self) -> None:
        index_map = {"Google Play": 0, "MEmu": 1, "BlueStacks 5": 2}
        self.sub_notebook.select(index_map.get(self.emulator_var.get(), 1))

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
    def _extract_winrate(raw: object, wins: int, losses: int) -> float:
        if isinstance(raw, str) and raw.endswith("%"):
            try:
                return float(raw.strip("%"))
            except ValueError:
                pass
        total = wins + losses
        if total == 0:
            return 0.0
        return wins / total * 100
