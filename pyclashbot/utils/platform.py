"""Platform detection and OS-specific directory helpers."""

import os
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
    if get_platform() == Platform.MACOS:
        return os.path.join(os.path.expanduser("~/Library/Application Support"), app_name)
    elif get_platform() == Platform.LINUX:
        return os.path.join(os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share")), app_name)
    return os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), app_name)


def get_log_dir(app_name: str) -> str:
    """Return OS-appropriate directory for log files."""
    if get_platform() == Platform.MACOS:
        return os.path.join(os.path.expanduser("~/Library/Logs"), app_name)
    elif get_platform() == Platform.LINUX:
        return os.path.join(os.environ.get("XDG_STATE_HOME", os.path.expanduser("~/.local/state")), app_name, "logs")
    return os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), app_name, "logs")


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
