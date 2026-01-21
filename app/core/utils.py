"""Core utility functions for the application."""

from datetime import datetime
from zoneinfo import ZoneInfo


def now_in_ist() -> datetime:
    """Returns the current time as a timezone-aware datetime object in IST."""
    return datetime.now(ZoneInfo("Asia/Kolkata"))

def ensure_ist_aware(dt: datetime) -> datetime:
    """
    Ensures a datetime object is timezone-aware and set to IST.

    Handles both naive (e.g., from SQLite) and aware datetime objects
    to make timezone comparisons correct and database-agnostic.
    """
    ist_tz = ZoneInfo("Asia/Kolkata")

    if dt.tzinfo is None:
        # It's naive, assign the timezone
        return dt.replace(tzinfo=ist_tz)
    else:
        # Already aware, convert to IST
        return dt.astimezone(ist_tz)