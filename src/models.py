"""Core business logic — toggle handling, summaries, analytics."""

import calendar
from datetime import datetime, timedelta
from src.config import (
    NIGHT_OWL_START, NIGHT_OWL_END,
    AUTO_CLOSE_HOURS, SLEEP_INFER_HOURS,
    get_current_timezone, get_timezone_label,
)
from src import db


def _tz():
    """Get the current dynamic timezone."""
    return get_current_timezone()


def _tz_name():
    """Get the current dynamic timezone name string for SQL queries."""
    return str(get_current_timezone())


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now():
    return datetime.now(_tz())


def _to_local(dt):
    """Convert an aware datetime to our configured timezone."""
    if dt is None:
        return None
    return dt.astimezone(_tz())


def _fmt_duration(seconds: int | float | None) -> str:
    """Human-readable duration string."""
    if seconds is None or seconds < 0:
        return "0s"
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    remaining = minutes % 60
    if remaining == 0:
        return f"{hours}h"
    return f"{hours}h {remaining}m"


def _session_duration_seconds(session: dict) -> int:
    """Compute duration for a session, using now() for still-open sessions."""
    if session.get("duration_seconds") is not None:
        return session["duration_seconds"]
    if session.get("end_ts"):
        return int((session["end_ts"] - session["start_ts"]).total_seconds())
    return int((_now() - _to_local(session["start_ts"])).total_seconds())


# ---------------------------------------------------------------------------
# Toggle — the critical function
# ---------------------------------------------------------------------------

# Debug log for toggle events (in-memory, last 200 entries)
_toggle_log: list[dict] = []
_TOGGLE_LOG_MAX = 200


def get_toggle_log() -> list[dict]:
    return list(_toggle_log)


def handle_toggle(app_name: str) -> dict:
    """Process a toggle signal from the iPhone shortcut.

    Logic:
    1. Active session for same app  -> close it (manual)
    2. Active session for diff app  -> close old (new_app), open new
    3. No active session            -> open new
    Always records an app_toggle event.
    """
    from datetime import timezone as tz
    now_utc = datetime.now(tz.utc)
    log_entry = {
        "time": _now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        "app": app_name,
        "active_before": None,
        "action": None,
        "fast_guard": False,
        "guard_ms": None,
        "last_toggle_ms": None,
    }

    # Calculate ms since last toggle
    if _toggle_log:
        last_log_time = _toggle_log[-1].get("_utc")
        if last_log_time:
            log_entry["last_toggle_ms"] = round((now_utc - last_log_time).total_seconds() * 1000)
    log_entry["_utc"] = now_utc  # internal, stripped before output

    # Clean up stale sessions first
    auto_close_stale_sessions()

    # Same-app duplicate guard: ignore if same app toggled within 0.5s
    if _toggle_log:
        last = _toggle_log[-1]
        if last.get("app") == app_name and last.get("_utc"):
            ms_since_last = (now_utc - last["_utc"]).total_seconds()
            if ms_since_last < 0.5:
                log_entry["action"] = "ignored(duplicate)"
                log_entry["guard_ms"] = round(ms_since_last * 1000)
                _toggle_log.append(log_entry)
                if len(_toggle_log) > _TOGGLE_LOG_MAX:
                    _toggle_log.pop(0)
                db.insert_event("app_toggle", value=app_name)
                return {"action": "ignored", "app": app_name, "reason": "duplicate_guard", "ms_since_last": round(ms_since_last * 1000)}

    # Fast-switch guard: ignore if this app was closed within 1.3s
    last_closed = db.get_last_closed_session_for_app(app_name)
    if last_closed and last_closed.get("end_ts"):
        closed_at = last_closed["end_ts"]
        if closed_at.tzinfo is None:
            closed_at = closed_at.replace(tzinfo=tz.utc)
        seconds_since_close = (now_utc - closed_at).total_seconds()
        if seconds_since_close < 1.3:
            log_entry["fast_guard"] = True
            log_entry["guard_ms"] = round(seconds_since_close * 1000)
            log_entry["action"] = "ignored"
            _toggle_log.append(log_entry)
            if len(_toggle_log) > _TOGGLE_LOG_MAX:
                _toggle_log.pop(0)
            db.insert_event("app_toggle", value=app_name)
            return {"action": "ignored", "app": app_name, "reason": "fast_switch_guard", "seconds_since_close": round(seconds_since_close, 1)}

    active = db.get_active_session()
    log_entry["active_before"] = active["app"] if active else None

    result = {}

    if active and active["app"] == app_name:
        closed = db.close_session(active["id"], end_reason="manual")
        result = {
            "action": "closed",
            "app": app_name,
            "duration_seconds": closed["duration_seconds"] if closed else 0,
            "duration": _fmt_duration(closed["duration_seconds"] if closed else 0),
        }
        log_entry["action"] = "closed"
    elif active and active["app"] != app_name:
        db.close_session(active["id"], end_reason="new_app")
        new_session = db.create_session(app_name)
        result = {
            "action": "switched",
            "closed_app": active["app"],
            "opened_app": app_name,
            "session_id": new_session["id"],
        }
        log_entry["action"] = f"switched({active['app']}->{app_name})"
    else:
        new_session = db.create_session(app_name)
        result = {
            "action": "opened",
            "app": app_name,
            "session_id": new_session["id"],
        }
        log_entry["action"] = "opened"

    _toggle_log.append(log_entry)
    if len(_toggle_log) > _TOGGLE_LOG_MAX:
        _toggle_log.pop(0)

    # Always record the event
    db.insert_event("app_toggle", value=app_name)

    return result


