"""Discord Rich Presence integration."""

from __future__ import annotations

import time
from typing import Any

try:
    from pypresence import Presence
except Exception:  # pragma: no cover - dependency may be optional at runtime
    Presence = None  # type: ignore[assignment]


class DiscordRPCManager:
    """Manages Discord Rich Presence lifecycle and updates."""

    APP_ID = "1181655703446888469"
    BUTTONS = [
        {"label": "GitHub", "url": "https://github.com/pyclashbot/py-clash-bot"},
        {"label": "Discord", "url": "https://discord.gg/X7YGaX76EH"},
    ]

    def __init__(self) -> None:
        self.rpc: Presence | None = None
        self.connected = False
        self.last_payload: dict[str, Any] | None = None

    def enable(self) -> None:
        """Connect to Discord if not already connected."""
        if self.connected or Presence is None:
            return
        try:
            self.rpc = Presence(self.APP_ID)
            self.rpc.connect()
            self.connected = True
        except Exception:
            self.rpc = None
            self.connected = False
            self.last_payload = None

    def disable(self) -> None:
        """Disconnect and clear presence."""
        if self.rpc is not None:
            try:
                self.rpc.clear()
            except Exception:
                pass
            try:
                self.rpc.close()
            except Exception:
                pass
        self.rpc = None
        self.connected = False
        self.last_payload = None

    def sync(self, enabled: bool, stats: dict[str, Any] | None) -> None:
        """Enable/disable and update presence based on current stats."""
        if not enabled:
            if self.connected:
                self.disable()
            return

        self.enable()
        if not self.connected or self.rpc is None or stats is None:
            return

        payload = self._build_payload(stats)
        if payload == self.last_payload:
            return

        try:
            self.rpc.update(**payload)
            self.last_payload = payload
        except Exception:
            # If update fails, drop connection to avoid repeated failures.
            self.disable()

    def _build_payload(self, stats: dict[str, Any]) -> dict[str, Any]:
        wins = int(stats.get("wins", 0) or 0)
        losses = int(stats.get("losses", 0) or 0)
        winrate = str(stats.get("winrate", "0%") or "0%")
        status = str(stats.get("current_status", "Idle") or "Idle")

        state_text, small_image, small_text = self._map_status_to_activity(status)

        return {
            "details": "pyclashbot",
            "state": f"{state_text} | W/L: {wins}/{losses} | {winrate}",
            "large_image": "robot",
            "large_text": "pyclashbot",
            "small_image": small_image,
            "small_text": small_text,
            "buttons": self.BUTTONS,
        }

    @staticmethod
    def _map_status_to_activity(status: str) -> tuple[str, str, str]:
        """Derive activity text and small image key from status string."""
        lower = status.lower()
        if "1v1" in lower:
            return "In a 1v1", "1v1", "Classic 1v1"
        if "2v2" in lower:
            return "In a 2v2", "2v2", "Classic 2v2"
        if "trophy" in lower or "road" in lower:
            return "Climbing Trophy Road", "trophy", "Trophy Road"
        if "menu" in lower or "idle" in lower:
            return "In menus", "robot", "Idle"
        return status if status else "Idle", "robot", "Idle"
