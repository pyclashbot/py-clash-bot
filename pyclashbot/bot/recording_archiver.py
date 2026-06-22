"""Periodic, crash-safe archiving of recorded fight packs into ~5 GB zip bundles.

The recorder writes one folder per fight into the recordings directory (see
``recorder.py``). Those packs accumulate quickly. ``maybe_archive_recordings``
is called after each finished fight: when the loose packs in the recordings
folder exceed :data:`ARCHIVE_THRESHOLD_BYTES`, it peels the *oldest* whole packs
off (never splitting a pack) until it has gathered about :data:`TARGET_ARCHIVE_BYTES`,
bundles them into a single ``.zip`` in the sibling ``recording-zips`` folder, and
deletes the source packs.

Idempotency / crash-safety
--------------------------
The worker is stopped by an OS-level ``terminate()`` (see the root AGENTS.md), so
this routine can die at any instruction. Two failure modes matter, both about
disk, not data: losing the odd fight is fine, but **duplicated packs** and
**unbounded disk growth** are not. The protocol below is self-healing against an
abort at any point, because it makes the rename the single commit point and then
*reconciles* on the next run rather than trusting the previous one finished:

1. **Sweep orphan ``*.zip.tmp``** every call (a zip whose write was interrupted
   before the atomic rename). These are never read; deleting them caps disk
   growth, and the sweep is a single directory scan with no archive reads.
2. **Reconcile** committed archives, but only once loose packs cross the threshold
   and we are about to archive. Every finalized ``.zip`` lists its member slugs in
   its central directory; for each, delete any source pack still on disk. This
   finishes a delete a crash interrupted and, crucially, runs *before* a new batch
   is selected, so a pack already inside a committed archive can never be
   re-selected and re-zipped -> no duplicates. Reading every archive's directory
   on every fight would be wasted I/O that grows with the (unbounded) archive
   count, so it is deferred to the archive path; a leftover straggler simply waits
   to be reclaimed until the next run that archives.
3. **Archive**: write to ``<name>.zip.tmp``, then ``os.replace`` to the final
   name (atomic = the commit point), then delete the sources. A crash before
   the rename leaves only an orphan tmp (swept next run, sources intact); a crash
   after the rename leaves a valid archive whose stragglers reconcile finishes.

Why zip and not tar
-------------------
Tarballs do not help here: idempotency comes from the commit-then-reconcile
protocol, not the container. Worse, reconcile needs to list an archive's member
slugs cheaply, and zip's central directory makes that O(1) without reading the
payload, whereas a tar must be scanned sequentially (or carry a sidecar index).
And because we only ever read archives we committed via ``os.replace``, a zip's
"central directory required to read" property is always satisfied.

Packs are zipped with ``ZIP_STORED`` (no compression): the captured media (FFV1
``.mkv`` / PNG frames) is already compressed, so deflating it wastes CPU for no
size gain -- the goal here is *bundling* loose 5 GB chunks, not shrinking them.

Slugs sort lexically in chronological order (``%Y%m%d-%H%M%S-<hex>``), so the
oldest packs are simply the first ones after a plain sort.
"""

from __future__ import annotations

import os
import shutil
import zipfile

from pyclashbot.utils.platform import (
    _PACK_SLUG_RE,
    _dir_size,
    get_recording_zips_dir,
    get_recordings_dir,
)

# Start archiving once loose packs exceed this; gather about this much per run.
ARCHIVE_THRESHOLD_BYTES = 5 * 1024**3  # 5 GB
TARGET_ARCHIVE_BYTES = 5 * 1024**3  # 5 GB


def _log(logger, message: str) -> None:
    if logger is not None:
        logger.log(message)
    else:
        print(message)


def _pack_dirs_oldest_first(rec_dir: str) -> list[str]:
    """Slug-named pack directory names in chronological (oldest-first) order."""
    if not os.path.isdir(rec_dir):
        return []
    names = [
        name for name in os.listdir(rec_dir) if _PACK_SLUG_RE.match(name) and os.path.isdir(os.path.join(rec_dir, name))
    ]
    return sorted(names)


def _archived_slugs(zip_path: str) -> set[str]:
    """Top-level slug folders recorded inside a committed archive.

    Members are stored as ``<slug>/...``; the first path component is the slug.
    Returns an empty set if the archive can't be read.
    """
    slugs: set[str] = set()
    try:
        with zipfile.ZipFile(zip_path) as zf:
            for member in zf.namelist():
                head = member.replace("\\", "/").split("/", 1)[0]
                if _PACK_SLUG_RE.match(head):
                    slugs.add(head)
    except (OSError, zipfile.BadZipFile):
        return set()
    return slugs


def _sweep_orphan_tmps(zips_dir: str, logger) -> None:
    """Delete orphan ``*.zip.tmp`` files (a write interrupted before the atomic
    rename). Cheap -- a single directory scan, no archive reads -- so it is safe
    to run on every call to cap disk growth from abandoned temp archives.
    """
    if not os.path.isdir(zips_dir):
        return
    for name in os.listdir(zips_dir):
        if name.lower().endswith(".zip.tmp"):
            try:
                os.remove(os.path.join(zips_dir, name))
            except OSError:
                pass


