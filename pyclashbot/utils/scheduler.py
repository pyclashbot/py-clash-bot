"""Scheduler for running the bot at specific times."""

import datetime
from dataclasses import dataclass


@dataclass
class ScheduleConfig:
    """Configuration for bot scheduling."""

    enabled: bool = False
    start_hour: int = 8  # 0-23
    start_minute: int = 0  # 0-59
    end_hour: int = 22  # 0-23
    end_minute: int = 0  # 0-59

    @property
    def start_time(self) -> datetime.time:
        """Get start time as time object."""
        return datetime.time(self.start_hour, self.start_minute)

    @property
    def end_time(self) -> datetime.time:
        """Get end time as time object."""
        return datetime.time(self.end_hour, self.end_minute)

    def is_within_schedule(self) -> bool:
        """Check if current time is within schedule.

        Returns:
            True if within schedule, False otherwise
        """
        if not self.enabled:
            return True

        now = datetime.datetime.now().time()

        # If start time < end time (same day)
        if self.start_time <= self.end_time:
            return self.start_time <= now <= self.end_time

        # If start time > end time (crosses midnight)
        return now >= self.start_time or now <= self.end_time

    def time_until_start(self) -> datetime.timedelta:
        """Get time remaining until schedule starts.

        Returns:
            Timedelta object representing time until start
        """
        if not self.enabled or self.is_within_schedule():
            return datetime.timedelta(0)

        now = datetime.datetime.now()
        start_today = now.replace(hour=self.start_hour, minute=self.start_minute, second=0, microsecond=0)

        if start_today > now:
            return start_today - now

        # Start is tomorrow
        start_tomorrow = start_today + datetime.timedelta(days=1)
        return start_tomorrow - now

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "enabled": self.enabled,
            "start_hour": self.start_hour,
            "start_minute": self.start_minute,
            "end_hour": self.end_hour,
            "end_minute": self.end_minute,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ScheduleConfig":
        """Create from dictionary."""
        return cls(
            enabled=data.get("enabled", False),
            start_hour=data.get("start_hour", 8),
            start_minute=data.get("start_minute", 0),
            end_hour=data.get("end_hour", 22),
            end_minute=data.get("end_minute", 0),
        )
