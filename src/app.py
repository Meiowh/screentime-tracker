"""FastMCP application — HTTP routes and MCP tools."""

import json
import re
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from mcp.server.fastmcp import FastMCP

from src.config import PORT, get_current_timezone, get_timezone_offset, get_timezone_label
from src import models
from src.dashboard import render_dashboard
from src.notify import send_telegram_notification

# ---------------------------------------------------------------------------
# Timezone auto-detection helper
# ---------------------------------------------------------------------------

def _auto_detect_timezone(t_param: str) -> dict | None:
    """Parse a ?t= ISO timestamp, extract timezone offset, update if changed.
    Example: t=2026-03-29T12:28:00-04:00 -> offset = -4
    Returns dict with old/new offset if changed, else None.
    """
    from src.db import get_setting, set_setting

    # Match timezone offset like -04:00, +05:30, +00:00, Z
    match = re.search(r'([+-])(\d{2}):(\d{2})$', t_param)
    if not match and t_param.endswith('Z'):
        new_offset = 0
    elif match:
        sign = 1 if match.group(1) == '+' else -1
        hours = int(match.group(2))
        minutes = int(match.group(3))
        new_offset = sign * hours + (sign * minutes / 60 if minutes else 0)
        # Keep as int if it's a whole number
        if new_offset == int(new_offset):
            new_offset = int(new_offset)
    else:
        return None

    old_offset_str = get_setting('timezone_offset', '-4')
    try:
        old_offset = float(old_offset_str) if '.' in old_offset_str else int(old_offset_str)
    except ValueError:
        old_offset = -4

    if new_offset != old_offset:
        set_setting('timezone_offset', str(new_offset))

        # Try to map offset to a timezone name
        offset_to_tz = {
            -12: "Etc/GMT+12", -11: "Pacific/Midway", -10: "Pacific/Honolulu",
            -9: "America/Anchorage", -8: "America/Los_Angeles", -7: "America/Denver",
            -6: "America/Chicago", -5: "America/New_York", -4: "America/New_York",
            -3: "America/Sao_Paulo", 0: "UTC",
            1: "Europe/London", 2: "Europe/Berlin", 3: "Europe/Moscow",
            4: "Asia/Dubai", 5: "Asia/Karachi", 6: "Asia/Dhaka",
            7: "Asia/Bangkok", 8: "Asia/Shanghai", 9: "Asia/Tokyo",
            10: "Australia/Sydney", 12: "Pacific/Auckland",
        }
        int_offset = int(new_offset) if new_offset == int(new_offset) else None
        if int_offset is not None and int_offset in offset_to_tz:
            set_setting('timezone_name', offset_to_tz[int_offset])

        print(f"[timezone] Auto-updated from {old_offset} to {new_offset}")
        return {"old_offset": old_offset, "new_offset": new_offset}

    return None


# ---------------------------------------------------------------------------
# FastMCP instance
# ---------------------------------------------------------------------------

mcp = FastMCP("Screen Time", host="0.0.0.0", port=PORT)

# =========================================================================
# HTTP Routes
# =========================================================================

@mcp.custom_route("/", methods=["GET"])
async def root(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "Screen Time Tracker v3", "panel": "/panel"})


@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "healthy"})


@mcp.custom_route("/api/debug/togglelog", methods=["GET"])
async def toggle_log(request: Request) -> HTMLResponse:
    """Plain text debug log of recent toggle events."""
    from src.models import get_toggle_log
    log = get_toggle_log()
    lines = ["=== Toggle Debug Log (last 200) ===", ""]
    for entry in log:
        e = {k: v for k, v in entry.items() if k != "_utc"}
        guard_info = f" BLOCKED({e['guard_ms']}ms)" if e.get("fast_guard") else ""
        since_last = f" +{e['last_toggle_ms']}ms" if e.get("last_toggle_ms") is not None else " (first)"
        active = f" active={e['active_before']}" if e.get("active_before") else " active=none"
        lines.append(f"{e['time']} | {e['app']:20s} | {e['action']:30s}{active}{since_last}{guard_info}")
    lines.append("")
    lines.append(f"Total entries: {len(log)}")
    return HTMLResponse("<pre>" + "\n".join(lines) + "</pre>", headers={"Content-Type": "text/html; charset=utf-8"})


# --- Core toggle (iPhone shortcut hits this) ---