def _reconcile(rec_dir: str, zips_dir: str, logger) -> set[str]:
    """Finish interrupted deletes from committed archives.

    Reads each committed ``.zip``'s central directory, so this runs only on the
    archive path (not every fight). Returns the set of slugs now (or already)
    safely inside a committed archive, so the caller can exclude them from a new
    batch even if rmtree below fails to remove every straggler.
    """
    archived: set[str] = set()
    if not os.path.isdir(zips_dir):
        return archived
    for name in os.listdir(zips_dir):
        path = os.path.join(zips_dir, name)
        if not os.path.isfile(path) or not name.lower().endswith(".zip"):
            continue
        for slug in _archived_slugs(path):
            archived.add(slug)
            stale = os.path.join(rec_dir, slug)
            if os.path.isdir(stale):
                # Pack is already committed to this archive but its source
                # survived a crash mid-delete; remove it now (idempotent).
                shutil.rmtree(stale, ignore_errors=True)
                _log(logger, f"Recording archiver: reclaimed already-archived pack {slug}")
    return archived


def _select_batch(rec_dir: str, packs: list[str]) -> tuple[list[str], int]:
    """Pick oldest whole packs until the cumulative size reaches the target.

    Returns (selected_slugs, total_loose_bytes). Whole packs only -- a pack is
    never split across archives.
    """
    selected: list[str] = []
    selected_bytes = 0
    total_bytes = 0
    for name in packs:
        size = _dir_size(os.path.join(rec_dir, name))
        total_bytes += size
        if selected_bytes < TARGET_ARCHIVE_BYTES:
            selected.append(name)
            selected_bytes += size
    return selected, total_bytes


def _zip_path(zips_dir: str, slugs: list[str]) -> str:
    """A unique ``.zip`` path named for the first..last slug in the batch."""
    base = f"packs-{slugs[0]}__{slugs[-1]}"
    candidate = os.path.join(zips_dir, base + ".zip")
    suffix = 1
    while os.path.exists(candidate):
        candidate = os.path.join(zips_dir, f"{base}-{suffix}.zip")
        suffix += 1
    return candidate


def maybe_archive_recordings(logger=None, custom_path: str | None = None) -> str | None:
    """Bundle ~5 GB of the oldest recording packs into a zip when the loose
    recordings exceed the threshold. Returns the zip path written, else None.

    Safe to call after every fight and crash-safe at any point (see module
    docstring): it sweeps abandoned temp archives, then does nothing (a cheap
    pack scan) until loose packs cross :data:`ARCHIVE_THRESHOLD_BYTES`, at which
    point it reconciles prior interrupted runs before selecting a batch. It only
    ever archives one ~5 GB batch per call so the worker pause stays bounded. Any
    failure is logged and swallowed -- archiving must never break the bot loop,
    and source packs are only deleted after the archive is fully written and
    atomically renamed.
    """
    rec_dir = get_recordings_dir(custom_path=custom_path)
    zips_dir = get_recording_zips_dir(custom_path=custom_path)

    # Cheap every-fight work: sweep abandoned temp archives, then bail unless the
    # loose packs have crossed the threshold. The per-archive reconcile (which
    # opens every committed zip) is deferred to the archive path below.
    _sweep_orphan_tmps(zips_dir, logger)

    packs = _pack_dirs_oldest_first(rec_dir)
    selected, total_bytes = _select_batch(rec_dir, packs)
    if total_bytes < ARCHIVE_THRESHOLD_BYTES or not selected:
        return None

    # About to archive: reconcile committed archives so a pack a prior crashed run
    # already committed is healed and excluded here, never re-selected -> no dupes.
    already_archived = _reconcile(rec_dir, zips_dir, logger)
    if already_archived:
        packs = [p for p in packs if p not in already_archived]
        selected, total_bytes = _select_batch(rec_dir, packs)
        if total_bytes < ARCHIVE_THRESHOLD_BYTES or not selected:
            return None

    try:
        os.makedirs(zips_dir, exist_ok=True)
    except OSError as e:
        _log(logger, f"Recording archiver: cannot create zips folder {zips_dir}: {e}")
        return None

    final_path = _zip_path(zips_dir, selected)
    tmp_path = final_path + ".tmp"
    selected_bytes = 0
    try:
        with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as zf:
            for slug in selected:
                pack_dir = os.path.join(rec_dir, slug)
                for root, _dirs, files in os.walk(pack_dir):
                    for fname in files:
                        abs_path = os.path.join(root, fname)
                        # arcname keeps the "<slug>/..." layout inside the zip
                        # (reconcile reads the slug back from this first component).
                        arcname = os.path.relpath(abs_path, rec_dir)
                        zf.write(abs_path, arcname)
            selected_bytes = sum(zinfo.file_size for zinfo in zf.infolist())
        os.replace(tmp_path, final_path)  # atomic commit point
    except (OSError, zipfile.BadZipFile) as e:
        _log(logger, f"Recording archiver: failed to write {final_path}: {e}")
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        return None

    # Archive is committed; delete the sources. A crash here is harmless: the
    # next run's reconcile finishes the deletion from the committed archive.
    removed = 0
    for slug in selected:
        shutil.rmtree(os.path.join(rec_dir, slug), ignore_errors=True)
        removed += 1

    _log(
        logger,
        f"Recording archiver: bundled {removed} pack(s) "
        f"(~{selected_bytes / 1024**3:.2f} GB) into {os.path.basename(final_path)}",
    )
    return final_path
