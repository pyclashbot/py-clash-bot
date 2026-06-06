"""Enumerate every PyClashBotUI tab/state, screenshot each, save to disk.

UI states captured:
  - Jobs tab
  - Emulator tab x 4 sub-states (MEmu, Google Play, BlueStacks, ADB)
  - Stats tab
  - Misc tab

Output: tests/interface/screenshots/*.png

Run directly:
    py tests/interface/test_ui_screenshots.py
"""

from __future__ import annotations

import random
import sys
import time
from pathlib import Path

from PIL import ImageGrab

from pyclashbot.emulators import EmulatorType
from pyclashbot.interface.enums import PRIMARY_JOB_TOGGLES, UIField
from pyclashbot.interface.ui import PyClashBotUI

OUT_DIR = Path(__file__).parent / "screenshots"


def _settle(ui: PyClashBotUI, ticks: int = 30, pause_s: float = 0.0) -> None:
    """Pump the event loop so the requested layout actually paints before we grab."""
    for _ in range(ticks):
        ui.update_idletasks()
        ui.update()
        if pause_s:
            time.sleep(pause_s)  # noqa: TID251 — test-only compositor pacing, no worker context here


def _grab_window(ui: PyClashBotUI, out_path: Path) -> tuple[int, int]:
    # Force window to the foreground so nothing composites over it during the grab.
    ui.lift()
    ui.attributes("-topmost", True)
    ui.focus_force()
    _settle(ui, ticks=20, pause_s=0.01)
    # Extra settle: Windows compositor needs a beat after a topmost/lift to fully repaint.
    time.sleep(0.4)  # noqa: TID251 — test-only compositor pacing, no worker context here
    _settle(ui, ticks=10)
    x = ui.winfo_rootx()
    y = ui.winfo_rooty()
    w = ui.winfo_width()
    h = ui.winfo_height()
    img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    ui.attributes("-topmost", False)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    return img.size


def _select_tab(ui: PyClashBotUI, text: str) -> None:
    for tab_id in ui.notebook.tabs():
        if ui.notebook.tab(tab_id, "text") == text:
            ui.notebook.select(tab_id)
            return
    raise RuntimeError(f"tab not found: {text!r}")


def capture_all() -> dict[str, tuple[int, int]]:
    ui = PyClashBotUI()
    ui.geometry("490x550+50+50")
    ui.deiconify()
    _settle(ui, ticks=60)

    results: dict[str, tuple[int, int]] = {}
    try:
        _select_tab(ui, "Jobs")
        _settle(ui, ticks=20)

        toggleable = [f for f in PRIMARY_JOB_TOGGLES if f in ui.jobs_vars]
        rng = random.Random(0)
        scroll_positions = [0.0, 0.5, 1.0]
        sub_keys = [
            UIField.CLAN_DONATE_USER_TOGGLE,
            UIField.CLAN_REQUEST_CARDS_USER_TOGGLE,
            UIField.CLAN_CLAIM_GIFTS_USER_TOGGLE,
        ]
        for idx, frac in enumerate(scroll_positions, start=1):
            for field in toggleable:
                ui.jobs_vars[field].set(False)
            for field in rng.sample(toggleable, k=min(3, len(toggleable))):
                ui.jobs_vars[field].set(True)
            # Force Clan chat ON so sub-jobs are enabled and we can see selected + unselected states.
            ui.jobs_vars[UIField.CLAN_CHAT_USER_TOGGLE].set(True)
            # Show some subs selected, some not, so both states are captured.
            for k_idx, k in enumerate(sub_keys):
                if k in ui.jobs_vars:
                    ui.jobs_vars[k].set(k_idx == idx - 1)  # one selected, others not
            ui._on_clan_chat_master_toggle()
            ui.jobs_scroller.yview_moveto(frac)
            _settle(ui, ticks=10)
            label = f"jobs_scroll_{idx}"
            results[label] = _grab_window(ui, OUT_DIR / f"01_{idx}_jobs_scroll.png")

        _select_tab(ui, "Emulator")
        emu_states = [
            ("memu", EmulatorType.MEMU),
            ("google_play", EmulatorType.GOOGLE_PLAY),
            ("bluestacks", EmulatorType.BLUESTACKS),
            ("adb", EmulatorType.ADB),
        ]
        for i, (label, emu) in enumerate(emu_states, start=2):
            ui.emulator_var.set(emu)
            _settle(ui)
            results[f"emulator_{label}"] = _grab_window(ui, OUT_DIR / f"{i:02d}_emulator_{label}.png")

        _select_tab(ui, "Stats")
        results["stats"] = _grab_window(ui, OUT_DIR / "06_stats.png")

        _select_tab(ui, "Misc")
        results["misc"] = _grab_window(ui, OUT_DIR / "07_misc.png")
    finally:
        ui.destroy()

    return results


def main() -> int:
    results = capture_all()
    print(f"Saved {len(results)} screenshots to {OUT_DIR}:")
    for name, size in results.items():
        print(f"  {name}: {size[0]}x{size[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
