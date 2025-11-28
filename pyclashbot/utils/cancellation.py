"""Cancellation infrastructure for cooperative thread/process termination."""

import threading
import time as time_module
from multiprocessing.synchronize import Event as MPEvent
from typing import Optional


class CancelledError(Exception):
    """Raised when an operation is cancelled via cancellation token."""


class CancellationToken:
    """Cancellation token for cooperative thread/process termination.

    Uses Event.wait(timeout) instead of time.sleep() to allow
    immediate response to cancellation requests.

    Works with both threading.Event and multiprocessing.Event.
    """

    _current: Optional["CancellationToken"] = None

    def __init__(self, shutdown_event: threading.Event | MPEvent) -> None:
        self._shutdown = shutdown_event

    @classmethod
    def current(cls) -> Optional["CancellationToken"]:
        """Get the current token (set by worker thread)."""
        return cls._current

    @classmethod
    def set_current(cls, token: Optional["CancellationToken"]) -> None:
        """Set the current cancellation token for this thread context."""
        cls._current = token

    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        return self._shutdown.is_set()

    def sleep(self, seconds: float) -> bool:
        """Interruptible sleep that returns immediately if cancelled.

        Args:
            seconds: Time to sleep in seconds.

        Returns:
            True if cancelled during sleep, False if sleep completed normally.
        """
        return self._shutdown.wait(timeout=seconds)

    def check(self) -> None:
        """Raise CancelledError if cancelled.

        Use this at checkpoints in long-running operations without sleeps.
        """
        if self.is_cancelled():
            raise CancelledError()


def interruptible_sleep(seconds: float) -> bool:
    """Drop-in replacement for time.sleep() that respects cancellation.

    This function can be used anywhere time.sleep() is currently used.
    If there's an active cancellation token, the sleep will return early
    when cancellation is requested. Otherwise, it falls back to regular sleep.

    Args:
        seconds: Time to sleep in seconds.

    Returns:
        True if cancelled during sleep, False if sleep completed normally.
    """
    token = CancellationToken.current()
    if token is None:
        # No cancellation context, fall back to regular sleep
        time_module.sleep(seconds)  # noqa: TID251
        return False
    return token.sleep(seconds)
