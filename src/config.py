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


import time as _time

# In-memory timezone cache (avoids DB query on every API call)
_tz_cache = {"name": None, "offset": None, "expires": 0}
_TZ_CACHE_TTL = 60  # refresh from DB every 60 seconds


def _refresh_tz_cache():
    now = _time.time()
    if _tz_cache["expires"] > now:
        return
    from src.db import get_setting
    try:
        _tz_cache["name"] = get_setting('timezone_name', 'America/New_York')
        _tz_cache["offset"] = int(get_setting('timezone_offset', '-4'))
    except Exception:
        _tz_cache["name"] = 'America/New_York'
        _tz_cache["offset"] = -4
    _tz_cache["expires"] = now + _TZ_CACHE_TTL


def invalidate_tz_cache():
    """Call after timezone is updated to force refresh."""
    _tz_cache["expires"] = 0


def get_current_timezone() -> ZoneInfo:
    """Get current timezone from cache/database. Falls back to America/New_York."""
    _refresh_tz_cache()
    try:
        return ZoneInfo(_tz_cache["name"] or 'America/New_York')
    except Exception:
        return ZoneInfo('America/New_York')


def get_timezone_offset() -> int:
    """Get current UTC offset in hours."""
    _refresh_tz_cache()
    return _tz_cache["offset"] if _tz_cache["offset"] is not None else -4


def get_timezone_label() -> str:
    """Get a human-readable timezone label like 'UTC-4'."""
    offset = get_timezone_offset()
    sign = '+' if offset >= 0 else ''
    return f"UTC{sign}{offset}"
