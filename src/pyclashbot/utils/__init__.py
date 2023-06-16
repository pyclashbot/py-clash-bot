import contextlib

from .caching import (
    _cache_data,
    _load_data,
    cache_user_settings,
    check_user_settings,
    read_user_settings,
)
from .logger import Logger
from .server_notifications import Notification, get_latest_notification
from .thread import StoppableThread

__all__ = [
    "Logger",
    "StoppableThread",
    "read_user_settings",
    "cache_user_settings",
    "check_user_settings",
    "_cache_data",
    "_load_data",
    "get_latest_notification",
    "Notification",
]

# dependency module is only available on Windows
with contextlib.suppress(ImportError):
    from .dependency import setup_memu  # noqa

    __all__.extend(["setup_memu"])
