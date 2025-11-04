"""Discord webhook integration for sending notifications."""

from __future__ import annotations

import threading
from typing import Any

import requests


class DiscordWebhook:
    """Discord webhook client for sending notifications."""

    def __init__(self, webhook_url: str | None = None) -> None:
        """Initialize Discord webhook client.

        Args:
        ----
            webhook_url: Discord webhook URL. If None, webhook is disabled.
        """
        self.webhook_url = webhook_url
        self.enabled = webhook_url is not None and webhook_url.strip() != ""

    def _send_webhook(self, payload: dict[str, Any], timeout: int = 5) -> bool:
        """Send webhook payload to Discord.

        Args:
        ----
            payload: Discord webhook payload
            timeout: Request timeout in seconds

        Returns:
        -------
            True if successful, False otherwise
        """
        if not self.enabled or self.webhook_url is None:
            return False

        try:
            response = requests.post(self.webhook_url, json=payload, timeout=timeout)
            response.raise_for_status()
            return True
        except Exception:
            # Silently fail to avoid disrupting bot operation
            return False

    def send(self, content: str | None = None, embeds: list[dict[str, Any]] | None = None) -> bool:
        """Send a message to Discord webhook.

        Args:
        ----
            content: Message content (plain text)
            embeds: List of embed dictionaries

        Returns:
        -------
            True if successful, False otherwise
        """
        if not self.enabled:
            return False

        payload: dict[str, Any] = {}
        if content:
            payload["content"] = content
        if embeds:
            payload["embeds"] = embeds

        if not payload:
            return False

        # Send in a separate thread to avoid blocking
        thread = threading.Thread(target=self._send_webhook, args=(payload,), daemon=True)
        thread.start()
        return True

    def send_embed(
        self,
        title: str,
        description: str | None = None,
        color: int | None = None,
        fields: list[dict[str, Any]] | None = None,
        footer: dict[str, Any] | None = None,
    ) -> bool:
        """Send an embed message to Discord webhook.

        Args:
        ----
            title: Embed title
            description: Embed description
            color: Embed color (integer, e.g., 0x00ff00 for green)
            fields: List of field dictionaries with 'name' and 'value' keys
            footer: Footer dictionary with 'text' key

        Returns:
        -------
            True if successful, False otherwise
        """
        embed: dict[str, Any] = {"title": title}
        if description:
            embed["description"] = description
        if color is not None:
            embed["color"] = color
        if fields:
            embed["fields"] = fields
        if footer:
            embed["footer"] = footer

        return self.send(embeds=[embed])

    def send_bot_started(self, runtime_info: dict[str, Any] | None = None) -> bool:
        """Send notification that bot has started.

        Args:
        ----
            runtime_info: Optional dictionary with runtime information

        Returns:
        -------
            True if successful, False otherwise
        """
        fields = []
        if runtime_info:
            for key, value in runtime_info.items():
                if value is not None:
                    fields.append({"name": key.replace("_", " ").title(), "value": str(value), "inline": True})

        return self.send_embed(
            title="🤖 Bot Started",
            description="PyClashBot has started successfully",
            color=0x00FF00,  # Green
            fields=fields if fields else None,
        )

    def send_bot_stopped(self, stats: dict[str, Any] | None = None) -> bool:
        """Send notification that bot has stopped.

        Args:
        ----
            stats: Optional dictionary with bot statistics

        Returns:
        -------
            True if successful, False otherwise
        """
        fields = []
        if stats:
            important_stats = [
                ("wins", "Wins"),
                ("losses", "Losses"),
                ("winrate", "Win Rate"),
                ("time_since_start", "Runtime"),
                ("restarts_after_failure", "Failures"),
            ]
            for key, label in important_stats:
                if key in stats and stats[key] is not None:
                    fields.append({"name": label, "value": str(stats[key]), "inline": True})

        return self.send_embed(
            title="🛑 Bot Stopped",
            description="PyClashBot has stopped",
            color=0xFFA500,  # Orange
            fields=fields if fields else None,
        )

    def send_battle_result(self, won: bool, battle_type: str, stats: dict[str, Any] | None = None) -> bool:
        """Send notification about battle result.

        Args:
        ----
            won: True if battle was won, False if lost
            battle_type: Type of battle (e.g., "1v1", "2v2")
            stats: Optional dictionary with battle statistics

        Returns:
        -------
            True if successful, False otherwise
        """
        emoji = "🎉" if won else "😔"
        title = f"{emoji} Battle {'Won' if won else 'Lost'}"
        description = f"Battle result: {battle_type}"
        color = 0x00FF00 if won else 0xFF0000  # Green for win, red for loss

        fields = []
        if stats:
            for key, value in stats.items():
                if value is not None:
                    fields.append({"name": key.replace("_", " ").title(), "value": str(value), "inline": True})

        return self.send_embed(title=title, description=description, color=color, fields=fields if fields else None)

    def send_error(self, error_message: str, context: str | None = None) -> bool:
        """Send notification about an error.

        Args:
        ----
            error_message: Error message
            context: Optional context information

        Returns:
        -------
            True if successful, False otherwise
        """
        fields = []
        if context:
            fields.append({"name": "Context", "value": context, "inline": False})

        description = error_message[:2000] if len(error_message) > 2000 else error_message

        return self.send_embed(
            title="⚠️ Bot Error",
            description=description,
            color=0xFF0000,  # Red
            fields=fields if fields else None,
        )

    def send_status_update(self, status: str, details: dict[str, Any] | None = None) -> bool:
        """Send a status update notification.

        Args:
        ----
            status: Status message
            details: Optional dictionary with additional details

        Returns:
        -------
            True if successful, False otherwise
        """
        fields = []
        if details:
            for key, value in details.items():
                if value is not None:
                    fields.append({"name": key.replace("_", " ").title(), "value": str(value), "inline": True})

        return self.send_embed(
            title="ℹ️ Status Update",
            description=status,
            color=0x0099FF,  # Blue
            fields=fields if fields else None,
        )

    def send_statistics(self, stats: dict[str, Any], title: str = "📊 Bot Statistics") -> bool:
        """Send bot statistics as an embed.

        Args:
        ----
            stats: Dictionary with statistics
            title: Optional title for the embed

        Returns:
        -------
            True if successful, False otherwise
        """
        fields = []
        for key, value in stats.items():
            if value is not None:
                fields.append({"name": key.replace("_", " ").title(), "value": str(value), "inline": True})

        return self.send_embed(
            title=title,
            description="Current bot statistics",
            color=0x0099FF,  # Blue
            fields=fields if fields else None,
        )

