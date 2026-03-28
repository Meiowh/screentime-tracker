"""Configuration — all settings from environment variables."""

import os
from zoneinfo import ZoneInfo

DATABASE_URL: str = os.environ.get("DATABASE_URL", "")
PORT: int = int(os.environ.get("PORT", 8080))

TIMEZONE = ZoneInfo("America/New_York")
TIMEZONE_LABEL = "ET"  # covers both EDT and EST automatically

NIGHT_OWL_START: int = 1   # 1 AM
NIGHT_OWL_END: int = 6     # 6 AM

AUTO_CLOSE_HOURS: int = 24
SLEEP_INFER_HOURS: int = 2  # charging + night + no activity for 2h = probably sleeping
