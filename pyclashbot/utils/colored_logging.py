"""Colored logging utilities for the bot."""

import re
from enum import Enum


class LogLevel(Enum):
    """Log level types with associated colors."""

    INFO = ("\033[94m", "INFO")  # Blue
    SUCCESS = ("\033[92m", "SUCCESS")  # Green
    WARNING = ("\033[93m", "WARNING")  # Yellow
    ERROR = ("\033[91m", "ERROR")  # Red
    DEBUG = ("\033[96m", "DEBUG")  # Cyan
    NOTICE = ("\033[95m", "NOTICE")  # Magenta
    IDLE = ("\033[90m", "IDLE")  # Gray
    RESET = ("\033[0m", "RESET")  # Reset color

    @property
    def color(self) -> str:
        """Get ANSI color code."""
        return self.value[0]

    @property
    def label(self) -> str:
        """Get log level label."""
        return self.value[1]


class ColoredFormatter:
    """Formats log messages with colors for terminal output."""

    @staticmethod
    def format_message(level: LogLevel, message: str, use_colors: bool = True) -> str:
        """Format a log message with optional colors.

        Args:
            level: Log level
            message: Message to format
            use_colors: Whether to include ANSI color codes

        Returns:
            Formatted message
        """
        if not use_colors:
            return f"[{level.label}] {message}"

        return f"{level.color}[{level.label}]{LogLevel.RESET.color} {message}"

    @staticmethod
    def info(message: str) -> str:
        """Format an info message."""
        return ColoredFormatter.format_message(LogLevel.INFO, message)

    @staticmethod
    def success(message: str) -> str:
        """Format a success message."""
        return ColoredFormatter.format_message(LogLevel.SUCCESS, message)

    @staticmethod
    def warning(message: str) -> str:
        """Format a warning message."""
        return ColoredFormatter.format_message(LogLevel.WARNING, message)

    @staticmethod
    def error(message: str) -> str:
        """Format an error message."""
        return ColoredFormatter.format_message(LogLevel.ERROR, message)

    @staticmethod
    def debug(message: str) -> str:
        """Format a debug message."""
        return ColoredFormatter.format_message(LogLevel.DEBUG, message)


class LogColorMap:
    """Maps message patterns to colors for automatic coloring."""

    COLOR_CODES = {
        "yellow": "\033[93m",
        "gray": "\033[90m",
        "cyan": "\033[96m",
        "blue": "\033[94m",
        "green": "\033[92m",
        "magenta": "\033[95m",
        "orange": "\033[38;5;208m",
        "light_blue": "\033[96m",
        "red": "\033[91m",
    }

    COLOR_HEX = {
        "yellow": "#f1c40f",
        "gray": "#95a5a6",
        "cyan": "#00bcd4",
        "blue": "#3498db",
        "green": "#2ecc71",
        "magenta": "#9b59b6",
        "orange": "#e67e22",
        "light_blue": "#5dade2",
        "red": "#e74c3c",
    }

    # Pattern matching rules
    SUCCESS_KEYWORDS = [
        "success",
        "passed",
        "completed",
        "detected",
        "found",
        "connected",
        "started",
        "running",
    ]
    WARNING_KEYWORDS = [
        "warning",
        "retrying",
        "timeout",
        "skipping",
        "skipped",
        "suspended",
        "paused",
    ]
    STOP_KEYWORDS = [
        "stopping",
        "stopped",
        "outside",
    ]
    IDLE_KEYWORDS = [
        "waiting",
        "idle",
    ]
    ERROR_KEYWORDS = [
        "error",
        "failed",
        "crash",
        "exception",
        "fatal",
        "critical",
        "refused",
    ]
    DEBUG_KEYWORDS = [
        "debug",
    ]
    INFO_KEYWORDS = [
        "info",
        "status",
        "running",
    ]

    HIGHLIGHT_PATTERNS = [
        (r"returning to clash main", "magenta"),
        (r"back to main", "magenta"),
        (r"calculated play", "cyan"),
        (r"identified card", "blue"),
        (r"\bunknown\b", "yellow"),
        (r"\bunidentified\b", "yellow"),
        (r"\bwaiting\b", "gray"),
        (r"\belixer\b", "gray"),
        (r"\bplay\b", "cyan"),
        (r"\bcard\b", "blue"),
        (r"\bselecting\b|\bchosen\b|\bchoosing\b", "light_blue"),
        (r"\bdetected\b|\bfound\b", "green"),
        (r"\bretrying\b|\bfailed\b|\berror\b", "red"),
        (r"\bstart(?:ing|ed)?\b", "green"),
        (r"\bstopping\b|\bstopped\b|\boutside\b", "magenta"),
        (r"\bbattle\b|\bfight\b|\bmatch\b|\barena\b", "orange"),
        (r"\bcannon\b", "green"),
        (r"\b[a-z]+_[a-z_]+\b", "green"),
    ]

    @staticmethod
    def detect_level(message: str) -> LogLevel:
        """Detect appropriate log level based on message content.

        Args:
            message: Log message

        Returns:
            Appropriate LogLevel
        """
        lower_msg = message.lower()

        for keyword in LogColorMap.ERROR_KEYWORDS:
            if keyword in lower_msg:
                return LogLevel.ERROR

        for keyword in LogColorMap.WARNING_KEYWORDS:
            if keyword in lower_msg:
                return LogLevel.WARNING

        for keyword in LogColorMap.SUCCESS_KEYWORDS:
            if keyword in lower_msg:
                return LogLevel.SUCCESS

        for keyword in LogColorMap.STOP_KEYWORDS:
            if keyword in lower_msg:
                return LogLevel.NOTICE

        for keyword in LogColorMap.IDLE_KEYWORDS:
            if keyword in lower_msg:
                return LogLevel.IDLE

        for keyword in LogColorMap.DEBUG_KEYWORDS:
            if keyword in lower_msg:
                return LogLevel.DEBUG

        for keyword in LogColorMap.INFO_KEYWORDS:
            if keyword in lower_msg:
                return LogLevel.INFO

        return LogLevel.INFO

    @staticmethod
    def auto_format(message: str) -> str:
        """Automatically format a message based on its content.

        Args:
            message: Message to format

        Returns:
            Formatted message with appropriate color
        """
        level = LogColorMap.detect_level(message)
        highlighted = LogColorMap._apply_highlights(message)
        return ColoredFormatter.format_message(level, highlighted)

    @staticmethod
    def _apply_highlights(message: str) -> str:
        for pattern, color_name in LogColorMap.HIGHLIGHT_PATTERNS:
            color = LogColorMap.COLOR_CODES[color_name]
            message = re.sub(
                pattern,
                lambda match: f"{color}{match.group(0)}{LogLevel.RESET.color}",
                message,
                flags=re.IGNORECASE,
            )
        return message