# ---------------------------------------------------------------------------
# Event handler (charging, location)
# ---------------------------------------------------------------------------

def handle_event(event_type: str) -> dict:
    """Record a non-app event and potentially infer sleep."""
    ev = db.insert_event(event_type)

    result = {"event": event_type, "id": ev["id"], "ts": str(ev["ts"])}

    # Sleep inference: charging_start + night hours + no recent activity
    if event_type == "charging_start":
        now = _now()
        if 0 <= now.hour <= 8:
            last_event_time = db.get_last_event_time()
            if last_event_time:
                gap = (now - _to_local(last_event_time)).total_seconds() / 3600
                if gap >= SLEEP_INFER_HOURS:
                    active = db.get_active_session()
                    if active:
                        # Close at last activity time, not now
                        db.close_session(
                            active["id"],
                            end_reason="sleep_inferred",
                            end_ts_expr=f"(SELECT MAX(ts) FROM events WHERE ts < NOW())",
                        )
                        result["sleep_inferred"] = True
                        result["closed_session_app"] = active["app"]

    return result


# ---------------------------------------------------------------------------
# Stale session cleanup
# ---------------------------------------------------------------------------

def auto_close_stale_sessions():
    """Close sessions open for more than AUTO_CLOSE_HOURS."""
    stale = db.get_stale_sessions(AUTO_CLOSE_HOURS)
    for s in stale:
        db.close_session(
            s["id"],
            end_reason="timeout",
            end_ts_expr=f"start_ts + INTERVAL '{AUTO_CLOSE_HOURS} hours'",
        )
    return len(stale)


# ---------------------------------------------------------------------------
# Force reset
# ---------------------------------------------------------------------------

def force_close_app(app_name: str) -> dict:
    """Force-close all active sessions for a specific app."""
    actives = db.get_all_active_sessions()
    closed = 0
    for s in actives:
        if s["app"] == app_name:
            db.close_session(s["id"], end_reason="force_closed")
            closed += 1
    db.insert_event("force_close", value=app_name)
    return {"app": app_name, "closed_sessions": closed}


def force_close_all() -> dict:
    """Force-close every active session."""
    actives = db.get_all_active_sessions()
    for s in actives:
        db.close_session(s["id"], end_reason="force_closed")
    db.insert_event("force_close_all")
    return {"closed_sessions": len(actives)}


# ---------------------------------------------------------------------------
# Today summary
# ---------------------------------------------------------------------------