@mcp.custom_route("/api/screentime/toggle/{app_name}", methods=["GET"])
async def toggle(request: Request) -> JSONResponse:
    app_name = request.path_params["app_name"]
    result = models.handle_toggle(app_name)
    return JSONResponse(result)


# --- Open/Close observation endpoints (parallel data collection, no logic changes) ---

@mcp.custom_route("/api/screentime/open/{app_name}", methods=["GET"])
async def open_app(request: Request) -> JSONResponse:
    app_name = request.path_params["app_name"]
    from src.db import insert_event
    ev = insert_event("app_open", value=app_name)
    return JSONResponse({"event": "app_open", "app": app_name, "id": ev["id"], "ts": str(ev["ts"])})


@mcp.custom_route("/api/screentime/close/{app_name}", methods=["GET"])
async def close_app(request: Request) -> JSONResponse:
    app_name = request.path_params["app_name"]
    from src.db import insert_event
    ev = insert_event("app_close", value=app_name)
    return JSONResponse({"event": "app_close", "app": app_name, "id": ev["id"], "ts": str(ev["ts"])})


# --- Comparison page: toggle vs open/close ---

@mcp.custom_route("/api/debug/compare", methods=["GET"])
async def compare_signals(request: Request) -> HTMLResponse:
    """Compare toggle events vs open/close events to find discrepancies."""
    from src.db import get_cursor
    with get_cursor() as cur:
        cur.execute("""
            SELECT type, value, ts
            FROM events
            WHERE type IN ('app_toggle', 'app_open', 'app_close')
              AND ts >= NOW() - INTERVAL '3 days'
            ORDER BY ts
        """)
        rows = [dict(r) for r in cur.fetchall()]

    # Filter to only apps that have open/close data
    oc_apps = set(r["value"] for r in rows if r["type"] in ("app_open", "app_close"))

    lines = [
        "=== Toggle vs Open/Close 对比 (最近3天) ===",
        f"有 open/close 数据的 app: {', '.join(sorted(oc_apps)) if oc_apps else '无'}",
        "",
        "时间                     | 类型        | App                  | 备注",
        "-------------------------|-------------|----------------------|------",
    ]

    # Build timeline for comparison
    prev_toggle = {}  # app -> last toggle timestamp
    prev_oc = {}      # app -> last open/close timestamp + type

    for r in rows:
        ts = r["ts"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] if r["ts"] else "?"
        app = r["value"] or "?"
        etype = r["type"]

        note = ""

        if etype == "app_toggle":
            # Check if there's a matching open/close nearby
            if app in oc_apps:
                tag = "[toggle] "
                # Look for nearby open/close within 2 seconds
                matched = False
                for r2 in rows:
                    if r2["type"] in ("app_open", "app_close") and r2["value"] == app:
                        diff = abs((r["ts"] - r2["ts"]).total_seconds())
                        if diff < 2:
                            matched = True
                            break
                if not matched:
                    note = "⚠ toggle 无对应 open/close"
                else:
                    note = "✓"
            else:
                tag = "[toggle] "
                note = "(无对比数据)"

            lines.append(f"{ts} | {tag:11s} | {app:20s} | {note}")

        elif etype == "app_open":
            tag = "[open]   "
            # Check for matching toggle nearby
            matched = False
            for r2 in rows:
                if r2["type"] == "app_toggle" and r2["value"] == app:
                    diff = abs((r["ts"] - r2["ts"]).total_seconds())
                    if diff < 2:
                        matched = True
                        break
            if not matched:
                note = "⚠ open 无对应 toggle（自动化漏报？）"
            else:
                note = "✓"
            lines.append(f"{ts} | {tag:11s} | {app:20s} | {note}")

        elif etype == "app_close":
            tag = "[close]  "
            matched = False
            for r2 in rows:
                if r2["type"] == "app_toggle" and r2["value"] == app:
                    diff = abs((r["ts"] - r2["ts"]).total_seconds())
                    if diff < 2:
                        matched = True
                        break
            if not matched:
                note = "⚠ close 无对应 toggle（toggle 漏了？）"
            else:
                note = "✓"
            lines.append(f"{ts} | {tag:11s} | {app:20s} | {note}")

    # Summary
    toggles_for_oc_apps = [r for r in rows if r["type"] == "app_toggle" and r["value"] in oc_apps]
    opens = [r for r in rows if r["type"] == "app_open"]
    closes = [r for r in rows if r["type"] == "app_close"]

    lines.append("")
    lines.append("=== 统计 ===")
    lines.append(f"对比 app 的 toggle 总数: {len(toggles_for_oc_apps)}")
    lines.append(f"open 信号总数: {len(opens)}")
    lines.append(f"close 信号总数: {len(closes)}")
    lines.append(f"open + close 总数: {len(opens) + len(closes)}")
    lines.append("")
    lines.append("如果 toggle 数 ≈ open+close → toggle 没漏，问题在逻辑判断")
    lines.append("如果 toggle 数 < open+close → toggle 有信号丢失")
    lines.append("如果 open 无对应 toggle → 自动化发了 open 但 toggle 没到（网络问题？）")
    lines.append("如果 toggle 无对应 open/close → 自动化没发 open/close（iOS 漏报）")

    return HTMLResponse("<pre style='font-size:13px;line-height:1.5'>" + "\n".join(lines) + "</pre>",
                       headers={"Content-Type": "text/html; charset=utf-8"})


