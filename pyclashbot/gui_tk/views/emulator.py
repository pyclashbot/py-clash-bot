"""Emulator view for configuring emulator settings."""

from typing import Any, Dict

import customtkinter as ctk


class EmulatorView(ctk.CTkFrame):
    """View for configuring emulator settings."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Initialize widgets dictionary
        self.widgets = {}
        
        # Create the emulator interface
        self._create_emulator_interface()

    def _create_emulator_interface(self) -> None:
        """Create the emulator configuration interface."""
        # Create main scrollable frame
        scrollable = ctk.CTkScrollableFrame(self)
        scrollable.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        scrollable.grid_columnconfigure(0, weight=1)
        
        current_row = 0
        
        # Emulator Provider Section
        current_row = self._create_provider_section(scrollable, current_row)
        
        # Combined Configuration Section (MEmu/Google Play specific)
        current_row = self._create_configuration_section(scrollable, current_row)
        
        # Tips Section
        self._create_tips_section(scrollable, current_row)

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

    def _create_provider_section(self, parent, start_row: int) -> int:
        """Create the emulator provider selection section."""
        current_row = self._create_section_header(parent, "Emulator Provider", start_row)
        
        # Provider selection frame
        provider_frame = ctk.CTkFrame(parent)
        provider_frame.grid(row=current_row, column=0, sticky="ew", padx=20, pady=8)
        provider_frame.grid_columnconfigure(0, weight=1)
        
        # Segmented button for provider selection
        provider_var = ctk.StringVar(value="MEmu")
        provider_segment = ctk.CTkSegmentedButton(
            provider_frame,
            values=["MEmu", "Google Play Games"],
            variable=provider_var,
            command=self._on_provider_change
        )
        provider_segment.grid(row=0, column=0, padx=20, pady=16)
        
        # Store references
        self.widgets["provider_var"] = provider_var
        self.widgets["provider_segment"] = provider_segment
        
        return current_row + 1

    def _create_configuration_section(self, parent, start_row: int) -> int:
        """Create the unified configuration section that switches based on emulator type."""
        current_row = self._create_section_header(parent, "Configuration", start_row)
        
        # Configuration container frame
        self.config_container = ctk.CTkFrame(parent)
        self.config_container.grid(row=current_row, column=0, sticky="ew", padx=20, pady=8)
        self.config_container.grid_columnconfigure(0, weight=1)
        
        # MEmu Render Mode Frame
        self.memu_config_frame = ctk.CTkFrame(self.config_container)
        self.memu_config_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=16)
        self.memu_config_frame.grid_columnconfigure(0, weight=1)
        
        memu_label = ctk.CTkLabel(
            self.memu_config_frame,
            text="Render Mode:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        memu_label.grid(row=0, column=0, pady=(0, 8))
        
        render_var = ctk.StringVar(value="OpenGL")
        render_segment = ctk.CTkSegmentedButton(
            self.memu_config_frame,
            values=["DirectX", "OpenGL"],
            variable=render_var
        )
        render_segment.grid(row=1, column=0, pady=(0, 16))
        
        # Store references
        self.widgets["render_var"] = render_var
        self.widgets["render_segment"] = render_segment
        
        # Google Play Graphics Frame
        self.gplay_config_frame = ctk.CTkFrame(self.config_container)
        self.gplay_config_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=16)
        self.gplay_config_frame.grid_columnconfigure(0, weight=1)
        self.gplay_config_frame.grid_columnconfigure(1, weight=1)
        
        gplay_label = ctk.CTkLabel(
            self.gplay_config_frame,
            text="Graphics Settings:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        gplay_label.grid(row=0, column=0, columnspan=2, pady=(0, 12))
        
        # Create checkboxes for graphics options
        graphics_options = [
            ("angle", "ANGLE (Hardware acceleration)"),
            ("vulkan", "Vulkan API"),
            ("gles", "OpenGL ES"),
            ("surfaceless", "Surfaceless rendering"),
            ("egl", "EGL interface"),
        ]
        
        row_offset = 1
        for i, (key, label) in enumerate(graphics_options):
            checkbox = ctk.CTkCheckBox(
                self.gplay_config_frame,
                text=label,
                font=ctk.CTkFont(size=12)
            )
            col = i % 2
            grid_row = row_offset + (i // 2)
            checkbox.grid(row=grid_row, column=col, sticky="w", padx=16, pady=4)
            self.widgets[f"gfx_{key}"] = checkbox
        
        # Backend and WSI on last row
        last_row = row_offset + ((len(graphics_options) - 1) // 2) + 1
        
        backend_label = ctk.CTkLabel(
            self.gplay_config_frame,
            text="Backend:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        backend_label.grid(row=last_row, column=0, sticky="w", padx=16, pady=(8, 4))
        
        backend_combo = ctk.CTkComboBox(
            self.gplay_config_frame,
            values=["gfxstream", "swiftshader", "auto"],
            width=120,
            state="readonly"
        )
        backend_combo.set("gfxstream")
        backend_combo.grid(row=last_row + 1, column=0, sticky="w", padx=16, pady=(0, 4))
        self.widgets["gfx_backend"] = backend_combo
        
        wsi_label = ctk.CTkLabel(
            self.gplay_config_frame,
            text="WSI:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        wsi_label.grid(row=last_row, column=1, sticky="w", padx=16, pady=(8, 4))
        
        wsi_combo = ctk.CTkComboBox(
            self.gplay_config_frame,
            values=["surface", "headless", "auto"],
            width=120,
            state="readonly"
        )
        wsi_combo.set("surface")
        wsi_combo.grid(row=last_row + 1, column=1, sticky="w", padx=16, pady=(0, 16))
        self.widgets["gfx_wsi"] = wsi_combo
        
        # Initially hide Google Play frame (MEmu is default)
        self.gplay_config_frame.grid_remove()
        
        return current_row + 1

    def _create_tips_section(self, parent, start_row: int) -> int:
        """Create the tips section."""
        current_row = self._create_section_header(parent, "Tips", start_row)
        
        # Tips frame
        tips_frame = ctk.CTkFrame(parent)
        tips_frame.grid(row=current_row, column=0, sticky="ew", padx=20, pady=8)
        tips_frame.grid_columnconfigure(0, weight=1)
        
        # Tips text
        tips_text = """💡 Emulator Tips:

