"""Offline tests for recordings-path validation and disk-space helpers."""

import os

import pyclashbot.utils.platform as pf


def test_empty_path_uses_default():
    for value in (None, "", "   "):
        ok, message = pf.validate_recordings_path(value)
        assert ok is True
        assert "default" in message.lower()


def test_existing_writable_dir_is_valid(tmp_path):
    ok, message = pf.validate_recordings_path(str(tmp_path))
    assert ok is True
    assert "valid" in message.lower()


def test_path_pointing_at_file_is_invalid(tmp_path):
    file_path = tmp_path / "afile.txt"
    file_path.write_text("x")
    ok, message = pf.validate_recordings_path(str(file_path))
    assert ok is False
    assert "file" in message.lower()


def test_nonexistent_with_writable_ancestor_is_valid(tmp_path):
    target = tmp_path / "does" / "not" / "exist" / "yet"
    ok, message = pf.validate_recordings_path(str(target))
    assert ok is True
    assert "created" in message.lower()


def test_nonexistent_on_missing_root_is_invalid():
    # A drive/root that does not exist cannot be created.
    bogus = "Z:\\no\\such\\drive" if os.name == "nt" else "/nonexistent-root-xyz/sub/dir"
    ok, _ = pf.validate_recordings_path(bogus)
    assert ok is False


def test_drive_free_bytes_returns_positive_for_default():
    free = pf.recordings_drive_free_bytes(None)
    assert free is None or free > 0


def test_drive_free_bytes_for_custom_existing_dir(tmp_path):
    free = pf.recordings_drive_free_bytes(str(tmp_path))
    assert free is not None
    assert free > 0


def _make_pack(parent, slug, size_bytes):
    frames = parent / slug / "frames"
    frames.mkdir(parents=True)
    (frames / "0.png").write_bytes(b"x" * size_bytes)


def test_total_bytes_counts_only_slug_packs(tmp_path):
    _make_pack(tmp_path, "20240101-120000-abc123", 2000)
    unrelated = tmp_path / "my_notes"
    unrelated.mkdir()
    (unrelated / "big.bin").write_bytes(b"y" * 9999)

    total = pf.recordings_total_bytes(custom_path=str(tmp_path))
    assert total == 2000


def test_total_bytes_zero_for_missing_dir(tmp_path):
    assert pf.recordings_total_bytes(custom_path=str(tmp_path / "nope")) == 0


def test_total_all_locations_sums_default_and_custom(tmp_path, monkeypatch):
    default_dir = tmp_path / "appdata" / "py-clash-bot" / "recordings"
    custom_dir = tmp_path / "custom"
    default_dir.mkdir(parents=True)
    custom_dir.mkdir(parents=True)
    _make_pack(default_dir, "20240101-120000-aaa111", 1000)
    _make_pack(custom_dir, "20240102-130000-bbb222", 3000)

    # Point the default recordings dir at our temp appdata location.
    monkeypatch.setattr(pf, "get_app_data_dir", lambda *a, **k: str(tmp_path / "appdata" / "py-clash-bot"))

    total = pf.recordings_total_bytes_all_locations(custom_path=str(custom_dir))
    assert total == 4000


def test_total_all_locations_no_double_count_when_custom_equals_default(tmp_path, monkeypatch):
    default_dir = tmp_path / "appdata" / "py-clash-bot" / "recordings"
    default_dir.mkdir(parents=True)
    _make_pack(default_dir, "20240101-120000-aaa111", 1000)

    monkeypatch.setattr(pf, "get_app_data_dir", lambda *a, **k: str(tmp_path / "appdata" / "py-clash-bot"))

    # Custom path resolves to the same directory as the default.
    total = pf.recordings_total_bytes_all_locations(custom_path=str(default_dir))
    assert total == 1000
