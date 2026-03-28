"""PostgreSQL database layer — connection, schema, queries."""

import time
import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from src.config import DATABASE_URL

# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------

def _get_conn():
    """Create a new database connection.  Retries once on cold-start failure."""
    for attempt in range(3):
        try:
            conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
            conn.autocommit = True
            return conn
        except psycopg2.OperationalError:
            if attempt < 2:
                time.sleep(1)
            else:
                raise


@contextmanager
def get_cursor():
    """Yield a dict-cursor, closing the connection afterwards."""
    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            yield cur
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    type TEXT NOT NULL,
    value TEXT,
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    auto BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_events_type_ts ON events(type, ts);
CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);

CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    app TEXT NOT NULL,
    start_ts TIMESTAMPTZ NOT NULL,
    end_ts TIMESTAMPTZ,
    duration_seconds INTEGER,
    end_reason TEXT DEFAULT 'unknown',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sessions_app_start ON sessions(app, start_ts);
CREATE INDEX IF NOT EXISTS idx_sessions_start ON sessions(start_ts);
"""


def init_db():
    """Create tables and indexes if they do not exist."""
    with get_cursor() as cur:
        cur.execute(_SCHEMA_SQL)
    print("[db] Schema initialized.")


# ---------------------------------------------------------------------------
# Event helpers
# ---------------------------------------------------------------------------

def insert_event(event_type: str, value: str | None = None, auto: bool = False):
    """Insert a row into the events table and return its id."""
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO events (type, value, auto) VALUES (%s, %s, %s) RETURNING id, ts",
            (event_type, value, auto),
        )
        return dict(cur.fetchone())


def get_events_since(since_sql: str, event_type: str | None = None):
    """Return events since a TIMESTAMPTZ expression (e.g. NOW() - INTERVAL '24 hours')."""
    if event_type:
        sql = f"SELECT * FROM events WHERE ts >= ({since_sql}) AND type = %s ORDER BY ts"
        params = (event_type,)
    else:
        sql = f"SELECT * FROM events WHERE ts >= ({since_sql}) ORDER BY ts"
        params = ()
    with get_cursor() as cur:
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]


def get_events_between(start_sql: str, end_sql: str, event_type: str | None = None):
    """Return events between two TIMESTAMPTZ expressions."""
    if event_type:
        sql = f"SELECT * FROM events WHERE ts >= ({start_sql}) AND ts < ({end_sql}) AND type = %s ORDER BY ts"
        params = (event_type,)
    else:
        sql = f"SELECT * FROM events WHERE ts >= ({start_sql}) AND ts < ({end_sql}) ORDER BY ts"
        params = ()
    with get_cursor() as cur:
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]


# ---------------------------------------------------------------------------
# Session helpers
# ---------------------------------------------------------------------------

def get_active_session():
    """Return the currently open session (end_ts IS NULL), or None."""
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM sessions WHERE end_ts IS NULL ORDER BY start_ts DESC LIMIT 1"
        )
        row = cur.fetchone()
        return dict(row) if row else None


def get_last_closed_session_for_app(app_name: str):
    """Return the most recently closed session for a specific app, or None."""
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM sessions WHERE app = %s AND end_ts IS NOT NULL ORDER BY end_ts DESC LIMIT 1",
            (app_name,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def get_all_active_sessions():
    """Return ALL currently open sessions (end_ts IS NULL)."""
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM sessions WHERE end_ts IS NULL ORDER BY start_ts DESC"
        )
        return [dict(r) for r in cur.fetchall()]


def create_session(app: str):
    """Open a new session for the given app."""
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO sessions (app, start_ts) VALUES (%s, NOW()) RETURNING *",
            (app,),
        )
        return dict(cur.fetchone())


def close_session(session_id: int, end_reason: str = "manual", end_ts_expr: str = "NOW()"):
    """Close a session: set end_ts, compute duration, record reason."""
    with get_cursor() as cur:
        cur.execute(
            f"""UPDATE sessions
               SET end_ts = {end_ts_expr},
                   duration_seconds = EXTRACT(EPOCH FROM ({end_ts_expr} - start_ts))::int,
                   end_reason = %s
             WHERE id = %s
         RETURNING *""",
            (end_reason, session_id),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def update_session_end(session_id: int, new_end_ts: str):
    """Manual correction: update a session's end_ts and recalculate duration."""
    with get_cursor() as cur:
        cur.execute(
            """UPDATE sessions
               SET end_ts = %s::timestamptz,
                   duration_seconds = EXTRACT(EPOCH FROM (%s::timestamptz - start_ts))::int,
                   end_reason = 'corrected'
             WHERE id = %s
         RETURNING *""",
            (new_end_ts, new_end_ts, session_id),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def delete_session(session_id: int):
    """Delete a session by id."""
    with get_cursor() as cur:
        cur.execute("DELETE FROM sessions WHERE id = %s RETURNING id", (session_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def get_sessions_today(tz_name: str):
    """All sessions that started today in the given timezone."""
    with get_cursor() as cur:
        cur.execute(
            """SELECT * FROM sessions
             WHERE start_ts >= date_trunc('day', NOW() AT TIME ZONE %s) AT TIME ZONE %s
             ORDER BY start_ts""",
            (tz_name, tz_name),
        )
        return [dict(r) for r in cur.fetchall()]


def get_sessions_for_date(date_str: str, tz_name: str):
    """All sessions that started on a specific date (YYYY-MM-DD) in the given timezone."""
    with get_cursor() as cur:
        cur.execute(
            """SELECT * FROM sessions
             WHERE start_ts >= (%s::date AT TIME ZONE %s)
               AND start_ts < ((%s::date + INTERVAL '1 day') AT TIME ZONE %s)
             ORDER BY start_ts""",
            (date_str, tz_name, date_str, tz_name),
        )
        return [dict(r) for r in cur.fetchall()]


def get_sessions_between_dates(start_date: str, end_date: str, tz_name: str):
    """Sessions between two dates (inclusive start, exclusive end)."""
    with get_cursor() as cur:
        cur.execute(
            """SELECT * FROM sessions
             WHERE start_ts >= (%s::date AT TIME ZONE %s)
               AND start_ts < ((%s::date + INTERVAL '1 day') AT TIME ZONE %s)
             ORDER BY start_ts""",
            (start_date, tz_name, end_date, tz_name),
        )
        return [dict(r) for r in cur.fetchall()]


def get_sessions_for_month(year: int, month: int, tz_name: str):
    """All sessions for a given year/month in the given timezone."""
    with get_cursor() as cur:
        cur.execute(
            """SELECT * FROM sessions
             WHERE start_ts >= (make_date(%s, %s, 1) AT TIME ZONE %s)
               AND start_ts < ((make_date(%s, %s, 1) + INTERVAL '1 month') AT TIME ZONE %s)
             ORDER BY start_ts""",
            (year, month, tz_name, year, month, tz_name),
        )
        return [dict(r) for r in cur.fetchall()]


def get_sessions_today_et(tz_name: str):
    """All sessions that started today in the given timezone (filtered by local date)."""
    with get_cursor() as cur:
        cur.execute(
            """SELECT * FROM sessions
             WHERE start_ts >= date_trunc('day', NOW() AT TIME ZONE %s) AT TIME ZONE %s
               AND start_ts < (date_trunc('day', NOW() AT TIME ZONE %s) + INTERVAL '1 day') AT TIME ZONE %s
             ORDER BY start_ts DESC""",
            (tz_name, tz_name, tz_name, tz_name),
        )
        return [dict(r) for r in cur.fetchall()]


def get_recent_sessions(limit: int = 30):
    """Most recent sessions."""
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM sessions ORDER BY start_ts DESC LIMIT %s", (limit,)
        )
        return [dict(r) for r in cur.fetchall()]


def get_stale_sessions(hours: int):
    """Open sessions older than N hours."""
    with get_cursor() as cur:
        cur.execute(
            """SELECT * FROM sessions
             WHERE end_ts IS NULL
               AND start_ts < NOW() - make_interval(hours => %s)""",
            (hours,),
        )
        return [dict(r) for r in cur.fetchall()]


def get_sessions_in_hour_range(start_hour: int, end_hour: int, tz_name: str, days_back: int = 0):
    """Sessions active during a specific hour range (for night owl detection)."""
    with get_cursor() as cur:
        cur.execute(
            """SELECT * FROM sessions
             WHERE start_ts >= NOW() - make_interval(days => %s)
               AND (
                   EXTRACT(HOUR FROM start_ts AT TIME ZONE %s) >= %s
                   AND EXTRACT(HOUR FROM start_ts AT TIME ZONE %s) < %s
               )
             ORDER BY start_ts DESC""",
            (days_back if days_back > 0 else 1, tz_name, start_hour, tz_name, end_hour),
        )
        return [dict(r) for r in cur.fetchall()]


def get_last_event_time():
    """Timestamp of the most recent event."""
    with get_cursor() as cur:
        cur.execute("SELECT MAX(ts) as last_ts FROM events")
        row = cur.fetchone()
        return row["last_ts"] if row else None


def get_sessions_for_app_today(app: str, tz_name: str):
    """All sessions for a specific app today."""
    with get_cursor() as cur:
        cur.execute(
            """SELECT * FROM sessions
             WHERE app = %s
               AND start_ts >= date_trunc('day', NOW() AT TIME ZONE %s) AT TIME ZONE %s
             ORDER BY start_ts""",
            (app, tz_name, tz_name),
        )
        return [dict(r) for r in cur.fetchall()]


def get_weekly_sessions(tz_name: str):
    """All sessions from the last 7 days."""
    with get_cursor() as cur:
        cur.execute(
            """SELECT * FROM sessions
             WHERE start_ts >= (date_trunc('day', NOW() AT TIME ZONE %s) - INTERVAL '6 days') AT TIME ZONE %s
             ORDER BY start_ts""",
            (tz_name, tz_name),
        )
        return [dict(r) for r in cur.fetchall()]


def get_hourly_distribution(tz_name: str, days_back: int = 7):
    """Aggregate screen time by hour-of-day over the last N days."""
    with get_cursor() as cur:
        cur.execute(
            """SELECT
                 EXTRACT(HOUR FROM start_ts AT TIME ZONE %s)::int AS hour,
                 COUNT(*) AS session_count,
                 COALESCE(SUM(duration_seconds), 0)::int AS total_seconds
               FROM sessions
               WHERE start_ts >= NOW() - make_interval(days => %s)
                 AND duration_seconds IS NOT NULL
               GROUP BY hour
               ORDER BY hour""",
            (tz_name, days_back),
        )
        return [dict(r) for r in cur.fetchall()]


def get_events_recent(limit: int = 30):
    """Most recent events, newest first."""
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM events ORDER BY ts DESC LIMIT %s", (limit,)
        )
        return [dict(r) for r in cur.fetchall()]


def get_events_by_type_today(event_type: str, tz_name: str):
    """All events of a given type today."""
    with get_cursor() as cur:
        cur.execute(
            """SELECT * FROM events
             WHERE type = %s
               AND ts >= date_trunc('day', NOW() AT TIME ZONE %s) AT TIME ZONE %s
             ORDER BY ts""",
            (event_type, tz_name, tz_name),
        )
        return [dict(r) for r in cur.fetchall()]


def get_events_by_types_recent(types: list[str], days: int = 3):
    """Return events matching any of the given types from the last N days, newest first."""
    with get_cursor() as cur:
        cur.execute(
            """SELECT * FROM events
             WHERE type = ANY(%s)
               AND ts >= NOW() - make_interval(days => %s)
             ORDER BY ts DESC""",
            (types, days),
        )
        return [dict(r) for r in cur.fetchall()]


def get_latest_event_by_type(event_type: str):
    """Return the single most recent event of the given type, or None."""
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM events WHERE type = %s ORDER BY ts DESC LIMIT 1",
            (event_type,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def delete_event(event_id: int):
    """Delete an event by id."""
    with get_cursor() as cur:
        cur.execute("DELETE FROM events WHERE id = %s RETURNING id", (event_id,))
        row = cur.fetchone()
        return dict(row) if row else None
