"""Python logging configuration for py-clash-bot"""

import logging
import pprint
import sys
import time
from os import makedirs
from os.path import exists, expandvars, join
from pathlib import Path

from pyclashbot.utils.machine_info import MACHINE_INFO
from pyclashbot.utils.versioning import __version__

MODULE_NAME = "py-clash-bot"
LOGS_TO_KEEP = 20

log_dir = Path(join(expandvars("%appdata%"), MODULE_NAME, "logs"))
log_name = join(log_dir, time.strftime("%Y-%m-%d_%H-%M", time.localtime()) + ".txt")


def cleanup_old_logs() -> None:
    """Delete old log files, keeping only the most recent LOGS_TO_KEEP files."""
    if not log_dir.exists():
        return

    # Get all .txt log files sorted by modification time (newest first)
    log_files = sorted(
        log_dir.glob("*.txt"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )

    # Delete old logs beyond the limit
    for old_log in log_files[LOGS_TO_KEEP:]:
        old_log.unlink()


def configure_logging() -> None:
    """Configure Python logging for file and console output.

    This should be called once at application startup, before any other imports
    or operations that might log.
    """
    # Create logs directory if it doesn't exist
    if not exists(log_dir):
        makedirs(log_dir)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # File handler - logs everything to file
    file_handler = logging.FileHandler(log_name, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("%(levelname)s:%(asctime)s %(message)s")
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Console handler - logs INFO and above to console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Log startup information
    logging.info("Logging initialized for %s", __version__)
    logging.info(
        """
 ____  _  _       ___  __      __    ___  _   _     ____  _____  ____
(  _ \\( \\/ )___  / __)(  )    /__\\  / __)( )_( )___(  _ \\(  _  )(_  _)
 )___/ \\  /(___)( (__  )(__  /(__)\\ \\__ \\ ) _ ((___)) _ < )(_)(   )(
(__)   (__)      \\___)(____)(__)(__)(___/(_) (_)   (____/(_____) (__)
""",
    )
    logging.info(
        "Machine Info: \n%s",
        pprint.pformat(MACHINE_INFO, sort_dicts=False, indent=4),
    )

    # Clean up old logs
    cleanup_old_logs()
    logging.info("Log cleanup completed, keeping %d most recent logs", LOGS_TO_KEEP)


if __name__ == "__main__":
    pass