def calculate_today_summary() -> dict:
    """Aggregate today's sessions into a summary."""
    now = _now()
    sessions = db.get_sessions_today(_tz_name())

    apps: dict[str, dict] = {}
    for s in sessions:
        app = s["app"]
        if app not in apps:
            apps[app] = {"open_count": 0, "total_seconds": 0, "status": "closed", "current_session_seconds": 0}
        apps[app]["open_count"] += 1
        dur = _session_duration_seconds(s)
        apps[app]["total_seconds"] += dur
        if s["end_ts"] is None:
            apps[app]["status"] = "active"
            apps[app]["current_session_seconds"] = dur

    total_seconds = sum(a["total_seconds"] for a in apps.values())

    app_list = []
    for name, info in sorted(apps.items(), key=lambda x: x[1]["total_seconds"], reverse=True):
        app_list.append({
            "app": name,
            "open_count": info["open_count"],
            "total_seconds": info["total_seconds"],
            "total_minutes": round(info["total_seconds"] / 60, 1),
            "total_formatted": _fmt_duration(info["total_seconds"]),
            "status": info["status"],
            "current_session_seconds": info["current_session_seconds"],
            "current_session_formatted": _fmt_duration(info["current_session_seconds"]) if info["status"] == "active" else None,
            "percentage": round(info["total_seconds"] / total_seconds * 100, 1) if total_seconds > 0 else 0,
        })

    return {
        "date": now.strftime("%Y-%m-%d"),
        "timezone": get_timezone_label(),
        "current_time": now.strftime("%H:%M:%S"),
        "total_seconds": total_seconds,
        "total_minutes": round(total_seconds / 60, 1),
        "total_formatted": _fmt_duration(total_seconds),
        "app_count": len(apps),
        "total_opens": sum(a["open_count"] for a in apps.values()),
        "apps": app_list,
    }


# ---------------------------------------------------------------------------
# Current activity
# ---------------------------------------------------------------------------

def get_current_activity() -> dict:
    """What is she doing right now?"""
    now = _now()
    active = db.get_active_session()
    if active:
        dur = _session_duration_seconds(active)
        return {
            "status": "active",
            "app": active["app"],
            "since": _to_local(active["start_ts"]).strftime("%H:%M:%S"),
            "duration_seconds": dur,
            "duration_formatted": _fmt_duration(dur),
            "session_id": active["id"],
            "current_time": now.strftime("%H:%M:%S %Z"),
        }
    else:
        last_event = db.get_last_event_time()
        return {
            "status": "inactive",
            "app": None,
            "last_activity": _to_local(last_event).strftime("%H:%M:%S") if last_event else None,
            "current_time": now.strftime("%H:%M:%S %Z"),
            "note": "Not using phone right now. Might be sleeping, eating, or chatting on the computer.",
        }


# ---------------------------------------------------------------------------
# Night owl & all-nighter
# ---------------------------------------------------------------------------

def get_night_owl_info() -> dict:
    """Detect late-night activity (1-6 AM)."""
    now = _now()
    current_hour = now.hour
    is_night = NIGHT_OWL_START <= current_hour < NIGHT_OWL_END

    night_sessions = db.get_sessions_in_hour_range(NIGHT_OWL_START, NIGHT_OWL_END, _tz_name(), days_back=1)
    night_apps = list(set(s["app"] for s in night_sessions))

    active = db.get_active_session()
    currently_using = active["app"] if active else None
    is_staying_up = is_night and (len(night_sessions) > 0 or currently_using is not None)

    return {
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "is_night_hours": is_night,
        "is_staying_up_late": is_staying_up,
        "night_activity_count": len(night_sessions),
        "night_apps": night_apps,
        "currently_using": currently_using,
        "warning": "She's staying up late! She should be sleeping!" if is_staying_up else "Not staying up late right now.",
    }


