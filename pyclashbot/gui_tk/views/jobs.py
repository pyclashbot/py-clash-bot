"""Jobs view for configuring bot tasks."""

from typing import Any, Dict

import customtkinter as ctk


class JobsView(ctk.CTkFrame):
    """View for configuring bot jobs and tasks."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Initialize widgets dictionary
        self.widgets = {}
        
        # Create the jobs interface
        self._create_jobs_interface()

    def _create_jobs_interface(self) -> None:
        """Create the jobs configuration interface."""
        # Create main scrollable frame
        scrollable = ctk.CTkScrollableFrame(self)
        scrollable.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        scrollable.grid_columnconfigure(0, weight=1)
        
        current_row = 0
        
        # Battle Jobs Section
        current_row = self._create_battle_jobs_section(scrollable, current_row)
        
        # Random Settings Section
        current_row = self._create_random_settings_section(scrollable, current_row)
        
        # Collection Jobs Section
        current_row = self._create_collection_jobs_section(scrollable, current_row)
        
        # Data Settings Section
        self._create_data_settings_section(scrollable, current_row)

    def _create_section_header(self, parent, title: str, row: int) -> int:
        """Create a section header."""
        header_frame = ctk.CTkFrame(parent, height=40, corner_radius=8)
        header_frame.grid(row=row, column=0, sticky="ew", pady=(16, 8))
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)
        
        label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label.grid(row=0, column=0, pady=12)
        
        return row + 1

    def _create_job_checkbox(self, parent, key: str, text: str, row: int, default: bool = False) -> int:
        """Create a job checkbox widget."""
        checkbox = ctk.CTkCheckBox(
            parent,
            text=text,
            font=ctk.CTkFont(size=14)
        )
        checkbox.grid(row=row, column=0, sticky="w", padx=20, pady=8)
        
        if default:
            checkbox.select()
        
        self.widgets[key] = checkbox
        return row + 1

    def _create_battle_jobs_section(self, parent, start_row: int) -> int:
        """Create the battle jobs section."""
        current_row = self._create_section_header(parent, "Battle Jobs", start_row)
        
        # Battle job checkboxes
        current_row = self._create_job_checkbox(
            parent, "trophy_road_user_toggle", "Trophy Road battles", current_row, True
        )
        current_row = self._create_job_checkbox(
            parent, "classic_1v1_user_toggle", "Classic 1v1 battles", current_row
        )
        current_row = self._create_job_checkbox(
            parent, "classic_2v2_user_toggle", "Classic 2v2 battles", current_row
        )
        
        return current_row

    def _create_random_settings_section(self, parent, start_row: int) -> int:
        """Create the random settings section."""
        current_row = self._create_section_header(parent, "Random Settings", start_row)
        
        # Random decks with deck selector
        random_frame = ctk.CTkFrame(parent)
        random_frame.grid(row=current_row, column=0, sticky="ew", padx=20, pady=8)
        random_frame.grid_columnconfigure(0, weight=0)
        random_frame.grid_columnconfigure(1, weight=1)
        
        random_checkbox = ctk.CTkCheckBox(
            random_frame,
            text="Random decks",
            font=ctk.CTkFont(size=14)
        )
        random_checkbox.grid(row=0, column=0, sticky="w", padx=16, pady=12)
        self.widgets["random_decks_user_toggle"] = random_checkbox
        
        # Deck selector frame
        deck_frame = ctk.CTkFrame(random_frame, fg_color="transparent")
        deck_frame.grid(row=0, column=1, sticky="e", padx=16, pady=12)
        
        deck_label = ctk.CTkLabel(deck_frame, text="Deck #:", font=ctk.CTkFont(size=12))
        deck_label.grid(row=0, column=0, padx=(0, 8))
        
        deck_combo = ctk.CTkComboBox(
            deck_frame,
            values=["1", "2", "3", "4", "5"],
            width=80,
            state="readonly"
        )
        deck_combo.set("2")  # Default value
        deck_combo.grid(row=0, column=1)
        self.widgets["deck_number_selection"] = deck_combo
        
        current_row += 1
        
        # Other random settings
        current_row = self._create_job_checkbox(
            parent, "random_plays_user_toggle", "Random plays", current_row
        )
        current_row = self._create_job_checkbox(
            parent, "disable_win_track_toggle", "Skip win/loss check", current_row
        )
        
        return current_row

    def _create_collection_jobs_section(self, parent, start_row: int) -> int:
        """Create the collection jobs section."""
        current_row = self._create_section_header(parent, "Collection Jobs", start_row)
        
        current_row = self._create_job_checkbox(
            parent, "card_mastery_user_toggle", "Card Masteries", current_row
        )
        current_row = self._create_job_checkbox(
            parent, "card_upgrade_user_toggle", "Upgrade Cards", current_row  
        )
        
        return current_row

    def _create_data_settings_section(self, parent, start_row: int) -> int:
        """Create the data settings section."""
        current_row = self._create_section_header(parent, "Data Settings", start_row)
        
        current_row = self._create_job_checkbox(
            parent, "record_fights_toggle", "Record Fights", current_row
        )
        
        return current_row

    def get_settings(self) -> Dict[str, Any]:
        """Get current job settings."""
        settings = {}
        
        # Get checkbox values
        checkbox_keys = [
            "trophy_road_user_toggle",
            "classic_1v1_user_toggle", 
            "classic_2v2_user_toggle",
            "random_decks_user_toggle",
            "random_plays_user_toggle",
            "disable_win_track_toggle",
            "card_mastery_user_toggle",
            "card_upgrade_user_toggle",
            "record_fights_toggle",
        ]
        
        for key in checkbox_keys:
            if key in self.widgets:
                settings[key] = self.widgets[key].get()
        
        # Map card_upgrade_user_toggle to upgrade_user_toggle for backend compatibility
        if "card_upgrade_user_toggle" in settings:
            settings["upgrade_user_toggle"] = settings["card_upgrade_user_toggle"]
        
        # Get deck number selection
        if "deck_number_selection" in self.widgets:
            try:
                settings["deck_number_selection"] = int(self.widgets["deck_number_selection"].get())
            except ValueError:
                settings["deck_number_selection"] = 2
        
        return settings

    def load_settings(self, settings: Dict[str, Any]) -> None:
        """Load settings into the interface."""
        # Handle backend key mapping
        if "upgrade_user_toggle" in settings and "card_upgrade_user_toggle" not in settings:
            settings["card_upgrade_user_toggle"] = settings["upgrade_user_toggle"]
        
        for key, value in settings.items():
            if key in self.widgets:
                widget = self.widgets[key]
                
                if isinstance(widget, ctk.CTkCheckBox):
                    if value:
                        widget.select()
                    else:
                        widget.deselect()
                
                elif isinstance(widget, ctk.CTkComboBox):
                    widget.set(str(value))

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable all controls."""
        state = "normal" if enabled else "disabled"
        
        for widget in self.widgets.values():
            try:
                widget.configure(state=state)
            except Exception:
                pass  # Some widgets may not support state configuration