• MEmu: Traditional emulator with DirectX/OpenGL rendering options
• Google Play Games: Newer Android gaming platform
• If experiencing issues, try switching render modes (MEmu only)
• Ensure your selected emulator is installed and running"""
        
        tips_label = ctk.CTkLabel(
            tips_frame,
            text=tips_text,
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="nw"
        )
        tips_label.grid(row=0, column=0, padx=20, pady=16, sticky="w")
        
        return current_row + 1

    def _on_provider_change(self, value: str) -> None:
        """Handle provider selection change."""
        # Show/hide configuration frames based on provider
        if value == "MEmu":
            self.memu_config_frame.grid()
            self.gplay_config_frame.grid_remove()
        else:  # Google Play Games
            self.memu_config_frame.grid_remove()
            self.gplay_config_frame.grid()

    def get_settings(self) -> Dict[str, Any]:
        """Get current emulator settings."""
        settings = {}
        
        # Get provider selection
        provider = self.widgets["provider_var"].get()
        if provider == "MEmu":
            settings["memu_emulator_toggle"] = True
            settings["google_play_emulator_toggle"] = False
            settings["emulator"] = "MEmu"
        else:  # Google Play Games
            settings["memu_emulator_toggle"] = False
            settings["google_play_emulator_toggle"] = True
            settings["emulator"] = "Google Play"
        
        # Get render mode (only for MEmu)
        render_mode = self.widgets["render_var"].get()
        if render_mode == "DirectX":
            settings["directx_toggle"] = True
            settings["opengl_toggle"] = False
            settings["memu_render_mode"] = "directx"
        else:  # OpenGL
            settings["directx_toggle"] = False
            settings["opengl_toggle"] = True
            settings["memu_render_mode"] = "opengl"
        
        # Get graphics settings (only for Google Play)
        if provider == "Google Play Games":
            graphics_settings = {}
            
            # Get checkbox values
            for key in ["angle", "vulkan", "gles", "surfaceless", "egl"]:
                widget_key = f"gfx_{key}"
                if widget_key in self.widgets:
                    graphics_settings[key] = self.widgets[widget_key].get()
            
            # Get dropdown values
            if "gfx_backend" in self.widgets:
                graphics_settings["backend"] = self.widgets["gfx_backend"].get()
            if "gfx_wsi" in self.widgets:
                graphics_settings["wsi"] = self.widgets["gfx_wsi"].get()
            
            settings["google_play_graphics"] = graphics_settings
        
        return settings

    def load_settings(self, settings: Dict[str, Any]) -> None:
        """Load settings into the interface."""
        # Load provider setting and update configuration display
        if settings.get("google_play_emulator_toggle", False):
            provider = "Google Play Games"
            self.widgets["provider_var"].set(provider)
            self.memu_config_frame.grid_remove()
            self.gplay_config_frame.grid()
        else:
            provider = "MEmu" 
            self.widgets["provider_var"].set(provider)
            self.memu_config_frame.grid()
            self.gplay_config_frame.grid_remove()
        
        # Load render mode setting (MEmu)
        if settings.get("directx_toggle", False):
            self.widgets["render_var"].set("DirectX")
        else:
            self.widgets["render_var"].set("OpenGL")
        
        # Update the segmented buttons
        self.widgets["provider_segment"].set(provider)
        self.widgets["render_segment"].set(self.widgets["render_var"].get())
        
        # Load graphics settings (Google Play)
        graphics_settings = settings.get("google_play_graphics", {})
        for key in ["angle", "vulkan", "gles", "surfaceless", "egl"]:
            widget_key = f"gfx_{key}"
            if widget_key in self.widgets:
                if graphics_settings.get(key, False):
                    self.widgets[widget_key].select()
                else:
                    self.widgets[widget_key].deselect()
        
        # Load dropdown settings (Google Play)
        if "gfx_backend" in self.widgets and "backend" in graphics_settings:
            self.widgets["gfx_backend"].set(graphics_settings["backend"])
        if "gfx_wsi" in self.widgets and "wsi" in graphics_settings:
            self.widgets["gfx_wsi"].set(graphics_settings["wsi"])

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable all controls."""
        state = "normal" if enabled else "disabled"
        
        # Enable/disable all widgets
        for widget in self.widgets.values():
            try:
                widget.configure(state=state)
            except Exception:
                pass  # Handle any configuration errors gracefully