def get_all_nighter_info() -> dict:
    """Detect if there's been continuous activity past 4 AM without a sleep break."""
    now = _now()

    # Check for any session that was active at or after 4 AM today
    sessions = db.get_sessions_today(_tz_name())
    past_4am = False
    continuous = False
    last_end = None

    for s in sessions:
        local_start = _to_local(s["start_ts"])
        if local_start.hour >= 4 or (s["end_ts"] is None and now.hour >= 4):
            past_4am = True
        # Check for gaps > 30 min (would indicate a break)
        if last_end:
            gap = (_to_local(s["start_ts"]) - last_end).total_seconds()
            if gap > 1800:  # 30 min gap = break
                continuous = False
        if s["end_ts"]:
            last_end = _to_local(s["end_ts"])
        else:
            last_end = now

    # An all-nighter: activity past 4 AM with sessions going back to before 1 AM
    pre_1am = any(_to_local(s["start_ts"]).hour < NIGHT_OWL_START or _to_local(s["start_ts"]).hour >= 22 for s in sessions)
    is_all_nighter = past_4am and pre_1am and now.hour < 8

    return {
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "is_all_nighter": is_all_nighter,
        "sessions_today": len(sessions),
        "has_activity_past_4am": past_4am,
        "has_late_night_activity": pre_1am,
        "warning": "ALL-NIGHTER DETECTED! She has been up all night!" if is_all_nighter else "No all-nighter detected.",
    }


# ---------------------------------------------------------------------------
# Weekly trend
# ---------------------------------------------------------------------------

def get_weekly_trend() -> dict:
    """7-day usage summary."""
    now = _now()
    sessions = db.get_weekly_sessions(_tz_name())
    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    days = {}
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        day_key = day.strftime("%Y-%m-%d")
        days[day_key] = {
            "weekday": weekday_names[day.weekday()],
            "total_seconds": 0,
            "total_formatted": "0m",
            "app_count": 0,
            "total_opens": 0,
            "top_app": None,
            "apps": {},
        }

    for s in sessions:
        local_start = _to_local(s["start_ts"])
        day_key = local_start.strftime("%Y-%m-%d")
        if day_key not in days:
            continue
        app = s["app"]
        dur = _session_duration_seconds(s)
        d = days[day_key]
        d["total_seconds"] += dur
        d["total_opens"] += 1
        if app not in d["apps"]:
            d["apps"][app] = 0
        d["apps"][app] += dur

    for day_key, d in days.items():
        d["total_formatted"] = _fmt_duration(d["total_seconds"])
        d["total_minutes"] = round(d["total_seconds"] / 60, 1)
        d["app_count"] = len(d["apps"])
        if d["apps"]:
            d["top_app"] = max(d["apps"], key=d["apps"].get)
        del d["apps"]

    return {
        "period": f"{(now - timedelta(days=6)).strftime('%m-%d')} ~ {now.strftime('%m-%d')}",
        "timezone": get_timezone_label(),
        "days": days,
    }


# ---------------------------------------------------------------------------
# Hourly distribution
# ---------------------------------------------------------------------------

def get_hourly_distribution() -> dict:
    """24-hour heatmap data with per-app breakdown."""
    rows = db.get_hourly_distribution(_tz_name(), days_back=7)
    hours = {h: {"session_count": 0, "total_seconds": 0, "total_formatted": "0m", "apps": {}} for h in range(24)}
    for r in rows:
        h = r["hour"]
        hours[h]["session_count"] = r["session_count"]
        hours[h]["total_seconds"] = r["total_seconds"]
        hours[h]["total_formatted"] = _fmt_duration(r["total_seconds"])

    # Per-app breakdown: iterate sessions, distribute seconds to hours
    sessions = db.get_sessions_today(_tz_name())
    now = _now()
    for s in sessions:
        app = s["app"]
        start = _to_local(s["start_ts"])
        end = _to_local(s["end_ts"]) if s["end_ts"] else now

        # Walk through each hour the session spans
        current = start
        while current < end:
            h = current.hour
            # End of this hour slot
            next_hour = current.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            slot_end = min(next_hour, end)
            secs = int((slot_end - current).total_seconds())
            if secs > 0:
                hours[h]["apps"][app] = hours[h]["apps"].get(app, 0) + secs
            current = slot_end

    return {"hours": hours, "period": "last 7 days"}


# ---------------------------------------------------------------------------
# Longest session today
# ---------------------------------------------------------------------------

