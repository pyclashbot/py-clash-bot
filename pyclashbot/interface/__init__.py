"""GUI package with lazy re-exports."""

from __future__ import annotations

from importlib import import_module
from typing import Any

_LAZY = {
    "DISABLE_KEYS": ".config",
    "USER_CONFIG_KEYS": ".config",
    "PyClashBotUI": ".ui",
    "no_jobs_popup": ".ui",
    "show_clash_royale_setup_gui": ".setup",
    "show_help_gui": ".help",
}

__all__ = [
    "DISABLE_KEYS",
    "USER_CONFIG_KEYS",
    "PyClashBotUI",
    "no_jobs_popup",
    "show_clash_royale_setup_gui",
    "show_help_gui",
]


def __getattr__(name: str) -> Any:
    """Import GUI symbols only when they are actually used."""
    module_name = _LAZY.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name, __name__), name)
    globals()[name] = value
    return value
