from __future__ import annotations

import sys
import tkinter as tk

import ttkbootstrap as ttk


class ScrollableFrame(ttk.Frame):
    """Vertical scroll area that shows a scrollbar only when content overflows."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._canvas = tk.Canvas(self, highlightthickness=0, borderwidth=0)
        self._scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self.inner = ttk.Frame(self._canvas)

        self._inner_window = self._canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._scrollbar.grid(row=0, column=1, sticky="ns")
        self._scrollbar.grid_remove()

        self.inner.bind("<Configure>", self._on_inner_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind("<Enter>", self._bind_mousewheel)
        self._canvas.bind("<Leave>", self._unbind_mousewheel)
        self._mousewheel_bound = False

    def _on_inner_configure(self, _event: tk.Event) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        self._update_scrollbar_visibility()

    def _on_canvas_configure(self, event: tk.Event) -> None:
        self._canvas.itemconfigure(self._inner_window, width=event.width)
        self._update_scrollbar_visibility()

    def _update_scrollbar_visibility(self) -> None:
        self.update_idletasks()
        canvas_height = self._canvas.winfo_height()
        inner_height = self.inner.winfo_reqheight()
        if inner_height > canvas_height:
            self._scrollbar.grid(row=0, column=1, sticky="ns")
        else:
            self._scrollbar.grid_remove()
            self._canvas.yview_moveto(0)

    def _bind_mousewheel(self, _event: tk.Event) -> None:
        if self._mousewheel_bound:
            return
        self._mousewheel_bound = True
        if sys.platform == "darwin":
            self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        else:
            self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)
            self._canvas.bind_all("<Button-4>", self._on_mousewheel_linux_up)
            self._canvas.bind_all("<Button-5>", self._on_mousewheel_linux_down)

    def _unbind_mousewheel(self, _event: tk.Event) -> None:
        if not self._mousewheel_bound:
            return
        self._mousewheel_bound = False
        self._canvas.unbind_all("<MouseWheel>")
        if sys.platform != "darwin":
            self._canvas.unbind_all("<Button-4>")
            self._canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event: tk.Event) -> None:
        if sys.platform == "darwin":
            delta = -1 * int(event.delta)
        else:
            delta = -1 * int(event.delta / 120)
        self._canvas.yview_scroll(delta, "units")

    def _on_mousewheel_linux_up(self, _event: tk.Event) -> None:
        self._canvas.yview_scroll(-1, "units")

    def _on_mousewheel_linux_down(self, _event: tk.Event) -> None:
        self._canvas.yview_scroll(1, "units")


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
        self._arc_fg: int | None = None
        self._arc_bg: int | None = None
        self._text: int | None = None
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
        label_size = 14 if self.diameter <= 80 else 16
        self._text = self.create_text(
            centre,
            centre,
            text="0%",
            fill=self.text_colour,
            font=("-size", label_size, "-weight", "bold"),
        )

    def _draw_dynamic(
        self,
        percent: float,
        label: str,
        fg_colour: str | None = None,
        text_colour: str | None = None,
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
        fg_colour: str | None = None,
        text_colour: str | None = None,
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
