import FreeSimpleGUI as sg  # noqa: N813

# Clean navy/yellow theme for readability
THEME = "DarkBlue3"

# Apply the theme
sg.theme(THEME)

# Navy blue and yellow color scheme
COLORS = {
    "navy": "#1e3a8a",
    "light_navy": "#3b82f6",
    "yellow": "#fbbf24",
    "light_yellow": "#fef3c7",
    "white": "#ffffff",
    "light_gray": "#f9fafb",
    "dark_text": "#1f2937",
    "light_text": "#6b7280",
}

# Apply minimal styling for clean appearance
sg.set_options(
    font=("Arial", 9),
    element_padding=(3, 2),
    margins=(5, 5),
    border_width=1,
    button_color=(COLORS["white"], COLORS["navy"]),
    progress_meter_color=COLORS["yellow"],
)
