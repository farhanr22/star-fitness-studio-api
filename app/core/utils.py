"""Core utility functions for the application."""

from datetime import datetime
from zoneinfo import ZoneInfo


def now_in_ist() -> datetime:
    """Returns the current time as a timezone-aware datetime object in IST."""
    return datetime.now(ZoneInfo("Asia/Kolkata"))