"""FastMCP application — HTTP routes and MCP tools."""

import json
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from mcp.server.fastmcp import FastMCP

from src.config import PORT
from src import models
from src.dashboard import render_dashboard

# ---------------------------------------------------------------------------
# FastMCP instance
# ---------------------------------------------------------------------------

mcp = FastMCP("Screen Time", host="0.0.0.0", port=PORT)

# Cache the dashboard HTML (it's a static string)
_DASHBOARD_HTML: str | None = None


def _dashboard():
    global _DASHBOARD_HTML
    if _DASHBOARD_HTML is None:
        _DASHBOARD_HTML = render_dashboard()
    return _DASHBOARD_HTML


# =========================================================================
# HTTP Routes
# =========================================================================

@mcp.custom_route("/", methods=["GET"])
async def root(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "Screen Time Tracker v3"})


@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "healthy"})


# --- Core toggle (iPhone shortcut hits this) ---

@mcp.custom_route("/api/screentime/toggle/{app_name}", methods=["GET"])
async def toggle(request: Request) -> JSONResponse:
    app_name = request.path_params["app_name"]
    result = models.handle_toggle(app_name)
    return JSONResponse(result)


# --- Events (charging, location) ---

@mcp.custom_route("/api/event/{event_type}", methods=["GET"])
async def event(request: Request) -> JSONResponse:
    event_type = request.path_params["event_type"]
    result = models.handle_event(event_type)
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
        if not new_end:
            return JSONResponse({"error": "end_ts required"}, status_code=400)
        from src.db import update_session_end
        result = update_session_end(session_id, new_end)
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


# --- Charging & location history for dashboard ---

@mcp.custom_route("/api/event/charging_history", methods=["GET"])
async def charging_history_api(request: Request) -> JSONResponse:
    return JSONResponse(models.get_charging_history())


@mcp.custom_route("/api/event/location_history", methods=["GET"])
async def location_history_api(request: Request) -> JSONResponse:
    return JSONResponse(models.get_location_history())


# --- Dashboard ---

@mcp.custom_route("/dashboard", methods=["GET"])
async def dashboard(request: Request) -> HTMLResponse:
    return HTMLResponse(_dashboard())


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
def compare_days(date1: str, date2: str) -> str:
    """Compare screen time between two dates.

    Args:
        date1: First date in YYYY-MM-DD format
        date2: Second date in YYYY-MM-DD format
    """
    return json.dumps(models.compare_days(date1, date2), ensure_ascii=False, indent=2, default=str)
