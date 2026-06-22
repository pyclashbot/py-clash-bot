"""Per-fight pack recorder for the opt-in "record training data" feature.

Writes one self-contained folder per fight (the "pack" format consumed by the
royalestrat ``user_data`` importer):

    recordings/<slug>/
      capture.mkv            # lossless FFV1 video, 419x633, BGR, 3 fps  (only if dimension/color-exact)
       --- or, when cv2's FFV1 crops odd dims / subsamples chroma (the common case): ---
      frames/000000.png ...  # lossless PNG, 419x633, BGR, 3 fps         (fallback)
      plays.jsonl            # one JSON line per deploy: {frame_index, card_index (hand slot 0-3), x, y, elapsed_s}
      manifest.json

The frame size 419x633 is odd on both axes; cv2.VideoWriter's FFV1 defaults to a
yuv420p pixel format that needs even dims and subsamples chroma, so it would crop
to 418x632 and corrupt color. _ffv1_available() probes for this and falls back to
PNG (lossless, exact dims, exact BGR) whenever FFV1 is not pixel-faithful.

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
import shutil
import threading
import time
import uuid
from typing import Any

import cv2
import numpy as np

from pyclashbot.utils.platform import get_recordings_dir

# Fixed capture geometry (absolute emulator resolution). VideoWriter wants (w, h);
# screenshots are (h, w, c) == (633, 419, 3).
FRAME_W, FRAME_H = 419, 633
DEFAULT_FPS = 3.0
# Skip starting a new recording once the recordings drive is over 90% full
# (free space below this fraction of total). Never deletes anything -- it just
# stops adding to a nearly-full disk. Manual cleanup is the "Clear recordings"
# button in the interface.
MIN_FREE_DISK_FRACTION = 0.10
SCHEMA = "pcb-pack/v1"
# Max per-channel deviation tolerated on the FFV1 round-trip probe. Lossless RGB
# (gbrp) round-trips bit-exact; yuv444p adds a few counts of matrix rounding;
# yuv420p chroma subsampling blows past this on the red/blue probe pattern.
FFV1_COLOR_TOLERANCE = 4


def _new_slug() -> str:
    """Slug = ``%Y%m%d-%H%M%S-<6 hex>`` (matches the rl-bot record format)."""
    return time.strftime("%Y%m%d-%H%M%S", time.localtime()) + "-" + secrets.token_hex(3)


class FightPackRecorder:
    """Captures one fight's frames + plays + outcome to a pack folder."""

    def __init__(self, logger=None) -> None:
        self.logger = logger
        self.slug: str | None = None
        self.uuid: str = ""
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

    def start(
        self, emulator, fight_mode: str, version: str, fps: float = DEFAULT_FPS, custom_path: str | None = None
    ) -> bool:
        """Begin capturing. Returns True on success (a frame thread is running)."""
        self.slug = _new_slug()
        # Stable dedup key for the importer: generated once here and persisted
        # immediately (see below), so a re-exported/re-sent pack keeps the same uuid.
        self.uuid = uuid.uuid4().hex
        self.dir = os.path.join(get_recordings_dir(custom_path=custom_path), self.slug)
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
        # Persist a stub manifest now so the uuid survives even if the fight crashes
        # before finish(); finish() overwrites it with the same uuid plus the outcome.
        self._write_manifest(None)

        self._thread = threading.Thread(target=self._capture_loop, name="fight-capture", daemon=True)
        self._thread.start()
        self._log(f"Started fight recording {self.slug} (source={self.frames_source}, fps={fps})")
        return True

    def log_play(self, card_index: int, x: int, y: int, elapsed_s: float) -> None:
        """Record one card deploy, pairing it to the current frame index.

        Logs the hand slot (0-3) the card was played from, not the card identity:
        a vision model labels the hand from the frames and maps index -> card later.
        """
        if self.dir is None:
            return
        entry = {
            "frame_index": self._frame_count,  # atomic int read under the GIL
            "card_index": int(card_index),
            "x": int(x),
            "y": int(y),
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
        """One-time codec probe: accept FFV1 only if it is dimension- and color-exact.

        cv2.VideoWriter's FFV1 defaults to a yuv420p pixel format, which requires
        even dimensions (it silently crops our odd 419x633 to 418x632) and subsamples
        chroma (corrupting the exact BGR that side detection relies on). A naive
        "can I decode a frame" probe misses both. So we round-trip a red/blue striped
        frame and reject FFV1 unless the readback is the right shape AND color-faithful;
        the caller then falls back to lossless PNG frames, which have neither constraint.
        """
        assert self.dir is not None
        probe = os.path.join(self.dir, "_probe.mkv")
        # Chroma-stress pattern: saturated red/blue alternating columns. Subsampling
        # averages neighbouring columns and fails the comparison; a crop changes shape.
        test = np.empty((FRAME_H, FRAME_W, 3), dtype=np.uint8)
        test[:, 0::2] = (0, 0, 255)  # BGR red on even columns
        test[:, 1::2] = (255, 0, 0)  # BGR blue on odd columns
        try:
            writer = cv2.VideoWriter(probe, cv2.VideoWriter.fourcc(*"FFV1"), self.fps, (FRAME_W, FRAME_H))
            if not writer.isOpened():
                writer.release()
                return False
            writer.write(test)
            writer.release()
            cap = cv2.VideoCapture(probe)
            ok, frame = cap.read()
            cap.release()
            if not ok or frame is None:
                return False
            if frame.shape != (FRAME_H, FRAME_W, 3):
                got_w, got_h = frame.shape[1], frame.shape[0]
                self._log(
                    f"FFV1 rejected: decoded {got_w}x{got_h}, expected {FRAME_W}x{FRAME_H} "
                    "(odd-dimension crop) -- using lossless PNG frames",
                )
                return False
            max_dev = int(np.abs(frame.astype(np.int16) - test.astype(np.int16)).max())
            if max_dev > FFV1_COLOR_TOLERANCE:
                self._log(
                    f"FFV1 rejected: color round-trip off by {max_dev} (chroma subsampling) "
                    "-- using lossless PNG frames",
                )
                return False
            return True
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
            "uuid": self.uuid,
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


def _enough_disk_for_recording(custom_path: str | None = None) -> bool:
    """True if the recordings drive has at least MIN_FREE_DISK_FRACTION free.

    Returns False (skip recording) if the recordings folder can't be created or
    queried -- a user-supplied custom path may be invalid or unwritable.
    """
    path = get_recordings_dir(custom_path=custom_path)
    try:
        os.makedirs(path, exist_ok=True)
        usage = shutil.disk_usage(path)
    except OSError:
        return False
    return usage.free / usage.total >= MIN_FREE_DISK_FRACTION


def start_fight_recording(
    emulator, fight_mode: str, version: str, logger=None, fps: float = DEFAULT_FPS, custom_path: str | None = None
) -> None:
    global _active
    finish_fight_recording(None)  # defensively close any stale recorder
    if not _enough_disk_for_recording(custom_path):
        msg = "Recordings drive over 90% full -- skipping fight recording"
        if logger is not None:
            logger.log(msg)
        else:
            print(msg)
        _active = None
        return
    recorder = FightPackRecorder(logger=logger)
    try:
        recorder.start(emulator, fight_mode, version, fps=fps, custom_path=custom_path)
        _active = recorder
    except Exception as e:
        if logger is not None:
            logger.log(f"Failed to start fight recording: {e}")
        else:
            print(f"Failed to start fight recording: {e}")
        _active = None


def log_play(card_index: int, x: int, y: int, elapsed_s: float) -> None:
    if _active is not None:
        _active.log_play(card_index, x, y, elapsed_s)


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