def get_longest_session_today() -> dict:
    """Find the longest single session today."""
    sessions = db.get_sessions_today(_tz_name())
    if not sessions:
        return {"found": False, "message": "No sessions today."}

    longest = max(sessions, key=lambda s: _session_duration_seconds(s))
    dur = _session_duration_seconds(longest)
    return {
        "found": True,
        "app": longest["app"],
        "duration_seconds": dur,
        "duration_formatted": _fmt_duration(dur),
        "started": _to_local(longest["start_ts"]).strftime("%H:%M:%S"),
        "ended": _to_local(longest["end_ts"]).strftime("%H:%M:%S") if longest["end_ts"] else "still active",
        "session_id": longest["id"],
    }


# ---------------------------------------------------------------------------
# App-specific queries
# ---------------------------------------------------------------------------

def get_app_usage(app_name: str) -> dict:
    """Usage history for a specific app."""
    sessions = db.get_sessions_for_app_today(app_name, _tz_name())
    total = sum(_session_duration_seconds(s) for s in sessions)
    return {
        "app": app_name,
        "today_sessions": len(sessions),
        "today_total_seconds": total,
        "today_total_formatted": _fmt_duration(total),
        "sessions": [
            {
                "id": s["id"],
                "start": _to_local(s["start_ts"]).strftime("%H:%M:%S"),
                "end": _to_local(s["end_ts"]).strftime("%H:%M:%S") if s["end_ts"] else "active",
                "duration": _fmt_duration(_session_duration_seconds(s)),
            }
            for s in sessions
        ],
    }


def app_open_count(app_name: str) -> dict:
    """How many times an app was opened today."""
    sessions = db.get_sessions_for_app_today(app_name, _tz_name())
    return {
        "app": app_name,
        "open_count_today": len(sessions),
    }


# ---------------------------------------------------------------------------
# Charging & location history
# ---------------------------------------------------------------------------

def get_charging_history() -> dict:
    """Last 3 days of charging events, paired as start/stop sessions."""
    events = db.get_events_by_types_recent(["charging_start", "charging_stop"], days=3)
    # Events come newest-first; reverse to chronological for pairing
    events = list(reversed(events))

    now = _now()
    pairs = []
    pending_start = None

    for e in events:
        local_ts = _to_local(e["ts"])
        if e["type"] == "charging_start":
            # If there's already a pending start without a stop, close it as incomplete
            if pending_start is not None:
                pairs.append({
                    "start_time": pending_start["time_str"],
                    "end_time": None,
                    "duration_minutes": int((local_ts - pending_start["ts"]).total_seconds() / 60),
                    "start_id": pending_start["id"],
                    "end_id": None,
                    "date": pending_start["date_str"],
                    "ongoing": False,
                })
            pending_start = {
                "id": e["id"],
                "ts": local_ts,
                "time_str": local_ts.strftime("%H:%M"),
                "date_str": local_ts.strftime("%Y-%m-%d"),
            }
        elif e["type"] == "charging_stop" and pending_start is not None:
            pairs.append({
                "start_time": pending_start["time_str"],
                "end_time": local_ts.strftime("%H:%M"),
                "duration_minutes": int((local_ts - pending_start["ts"]).total_seconds() / 60),
                "start_id": pending_start["id"],
                "end_id": e["id"],
                "date": pending_start["date_str"],
            })
            pending_start = None

    # If there's still a pending start with no stop, it's ongoing
    if pending_start is not None:
        pairs.append({
            "start_time": pending_start["time_str"],
            "end_time": None,
            "duration_minutes": int((now - pending_start["ts"]).total_seconds() / 60),
            "start_id": pending_start["id"],
            "end_id": None,
            "date": pending_start["date_str"],
            "ongoing": True,
        })

    # Group by day
    by_day: dict[str, list] = {}
    for p in pairs:
        day = p["date"]
        by_day.setdefault(day, []).append(p)

    return {"pairs": pairs, "by_day": by_day}


