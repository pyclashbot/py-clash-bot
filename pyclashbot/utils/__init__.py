import contextlib

from .caching import (
    _cache_data,
    _load_data,
    cache_user_settings,
    check_user_settings,
    read_user_settings,
)
from .logger import Logger
from .thread import StoppableThread

__all__ = [
    "Logger",
    "StoppableThread",
    "read_user_settings",
    "cache_user_settings",
    "check_user_settings",
    "_cache_data",
    "_load_data",
]

# dependency module is only available on Windows
with contextlib.suppress(ImportError):
    from .dependency import setup_ahk, setup_memu  # noqa

    __all__.extend(["setup_ahk", "setup_memu"])
