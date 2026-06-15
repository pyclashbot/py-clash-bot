"""Per-fight pack recorder for the opt-in "record training data" feature.

Writes one self-contained folder per fight (the "pack" format consumed by the
royalestrat ``user_data`` importer):

    recordings/<slug>/
      capture.mkv            # lossless FFV1 video, 419x633, BGR, 3 fps  (primary)
       --- or, when FFV1 is unavailable on the user's machine: ---
      frames/000000.png ...  # lossless PNG, 419x633, BGR, 3 fps         (fallback)
      plays.jsonl            # one JSON line per actual card deploy
      manifest.json

Channel order is load-bearing: ``emulator.screenshot()`` is BGR and we keep it
BGR end to end via cv2 (no PIL RGB flip). A fixed-cadence background thread grabs
frames at ``fps`` while the worker thread logs the plays it makes inline.

Only 1v1-type fights (Trophy Road, Classic 1v1) are recorded; 2v2 is never
recorded (gated by the caller).
"""

from __future__ import annotations

import json
import os
import secrets
import threading
import time
from typing import Any

import cv2
import numpy as np

from pyclashbot.utils.platform import get_recordings_dir

# Fixed capture geometry (absolute emulator resolution). VideoWriter wants (w, h);
# screenshots are (h, w, c) == (633, 419, 3).
FRAME_W, FRAME_H = 419, 633
DEFAULT_FPS = 3.0
SCHEMA = "pcb-pack/v1"


def _new_slug() -> str:
    """Slug = ``%Y%m%d-%H%M%S-<6 hex>`` (matches the rl-bot record format)."""
    return time.strftime("%Y%m%d-%H%M%S", time.localtime()) + "-" + secrets.token_hex(3)


