from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import discordrpc

if TYPE_CHECKING:
    from pyclashbot.utils.logger import Logger

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class PresenceSnapshot:
    wins: int
    losses: int
    winrate: str
    elapsed: str = field(compare=False)
    mode: str | None
    state: str | None
    emulator: str | None
    start_timestamp: int | None = field(compare=False)


class DiscordRPCManager:
    """Manage Discord Rich Presence for the application."""

    APPLICATION_ID = "1181655703446888469"
    MODE_ASSET_KEYS = {
        "classic 1v1": "1v1",
        "1v1": "1v1",
        "classic 2v2": "2v2",
        "2v2": "2v2",
        "trophy road": "trophy",
        "trophy": "trophy",
    }
    EMULATOR_ASSET_KEYS = {
        "bluestacks": "bluestacks",
        "bluestacks 5": "bluestacks",
        "google play": "gplay",
        "memu": "memu",
    }
    BUTTONS = (
        ("View on Github", "https://github.com/pyclashbot/py-clash-bot"),
        ("Join the Discord", "https://discord.gg/X7YGaX76EH"),
    )

    def __init__(self, application_id: str | int | None = None) -> None:
        self.application_id = str(application_id or self.APPLICATION_ID)
        self._enabled = False
        self._rpc: Any | None = None
        self._last_snapshot: PresenceSnapshot | None = None

    @property
    def enabled(self) -> bool:
        """Expose the current enable state."""
        return self._enabled

    def enable(self) -> None:
        """Enable Discord Rich Presence updates."""
        self._enabled = True
        self._ensure_connection()

    def disable(self) -> None:
        """Disable Rich Presence and clear any active activity."""
        self._enabled = False
        self._last_snapshot = None
        self._clear_presence()
        self._drop_connection()

    def shutdown(self) -> None:
        """Shut down the RPC manager."""
        self.disable()

    def update(self, logger: Logger | None, force: bool = False) -> None:
        """Update Discord Rich Presence from the provided logger."""
        if not self._enabled or logger is None:
            return

        snapshot = self._build_snapshot(logger)
        if snapshot is None:
            return

        if not force and snapshot == self._last_snapshot:
            return

        if not self._ensure_connection():
            return

        payload = self._build_activity(snapshot)
        if not payload:
            return

        try:
            self._rpc.set_activity(**payload)
        except Exception:  # pragma: no cover - defensive
            log.exception("Failed to update Discord RPC presence")
            self._last_snapshot = None
            self._drop_connection()
        else:
            self._last_snapshot = snapshot

    def _build_snapshot(self, logger: Logger) -> PresenceSnapshot | None:
        wins = getattr(logger, "wins", None)
        losses = getattr(logger, "losses", None)
        winrate = getattr(logger, "winrate", None)

        if wins is None or losses is None or winrate is None:
            return None

        elapsed = "00:00:00"
        if hasattr(logger, "calc_time_since_start"):
            try:
                elapsed = str(logger.calc_time_since_start())
            except Exception:  # pragma: no cover - defensive
                log.debug("Unable to calculate elapsed time for RPC", exc_info=True)

        mode = getattr(logger, "current_mode", None)
        state = getattr(logger, "current_state", None)
        emulator = getattr(logger, "current_emulator", None)

        start_timestamp: int | None = None
        start_time = getattr(logger, "start_time", None)
        if isinstance(start_time, (int, float)):
            start_timestamp = int(start_time)
        elif start_time is None and hasattr(logger, "calc_time_since_start"):
            # Approximate a start timestamp if the logger is timed but missing start_time
            try:
                elapsed_seconds = self._parse_elapsed_seconds(elapsed)
                if elapsed_seconds is not None:
                    start_timestamp = int(time.time() - elapsed_seconds)
            except Exception:  # pragma: no cover - defensive
                log.debug("Unable to backfill RPC start timestamp", exc_info=True)

        return PresenceSnapshot(
            wins=int(wins),
            losses=int(losses),
            winrate=str(winrate),
            elapsed=str(elapsed),
            mode=str(mode) if mode else None,
            state=str(state) if state else None,
            emulator=str(emulator) if emulator else None,
            start_timestamp=start_timestamp,
        )

    def _build_activity(self, snapshot: PresenceSnapshot) -> dict[str, Any] | None:
        if not self._rpc:
            return None

        buttons = (
            [discordrpc.Button(text, url) for text, url in self.BUTTONS]
            if self.BUTTONS
            else None
        )

        details = f"W {snapshot.wins} | L {snapshot.losses} | WR {snapshot.winrate}"
        large_text = f"{snapshot.mode or 'py-clash-bot'} | {snapshot.elapsed}"

        state_text = snapshot.state or snapshot.mode or "Idle"

        return {
            "state": state_text,
            "details": details,
            "ts_start": snapshot.start_timestamp,
            "large_image": self._resolve_mode_asset(snapshot.mode),
            "large_text": large_text,
            "small_image": self._resolve_emulator_asset(snapshot.emulator),
            "small_text": snapshot.emulator or "Unknown",
            "buttons": buttons,
        }

    def _resolve_mode_asset(self, mode: str | None) -> str:
        if not mode:
            return "trophy"
        normalized = mode.strip().lower()
        return self.MODE_ASSET_KEYS.get(normalized, "trophy")

    def _resolve_emulator_asset(self, emulator: str | None) -> str:
        if not emulator:
            return "memu"
        normalized = emulator.strip().lower()
        return self.EMULATOR_ASSET_KEYS.get(normalized, "memu")

    def _ensure_connection(self) -> bool:
        if not self._enabled:
            return False
        if self._rpc is not None and getattr(self._rpc, "ipc", None) is not None:
            if getattr(self._rpc.ipc, "connected", False):
                return True

        try:
            self._rpc = discordrpc.RPC(
                app_id=self.application_id,
                output=False,
                exit_on_disconnect=False,
            )
        except Exception:  # pragma: no cover - defensive
            log.exception("Unable to establish Discord RPC connection")
            self._rpc = None
            return False
        return True

    def _clear_presence(self) -> None:
        if not self._rpc:
            return
        try:
            self._rpc.clear()
        except Exception:  # pragma: no cover - defensive
            log.debug("Failed to clear Discord RPC presence", exc_info=True)

    def _drop_connection(self) -> None:
        if not self._rpc:
            return
        try:
            self._rpc.disconnect()
        except Exception:  # pragma: no cover - defensive
            log.debug("Failed to disconnect Discord RPC", exc_info=True)
        finally:
            self._rpc = None

    @staticmethod
    def _parse_elapsed_seconds(elapsed: str) -> int | None:
        parts = elapsed.split(":")
        if len(parts) != 3:
            return None
        try:
            hours, minutes, seconds = (int(part) for part in parts)
        except ValueError:
            return None
        return hours * 3600 + minutes * 60 + seconds
