"""Statistics view for displaying bot performance metrics."""

from typing import Any, Dict

import customtkinter as ctk


class MetricTile(ctk.CTkFrame):
    """A tile widget for displaying a metric."""

    def __init__(self, parent, title: str, value: str = "0", color: str = "#14b8a6"):
        super().__init__(parent, corner_radius=12)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        
        # Value label (large)
        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=color
        )
        self.value_label.grid(row=0, column=0, pady=(12, 2), sticky="n")
        
        # Title label (smaller)
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=11),
            text_color="#a0aec0"
        )
        self.title_label.grid(row=1, column=0, pady=(2, 12), sticky="n")

    def update_value(self, value: str) -> None:
        """Update the tile's value."""
        self.value_label.configure(text=value)


class StatusPill(ctk.CTkFrame):
    """A pill-shaped status indicator."""

    def __init__(self, parent, text: str = "Idle", color: str = "#4a5568"):
        super().__init__(parent, corner_radius=20, height=32)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_propagate(False)
        
        self.label = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white"
        )
        self.label.grid(row=0, column=0, padx=16, pady=6)
        
        self.configure(fg_color=color)

    def update_status(self, text: str, color: str) -> None:
        """Update the status pill."""
        self.label.configure(text=text)
        self.configure(fg_color=color)