def get_location_history() -> dict:
    """Last 3 days of location events, paired as left_home/arrived_home trips."""
    events = db.get_events_by_types_recent(["left_home", "arrived_home"], days=3)
    # Events come newest-first; reverse to chronological for pairing
    events = list(reversed(events))

    now = _now()
    pairs = []
    pending_left = None

    for e in events:
        local_ts = _to_local(e["ts"])
        if e["type"] == "left_home":
            # If there's already a pending left without an arrival, close it as incomplete
            if pending_left is not None:
                pairs.append({
                    "left_time": pending_left["time_str"],
                    "arrived_time": None,
                    "duration_minutes": int((local_ts - pending_left["ts"]).total_seconds() / 60),
                    "left_id": pending_left["id"],
                    "arrived_id": None,
                    "date": pending_left["date_str"],
                    "ongoing": False,
                })
            pending_left = {
                "id": e["id"],
                "ts": local_ts,
                "time_str": local_ts.strftime("%H:%M"),
                "date_str": local_ts.strftime("%Y-%m-%d"),
            }
        elif e["type"] == "arrived_home" and pending_left is not None:
            pairs.append({
                "left_time": pending_left["time_str"],
                "arrived_time": local_ts.strftime("%H:%M"),
                "duration_minutes": int((local_ts - pending_left["ts"]).total_seconds() / 60),
                "left_id": pending_left["id"],
                "arrived_id": e["id"],
                "date": pending_left["date_str"],
            })
            pending_left = None

    # If there's still a pending left with no arrival, she's currently out
    if pending_left is not None:
        pairs.append({
            "left_time": pending_left["time_str"],
            "arrived_time": None,
            "duration_minutes": int((now - pending_left["ts"]).total_seconds() / 60),
            "left_id": pending_left["id"],
            "arrived_id": None,
            "date": pending_left["date_str"],
            "ongoing": True,
        })

    # Check if today has no left_home at all -> home all day
    today_str = now.strftime("%Y-%m-%d")
    today_has_left = any(p["date"] == today_str for p in pairs)

    # Group by day
    by_day: dict[str, list] = {}
    for p in pairs:
        day = p["date"]
        by_day.setdefault(day, []).append(p)

    # If today has no trips, mark as home all day
    if not today_has_left:
        by_day.setdefault(today_str, []).append({"status": "home_all_day", "date": today_str})

    return {"pairs": pairs, "by_day": by_day}


def get_current_status() -> dict:
    """Current charging and location state — single DB query."""
    latest = db.get_latest_events_by_types([
        "charging_start", "charging_stop", "arrived_home", "left_home"
    ])
    lc = latest.get("charging_start")
    lu = latest.get("charging_stop")
    if lc and lu:
        charging = lc["ts"] > lu["ts"]
    elif lc:
        charging = True
    else:
        charging = False

    la = latest.get("arrived_home")
    ll = latest.get("left_home")
    if la and ll:
        at_home = la["ts"] > ll["ts"]
    elif la:
        at_home = True
    else:
        at_home = False

    return {"charging": charging, "at_home": at_home}


# ---------------------------------------------------------------------------
# Recent activity
# ---------------------------------------------------------------------------

def get_recent_activity(limit: int = 20) -> dict:
    """Recent events across all types."""
    events = db.get_events_recent(limit)
    return {
        "events": [
            {
                "id": e["id"],
                "type": e["type"],
                "value": e["value"],
                "time": _to_local(e["ts"]).strftime("%Y-%m-%d %H:%M:%S %Z"),
                "auto": e["auto"],
            }
            for e in events
        ]
    }


# ---------------------------------------------------------------------------
# Daily report
# ---------------------------------------------------------------------------

def daily_report() -> dict:
    """Comprehensive daily report combining multiple data sources."""
    summary = calculate_today_summary()
    longest = get_longest_session_today()
    night = get_night_owl_info()
    all_nighter = get_all_nighter_info()
    current = get_current_activity()

    return {
        "date": summary["date"],
        "current_time": summary["current_time"],
        "timezone": summary["timezone"],
        "total_screen_time": summary["total_formatted"],
        "total_minutes": summary["total_minutes"],
        "app_count": summary["app_count"],
        "total_opens": summary["total_opens"],
        "top_apps": summary["apps"][:5],
        "longest_session": longest,
        "current_activity": current,
        "night_owl": night,
        "all_nighter": all_nighter,
    }


# ---------------------------------------------------------------------------
# Compare two days
# ---------------------------------------------------------------------------