# --- Charging & location history (must be before wildcard /api/event/{event_type}) ---

@mcp.custom_route("/api/history/charging", methods=["GET"])
async def charging_history_api(request: Request) -> JSONResponse:
    return JSONResponse(models.get_charging_history())


@mcp.custom_route("/api/history/location", methods=["GET"])
async def location_history_api(request: Request) -> JSONResponse:
    return JSONResponse(models.get_location_history())


# --- Day summary & month overview (must be before wildcard routes) ---

@mcp.custom_route("/api/screentime/day/{date}", methods=["GET"])
async def day_summary_api(request: Request) -> JSONResponse:
    date_str = request.path_params["date"]
    return JSONResponse(models.get_day_summary(date_str))


@mcp.custom_route("/api/screentime/month/{year}/{month}", methods=["GET"])
async def month_overview_api(request: Request) -> JSONResponse:
    year = int(request.path_params["year"])
    month = int(request.path_params["month"])
    return JSONResponse(models.get_month_overview(year, month))


@mcp.custom_route("/api/history/delete/{event_id}", methods=["GET", "DELETE"])
async def delete_event_route(request: Request) -> JSONResponse:
    event_id = int(request.path_params["event_id"])
    from src.db import delete_event
    result = delete_event(event_id)
    if result:
        return JSONResponse({"status": "deleted", "id": result["id"]})
    return JSONResponse({"error": "event not found"}, status_code=404)


# --- Timezone settings ---

@mcp.custom_route("/api/settings/timezone", methods=["GET"])
async def get_timezone(request: Request) -> JSONResponse:
    """Get current timezone setting."""
    from src.db import get_setting
    tz_name = get_setting('timezone_name', 'America/New_York')
    tz_offset = get_setting('timezone_offset', '-4')
    return JSONResponse({
        "timezone_name": tz_name,
        "timezone_offset": int(tz_offset),
        "label": get_timezone_label(),
    })


@mcp.custom_route("/api/settings/timezone", methods=["POST"])
async def set_timezone(request: Request) -> JSONResponse:
    """Set timezone. Body: {"offset": -7} or {"name": "America/Los_Angeles"} or both."""
    from src.db import set_setting
    from zoneinfo import ZoneInfo
    try:
        body = await request.json()
        updated = {}

        if "offset" in body:
            offset = body["offset"]
            set_setting('timezone_offset', str(offset))
            updated["timezone_offset"] = offset

        if "name" in body:
            tz_name = body["name"]
            # Validate timezone name
            try:
                ZoneInfo(tz_name)
            except Exception:
                return JSONResponse({"error": f"Invalid timezone name: {tz_name}"}, status_code=400)
            set_setting('timezone_name', tz_name)
            updated["timezone_name"] = tz_name

        # If only offset provided, try to keep name in sync
        if "offset" in body and "name" not in body:
            # Map common offsets to timezone names
            offset_to_tz = {
                -12: "Etc/GMT+12", -11: "Pacific/Midway", -10: "Pacific/Honolulu",
                -9: "America/Anchorage", -8: "America/Los_Angeles", -7: "America/Denver",
                -6: "America/Chicago", -5: "America/New_York", -4: "America/New_York",
                -3: "America/Sao_Paulo", -2: "Atlantic/South_Georgia", -1: "Atlantic/Azores",
                0: "UTC", 1: "Europe/London", 2: "Europe/Berlin", 3: "Europe/Moscow",
                4: "Asia/Dubai", 5: "Asia/Karachi", 6: "Asia/Dhaka",
                7: "Asia/Bangkok", 8: "Asia/Shanghai", 9: "Asia/Tokyo",
                10: "Australia/Sydney", 11: "Pacific/Noumea", 12: "Pacific/Auckland",
            }
            if offset in offset_to_tz:
                set_setting('timezone_name', offset_to_tz[offset])
                updated["timezone_name"] = offset_to_tz[offset]

        from src.config import invalidate_tz_cache
        invalidate_tz_cache()
        return JSONResponse({"status": "updated", **updated})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# --- Events (charging, location) ---

