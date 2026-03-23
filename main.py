"""
Screen Time Tracker - 屏幕时间追踪器
=================================
三层架构：
  iPhone (快捷指令自动化) → 服务器 (Railway) → Claude (MCP)

iPhone通过 /api/screentime/toggle/{app名} 发送数据
Claude通过 MCP 工具读取数据
两个功能跑在同一个服务器同一个端口上
"""

import os
import json
from datetime import datetime, timedelta, timezone
from starlette.requests import Request
from starlette.responses import JSONResponse
from mcp.server.fastmcp import FastMCP

# ========== 配置 ==========
DATA_FILE = "screentime_data.json"
PORT = int(os.environ.get("PORT", 8080))

# ========== 数据存储层 ==========

def load_data() -> dict:
    """从文件加载数据"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"events": [], "last_state": {}}


def save_data(data: dict):
    """保存数据到文件，同时清理7天前的旧记录"""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    data["events"] = [e for e in data["events"] if e["time"] > cutoff]
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def calculate_today_summary() -> dict:
    """计算今天每个App的使用时间和次数"""
    data = load_data()
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    today_events = [e for e in data["events"] if e["time"] >= today_start.isoformat()]

    apps = {}
    for event in today_events:
        app_name = event["app"]
        if app_name not in apps:
            apps[app_name] = {"open_count": 0, "total_minutes": 0, "last_open": None}

        if event["action"] == "open":
            apps[app_name]["open_count"] += 1
            apps[app_name]["last_open"] = event["time"]
        elif event["action"] == "close" and apps[app_name]["last_open"]:
            open_time = datetime.fromisoformat(apps[app_name]["last_open"])
            close_time = datetime.fromisoformat(event["time"])
            duration = (close_time - open_time).total_seconds() / 60
            if duration < 480:
                apps[app_name]["total_minutes"] += duration
            apps[app_name]["last_open"] = None

    for app_name, info in apps.items():
        if info["last_open"]:
            open_time = datetime.fromisoformat(info["last_open"])
            duration = (now - open_time).total_seconds() / 60
            if duration < 480:
                info["total_minutes"] += duration
            info["status"] = "正在使用"
        else:
            info["status"] = "已关闭"

        info["total_minutes"] = round(info["total_minutes"], 1)
        del info["last_open"]

    return {
        "date": today_start.strftime("%Y-%m-%d"),
        "timezone": "UTC",
        "apps": apps,
        "total_screen_time_minutes": round(sum(a["total_minutes"] for a in apps.values()), 1),
    }


# ========== MCP 服务器 ==========
mcp = FastMCP("Screen Time", host="0.0.0.0", port=PORT)


@mcp.tool()
def get_today_screentime() -> str:
    """获取今天的屏幕使用时间摘要。
    返回今天使用过的所有App的名称、打开次数、总使用时长（分钟）。
    """
    summary = calculate_today_summary()
    return json.dumps(summary, ensure_ascii=False, indent=2)


@mcp.tool()
def get_app_usage(app_name: str) -> str:
    """获取特定App的最近使用记录。

    Args:
        app_name: App的名称，比如 xiaohongshu、Claude、WeChat
    """
    data = load_data()
    app_events = [e for e in data["events"] if e["app"] == app_name]
    return json.dumps({
        "app": app_name,
        "total_events": len(app_events),
        "recent_events": app_events[-30:]
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def get_recent_activity(limit: int = 20) -> str:
    """获取最近的App活动记录，按时间倒序。

    Args:
        limit: 返回多少条记录，默认20条
    """
    data = load_data()
    events = data["events"][-limit:]
    events.reverse()
    return json.dumps({"events": events}, ensure_ascii=False, indent=2)


# ========== iPhone HTTP 接口 ==========
@mcp.custom_route("/api/screentime/toggle/{app_name}", methods=["GET"])
async def toggle(request: Request) -> JSONResponse:
    """iPhone快捷指令调用这个接口，自动判断open/close"""
    app_name = request.path_params["app_name"]
    data = load_data()

    last = data["last_state"].get(app_name, "close")
    new_state = "open" if last == "close" else "close"

    event = {
        "app": app_name,
        "action": new_state,
        "time": datetime.now(timezone.utc).isoformat(),
    }
    data["events"].append(event)
    data["last_state"][app_name] = new_state
    save_data(data)

    return JSONResponse({
        "app": app_name,
        "action": new_state,
        "time": event["time"],
    })


@mcp.custom_route("/", methods=["GET"])
async def root(request: Request) -> JSONResponse:
    """健康检查"""
    return JSONResponse({
        "status": "ok",
        "service": "Screen Time Tracker",
    })


@mcp.custom_route("/api/screentime/today", methods=["GET"])
async def today_api(request: Request) -> JSONResponse:
    """HTTP版的今日摘要，调试用"""
    return JSONResponse(calculate_today_summary())


# ========== 启动 ==========
if __name__ == "__main__":
    print(f"Screen Time Tracker starting on port {PORT}")
    print(f"  MCP endpoint: http://0.0.0.0:{PORT}/mcp")
    print(f"  Toggle API:   http://0.0.0.0:{PORT}/api/screentime/toggle/{{app_name}}")
    mcp.run(transport="streamable-http")
