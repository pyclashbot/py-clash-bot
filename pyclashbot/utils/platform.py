"""Platform detection and OS-specific directory helpers."""

import os
import shutil
import sys
from enum import StrEnum, auto


class Platform(StrEnum):
    """Supported platforms."""

    WINDOWS = auto()
    MACOS = auto()
    LINUX = auto()


def get_platform() -> Platform:
    """Detect the current platform."""
    if sys.platform == "darwin":
        return Platform.MACOS
    elif sys.platform.startswith("linux"):
        return Platform.LINUX
    return Platform.WINDOWS


def get_app_data_dir(app_name: str) -> str:
    """Return OS-appropriate directory for application data/cache."""
    platform = get_platform()
    if platform == Platform.MACOS:
        return os.path.join(os.path.expanduser("~/Library/Application Support"), app_name)
    elif platform == Platform.LINUX:
        return os.path.join(os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share")), app_name)
    return os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), app_name)


def get_log_dir(app_name: str) -> str:
    """Return OS-appropriate directory for log files."""
    platform = get_platform()
    if platform == Platform.MACOS:
        return os.path.join(os.path.expanduser("~/Library/Logs"), app_name)
    elif platform == Platform.LINUX:
        return os.path.join(os.environ.get("XDG_STATE_HOME", os.path.expanduser("~/.local/state")), app_name, "logs")
    return os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), app_name, "logs")


def get_recordings_dir(app_name: str = "py-clash-bot") -> str:
    """Return the single source-of-truth directory for recorded fight packs."""
    return os.path.join(get_app_data_dir(app_name), "recordings")


def _dir_size(path: str) -> int:
    """Best-effort total size in bytes of every file under path."""
    total = 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += os.path.getsize(os.path.join(root, name))
            except OSError:
                continue
    return total


def clear_recordings(app_name: str = "py-clash-bot") -> tuple[int, int]:
    """Delete every recorded fight pack. Returns (packs_removed, bytes_freed).

    Manual only: nothing in the bot calls this automatically. Wired to the
    "Clear recordings" button in the interface.
    """
    rec_dir = get_recordings_dir(app_name)
    if not os.path.isdir(rec_dir):
        return (0, 0)
    removed = 0
    freed = 0
    for name in os.listdir(rec_dir):
        pack = os.path.join(rec_dir, name)
        if not os.path.isdir(pack):
            continue
        freed += _dir_size(pack)
        shutil.rmtree(pack, ignore_errors=True)
        removed += 1
    return (removed, freed)


def is_windows() -> bool:
    """Check if running on Windows."""
    return get_platform() == Platform.WINDOWS


def is_macos() -> bool:
    """Check if running on macOS."""
    return get_platform() == Platform.MACOS


def is_linux() -> bool:
    """Check if running on Linux."""
    return get_platform() == Platform.LINUX


CURRENT_PLATFORM = get_platform()
