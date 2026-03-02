"""Open folders in the OS file explorer (Finder/Explorer/etc)."""

from __future__ import annotations

import logging
import os
import subprocess

from pyclashbot.utils.platform import is_macos, is_windows


def open_folder(folder_path: str) -> None:
    """Open a folder in the platform's file explorer."""
    os.makedirs(folder_path, exist_ok=True)

    try:
        if is_windows():
            os.startfile(folder_path)  # type: ignore[attr-defined]
            return

        if is_macos():
            subprocess.Popen(["open", folder_path])
        else:
            subprocess.Popen(["xdg-open", folder_path])
    except FileNotFoundError as exc:
        logging.error("Folder opener command not found when opening %s: %s", folder_path, exc)
    except Exception as exc:
        # Log but don't crash the UI
        logging.error("Failed to open folder %s: %s", folder_path, exc)
