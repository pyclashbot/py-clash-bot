"""Reusable panel widgets for the Royale Engine GUI."""

from typing import Callable, Dict

import customtkinter as ctk


class BotControlPanel(ctk.CTkFrame):
    """Panel with bot control buttons."""

    def __init__(self, parent, start_callback: Callable, stop_callback: Callable):
        super().__init__(parent, corner_radius=12)
        
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Content
        
        self._create_panel()

    def _create_panel(self) -> None:
        """Create the bot control panel."""
        # Header
        header_label = ctk.CTkLabel(
            self,
            text="Bot Control",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header_label.grid(row=0, column=0, pady=(16, 8), sticky="w", padx=16)
        
        # Content frame
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(8, 16))
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Start button
        self.start_button = ctk.CTkButton(
            content_frame,
            text="▶️ Start Bot",
            command=self.start_callback,
            height=36,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669"
        )
        self.start_button.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        
        # Stop button
        self.stop_button = ctk.CTkButton(
            content_frame,
            text="⏹️ Stop Bot",
            command=self.stop_callback,
            height=36,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#ef4444",
            hover_color="#dc2626",
            state="disabled"
        )
        self.stop_button.grid(row=1, column=0, sticky="ew")

    def set_running_state(self, running: bool) -> None:
        """Update button states based on running status."""
        if running:
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
        else:
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")


class SystemStatusPanel(ctk.CTkFrame):
    """Panel showing system status information."""

    def __init__(self, parent):
        super().__init__(parent, corner_radius=12)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Content
        
        self._create_panel()

    def _create_panel(self) -> None:
        """Create the system status panel."""
        # Header
        header_label = ctk.CTkLabel(
            self,
            text="System Status",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header_label.grid(row=0, column=0, pady=(16, 8), sticky="w", padx=16)
        
        # Content frame
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(8, 16))
        content_frame.grid_columnconfigure(0, weight=0)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Connection status
        connection_label = ctk.CTkLabel(
            content_frame,
            text="Connection:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        connection_label.grid(row=0, column=0, sticky="w", pady=2)
        
        self.connection_status = ctk.CTkLabel(
            content_frame,
            text="🟢 Online",
            font=ctk.CTkFont(size=12),
            text_color="#10b981"
        )
        self.connection_status.grid(row=0, column=1, sticky="e", pady=2)
        
        # Bot status
        status_label = ctk.CTkLabel(
            content_frame,
            text="Status:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        status_label.grid(row=1, column=0, sticky="w", pady=2)
        
        self.bot_status = ctk.CTkLabel(
            content_frame,
            text="Idle",
            font=ctk.CTkFont(size=12),
            text_color="#a0aec0"
        )
        self.bot_status.grid(row=1, column=1, sticky="e", pady=2)
        
        # Current state
        state_label = ctk.CTkLabel(
            content_frame,
            text="State:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        state_label.grid(row=2, column=0, sticky="w", pady=2)
        
        self.current_state = ctk.CTkLabel(
            content_frame,
            text="--",
            font=ctk.CTkFont(size=12),
            text_color="#a0aec0"
        )
        self.current_state.grid(row=2, column=1, sticky="e", pady=2)

    def update_status(self, status_info: Dict[str, str]) -> None:
        """Update the status information."""
        status = status_info.get("status", "Idle")
        current_state = status_info.get("current_state", "--")
        
        # Update bot status with color
        if status == "Idle":
            self.bot_status.configure(text=status, text_color="#a0aec0")
        elif "Running" in status or "Starting" in status:
            self.bot_status.configure(text=status, text_color="#10b981")
        elif "Stopping" in status:
            self.bot_status.configure(text=status, text_color="#f59e0b")
        else:
            self.bot_status.configure(text=status, text_color="#ef4444")
        
        # Update current state
        self.current_state.configure(text=current_state if current_state else "--")


class QuickGuidePanel(ctk.CTkFrame):
    """Panel showing quick guide information."""

    def __init__(self, parent):
        super().__init__(parent, corner_radius=12)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Content
        
        self._create_panel()

    def _create_panel(self) -> None:
        """Create the quick guide panel."""
        # Header
        header_label = ctk.CTkLabel(
            self,
            text="Quick Guide",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header_label.grid(row=0, column=0, pady=(16, 8), sticky="w", padx=16)
        
        # Content frame with scrollable text
        content_frame = ctk.CTkScrollableFrame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=(8, 16))
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Guide text
        guide_text = """🚀 Getting Started:

• Select your desired jobs in the Jobs tab
• Configure your emulator in the Emulator tab
• Save settings before starting the bot
• Monitor progress in the Stats tab

📋 Key Features:

• Trophy Road: Automated ladder battles
• Classic Battles: 1v1 and 2v2 matches
• Collection Jobs: Card masteries & upgrades
• Random Settings: Deck variety & plays

⚙️ Tips:

• Start with Classic 2v2 or Classic 1v1 to avoid losing trophies
• Enable Random Decks to farm all card masteries efficiently
• Disable Random Decks to grind out a single deck for mastery
• Check emulator compatibility first
• Monitor stats for performance tracking
• Save settings regularly"""
        
        guide_label = ctk.CTkLabel(
            content_frame,
            text=guide_text,
            font=ctk.CTkFont(size=11),
            justify="left",
            anchor="nw"
        )
        guide_label.grid(row=0, column=0, sticky="ew")