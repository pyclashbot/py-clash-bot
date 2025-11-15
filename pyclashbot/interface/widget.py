from __future__ import annotations

import tkinter as tk
from tkinter import Canvas
from typing import TYPE_CHECKING

import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, YES

from pyclashbot.interface.enums import (
    BATTLE_STAT_FIELDS,
    BATTLE_STAT_LABELS,
    BOT_STAT_FIELDS,
    BOT_STAT_LABELS,
    COLLECTION_STAT_FIELDS,
    COLLECTION_STAT_LABELS,
    BotStatField,
    StatField,
)

if TYPE_CHECKING:
    from collections.abc import Callable


class StatsWidget(ttk.Toplevel):
    """Transparent widget window for displaying beautiful stats."""

    def __init__(self, parent: ttk.Window, stats_callback: Callable[[], dict[str, object] | None]) -> None:
        super().__init__(parent)
        self.parent = parent
        self.stats_callback = stats_callback
        self._pinned = True  # Start pinned (always on top)
        self._setup_window()
        self._create_widgets()
        self._setup_bindings()
        self._update_stats()

    def _setup_window(self) -> None:
        """Configure the widget window properties."""
        self.title("py-clash-bot - Widget Mode")
        self.geometry("600x400")  # Landscape orientation
        self.resizable(False, False)

        # Make window transparent and always on top
        self.attributes("-alpha", 0.9)  # Slight transparency
        self.attributes("-topmost", True)  # Always on top
        self.attributes("-toolwindow", True)  # Remove from taskbar

        # Remove window decorations for cleaner look
        self.overrideredirect(True)

        # Set window background to be transparent
        self.configure(bg="")

        # Center the widget on screen initially
        self._center_on_screen()

    def _center_on_screen(self) -> None:
        """Center the widget on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _create_widgets(self) -> None:
        """Create the widget UI components."""
        # Main container with glass effect
        self.main_frame = tk.Frame(self, bg="#1a1a1a", relief="flat", bd=0)
        self.main_frame.pack(fill=BOTH, expand=YES, padx=2, pady=2)

        # Title bar for dragging
        self.title_bar = tk.Frame(self.main_frame, bg="#2d2d2d", height=30, relief="flat", bd=0)
        self.title_bar.pack(fill="x", padx=2, pady=(2, 0))
        self.title_bar.pack_propagate(False)

        # Title text
        self.title_label = tk.Label(
            self.title_bar, text="🎮 py-clash-bot Stats", bg="#2d2d2d", fg="#ffffff", font=("Segoe UI", 11, "bold")
        )
        self.title_label.pack(side="left", padx=10, pady=5)

        # Get theme colors
        pinned_color = self._get_theme_color("success", "#ffd700")
        close_color = self._get_theme_color("danger", "#ff6b6b")

        # Pin button
        self.pin_btn = tk.Label(
            self.title_bar, text="📌", bg="#2d2d2d", fg=pinned_color, font=("Segoe UI", 8, "bold"), cursor="hand2"
        )
        self.pin_btn.pack(side="right", padx=(0, 5), pady=5)
        self.pin_btn.bind("<Button-1>", lambda e: self._toggle_pin())
        self.pin_btn.bind("<Enter>", lambda e: self._on_pin_hover(e, True))
        self.pin_btn.bind("<Leave>", lambda e: self._on_pin_hover(e, False))

        # Create tooltip for pin button
        self._create_tooltip(self.pin_btn, "Toggle 'Always on Top'")

        # Close button
        self.close_btn = tk.Label(
            self.title_bar, text="✕", bg="#2d2d2d", fg=close_color, font=("Segoe UI", 10, "bold"), cursor="hand2"
        )
        self.close_btn.pack(side="right", padx=10, pady=5)
        self.close_btn.bind("<Button-1>", lambda e: self._on_close())

        # Create tooltip for close button
        self._create_tooltip(self.close_btn, "Close Widget (Return to Main UI)")

        # Content area with horizontal layout
        self.content_frame = tk.Frame(self.main_frame, bg="#1a1a1a", relief="flat", bd=0)
        self.content_frame.pack(fill=BOTH, expand=YES, padx=2, pady=2)

        # Left column - Win rate gauge and battle stats
        self.left_column = tk.Frame(self.content_frame, bg="#1a1a1a")
        self.left_column.pack(side="left", fill="both", expand=True, padx=(5, 2), pady=5)

        # Right column - Collection and bot stats
        self.right_column = tk.Frame(self.content_frame, bg="#1a1a1a")
        self.right_column.pack(side="right", fill="both", expand=True, padx=(2, 5), pady=5)

        # Win rate gauge at top of left column
        self._create_win_rate_section()

        # Stats sections
        self._create_battle_stats()
        self._create_collection_stats()
        self._create_bot_stats()

    def _create_win_rate_section(self) -> None:
        """Create the win rate gauge section."""
        gauge_container = tk.Frame(self.left_column, bg="#1a1a1a")
        gauge_container.pack(fill="x", padx=10, pady=(10, 5))

        # Title
        title = tk.Label(gauge_container, text="WIN RATE", bg="#1a1a1a", fg="#00aaff", font=("Segoe UI", 12, "bold"))
        title.pack()

        # Create a custom canvas-based gauge for better transparency support
        self.win_gauge_canvas = Canvas(gauge_container, width=120, height=120, bg="#1a1a1a", highlightthickness=0)
        self.win_gauge_canvas.pack(pady=5)

        # Initialize gauge
        self._draw_win_gauge(0)

    def _draw_win_gauge(self, percentage: float) -> None:
        """Draw the win rate gauge on canvas."""
        self.win_gauge_canvas.delete("all")

        cx, cy = 60, 60
        radius = 40
        thickness = 6

        # Background circle
        self.win_gauge_canvas.create_arc(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            outline="#333333",
            width=thickness,
            style="arc",
            start=0,
            extent=360,
        )

        # Progress arc
        if percentage > 0:
            extent = (percentage / 100) * 360
            color = "#00ff88" if percentage >= 50 else "#ffaa00"
            self.win_gauge_canvas.create_arc(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                start=90,
                extent=-extent,
                outline=color,
                width=thickness,
                style="arc",
            )

        # Center text
        self.win_gauge_canvas.create_text(
            cx, cy - 8, text=f"{percentage:.0f}%", fill="#ffffff", font=("Segoe UI", 16, "bold")
        )

        self.win_gauge_canvas.create_text(cx, cy + 8, text="Win Rate", fill="#888888", font=("Segoe UI", 9, "bold"))

    def _create_battle_stats(self) -> None:
        """Create battle statistics section."""
        section = tk.Frame(self.left_column, bg="#252525", relief="flat", bd=0)
        section.pack(fill="both", expand=True, padx=5, pady=5)

        # Section header
        header = tk.Label(section, text="⚔️ BATTLE STATS", bg="#252525", fg="#ff6b6b", font=("Segoe UI", 10, "bold"))
        header.pack(pady=(5, 3))

        # Stats container
        stats_container = tk.Frame(section, bg="#252525")
        stats_container.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        self.battle_labels = {}
        # Show all battle stats in a grid layout
        cols = 2
        for i, field in enumerate(BATTLE_STAT_FIELDS):
            row = i // cols
            col = i % cols

            row_frame = tk.Frame(stats_container, bg="#252525")
            row_frame.grid(row=row, column=col, sticky="ew", padx=2, pady=1)

            # Configure grid weights
            stats_container.columnconfigure(col, weight=1)

            label_text = BATTLE_STAT_LABELS[field].replace(":", "")
            label = tk.Label(
                row_frame, text=label_text, bg="#252525", fg="#cccccc", font=("Segoe UI", 8, "bold"), anchor="w"
            )
            label.pack(side="left", fill="x", expand=True)

            value_var = tk.StringVar(value="0")
            value_label = tk.Label(
                row_frame, textvariable=value_var, bg="#252525", fg="#00aaff", font=("Segoe UI", 9, "bold"), anchor="e"
            )
            value_label.pack(side="right")

            self.battle_labels[field] = value_var

    def _create_collection_stats(self) -> None:
        """Create collection statistics section."""
        section = tk.Frame(self.right_column, bg="#252525", relief="flat", bd=0)
        section.pack(fill="x", padx=5, pady=5)

        # Section header
        header = tk.Label(section, text="💎 COLLECTION", bg="#252525", fg="#ffd700", font=("Segoe UI", 10, "bold"))
        header.pack(pady=(5, 3))

        # Stats container
        stats_container = tk.Frame(section, bg="#252525")
        stats_container.pack(fill="x", padx=5, pady=(0, 5))

        self.collection_labels = {}
        # Show all collection stats
        for field in COLLECTION_STAT_FIELDS:
            row_frame = tk.Frame(stats_container, bg="#252525")
            row_frame.pack(fill="x", pady=1)

            label_text = COLLECTION_STAT_LABELS[field].replace(":", "")
            label = tk.Label(
                row_frame, text=label_text, bg="#252525", fg="#cccccc", font=("Segoe UI", 8, "bold"), anchor="w"
            )
            label.pack(side="left")

            value_var = tk.StringVar(value="0")
            value_label = tk.Label(
                row_frame, textvariable=value_var, bg="#252525", fg="#ffd700", font=("Segoe UI", 9, "bold"), anchor="e"
            )
            value_label.pack(side="right")

            self.collection_labels[field] = value_var

    def _create_bot_stats(self) -> None:
        """Create bot statistics section."""
        section = tk.Frame(self.right_column, bg="#252525", relief="flat", bd=0)
        section.pack(fill="both", expand=True, padx=5, pady=5)

        # Section header
        header = tk.Label(section, text="🤖 BOT STATUS", bg="#252525", fg="#00ff88", font=("Segoe UI", 10, "bold"))
        header.pack(pady=(5, 3))

        # Stats container
        stats_container = tk.Frame(section, bg="#252525")
        stats_container.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        self.bot_labels = {}
        for field in BOT_STAT_FIELDS:
            row_frame = tk.Frame(stats_container, bg="#252525")
            row_frame.pack(fill="x", pady=1)

            label_text = BOT_STAT_LABELS[field].replace(":", "")
            label = tk.Label(
                row_frame, text=label_text, bg="#252525", fg="#cccccc", font=("Segoe UI", 8, "bold"), anchor="w"
            )
            label.pack(side="left")

            value_var = tk.StringVar(value="00:00:00" if field == BotStatField.TIME_SINCE_START else "0")
            value_label = tk.Label(
                row_frame, textvariable=value_var, bg="#252525", fg="#00ff88", font=("Segoe UI", 9, "bold"), anchor="e"
            )
            value_label.pack(side="right")

            self.bot_labels[field] = value_var

    def _setup_bindings(self) -> None:
        """Setup mouse bindings for dragging the window."""
        self.start_x = 0
        self.start_y = 0

        def start_drag(event):
            self.start_x = event.x
            self.start_y = event.y

        def drag(event):
            x = self.winfo_x() + (event.x - self.start_x)
            y = self.winfo_y() + (event.y - self.start_y)
            self.geometry(f"+{x}+{y}")

        self.title_bar.bind("<Button-1>", start_drag)
        self.title_bar.bind("<B1-Motion>", drag)
        self.title_label.bind("<Button-1>", start_drag)
        self.title_label.bind("<B1-Motion>", drag)

    def _update_stats(self) -> None:
        """Update the widget with latest stats."""
        stats = self.stats_callback()
        if not stats:
            # Schedule next update
            self.after(1000, self._update_stats)
            return

        # Update battle stats
        for field, var in self.battle_labels.items():
            value = stats.get(field.value, "0")
            var.set(str(value))

        # Update collection stats
        for field, var in self.collection_labels.items():
            value = stats.get(field.value, "0")
            var.set(str(value))

        # Update bot stats
        for field, var in self.bot_labels.items():
            value = stats.get(field.value, "0")
            var.set(str(value))

        # Update win rate gauge
        wins = int(stats.get(StatField.WINS.value, 0))
        losses = int(stats.get(StatField.LOSSES.value, 0))
        total = wins + losses
        winrate = (wins / total * 100) if total > 0 else 0
        self._draw_win_gauge(winrate)

        # Schedule next update
        self.after(1000, self._update_stats)

    def _get_theme_color(self, color_type: str, fallback: str) -> str:
        """Get theme color from parent or use fallback."""
        try:
            if hasattr(self.parent, "style") and hasattr(self.parent.style, "colors"):
                # Try to get color from ttkbootstrap theme
                if color_type == "success":
                    return getattr(self.parent.style.colors, "success", fallback)
                elif color_type == "secondary":
                    return getattr(self.parent.style.colors, "secondary", fallback)
                elif color_type == "primary":
                    return getattr(self.parent.style.colors, "primary", fallback)
                elif color_type == "danger":
                    return getattr(self.parent.style.colors, "danger", fallback)
        except (AttributeError, TypeError):
            pass
        return fallback

    def _create_tooltip(self, widget: tk.Widget, text: str) -> None:
        """Create a simple tooltip for a widget."""

        def on_enter(event):
            # Create tooltip window
            tooltip = tk.Toplevel(self)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

            label = tk.Label(
                tooltip,
                text=text,
                bg="#333333",
                fg="#ffffff",
                font=("Segoe UI", 9, "bold"),
                relief="solid",
                borderwidth=1,
                padx=5,
                pady=2,
            )
            label.pack()

            # Store tooltip reference on widget instance
            widget._tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, "_tooltip"):
                widget._tooltip.destroy()
                delattr(widget, "_tooltip")

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def _toggle_pin(self) -> None:
        """Toggle pin state - always on top vs normal window."""
        self._pinned = not self._pinned
        self._update_pin_display()
        self._update_window_attributes()

    def _update_pin_display(self) -> None:
        """Update pin button appearance based on state."""
        # Get theme colors from parent if available
        pinned_color = self._get_theme_color("success", "#ffd700")  # Gold fallback
        unpinned_color = self._get_theme_color("secondary", "#888888")  # Gray fallback

        if self._pinned:
            self.pin_btn.configure(text="📌", fg=pinned_color)
        else:
            self.pin_btn.configure(text="📍", fg=unpinned_color)

    def _update_window_attributes(self) -> None:
        """Update window attributes based on pin state."""
        if self._pinned:
            self.attributes("-topmost", True)  # Always on top
        else:
            self.attributes("-topmost", False)  # Normal window behavior

    def _on_pin_hover(self, event, entering: bool) -> None:
        """Handle pin button hover effects."""
        if entering:
            # Show tooltip or change cursor
            self.pin_btn.configure(cursor="hand2")
            # You could add a tooltip here if needed
        else:
            self.pin_btn.configure(cursor="hand2")

    def _on_close(self) -> None:
        """Handle close button click - restore main UI and destroy widget."""
        if hasattr(self.parent, "deiconify"):
            self.parent.deiconify()

        # Update parent's widget mode button
        if hasattr(self.parent, "_update_widget_mode_button"):
            self.parent._update_widget_mode_button(False)

        self.destroy()

    def show(self) -> None:
        """Show the widget and hide main UI."""
        # Hide main UI
        if hasattr(self.parent, "withdraw"):
            self.parent.withdraw()

        # Show widget
        self.deiconify()
        self.lift()

        # Ensure pin state is applied
        self._update_window_attributes()

    def hide(self) -> None:
        """Hide the widget and restore main UI."""
        # Hide widget
        self.withdraw()

        # Restore main UI
        if hasattr(self.parent, "deiconify"):
            self.parent.deiconify()
