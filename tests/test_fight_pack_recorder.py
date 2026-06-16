"""Offline tests for the per-fight pack recorder (no emulator).

Drives FightPackRecorder over a fake screenshot() source and asserts the
written pack matches the shared pack format, including the FFV1 -> PNG fallback.
"""

from __future__ import annotations

import json
import os
import time

import numpy as np

from pyclashbot.bot import recorder as rec
from pyclashbot.bot.recorder import FightPackRecorder


class _FakeEmu:
    """Returns a valid (633, 419, 3) BGR frame on every screenshot()."""

    def screenshot(self) -> np.ndarray:
        return np.zeros((633, 419, 3), dtype=np.uint8)


def _read_manifest(pack_dir: str) -> dict:
    with open(os.path.join(pack_dir, "manifest.json"), encoding="utf-8") as f:
        return json.load(f)


def _drive_one_fight(recorder: FightPackRecorder, *, fps: float = 20.0) -> str:
    recorder.start(_FakeEmu(), "1v1_trophy", "vTEST", fps=fps)
    recorder.log_play(2, 215, 360, 47.3)
    time.sleep(0.5)  # let the capture thread grab several frames
    slug = recorder.finish("win")
    assert slug is not None
    return os.path.join(rec.get_recordings_dir(), slug)


def test_uuid_persisted_at_start_and_stable(tmp_path, monkeypatch):
    monkeypatch.setattr(rec, "get_recordings_dir", lambda *a, **k: str(tmp_path))

    recorder = FightPackRecorder()
    recorder.start(_FakeEmu(), "1v1_classic", "vTEST", fps=20.0)
    assert recorder.slug is not None  # set by start(); narrows str | None for os.path.join
    pack_dir = os.path.join(rec.get_recordings_dir(), recorder.slug)

    # uuid is written to the manifest immediately at start (before finish).
    started = _read_manifest(pack_dir)
    assert started["uuid"] == recorder.uuid and len(recorder.uuid) == 32

    recorder.finish("win")
    finished = _read_manifest(pack_dir)
    # Same uuid survives finish() -- a re-exported pack carries the original.
    assert finished["uuid"] == started["uuid"]


def test_stop_capture_freezes_frames(tmp_path, monkeypatch):
    monkeypatch.setattr(rec, "get_recordings_dir", lambda *a, **k: str(tmp_path))

    recorder = FightPackRecorder()
    recorder.start(_FakeEmu(), "1v1_classic", "vTEST", fps=20.0)
    time.sleep(0.4)
    recorder.stop_capture()
    frozen = recorder._frame_count
    time.sleep(0.4)  # capture is stopped: the frame count must not grow
    assert recorder._frame_count == frozen
    recorder.finish("win")

    assert recorder.slug is not None  # set by start(); narrows str | None for os.path.join
    manifest = _read_manifest(os.path.join(rec.get_recordings_dir(), recorder.slug))
    assert manifest["n_frames"] == frozen


def test_pack_is_spec_valid(tmp_path, monkeypatch):
    monkeypatch.setattr(rec, "get_recordings_dir", lambda *a, **k: str(tmp_path))

    recorder = FightPackRecorder()
    pack_dir = _drive_one_fight(recorder)

    manifest = _read_manifest(pack_dir)
    assert manifest["schema"] == "pcb-pack/v1"
    # uuid is the importer's dedup key: 32-char lowercase hex, stable across re-exports.
    assert isinstance(manifest["uuid"], str) and len(manifest["uuid"]) == 32
    assert int(manifest["uuid"], 16) >= 0  # valid hex
    assert manifest["resolution"] == [419, 633]
    assert manifest["fight_mode"] == "1v1_trophy"
    assert manifest["outcome"] == "win"
    assert manifest["pcb_version"] == "vTEST"
    assert manifest["frames_source"] in ("ffv1", "png")
    assert manifest["n_frames"] >= 1
    assert manifest["n_plays"] == 1

    # plays.jsonl: one valid line, frame_index within range.
    with open(os.path.join(pack_dir, "plays.jsonl"), encoding="utf-8") as f:
        plays = [json.loads(line) for line in f if line.strip()]
    assert len(plays) == 1
    play = plays[0]
    assert play["card_index"] == 2 and play["x"] == 215 and play["y"] == 360
    assert 0 <= play["frame_index"] <= manifest["n_frames"]


def test_png_fallback_when_ffv1_unavailable(tmp_path, monkeypatch):
    monkeypatch.setattr(rec, "get_recordings_dir", lambda *a, **k: str(tmp_path))
    # Force the codec probe to fail so the PNG fallback path is exercised.
    monkeypatch.setattr(FightPackRecorder, "_ffv1_available", lambda self: False)

    recorder = FightPackRecorder()
    pack_dir = _drive_one_fight(recorder)

    manifest = _read_manifest(pack_dir)
    assert manifest["frames_source"] == "png"

    frames_dir = os.path.join(pack_dir, "frames")
    pngs = sorted(p for p in os.listdir(frames_dir) if p.endswith(".png"))
    assert len(pngs) == manifest["n_frames"]
    assert not os.path.exists(os.path.join(pack_dir, "capture.mkv"))


def test_module_singleton_helpers(tmp_path, monkeypatch):
    monkeypatch.setattr(rec, "get_recordings_dir", lambda *a, **k: str(tmp_path))

    assert rec.is_recording() is False
    rec.start_fight_recording(_FakeEmu(), "1v1_classic", "vTEST")
    assert rec.is_recording() is True
    rec.log_play(0, 100, 200, 1.0)
    time.sleep(0.3)
    rec.finish_fight_recording("loss")
    assert rec.is_recording() is False