def compare_days(date1: str, date2: str) -> dict:
    """Compare screen time between two dates (YYYY-MM-DD)."""
    s1 = db.get_sessions_for_date(date1, _tz_name())
    s2 = db.get_sessions_for_date(date2, _tz_name())

    def _summarize(sessions):
        total = sum(_session_duration_seconds(s) for s in sessions)
        apps = {}
        for s in sessions:
            apps.setdefault(s["app"], 0)
            apps[s["app"]] += _session_duration_seconds(s)
        return {
            "total_seconds": total,
            "total_formatted": _fmt_duration(total),
            "session_count": len(sessions),
            "app_count": len(apps),
            "top_app": max(apps, key=apps.get) if apps else None,
        }

    d1 = _summarize(s1)
    d2 = _summarize(s2)
    diff = d1["total_seconds"] - d2["total_seconds"]

    return {
        date1: d1,
        date2: d2,
        "difference_seconds": diff,
        "difference_formatted": f"{'+'if diff>=0 else ''}{_fmt_duration(abs(diff))}",
        "comparison": f"{date1} had {'more' if diff > 0 else 'less'} screen time by {_fmt_duration(abs(diff))}",
    }


# ---------------------------------------------------------------------------
# Day summary (specific date)
# ---------------------------------------------------------------------------

def get_day_summary(date_str: str) -> dict:
    """Detailed summary for a specific date (YYYY-MM-DD) in configured timezone."""
    sessions = db.get_sessions_for_date(date_str, _tz_name())
    now = _now()

    apps: dict[str, int] = {}
    hourly: dict[int, dict] = {h: {"total_seconds": 0, "apps": {}} for h in range(24)}

    for s in sessions:
        app = s["app"]
        dur = _session_duration_seconds(s)
        apps[app] = apps.get(app, 0) + dur

        # Distribute seconds across hours
        start = _to_local(s["start_ts"])
        end = _to_local(s["end_ts"]) if s["end_ts"] else now
        current = start
        while current < end:
            h = current.hour
            next_hour = current.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            slot_end = min(next_hour, end)
            secs = int((slot_end - current).total_seconds())
            if secs > 0:
                hourly[h]["total_seconds"] += secs
                hourly[h]["apps"][app] = hourly[h]["apps"].get(app, 0) + secs
            current = slot_end

    total_seconds = sum(apps.values())

    app_list = []
    for name, secs in sorted(apps.items(), key=lambda x: x[1], reverse=True):
        app_list.append({
            "app": name,
            "total_seconds": secs,
            "total_formatted": _fmt_duration(secs),
            "percentage": round(secs / total_seconds * 100, 1) if total_seconds > 0 else 0,
        })

    return {
        "date": date_str,
        "total_seconds": total_seconds,
        "total_formatted": _fmt_duration(total_seconds),
        "app_count": len(apps),
        "apps": app_list,
        "hourly": {str(h): data for h, data in hourly.items()},
    }


# ---------------------------------------------------------------------------
# Month overview
# ---------------------------------------------------------------------------

def get_month_overview(year: int, month: int) -> dict:
    """Per-day totals for a given month — uses SQL aggregation for speed."""
    num_days = calendar.monthrange(year, month)[1]
    days: dict[str, dict] = {}
    for d in range(1, num_days + 1):
        days[str(d)] = {"total_seconds": 0, "has_data": False}

    rows = db.get_month_day_totals(year, month, _tz_name())
    for r in rows:
        day_key = str(r["day"])
        if day_key in days:
            days[day_key]["total_seconds"] = r["total_seconds"]
            days[day_key]["has_data"] = r["total_seconds"] > 0

    return {"year": year, "month": month, "days": days}


# ---------------------------------------------------------------------------
# Sessions list for API/dashboard
# ---------------------------------------------------------------------------

