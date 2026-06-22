"""Offline tests for the periodic recording archiver (bundle + crash-safety)."""

import json
import os
import shutil
import zipfile

import pyclashbot.bot.recording_archiver as arch
import pyclashbot.utils.platform as pf


def _make_pack(rec_dir, slug, size_bytes):
    """Create a slug-named pack folder of roughly size_bytes."""
    pack = os.path.join(rec_dir, slug)
    os.makedirs(os.path.join(pack, "frames"), exist_ok=True)
    with open(os.path.join(pack, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"slug": slug}, f)
    with open(os.path.join(pack, "frames", "000000.bin"), "wb") as f:
        f.write(b"\x00" * size_bytes)
    return pack


def _slugs(n):
    # Chronological slugs (timestamp-ordered) matching recorder._new_slug shape.
    return [f"2026010{i}-120000-0000{i:02x}" for i in range(1, n + 1)]


def test_below_threshold_does_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(arch, "ARCHIVE_THRESHOLD_BYTES", 1000)
    monkeypatch.setattr(arch, "TARGET_ARCHIVE_BYTES", 1000)
    rec = str(tmp_path / "recordings")
    os.makedirs(rec)
    for slug in _slugs(2):
        _make_pack(rec, slug, 100)

    assert arch.maybe_archive_recordings(custom_path=rec) is None
    assert sorted(os.listdir(rec)) == _slugs(2)


def test_archives_oldest_without_splitting(tmp_path, monkeypatch):
    # Use tiny thresholds so the test moves bytes, not gigabytes.
    monkeypatch.setattr(arch, "ARCHIVE_THRESHOLD_BYTES", 1000)
    monkeypatch.setattr(arch, "TARGET_ARCHIVE_BYTES", 500)
    rec = str(tmp_path / "recordings")
    os.makedirs(rec)
    slugs = _slugs(4)
    # 300 B each: total 1200 B > 1000 B threshold; oldest packs gathered until
    # the 500 B target is reached -> the first two whole packs, never a partial.
    for slug in slugs:
        _make_pack(rec, slug, 300)

    zip_path = arch.maybe_archive_recordings(custom_path=rec)
    assert zip_path is not None and os.path.isfile(zip_path)

    # Oldest two are gone from loose recordings; newest two remain. The "zips"
    # archive folder now lives inside the recordings dir, so exclude it.
    assert sorted(n for n in os.listdir(rec) if n != "zips") == slugs[2:]
    with zipfile.ZipFile(zip_path) as zf:
        archived = {m.replace("\\", "/").split("/", 1)[0] for m in zf.namelist()}
    assert archived == set(slugs[:2])

    # Disk accounting includes the zip via the all-locations total.
    zips_dir = pf.get_recording_zips_dir(custom_path=rec)
    assert os.path.dirname(zip_path) == zips_dir
    assert pf.recording_zips_total_bytes(custom_path=rec) == os.path.getsize(zip_path)


def test_reconcile_heals_partial_delete_without_duplicating(tmp_path, monkeypatch):
    """A crash after committing the zip but before deleting all sources must not
    re-archive the survivor (no dupes). Reconcile now runs on the archive path, so
    drive the loose packs over the threshold to trigger it; it then finishes the
    delete instead of re-zipping the survivor."""
    monkeypatch.setattr(arch, "ARCHIVE_THRESHOLD_BYTES", 100)
    monkeypatch.setattr(arch, "TARGET_ARCHIVE_BYTES", 100)
    rec = str(tmp_path / "recordings")
    zips = pf.get_recording_zips_dir(custom_path=rec)
    os.makedirs(rec)
    os.makedirs(zips)

    slugs = _slugs(2)
    for slug in slugs:
        _make_pack(rec, slug, 300)  # each well over the 100 B threshold

    # Hand-build a committed archive of both packs, then simulate a crash that
    # deleted only the first source: the second pack is still loose AND archived.
    zip_path = os.path.join(zips, f"packs-{slugs[0]}__{slugs[1]}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_STORED) as zf:
        for slug in slugs:
            zf.writestr(f"{slug}/manifest.json", "{}")

    # first delete "succeeded" before the simulated crash
    shutil.rmtree(os.path.join(rec, slugs[0]))

    before = set(os.listdir(zips))
    arch.maybe_archive_recordings(custom_path=rec)

    # Survivor reclaimed (no loose packs left besides the "zips" folder), and no
    # new duplicate zip created.
    assert [n for n in os.listdir(rec) if n != "zips"] == []
    assert set(os.listdir(zips)) == before


def test_orphan_tmp_is_swept(tmp_path):
    rec = str(tmp_path / "recordings")
    zips = pf.get_recording_zips_dir(custom_path=rec)
    os.makedirs(rec)
    os.makedirs(zips)
    orphan = os.path.join(zips, "packs-x__y.zip.tmp")
    with open(orphan, "wb") as f:
        f.write(b"partial")

    arch.maybe_archive_recordings(custom_path=rec)
    assert not os.path.exists(orphan)
