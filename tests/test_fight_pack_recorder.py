"""Offline tests for the per-fight pack recorder (no emulator).

Drives FightPackRecorder over a fake screenshot() source and asserts the
written pack matches the shared pack format, including the FFV1 -> PNG fallback.
"""

from __future__ import annotations

import json
import os
import time
from types import SimpleNamespace

import numpy as np

from pyclashbot.bot import recorder as rec
from pyclashbot.bot.recorder import FightPackRecorder
from pyclashbot.utils import platform as pf


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


def test_low_disk_space_skips_recording(tmp_path, monkeypatch):
    """At >90% used (free < 10%), start_fight_recording records nothing."""
    monkeypatch.setattr(rec, "get_recordings_dir", lambda *a, **k: str(tmp_path))
    # 95% used: 5 free of 100 total -> below the 10% floor.
    monkeypatch.setattr(rec.shutil, "disk_usage", lambda _p: SimpleNamespace(total=100, used=95, free=5))

    rec.start_fight_recording(_FakeEmu(), "1v1_classic", "vTEST", logger=None)

    assert rec.is_recording() is False
    assert not any(p.is_dir() for p in tmp_path.iterdir())


def test_sufficient_disk_allows_recording(tmp_path, monkeypatch):
    """With plenty of free space, recording starts normally."""
    monkeypatch.setattr(rec, "get_recordings_dir", lambda *a, **k: str(tmp_path))
    monkeypatch.setattr(rec.shutil, "disk_usage", lambda _p: SimpleNamespace(total=100, used=10, free=90))
    monkeypatch.setattr(FightPackRecorder, "_ffv1_available", lambda self: False)

    rec.start_fight_recording(_FakeEmu(), "1v1_classic", "vTEST", logger=None)
    try:
        assert rec.is_recording() is True
    finally:
        rec.finish_fight_recording("win")
    assert rec.is_recording() is False


def test_clear_recordings_removes_all_packs(tmp_path, monkeypatch):
    """clear_recordings() deletes every pack folder and reports freed bytes."""
    monkeypatch.setattr(pf, "get_recordings_dir", lambda *a, **k: str(tmp_path))
    for slug in ("20240101-120000-abc123", "20240102-130000-def456"):
        frames = tmp_path / slug / "frames"
        frames.mkdir(parents=True)
        (frames / "0.png").write_bytes(b"x" * 1000)

    removed, freed = pf.clear_recordings()

    assert removed == 2
    assert freed >= 2000
    assert list(tmp_path.iterdir()) == []


def test_clear_recordings_preserves_unrelated_dirs(tmp_path, monkeypatch):
    """A custom recordings folder may hold unrelated content -- only slug-named
    pack folders are deleted, everything else is left untouched."""
    monkeypatch.setattr(pf, "get_recordings_dir", lambda *a, **k: str(tmp_path))

    pack = tmp_path / "20240101-120000-abc123" / "frames"
    pack.mkdir(parents=True)
    (pack / "0.png").write_bytes(b"x" * 1000)

    unrelated_dir = tmp_path / "My Important Documents"
    unrelated_dir.mkdir()
    (unrelated_dir / "keep.txt").write_bytes(b"keep me")
    loose_file = tmp_path / "notes.txt"
    loose_file.write_bytes(b"keep me too")

    removed, _ = pf.clear_recordings()

    assert removed == 1
    assert unrelated_dir.is_dir()
    assert (unrelated_dir / "keep.txt").exists()
    assert loose_file.exists()


def test_clear_recordings_removes_zip_archives(tmp_path, monkeypatch):
    """clear_recordings() also drops archived zip bundles so the button reclaims
    all recording space, and counts their bytes in bytes_freed."""
    monkeypatch.setattr(pf, "get_recordings_dir", lambda *a, **k: str(tmp_path))

    pack = tmp_path / "20240101-120000-abc123" / "frames"
    pack.mkdir(parents=True)
    (pack / "0.png").write_bytes(b"x" * 1000)

    zips_dir = tmp_path / "zips"
    zips_dir.mkdir()
    (zips_dir / "packs-a__b.zip").write_bytes(b"z" * 2000)

    removed, freed = pf.clear_recordings()

    assert removed == 1  # only loose packs counted as packs_removed
    assert freed >= 3000  # 1000 (pack) + 2000 (zip)
    assert not zips_dir.exists()
    assert list(tmp_path.iterdir()) == []


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