class FightPackRecorder:
    """Captures one fight's frames + plays + outcome to a pack folder."""

    def __init__(self, logger=None) -> None:
        self.logger = logger
        self.slug: str | None = None
        self.dir: str | None = None
        self.fps: float = DEFAULT_FPS
        self.fight_mode: str = ""
        self.version: str = ""
        self.frames_source: str = "ffv1"

        self._emulator: Any = None
        self._writer: cv2.VideoWriter | None = None
        self._frames_dir: str | None = None
        self._frame_count: int = 0
        self._plays: list[dict] = []
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._started_wall: float = 0.0
        self._capture_stopped: float = 0.0

    # ---- lifecycle ------------------------------------------------------

    def start(self, emulator, fight_mode: str, version: str, fps: float = DEFAULT_FPS) -> bool:
        """Begin capturing. Returns True on success (a frame thread is running)."""
        self.slug = _new_slug()
        self.dir = os.path.join(get_recordings_dir(), self.slug)
        self.fps = fps
        self.fight_mode = fight_mode
        self.version = version
        self._emulator = emulator
        self._frame_count = 0
        self._plays = []
        self._stop.clear()
        self._started_wall = time.time()

        os.makedirs(self.dir, exist_ok=True)
        self.frames_source = self._open_encoder()

        self._thread = threading.Thread(target=self._capture_loop, name="fight-capture", daemon=True)
        self._thread.start()
        self._log(f"Started fight recording {self.slug} (source={self.frames_source}, fps={fps})")
        return True

    def log_play(self, slot: int, x: int, y: int, card_id: str, elapsed_s: float) -> None:
        """Record one card deploy, pairing it to the current frame index."""
        if self.dir is None:
            return
        entry = {
            "frame_index": self._frame_count,  # atomic int read under the GIL
            "slot": int(slot),
            "x": int(x),
            "y": int(y),
            "card_id": str(card_id) if card_id else "UNKNOWN",
            "elapsed_s": round(float(elapsed_s), 2),
        }
        with self._lock:
            self._plays.append(entry)

    def stop_capture(self) -> None:
        """Halt frame capture at the battle boundary, before post-fight navigation.

        Idempotent: called from the battle-end hook so the pack holds only in-fight
        frames, and again (as a no-op) from finish().
        """
        if self.dir is None or self._stop.is_set():
            return
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=10)
        if self._writer is not None:
            self._writer.release()
            self._writer = None
        self._capture_stopped = time.time()

    def finish(self, outcome: str | None) -> str | None:
        """Finalize the pack: stop capture (if still running) and write metadata."""
        if self.dir is None:
            return None

        self.stop_capture()
        self._write_plays()
        self._write_manifest(outcome)
        self._log(f"Finished fight recording {self.slug}: {self._frame_count} frames, {len(self._plays)} plays")
        return self.slug

    # ---- internals ------------------------------------------------------

    def _open_encoder(self) -> str:
        """Probe FFV1; return 'ffv1' (and open self._writer) or 'png' (frames dir)."""
        assert self.dir is not None
        if self._ffv1_available():
            self._writer = cv2.VideoWriter(
                os.path.join(self.dir, "capture.mkv"),
                cv2.VideoWriter.fourcc(*"FFV1"),
                self.fps,
                (FRAME_W, FRAME_H),
            )
            if self._writer.isOpened():
                return "ffv1"
            self._writer = None

        # Fallback: lossless PNG frames.
        self._frames_dir = os.path.join(self.dir, "frames")
        os.makedirs(self._frames_dir, exist_ok=True)
        return "png"

    def _ffv1_available(self) -> bool:
        """One-time codec probe: write a throwaway FFV1 frame and read it back."""
        assert self.dir is not None
        probe = os.path.join(self.dir, "_probe.mkv")
        try:
            writer = cv2.VideoWriter(probe, cv2.VideoWriter.fourcc(*"FFV1"), self.fps, (FRAME_W, FRAME_H))
            if not writer.isOpened():
                writer.release()
                return False
            writer.write(np.zeros((FRAME_H, FRAME_W, 3), dtype=np.uint8))
            writer.release()
            cap = cv2.VideoCapture(probe)
            ok, _ = cap.read()
            cap.release()
            return bool(ok)
        except Exception as e:
            self._log(f"FFV1 probe failed, falling back to PNG frames: {e}")
            return False
        finally:
            if os.path.exists(probe):
                try:
                    os.remove(probe)
                except OSError:
                    pass

    def _capture_loop(self) -> None:
        interval = 1.0 / self.fps
        next_t = time.time()
        while not self._stop.is_set():
            try:
                frame = self._emulator.screenshot()
            except Exception as e:
                self._log(f"Capture screenshot failed: {e}")
                frame = None
            if frame is not None and frame.shape == (FRAME_H, FRAME_W, 3):
                self._write_frame(frame)
                self._frame_count += 1
            next_t += interval
            delay = next_t - time.time()
            if delay > 0:
                self._stop.wait(delay)
            else:
                next_t = time.time()  # behind schedule; resync

    def _write_frame(self, frame: np.ndarray) -> None:
        if self.frames_source == "ffv1" and self._writer is not None:
            self._writer.write(frame)  # BGR in, BGR out
        elif self._frames_dir is not None:
            cv2.imwrite(os.path.join(self._frames_dir, f"{self._frame_count:06d}.png"), frame)

    def _write_plays(self) -> None:
        assert self.dir is not None
        with self._lock, open(os.path.join(self.dir, "plays.jsonl"), "w", encoding="utf-8") as f:
            for entry in self._plays:
                f.write(json.dumps(entry) + "\n")

    def _write_manifest(self, outcome: str | None) -> None:
        assert self.dir is not None
        # Report the achieved frame rate. Screenshot latency / ADB contention can
        # hold the effective cadence below the target fps; the home-side pipeline is
        # per-frame and reads the game clock from pixels, so this is informational.
        duration = max(self._capture_stopped - self._started_wall, 1e-6)
        achieved_fps = round(self._frame_count / duration, 3) if self._frame_count else self.fps
        manifest = {
            "schema": SCHEMA,
            "slug": self.slug,
            "outcome": outcome,
            "fight_mode": self.fight_mode,
            "fps": achieved_fps,
            "resolution": [FRAME_W, FRAME_H],
            "frames_source": self.frames_source,
            "n_frames": self._frame_count,
            "n_plays": len(self._plays),
            "pcb_version": self.version,
            "started_wall": self._started_wall,
            "ended_wall": self._capture_stopped,
        }
        with open(os.path.join(self.dir, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    def _log(self, message: str) -> None:
        if self.logger is not None:
            self.logger.log(message)
        else:
            print(message)


# ---- module-level active-recorder singleton -----------------------------
# The fight lifecycle spans separate state functions (do_fight_state ->
# play_a_card -> end_fight_state) inside the single worker process, so the
# active recorder is held here and driven through thin module functions.

_active: FightPackRecorder | None = None


def start_fight_recording(emulator, fight_mode: str, version: str, logger=None, fps: float = DEFAULT_FPS) -> None:
    global _active
    finish_fight_recording(None)  # defensively close any stale recorder
    recorder = FightPackRecorder(logger=logger)
    try:
        recorder.start(emulator, fight_mode, version, fps=fps)
        _active = recorder
    except Exception as e:
        if logger is not None:
            logger.log(f"Failed to start fight recording: {e}")
        else:
            print(f"Failed to start fight recording: {e}")
        _active = None


def log_play(slot: int, x: int, y: int, card_id: str, elapsed_s: float) -> None:
    if _active is not None:
        _active.log_play(slot, x, y, card_id, elapsed_s)


def stop_fight_capture() -> None:
    """Freeze frame capture at the battle boundary (manifest is written by finish)."""
    if _active is not None:
        _active.stop_capture()


def finish_fight_recording(outcome: str | None) -> None:
    global _active
    if _active is not None:
        try:
            _active.finish(outcome)
        finally:
            _active = None


def is_recording() -> bool:
    return _active is not None
