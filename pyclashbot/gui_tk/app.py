"""Main customtkinter application for Royale Engine."""

import json
import os
import threading
import tkinter as tk
from pathlib import Path
from typing import Any, Dict, Optional

import customtkinter as ctk

from pyclashbot.bot.worker import WorkerThread
from pyclashbot.interface.config import USER_CONFIG_KEYS
from pyclashbot.utils.caching import USER_SETTINGS_CACHE
from pyclashbot.utils.logger import Logger
from pyclashbot.utils.versioning import __version__

from .views.emulator import EmulatorView
from .views.jobs import JobsView
from .views.stats import StatsView
from .widgets.panels import BotControlPanel, QuickGuidePanel, SystemStatusPanel


class BotController:
    """Controller to manage bot worker thread safely."""

    def __init__(self):
        self.worker: Optional[WorkerThread] = None
        self.logger = Logger(timed=False)
        self._is_running = False

    def start(self, job_dict: Dict[str, Any]) -> bool:
        """Start the bot worker thread."""
        if self._is_running:
            return False

        try:
            self.logger = Logger(timed=True)
            self.worker = WorkerThread(self.logger, job_dict)
            self.worker.start()
            self._is_running = True
            return True
        except Exception as e:
            self.logger.error(f"Failed to start bot: {e}")
            return False

    def stop(self) -> None:
        """Stop the bot worker thread."""
        if self.worker and self._is_running:
            self.logger.change_status(status="Stopping")
            self.worker.shutdown(kill=False)
            self._is_running = False

    def is_running(self) -> bool:
        """Check if bot is currently running."""
        if not self._is_running:
            return False

        if self.worker and not self.worker.is_alive():
            self._is_running = False
            return False

        return True

    def get_status(self) -> Dict[str, str]:
        """Get current bot status information."""
        if not self.is_running():
            return {"status": "Idle", "current_state": "", "error_message": ""}

        # Get logger from worker thread if available
        active_logger = self.worker.logger if self.worker else self.logger
        
        return {
            "status": getattr(active_logger, 'current_status', 'Running'),
            "current_state": getattr(active_logger, 'current_state', ''),
            "error_message": "",
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get current bot statistics."""
        # Get logger from worker thread if available
        active_logger = self.worker.logger if self.worker else self.logger
        
        if hasattr(active_logger, 'get_stats'):
            return active_logger.get_stats() or {}
        return {}

    def get_uptime(self) -> str:
        """Get bot uptime string."""
        # Get logger from worker thread if available
        active_logger = self.worker.logger if self.worker else self.logger
        
        if hasattr(active_logger, 'calc_time_since_start'):
            return active_logger.calc_time_since_start()
        return "00:00:00"


class BotGUI(ctk.CTk):
    """Main Royale Engine customtkinter GUI application."""

    def __init__(self):
        super().__init__()

        self.controller = BotController()
        self.settings: Dict[str, Any] = {}
        
        # Configure window
        self.title(f"Royale Engine | {__version__}")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Load and apply theme
        self._load_theme()
        
        # Initialize GUI elements
        self._setup_ui()
        self._load_settings()
        
        # Start status update timer
        self._start_status_timer()

    def _load_theme(self) -> None:
        """Load and apply the Arctic theme."""
        theme_path = Path(__file__).parent / "theme.json"
        try:
            with open(theme_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            ctk.set_default_color_theme(str(theme_path))
        except Exception as e:
            print(f"Warning: Could not load theme: {e}")
        
        ctk.set_appearance_mode("dark")

    def _setup_ui(self) -> None:
        """Set up the main UI layout."""
        # Configure grid weights
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Main content

        # Header
        self._create_header()
        
        # Sidebar (left column)
        self._create_sidebar()
        
        # Main content (right column)
        self._create_main_content()
        
        # Sticky bottom control bar
        self._create_control_bar()

    def _create_header(self) -> None:
        """Create the header section."""
        header_frame = ctk.CTkFrame(self, corner_radius=0, height=80)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=(0, 16))
        header_frame.grid_propagate(False)
        
        # Configure header layout
        header_frame.grid_columnconfigure(0, weight=0)  # Logo placeholder
        header_frame.grid_columnconfigure(1, weight=1)  # Title section
        header_frame.grid_columnconfigure(2, weight=0)  # Status pill
        
        # Logo placeholder
        logo_label = ctk.CTkLabel(
            header_frame,
            text="🎮",
            font=ctk.CTkFont(size=32)
        )
        logo_label.grid(row=0, column=0, padx=(20, 16), pady=16, sticky="w")
        
        # Title section
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=1, padx=16, pady=16, sticky="w")
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="Royale Engine",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Advanced Gaming Automation",
            font=ctk.CTkFont(size=14),
            text_color="#a0aec0"
        )
        subtitle_label.grid(row=1, column=0, sticky="w")
        
        # Status pill
        self.status_pill = ctk.CTkLabel(
            header_frame,
            text="⚪ Idle",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=20,
            fg_color="#4a5568",
            text_color="white",
            height=24,
            width=80
        )
        self.status_pill.grid(row=0, column=2, padx=(16, 20), pady=16, sticky="e")

    def _create_sidebar(self) -> None:
        """Create the left sidebar with panels."""
        sidebar_frame = ctk.CTkFrame(self, width=300)
        sidebar_frame.grid(row=1, column=0, sticky="nsew", padx=(16, 8), pady=(0, 16))
        sidebar_frame.grid_propagate(False)
        
        # Configure sidebar layout
        sidebar_frame.grid_rowconfigure(0, weight=0)  # Bot control
        sidebar_frame.grid_rowconfigure(1, weight=0)  # System status
        sidebar_frame.grid_rowconfigure(2, weight=1)  # Quick guide (expandable)
        sidebar_frame.grid_columnconfigure(0, weight=1)
        
        # Bot Control Panel
        self.bot_control = BotControlPanel(sidebar_frame, self._on_start_bot, self._on_stop_bot)
        self.bot_control.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        
        # System Status Panel
        self.system_status = SystemStatusPanel(sidebar_frame)
        self.system_status.grid(row=1, column=0, sticky="ew", padx=16, pady=8)
        
        # Quick Guide Panel
        self.quick_guide = QuickGuidePanel(sidebar_frame)
        self.quick_guide.grid(row=2, column=0, sticky="nsew", padx=16, pady=(8, 16))

    def _create_main_content(self) -> None:
        """Create the main content area with tabs."""
        # Main content frame
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=1, sticky="nsew", padx=(8, 16), pady=(0, 16))
        
        # Configure content layout
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Tab view
        self.tabview = ctk.CTkTabview(content_frame)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        
        # Create tabs
        self.tabview.add("Jobs")
        self.tabview.add("Emulator")
        self.tabview.add("Stats")
        
        # Initialize tab content
        self.jobs_view = JobsView(self.tabview.tab("Jobs"))
        self.jobs_view.grid(row=0, column=0, sticky="nsew")
        self.tabview.tab("Jobs").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Jobs").grid_columnconfigure(0, weight=1)
        
        self.emulator_view = EmulatorView(self.tabview.tab("Emulator"))
        self.emulator_view.grid(row=0, column=0, sticky="nsew")
        self.tabview.tab("Emulator").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Emulator").grid_columnconfigure(0, weight=1)
        
        self.stats_view = StatsView(self.tabview.tab("Stats"))
        self.stats_view.grid(row=0, column=0, sticky="nsew")
        self.tabview.tab("Stats").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Stats").grid_columnconfigure(0, weight=1)

    def _create_control_bar(self) -> None:
        """Create the sticky bottom control bar."""
        control_frame = ctk.CTkFrame(self, height=60, corner_radius=0)
        control_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        control_frame.grid_propagate(False)
        
        # Configure control bar layout
        control_frame.grid_columnconfigure(0, weight=1)  # Spacer
        control_frame.grid_columnconfigure(1, weight=0)  # Save button
        control_frame.grid_columnconfigure(2, weight=0)  # Start button
        control_frame.grid_columnconfigure(3, weight=0)  # Stop button
        control_frame.grid_columnconfigure(4, weight=1)  # Spacer
        
        # Save button
        self.save_button = ctk.CTkButton(
            control_frame,
            text="Save",
            width=100,
            command=self._save_settings,
            font=ctk.CTkFont(weight="bold")
        )
        self.save_button.grid(row=0, column=1, padx=8, pady=16)
        
        # Start button
        self.start_button = ctk.CTkButton(
            control_frame,
            text="Start",
            width=120,
            command=self._on_start_bot,
            fg_color="#10b981",
            hover_color="#059669",
            font=ctk.CTkFont(weight="bold")
        )
        self.start_button.grid(row=0, column=2, padx=8, pady=16)
        
        # Stop button
        self.stop_button = ctk.CTkButton(
            control_frame,
            text="Stop",
            width=120,
            command=self._on_stop_bot,
            fg_color="#ef4444",
            hover_color="#dc2626",
            font=ctk.CTkFont(weight="bold"),
            state="disabled"
        )
        self.stop_button.grid(row=0, column=3, padx=8, pady=16)

    def _load_settings(self) -> None:
        """Load saved settings."""
        if USER_SETTINGS_CACHE.exists():
            self.settings = USER_SETTINGS_CACHE.load_data() or {}
            
            # Apply settings to views
            self.jobs_view.load_settings(self.settings)
            self.emulator_view.load_settings(self.settings)

    def _save_settings(self) -> None:
        """Save current settings."""
        # Collect settings from all views
        settings = {}
        settings.update(self.jobs_view.get_settings())
        settings.update(self.emulator_view.get_settings())
        
        # Cache settings
        USER_SETTINGS_CACHE.cache_data(settings)
        self.settings = settings
        print("Settings saved successfully")

    def _make_job_dictionary(self) -> Dict[str, Any]:
        """Create job dictionary from current settings."""
        job_settings = self.jobs_view.get_settings()
        emulator_settings = self.emulator_view.get_settings()
        
        job_dict = {}
        job_dict.update(job_settings)
        job_dict.update(emulator_settings)
        
        return job_dict

    def _has_no_jobs_selected(self, job_dict: Dict[str, Any]) -> bool:
        """Check if no jobs are selected."""
        job_keys = [
            "card_mastery_user_toggle",
            "classic_1v1_user_toggle", 
            "classic_2v2_user_toggle",
            "trophy_road_user_toggle",
            "upgrade_user_toggle",
        ]
        return not any(job_dict.get(key, False) for key in job_keys)

    def _on_start_bot(self) -> None:
        """Handle start bot button click."""
        if self.controller.is_running():
            return
        
        job_dict = self._make_job_dictionary()
        
        if self._has_no_jobs_selected(job_dict):
            self._show_no_jobs_dialog()
            return
        
        # Save settings before starting
        self._save_settings()
        
        # Disable controls and start bot
        if self.controller.start(job_dict):
            self._update_ui_for_running_state()
            # Switch to stats tab
            self.tabview.set("Stats")

    def _on_stop_bot(self) -> None:
        """Handle stop bot button click."""
        if not self.controller.is_running():
            return
        
        self.controller.stop()
        self._update_ui_for_stopped_state()

    def _show_no_jobs_dialog(self) -> None:
        """Show dialog when no jobs are selected."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("No Jobs Selected")
        dialog.geometry("300x150")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry(f"+{self.winfo_x() + 50}+{self.winfo_y() + 50}")
        
        label = ctk.CTkLabel(
            dialog,
            text="You must select at least one job!",
            font=ctk.CTkFont(size=14)
        )
        label.pack(pady=(30, 20))
        
        button = ctk.CTkButton(
            dialog,
            text="OK",
            width=100,
            command=dialog.destroy
        )
        button.pack(pady=(0, 30))

    def _update_ui_for_running_state(self) -> None:
        """Update UI elements when bot starts running."""
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        
        # Disable settings controls
        self.jobs_view.set_enabled(False)
        self.emulator_view.set_enabled(False)

    def _update_ui_for_stopped_state(self) -> None:
        """Update UI elements when bot stops running."""
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        
        # Re-enable settings controls  
        self.jobs_view.set_enabled(True)
        self.emulator_view.set_enabled(True)

    def _start_status_timer(self) -> None:
        """Start the status update timer."""
        self._update_status()
        self.after(250, self._start_status_timer)  # Update every 250ms

    def _update_status(self) -> None:
        """Update status displays."""
        # Update status pill
        if self.controller.is_running():
            status_info = self.controller.get_status()
            status_text = f"🟢 {status_info['status']}"
            self.status_pill.configure(
                text=status_text,
                fg_color="#10b981"
            )
        else:
            self.status_pill.configure(
                text="⚪ Idle",
                fg_color="#4a5568"
            )
        
        # Update system status panel
        if hasattr(self, 'system_status'):
            self.system_status.update_status(self.controller.get_status())
        
        # Update stats view
        if hasattr(self, 'stats_view'):
            stats = self.controller.get_stats()
            uptime = self.controller.get_uptime()
            self.stats_view.update_stats(stats, uptime, self.controller.get_status())
        
        # Check if thread finished
        if not self.controller.is_running() and self.stop_button.cget("state") == "normal":
            self._update_ui_for_stopped_state()

    def run(self) -> None:
        """Run the GUI main loop."""
        try:
            self.protocol("WM_DELETE_WINDOW", self._on_closing)
            self.mainloop()
        except KeyboardInterrupt:
            self._on_closing()

    def _on_closing(self) -> None:
        """Handle application closing."""
        if self.controller.is_running():
            self.controller.stop()
            # Give some time for graceful shutdown
            self.after(500, self.destroy)
        else:
            self.destroy()