class StatsView(ctk.CTkFrame):
    """View for displaying bot statistics and performance metrics."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Main content
        
        # Create stats interface
        self._create_stats_interface()

    def _create_stats_interface(self) -> None:
        """Create the statistics interface."""
        # Create main scrollable frame
        scrollable = ctk.CTkScrollableFrame(self)
        scrollable.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        scrollable.grid_columnconfigure(0, weight=1)
        scrollable.grid_columnconfigure(1, weight=1)
        
        current_row = 0
        
        # Battle Metrics Section
        current_row = self._create_battle_metrics_section(scrollable, current_row)
        
        # Collection Metrics Section
        current_row = self._create_collection_metrics_section(scrollable, current_row)
        
        # Bot Status Section
        current_row = self._create_bot_status_section(scrollable, current_row)

    def _create_section_header(self, parent, title: str, row: int, columnspan: int = 2) -> int:
        """Create a section header."""
        header_frame = ctk.CTkFrame(parent, height=32, corner_radius=8)
        header_frame.grid(row=row, column=0, columnspan=columnspan, sticky="ew", pady=(8, 4))
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)
        
        label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        label.grid(row=0, column=0, pady=8)
        
        return row + 1

    def _create_battle_metrics_section(self, parent, start_row: int) -> int:
        """Create the battle metrics section."""
        current_row = self._create_section_header(parent, "Battle Statistics", start_row)
        
        # Battle metrics tiles
        metrics_frame = ctk.CTkFrame(parent)
        metrics_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=0, pady=4)
        metrics_frame.grid_columnconfigure(0, weight=1)
        metrics_frame.grid_columnconfigure(1, weight=1)
        metrics_frame.grid_columnconfigure(2, weight=1)
        metrics_frame.grid_columnconfigure(3, weight=1)
        
        # Create metric tiles
        self.wins_tile = MetricTile(metrics_frame, "Wins", "0", "#10b981")
        self.wins_tile.grid(row=0, column=0, padx=4, pady=6, sticky="ew")
        
        self.losses_tile = MetricTile(metrics_frame, "Losses", "0", "#ef4444")
        self.losses_tile.grid(row=0, column=1, padx=4, pady=6, sticky="ew")
        
        self.winrate_tile = MetricTile(metrics_frame, "Win Rate", "0%", "#14b8a6")
        self.winrate_tile.grid(row=0, column=2, padx=4, pady=6, sticky="ew")
        
        self.runtime_tile = MetricTile(metrics_frame, "Runtime", "00:00:00", "#8b5cf6")
        self.runtime_tile.grid(row=0, column=3, padx=4, pady=6, sticky="ew")
        
        current_row += 1
        
        # Battle types frame
        battle_types_frame = ctk.CTkFrame(parent)
        battle_types_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=0, pady=4)
        battle_types_frame.grid_columnconfigure(0, weight=1)
        battle_types_frame.grid_columnconfigure(1, weight=1)
        battle_types_frame.grid_columnconfigure(2, weight=1)
        
        self.classic_1v1_tile = MetricTile(battle_types_frame, "Classic 1v1", "0", "#f59e0b")
        self.classic_1v1_tile.grid(row=0, column=0, padx=4, pady=6, sticky="ew")
        
        self.classic_2v2_tile = MetricTile(battle_types_frame, "Classic 2v2", "0", "#f59e0b")
        self.classic_2v2_tile.grid(row=0, column=1, padx=4, pady=6, sticky="ew")
        
        self.trophy_road_tile = MetricTile(battle_types_frame, "Trophy Road", "0", "#f59e0b")
        self.trophy_road_tile.grid(row=0, column=2, padx=4, pady=6, sticky="ew")
        
        return current_row + 1

    def _create_collection_metrics_section(self, parent, start_row: int) -> int:
        """Create the collection metrics section."""
        current_row = self._create_section_header(parent, "Collection Statistics", start_row)
        
        # Collection metrics frame
        collection_frame = ctk.CTkFrame(parent)
        collection_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=0, pady=4)
        collection_frame.grid_columnconfigure(0, weight=1)
        collection_frame.grid_columnconfigure(1, weight=1)
        collection_frame.grid_columnconfigure(2, weight=1)
        
        self.masteries_tile = MetricTile(collection_frame, "Card Masteries", "0", "#06b6d4")
        self.masteries_tile.grid(row=0, column=0, padx=4, pady=6, sticky="ew")
        
        self.upgrades_tile = MetricTile(collection_frame, "Upgrades", "0", "#06b6d4")
        self.upgrades_tile.grid(row=0, column=1, padx=4, pady=6, sticky="ew")
        
        self.war_chests_tile = MetricTile(collection_frame, "War Chests", "0", "#06b6d4")
        self.war_chests_tile.grid(row=0, column=2, padx=4, pady=6, sticky="ew")
        
        return current_row + 1

    def _create_bot_status_section(self, parent, start_row: int) -> int:
        """Create the bot status section."""
        current_row = self._create_section_header(parent, "Bot Status", start_row)
        
        # Status frame
        status_frame = ctk.CTkFrame(parent)
        status_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=0, pady=4)
        status_frame.grid_columnconfigure(0, weight=1)
        status_frame.grid_columnconfigure(1, weight=1)
        status_frame.grid_columnconfigure(2, weight=1)
        
        # Current status
        status_info_frame = ctk.CTkFrame(status_frame)
        status_info_frame.grid(row=0, column=0, padx=4, pady=6, sticky="ew")
        status_info_frame.grid_columnconfigure(0, weight=1)
        
        status_title = ctk.CTkLabel(
            status_info_frame,
            text="Current Status",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        status_title.grid(row=0, column=0, pady=(8, 4))
        
        self.status_pill = StatusPill(status_info_frame, "Idle", "#4a5568")
        self.status_pill.grid(row=1, column=0, pady=(4, 8), sticky="ew", padx=8)
        
        # Current state
        state_info_frame = ctk.CTkFrame(status_frame)
        state_info_frame.grid(row=0, column=1, padx=4, pady=6, sticky="ew")
        state_info_frame.grid_columnconfigure(0, weight=1)
        
        state_title = ctk.CTkLabel(
            state_info_frame,
            text="Current State",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        state_title.grid(row=0, column=0, pady=(8, 4))
        
        self.current_state_label = ctk.CTkLabel(
            state_info_frame,
            text="--",
            font=ctk.CTkFont(size=12),
            text_color="#a0aec0"
        )
        self.current_state_label.grid(row=1, column=0, pady=(4, 8))
        
        # Bot failures
        failures_info_frame = ctk.CTkFrame(status_frame)
        failures_info_frame.grid(row=0, column=2, padx=4, pady=6, sticky="ew")
        
        self.failures_tile = MetricTile(failures_info_frame, "Bot Failures", "0", "#ef4444")
        self.failures_tile.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        
        return current_row + 1

    def update_stats(self, stats: Dict[str, Any], uptime: str, status_info: Dict[str, str]) -> None:
        """Update all statistics displays."""
        # Update battle metrics
        self.wins_tile.update_value(str(stats.get("wins", 0)))
        self.losses_tile.update_value(str(stats.get("losses", 0)))
        
        # Calculate and update win rate
        wins = stats.get("wins", 0)
        losses = stats.get("losses", 0)
        total = wins + losses
        if total > 0:
            winrate = round((wins / total) * 100, 1)
            self.winrate_tile.update_value(f"{winrate}%")
        else:
            self.winrate_tile.update_value("0%")
        
        self.runtime_tile.update_value(uptime)
        
        # Update battle types
        self.classic_1v1_tile.update_value(str(stats.get("classic_1v1_fights", 0)))
        self.classic_2v2_tile.update_value(str(stats.get("classic_2v2_fights", 0)))
        self.trophy_road_tile.update_value(str(stats.get("trophy_road_1v1_fights", 0)))
        
        # Update collection metrics
        self.masteries_tile.update_value(str(stats.get("card_mastery_reward_collections", 0)))
        self.upgrades_tile.update_value(str(stats.get("upgrades", 0)))
        self.war_chests_tile.update_value(str(stats.get("war_chest_collects", 0)))
        
        # Update bot status
        status = status_info.get("status", "Idle")
        current_state = status_info.get("current_state", "--")
        
        if status == "Idle":
            self.status_pill.update_status("⚪ Idle", "#4a5568")
        elif "Running" in status or "Starting" in status:
            self.status_pill.update_status(f"🟢 {status}", "#10b981")
        elif "Stopping" in status:
            self.status_pill.update_status(f"🟡 {status}", "#f59e0b")
        else:
            self.status_pill.update_status(f"🔴 {status}", "#ef4444")
        
        self.current_state_label.configure(text=current_state if current_state else "--")
        self.failures_tile.update_value(str(stats.get("restarts_after_failure", 0)))