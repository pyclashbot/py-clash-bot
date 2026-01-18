"""Colored logging utilities for the bot."""

from enum import Enum


class LogLevel(Enum):
    """Log level types with associated colors."""

    INFO = ("\033[94m", "INFO")  # Blue
    SUCCESS = ("\033[92m", "SUCCESS")  # Green
    WARNING = ("\033[93m", "WARNING")  # Yellow
    ERROR = ("\033[91m", "ERROR")  # Red
    DEBUG = ("\033[96m", "DEBUG")  # Cyan
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
    ERROR_KEYWORDS = [
        "error",
        "failed",
        "crash",
        "exception",
        "fatal",
        "critical",
        "refused",
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
        return ColoredFormatter.format_message(level, message)