@mcp.custom_route("/api/event/{event_type}", methods=["GET"])
async def event(request: Request) -> JSONResponse:
    event_type = request.path_params["event_type"]

    # Auto-detect timezone from ?t= parameter on charging_start
    tz_auto_updated = None
    if event_type == "charging_start":
        t_param = request.query_params.get("t", "")
        if t_param:
            tz_auto_updated = _auto_detect_timezone(t_param)

    result = models.handle_event(event_type)

    if tz_auto_updated:
        from src.config import invalidate_tz_cache
        invalidate_tz_cache()
        result["timezone_auto_updated"] = tz_auto_updated

    return JSONResponse(result)


# --- Today summary ---

@mcp.custom_route("/api/screentime/today", methods=["GET"])
async def today_api(request: Request) -> JSONResponse:
    return JSONResponse(models.calculate_today_summary())


# --- Night owl ---

@mcp.custom_route("/api/screentime/nightowl", methods=["GET"])
async def nightowl_api(request: Request) -> JSONResponse:
    return JSONResponse(models.get_night_owl_info())


# --- All-nighter ---

@mcp.custom_route("/api/screentime/allnighter", methods=["GET"])
async def allnighter_api(request: Request) -> JSONResponse:
    return JSONResponse(models.get_all_nighter_info())


# --- Weekly ---

@mcp.custom_route("/api/screentime/weekly", methods=["GET"])
async def weekly_api(request: Request) -> JSONResponse:
    return JSONResponse(models.get_weekly_trend())


# --- Hourly distribution ---

@mcp.custom_route("/api/screentime/hourly", methods=["GET"])
async def hourly_api(request: Request) -> JSONResponse:
    return JSONResponse(models.get_hourly_distribution())


# --- Recent sessions ---

@mcp.custom_route("/api/screentime/sessions", methods=["GET"])
async def sessions_api(request: Request) -> JSONResponse:
    return JSONResponse(models.get_recent_sessions_list())


# --- Longest session today ---

@mcp.custom_route("/api/screentime/longest", methods=["GET"])
async def longest_api(request: Request) -> JSONResponse:
    return JSONResponse(models.get_longest_session_today())


# --- Manual correction ---

@mcp.custom_route("/api/screentime/correct/{session_id}", methods=["POST"])
async def correct_session(request: Request) -> JSONResponse:
    session_id = int(request.path_params["session_id"])
    try:
        body = await request.json()
        new_end = body.get("end_ts")
        new_start = body.get("start_ts")
        if not new_end and not new_start:
            return JSONResponse({"error": "end_ts or start_ts required"}, status_code=400)
        from src.db import update_session_end, get_setting
        # User inputs are in local time — if no timezone info, assume current configured timezone
        has_tz = lambda s: bool(re.search(r'[+-]\d{2}:\d{2}|[+-]\d{4}|Z$|America/|Europe/|Asia/', s)) if s else True
        current_tz = get_setting('timezone_name', 'America/New_York')
        if new_end and not has_tz(new_end):
            new_end = new_end + " " + current_tz
        if new_start and not has_tz(new_start):
            new_start = new_start + " " + current_tz
        result = update_session_end(session_id, new_end or None)
        if result:
            return JSONResponse({"status": "updated", "session": {
                "id": result["id"],
                "app": result["app"],
                "end_ts": str(result["end_ts"]),
                "duration_seconds": result["duration_seconds"],
            }})
        return JSONResponse({"error": "session not found"}, status_code=404)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# --- Delete session ---

@mcp.custom_route("/api/screentime/session/{session_id}", methods=["DELETE"])
async def delete_session_route(request: Request) -> JSONResponse:
    session_id = int(request.path_params["session_id"])
    from src.db import delete_session
    result = delete_session(session_id)
    if result:
        return JSONResponse({"status": "deleted", "id": result["id"]})
    return JSONResponse({"error": "session not found"}, status_code=404)


