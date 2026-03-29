"""Configuration — all settings from environment variables."""

import os
from zoneinfo import ZoneInfo

DATABASE_URL: str = os.environ.get("DATABASE_URL", "")
PORT: int = int(os.environ.get("PORT", 8080))

# Deprecated: use get_current_timezone() instead for dynamic timezone.
TIMEZONE = ZoneInfo("America/New_York")
TIMEZONE_LABEL = "ET"  # covers both EDT and EST automatically

NIGHT_OWL_START: int = 1   # 1 AM
NIGHT_OWL_END: int = 6     # 6 AM

AUTO_CLOSE_HOURS: int = 24
SLEEP_INFER_HOURS: int = 2  # charging + night + no activity for 2h = probably sleeping


def get_current_timezone() -> ZoneInfo:
    """Get current timezone from database settings. Falls back to America/New_York."""
    from src.db import get_setting
    try:
        tz_name = get_setting('timezone_name', 'America/New_York')
        return ZoneInfo(tz_name)
    except Exception:
        return ZoneInfo('America/New_York')


def get_timezone_offset() -> int:
    """Get current UTC offset in hours."""
    from src.db import get_setting
    try:
        return int(get_setting('timezone_offset', '-4'))
    except Exception:
        return -4


def get_timezone_label() -> str:
    """Get a human-readable timezone label like 'UTC-4'."""
    offset = get_timezone_offset()
    sign = '+' if offset >= 0 else ''
    return f"UTC{sign}{offset}"