def hourly_sleep_check() -> dict:
    """Check if the user is likely sleeping or needs a reminder.
    Called by cron job every hour.

    Rules (local timezone):
    1. Charging + no activity 2h + night(0-8) + active session -> auto close, msg: sleep
    2. Charging + no activity 3h + day(8-24) + active session -> auto close, msg: nap
    3. No charge + no activity 4h + night(0-8) + active session -> auto close, msg: night_warning
    4. No charge + no activity 2h + day(8-24) + active session -> no close, msg: reminder_2h
    5. No charge + no activity 3h + day(8-24) + active session -> no close, msg: reminder_3h
    6. No charge + no activity 4h + day(8-24) + active session -> auto close, msg: forced_close
    """
    now = _now()
    hour = now.hour
    is_night = 0 <= hour < 8

    active = db.get_active_session()
    if not active:
        return {"action": "none"}

    # Calculate hours idle: time since session started or last toggle event
    last_toggle_event = db.get_latest_event_by_type("app_toggle")
    if last_toggle_event and last_toggle_event["ts"]:
        last_activity = _to_local(last_toggle_event["ts"])
    else:
        last_activity = _to_local(active["start_ts"])

    hours_idle = (now - last_activity).total_seconds() / 3600
    app = active["app"]

    # Check charging status
    last_charge_start = db.get_latest_event_by_type("charging_start")
    last_charge_stop = db.get_latest_event_by_type("charging_stop")
    if last_charge_start and last_charge_stop:
        is_charging = last_charge_start["ts"] > last_charge_stop["ts"]
    elif last_charge_start:
        is_charging = True
    else:
        is_charging = False

    # Apply rules in order, return first match
    # Rule 1: Charging + 2h idle + night + active -> auto close, sleep
    if is_charging and hours_idle >= 2 and is_night:
        db.close_session(active["id"], end_reason="sleep_inferred")
        return {"action": "closed", "msg_type": "sleep", "app": app, "hours_idle": round(hours_idle, 1)}

    # Rule 2: Charging + 3h idle + day + active -> auto close, nap
    if is_charging and hours_idle >= 3 and not is_night:
        db.close_session(active["id"], end_reason="sleep_inferred")
        return {"action": "closed", "msg_type": "nap", "app": app, "hours_idle": round(hours_idle, 1)}

    # Rule 3: No charge + 4h idle + night + active -> auto close, night_warning
    if not is_charging and hours_idle >= 4 and is_night:
        db.close_session(active["id"], end_reason="auto_timeout")
        return {"action": "closed", "msg_type": "night_warning", "app": app, "hours_idle": round(hours_idle, 1)}

    # Rule 6: No charge + 4h idle + day + active -> auto close, forced_close
    # (check before 2h/3h reminders so 4h takes priority)
    if not is_charging and hours_idle >= 4 and not is_night:
        db.close_session(active["id"], end_reason="auto_timeout")
        return {"action": "closed", "msg_type": "forced_close", "app": app, "hours_idle": round(hours_idle, 1)}

    # Rule 5: No charge + 3h idle + day + active -> no close, reminder_3h
    if not is_charging and hours_idle >= 3 and not is_night:
        return {"action": "remind", "msg_type": "reminder_3h", "app": app, "hours_idle": round(hours_idle, 1)}

    # Rule 4: No charge + 2h idle + day + active -> no close, reminder_2h
    if not is_charging and hours_idle >= 2 and not is_night:
        return {"action": "remind", "msg_type": "reminder_2h", "app": app, "hours_idle": round(hours_idle, 1)}

    return {"action": "none"}


def get_recent_sessions_list(limit: int = 30) -> dict:
    """Today's sessions in configured timezone (most recent first)."""
    sessions = db.get_sessions_today_et(_tz_name())
    # Apply limit after filtering by today
    sessions = sessions[:limit]
    return {
        "sessions": [
            {
                "id": s["id"],
                "app": s["app"],
                "start": _to_local(s["start_ts"]).strftime("%Y-%m-%d %H:%M:%S"),
                "end": _to_local(s["end_ts"]).strftime("%Y-%m-%d %H:%M:%S") if s["end_ts"] else None,
                "duration_seconds": _session_duration_seconds(s),
                "duration_formatted": _fmt_duration(_session_duration_seconds(s)),
                "end_reason": s["end_reason"],
                "active": s["end_ts"] is None,
            }
            for s in sessions
        ]
    }