# --- Force reset ---

@mcp.custom_route("/api/screentime/reset/{app_name}", methods=["GET"])
async def reset_app(request: Request) -> JSONResponse:
    app_name = request.path_params["app_name"]
    result = models.force_close_app(app_name)
    return JSONResponse(result)


@mcp.custom_route("/api/screentime/reset_all", methods=["GET"])
async def reset_all(request: Request) -> JSONResponse:
    result = models.force_close_all()
    return JSONResponse(result)


# --- Current status (charging + location) ---

@mcp.custom_route("/api/screentime/status", methods=["GET"])
async def status_api(request: Request) -> JSONResponse:
    return JSONResponse(models.get_current_status())


# --- Hourly cron check ---

@mcp.custom_route("/api/cron/hourly_check", methods=["GET"])
async def hourly_check(request: Request) -> JSONResponse:
    result = models.hourly_sleep_check()
    if result.get("msg_type"):
        send_telegram_notification(result)
    return JSONResponse(result)


# --- Dashboard ---

@mcp.custom_route("/panel", methods=["GET"])
async def dashboard(request: Request) -> HTMLResponse:
    return HTMLResponse(render_dashboard())


# =========================================================================
# MCP Tools
# =========================================================================

@mcp.tool()
def get_today_screentime() -> str:
    """Get today's screen time summary.
    Returns all apps used today with open counts, total duration, and current session info.
    """
    return json.dumps(models.calculate_today_summary(), ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def whats_she_doing_now() -> str:
    """Check what she's doing right now.
    Returns the currently active app and how long she's been using it.
    If no app is active, she's not on her phone.
    """
    return json.dumps(models.get_current_activity(), ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def night_owl_check() -> str:
    """Check if she's staying up late (activity between 1-6 AM).
    Returns whether she's in night hours, what apps she's using, and a warning if she should be sleeping.
    """
    return json.dumps(models.get_night_owl_info(), ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def all_nighter_check() -> str:
    """Check if she's pulling an all-nighter.
    Detects continuous activity past 4 AM without a sleep break.
    """
    return json.dumps(models.get_all_nighter_info(), ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def weekly_trend() -> str:
    """Get the last 7 days of screen time trends.
    Shows daily totals, app counts, most-used app, and day-over-day comparison.
    """
    return json.dumps(models.get_weekly_trend(), ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def get_app_usage(app_name: str) -> str:
    """Get usage history for a specific app today.

    Args:
        app_name: The app name, e.g. WeChat, Claude, Telegram
    """
    return json.dumps(models.get_app_usage(app_name), ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def get_recent_activity(limit: int = 20) -> str:
    """Get recent activity events in reverse chronological order.

    Args:
        limit: How many events to return (default 20)
    """
    return json.dumps(models.get_recent_activity(limit), ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def get_charging_history() -> str:
    """Get recent charging events (charging_start, charging_stop)."""
    return json.dumps(models.get_charging_history(), ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def get_location_history() -> str:
    """Get recent location events (left_home, arrived_home)."""
    return json.dumps(models.get_location_history(), ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def longest_session_today() -> str:
    """Find the longest continuous screen time session today.
    Returns the app, duration, and start/end times.
    """
    return json.dumps(models.get_longest_session_today(), ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def app_open_count(app_name: str) -> str:
    """Check how many times a specific app was opened today.

    Args:
        app_name: The app name, e.g. WeChat, Claude
    """
    return json.dumps(models.app_open_count(app_name), ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def daily_report() -> str:
    """Generate a comprehensive daily report.
    Includes total screen time, top apps, longest session, night owl status,
    all-nighter check, and current activity.
    """
    return json.dumps(models.daily_report(), ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def get_day_screentime(date: str) -> str:
    """Get screen time summary for a specific date.
    Use this to check yesterday's screen time, or any past date.

    Args:
        date: Date in YYYY-MM-DD format, e.g. "2026-03-29" for yesterday
    """
    return json.dumps(models.get_day_summary(date), ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def compare_days(date1: str, date2: str) -> str:
    """Compare screen time between two dates.

    Args:
        date1: First date in YYYY-MM-DD format
        date2: Second date in YYYY-MM-DD format
    """
    return json.dumps(models.compare_days(date1, date2), ensure_ascii=False, indent=2, default=str)
