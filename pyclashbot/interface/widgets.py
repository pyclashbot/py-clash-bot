from __future__ import annotations

from typing import Optional

import tkinter as tk


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
    ) -> None:
        size = diameter + thickness + 4
        super().__init__(master, width=size, height=size, highlightthickness=0, **kwargs)
        self.diameter = diameter
        self.thickness = thickness
        self.start_angle = start_angle
        self.foreground_colour = fg
        self.background_colour = bg
        self.text_colour = text_color
        self._value = 0.0
        self._arc_fg: Optional[int] = None
        self._arc_bg: Optional[int] = None
        self._text: Optional[int] = None
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
