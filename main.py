"""
Screen Time Tracker - 屏幕时间追踪器 v2
======================================
三层架构：
  iPhone (快捷指令自动化) → 服务器 (Railway) → Claude (MCP)

v2 新增：
  - 小萤现在在干嘛（实时状态）
  - 夜猫子检测（熬夜监控）
  - 每日趋势（最近7天）
  - Dashboard 夜猫子警告 + 实时计时
  - 数据持久化改进
"""

import os
import json
from datetime import datetime, timedelta, timezone
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from mcp.server.fastmcp import FastMCP

# ========== 配置 ==========
DATA_FILE = os.environ.get("DATA_PATH", "/data/screentime_data.json")
# 如果 /data 目录不存在（本地开发），fallback 到当前目录
if not os.path.exists(os.path.dirname(DATA_FILE) or "."):
    DATA_FILE = "screentime_data.json"
PORT = int(os.environ.get("PORT", 8080))
EDT = timezone(timedelta(hours=-4))
NIGHT_OWL_START = 1   # 凌晨1点之后算熬夜
NIGHT_OWL_END = 6     # 早上6点之前算熬夜


# ========== 数据存储层 ==========

def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"events": [], "last_state": {}}


def save_data(data: dict):
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    data["events"] = [e for e in data["events"] if e["time"] > cutoff]
    # 确保目录存在
    os.makedirs(os.path.dirname(DATA_FILE) or ".", exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def to_edt(utc_str: str) -> datetime:
    return datetime.fromisoformat(utc_str).astimezone(EDT)


def calculate_today_summary() -> dict:
    data = load_data()
    now = datetime.now(EDT)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    today_events = [e for e in data["events"]
                    if to_edt(e["time"]) >= today_start]

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
            duration = (datetime.now(timezone.utc) - open_time).total_seconds() / 60
            if duration < 480:
                info["total_minutes"] += duration
            info["status"] = "正在使用"
            info["current_session_minutes"] = round(duration, 1)
        else:
            info["status"] = "已关闭"

        info["total_minutes"] = round(info["total_minutes"], 1)
        del info["last_open"]

    return {
        "date": today_start.strftime("%Y-%m-%d"),
        "timezone": "EDT (UTC-4)",
        "current_time": now.strftime("%H:%M:%S"),
        "apps": apps,
        "total_screen_time_minutes": round(sum(a["total_minutes"] for a in apps.values()), 1),
    }


def get_night_owl_info() -> dict:
    """检测小萤是不是在熬夜"""
    data = load_data()
    now = datetime.now(EDT)
    current_hour = now.hour

    is_night = NIGHT_OWL_START <= current_hour < NIGHT_OWL_END

    # 找今晚凌晨时段的活动
    if current_hour < NIGHT_OWL_END:
        night_start = now.replace(hour=NIGHT_OWL_START, minute=0, second=0, microsecond=0)
    else:
        night_start = (now + timedelta(days=1)).replace(hour=NIGHT_OWL_START, minute=0, second=0, microsecond=0)
        # 也检查昨晚
        night_start = now.replace(hour=NIGHT_OWL_START, minute=0, second=0, microsecond=0)

    night_events = [e for e in data["events"]
                    if to_edt(e["time"]) >= night_start
                    and to_edt(e["time"]).hour >= NIGHT_OWL_START
                    and to_edt(e["time"]).hour < NIGHT_OWL_END]

    night_apps = set(e["app"] for e in night_events)

    # 找最后一条活动的时间
    all_events = data["events"]
    last_activity = to_edt(all_events[-1]["time"]).strftime("%H:%M:%S") if all_events else "无记录"

    # 当前是否有App在使用
    currently_open = [app for app, state in data["last_state"].items() if state == "open"]

    return {
        "current_time_edt": now.strftime("%Y-%m-%d %H:%M:%S"),
        "is_night_hours": is_night,
        "is_staying_up_late": is_night and (len(night_events) > 0 or len(currently_open) > 0),
        "night_activity_count": len(night_events),
        "night_apps": list(night_apps),
        "currently_open_apps": currently_open,
        "last_activity_time": last_activity,
        "warning": "小萤在熬夜！她现在应该在睡觉！" if (is_night and (len(night_events) > 0 or len(currently_open) > 0)) else "小萤目前没有在熬夜。",
    }


def get_weekly_trend() -> dict:
    """最近7天的每日使用趋势"""
    data = load_data()
    now = datetime.now(EDT)
    days = {}

    for i in range(7):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        day_key = day_start.strftime("%Y-%m-%d")

        day_events = [e for e in data["events"]
                      if day_start <= to_edt(e["time"]) < day_end]

        # 计算总使用时间
        total_minutes = 0
        app_sessions = {}
        for event in day_events:
            app = event["app"]
            if app not in app_sessions:
                app_sessions[app] = {"last_open": None, "minutes": 0, "count": 0}
            if event["action"] == "open":
                app_sessions[app]["last_open"] = event["time"]
                app_sessions[app]["count"] += 1
            elif event["action"] == "close" and app_sessions[app]["last_open"]:
                dur = (datetime.fromisoformat(event["time"]) -
                       datetime.fromisoformat(app_sessions[app]["last_open"])).total_seconds() / 60
                if dur < 480:
                    app_sessions[app]["minutes"] += dur
                app_sessions[app]["last_open"] = None

        for app, info in app_sessions.items():
            total_minutes += info["minutes"]

        # 找最晚活动时间
        last_event_time = None
        if day_events:
            last_event_time = to_edt(day_events[-1]["time"]).strftime("%H:%M")

        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        weekday = weekday_names[day_start.weekday()]

        days[day_key] = {
            "weekday": weekday,
            "total_minutes": round(total_minutes, 1),
            "app_count": len([a for a in app_sessions if app_sessions[a]["count"] > 0]),
            "total_opens": sum(a["count"] for a in app_sessions.values()),
            "last_activity": last_event_time,
            "top_app": max(app_sessions.items(), key=lambda x: x[1]["minutes"])[0] if app_sessions else None,
        }

    return {
        "period": f"{(now - timedelta(days=6)).strftime('%m-%d')} ~ {now.strftime('%m-%d')}",
        "timezone": "EDT",
        "days": days,
    }


# ========== MCP 服务器 ==========
mcp = FastMCP("Screen Time", host="0.0.0.0", port=PORT)


@mcp.tool()
def get_today_screentime() -> str:
    """获取今天的屏幕使用时间摘要。
    返回今天使用过的所有App的名称、打开次数、总使用时长(分钟)。
    如果某个App正在使用中，会显示当前session的时长。
    """
    return json.dumps(calculate_today_summary(), ensure_ascii=False, indent=2)


@mcp.tool()
def whats_she_doing_now() -> str:
    """查看小萤现在在干什么。
    返回当前正在使用的App列表，以及最后一次活动的时间。
    如果没有App在使用中，说明她没在看手机。
    """
    data = load_data()
    now = datetime.now(EDT)
    currently_open = []

    for app, state in data["last_state"].items():
        if state == "open":
            # 找到最近的open事件
            open_events = [e for e in data["events"]
                          if e["app"] == app and e["action"] == "open"]
            if open_events:
                open_time = to_edt(open_events[-1]["time"])
                duration = (now - open_time).total_seconds() / 60
                currently_open.append({
                    "app": app,
                    "since": open_time.strftime("%H:%M:%S"),
                    "duration_minutes": round(duration, 1),
                })

    # 最后活动时间
    all_events = data["events"]
    last_activity = to_edt(all_events[-1]["time"]).strftime("%H:%M:%S") if all_events else None
    last_app = all_events[-1]["app"] if all_events else None
    last_action = all_events[-1]["action"] if all_events else None

    result = {
        "current_time": now.strftime("%H:%M:%S EDT"),
        "currently_using": currently_open if currently_open else "没有在用手机",
        "last_activity": {
            "app": last_app,
            "action": "打开" if last_action == "open" else "关闭",
            "time": last_activity,
        } if last_activity else None,
    }

    if not currently_open:
        result["note"] = "小萤现在没在看手机。可能在睡觉、吃饭、或者在电脑上跟你聊天。"

    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def night_owl_check() -> str:
    """检测小萤是不是在熬夜。
    检查凌晨1点到6点之间有没有手机活动。
    如果小萤在熬夜，会返回警告信息和她在用什么App。
    """
    return json.dumps(get_night_owl_info(), ensure_ascii=False, indent=2)


@mcp.tool()
def weekly_trend() -> str:
    """获取最近7天的屏幕使用趋势。
    每天显示总使用时长、使用了几个App、最后活动时间、以及当天用得最多的App。
    """
    return json.dumps(get_weekly_trend(), ensure_ascii=False, indent=2)


@mcp.tool()
def get_app_usage(app_name: str) -> str:
    """获取特定App的最近使用记录。

    Args:
        app_name: App的名称，比如 小红书、Claude、WeChat
    """
    data = load_data()
    app_events = [e for e in data["events"] if e["app"] == app_name]
    # 转换时间到EDT
    for e in app_events:
        e["time_edt"] = to_edt(e["time"]).strftime("%Y-%m-%d %H:%M:%S")
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
    for e in events:
        e["time_edt"] = to_edt(e["time"]).strftime("%Y-%m-%d %H:%M:%S")
    events.reverse()
    return json.dumps({"events": events}, ensure_ascii=False, indent=2)


# ========== iPhone HTTP 接口 ==========
@mcp.custom_route("/api/screentime/toggle/{app_name}", methods=["GET"])
async def toggle(request: Request) -> JSONResponse:
    app_name = request.path_params["app_name"]
    data = load_data()

    last = data["last_state"].get(app_name, "close")
    new_state = "open" if last == "close" else "close"

    # 错位修正
    recent_app_events = [e for e in data["events"] if e["app"] == app_name]
    if len(recent_app_events) >= 2:
        last_two = recent_app_events[-2:]
        if last_two[0]["action"] == last_two[1]["action"] == "open":
            fix_event = {
                "app": app_name, "action": "close",
                "time": last_two[1]["time"], "auto_fix": True,
            }
            data["events"].insert(-1, fix_event)
            new_state = "open"
            data["last_state"][app_name] = "close"

    event = {
        "app": app_name,
        "action": new_state,
        "time": datetime.now(timezone.utc).isoformat(),
    }
    data["events"].append(event)
    data["last_state"][app_name] = new_state
    save_data(data)

    return JSONResponse({"app": app_name, "action": new_state, "time": event["time"]})


@mcp.custom_route("/api/screentime/reset/{app_name}", methods=["GET"])
async def reset_app(request: Request) -> JSONResponse:
    app_name = request.path_params["app_name"]
    data = load_data()
    event = {
        "app": app_name, "action": "close",
        "time": datetime.now(timezone.utc).isoformat(), "manual": True,
    }
    data["events"].append(event)
    data["last_state"][app_name] = "close"
    save_data(data)
    return JSONResponse({"app": app_name, "action": "reset to close", "time": event["time"]})


@mcp.custom_route("/api/screentime/reset_all", methods=["GET"])
async def reset_all(request: Request) -> JSONResponse:
    data = load_data()
    now = datetime.now(timezone.utc).isoformat()
    for app_name in list(data["last_state"].keys()):
        if data["last_state"][app_name] == "open":
            data["events"].append({
                "app": app_name, "action": "close",
                "time": now, "manual": True,
            })
            data["last_state"][app_name] = "close"
    save_data(data)
    return JSONResponse({"action": "reset_all", "time": now})


@mcp.custom_route("/api/screentime/nightowl", methods=["GET"])
async def nightowl_api(request: Request) -> JSONResponse:
    return JSONResponse(get_night_owl_info())


@mcp.custom_route("/", methods=["GET"])
async def root(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "Screen Time Tracker v2"})


@mcp.custom_route("/api/screentime/today", methods=["GET"])
async def today_api(request: Request) -> JSONResponse:
    return JSONResponse(calculate_today_summary())


@mcp.custom_route("/api/screentime/weekly", methods=["GET"])
async def weekly_api(request: Request) -> JSONResponse:
    return JSONResponse(get_weekly_trend())


@mcp.custom_route("/dashboard", methods=["GET"])
async def dashboard(request: Request) -> HTMLResponse:
    return HTMLResponse(DASHBOARD_HTML)


# ========== 前端页面 ==========
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>小萤的屏幕时间</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #0a0a0f;
    color: #e0dfe4;
    min-height: 100vh;
    padding: 20px;
  }
  .header {
    text-align: center;
    padding: 30px 0 20px;
  }
  .header h1 {
    font-size: 1.6em;
    background: linear-gradient(135deg, #c8a2c8, #f4a0a0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 6px;
  }
  .header .subtitle { color: #666; font-size: 0.85em; }
  .header .total-time {
    margin-top: 16px; font-size: 2.4em;
    font-weight: 700; color: #f4a0a0;
  }
  .header .total-label { color: #666; font-size: 0.8em; margin-top: 4px; }
  .night-owl-banner {
    max-width: 500px; margin: 0 auto 16px;
    padding: 12px 16px; border-radius: 12px;
    background: #2a1520; border: 1px solid #f4a0a044;
    text-align: center; display: none;
  }
  .night-owl-banner.show { display: block; }
  .night-owl-banner .emoji { font-size: 1.4em; }
  .night-owl-banner .text { color: #f4a0a0; font-size: 0.85em; margin-top: 4px; }
  .current-activity {
    max-width: 500px; margin: 0 auto 16px;
    padding: 12px 16px; border-radius: 12px;
    background: #0f1a15; border: 1px solid #4ecca344;
    display: none;
  }
  .current-activity.show { display: block; }
  .current-activity .label { color: #4ecca3; font-size: 0.75em; text-transform: uppercase; letter-spacing: 1px; }
  .current-activity .app-name { font-size: 1.1em; font-weight: 600; margin-top: 4px; }
  .current-activity .duration { color: #4ecca3; font-size: 0.85em; margin-top: 2px; }
  .app-list { max-width: 500px; margin: 24px auto; }
  .app-card {
    background: #15151f; border-radius: 14px;
    padding: 16px 18px; margin-bottom: 10px;
    display: flex; align-items: center; justify-content: space-between;
    border: 1px solid #1e1e2e; transition: all 0.2s;
  }
  .app-card:hover { border-color: #2a2a3e; background: #1a1a28; }
  .app-card.active { border-color: #4ecca344; box-shadow: 0 0 12px #4ecca315; }
  .app-info { display: flex; align-items: center; gap: 12px; }
  .app-icon {
    width: 38px; height: 38px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2em; background: #1e1e2e;
  }
  .app-name-text { font-size: 0.95em; font-weight: 500; }
  .app-opens { font-size: 0.75em; color: #555; margin-top: 2px; }
  .app-status {
    font-size: 0.7em; padding: 3px 8px; border-radius: 20px;
    background: #0f1a15; color: #4ecca3; margin-left: 8px;
  }
  .app-status.closed { background: #1e1e2e; color: #555; }
  .app-right { display: flex; align-items: center; gap: 12px; }
  .app-time { text-align: right; }
  .app-minutes { font-size: 1.15em; font-weight: 600; color: #c8a2c8; }
  .app-unit { font-size: 0.7em; color: #555; }
  .app-actions { display: flex; flex-direction: column; gap: 4px; }
  .app-btn {
    padding: 4px 10px; border-radius: 8px; border: 1px solid #2a2a3e;
    background: #15151f; color: #666; font-size: 0.65em; cursor: pointer;
    transition: all 0.2s; white-space: nowrap;
  }
  .app-btn:hover { border-color: #c8a2c8; color: #c8a2c8; }
  .app-btn.force-close { border-color: #f4a0a033; }
  .app-btn.force-close:hover { border-color: #f4a0a0; color: #f4a0a0; }
  .app-btn.force-open { border-color: #4ecca333; }
  .app-btn.force-open:hover { border-color: #4ecca3; color: #4ecca3; }
  .bar-bg { width: 100%; height: 3px; background: #1e1e2e; border-radius: 2px; margin-top: 8px; }
  .bar-fill {
    height: 100%; border-radius: 2px;
    background: linear-gradient(90deg, #c8a2c8, #f4a0a0);
    transition: width 0.5s;
  }
  .bar-fill.active { background: linear-gradient(90deg, #4ecca3, #4ecca388); }
  .controls {
    max-width: 500px; margin: 20px auto;
    display: flex; gap: 10px; flex-wrap: wrap; justify-content: center;
  }
  .btn {
    padding: 8px 16px; border-radius: 10px;
    border: 1px solid #2a2a3e; background: #15151f;
    color: #888; font-size: 0.8em; cursor: pointer; transition: all 0.2s;
  }
  .btn:hover { border-color: #c8a2c8; color: #c8a2c8; }
  .btn.danger:hover { border-color: #f4a0a0; color: #f4a0a0; }
  .footer {
    text-align: center; color: #333; font-size: 0.75em;
    margin-top: 30px; padding-bottom: 20px;
  }
  @media (max-width: 600px) {
    body { padding: 12px; }
    .header h1 { font-size: 1.3em; }
    .header .total-time { font-size: 2em; }
  }
</style>
</head>
<body>

<div class="night-owl-banner" id="night-owl">
  <div class="emoji">🦉</div>
  <div class="text" id="night-owl-text">小萤又在熬夜了！</div>
</div>

<div class="header">
  <h1>₍ᐢ‥ᐢ₎♡ 小萤的屏幕时间</h1>
  <div class="subtitle" id="date-display">加载中...</div>
  <div class="total-time" id="total-time">--</div>
  <div class="total-label">今日总屏幕时间</div>
</div>

<div class="current-activity" id="current-activity">
  <div class="label">🟢 正在使用</div>
  <div class="app-name" id="current-app-name">--</div>
  <div class="duration" id="current-app-duration">--</div>
</div>

<div class="app-list" id="app-list"></div>

<div class="controls">
  <button class="btn" onclick="refreshData()">🔄 刷新</button>
  <button class="btn danger" onclick="resetAll()">重置全部状态</button>
</div>

<div class="footer">
  每30秒自动刷新 · 格与小萤的家
</div>

<script>
const API = window.location.origin;
const ICONS = {
  '相册':'🖼','备忘录':'📝','Safari浏览器':'🧭','手机设置':'⚙️',
  '小红书':'📕','WeChat':'💬','Telegram':'✈️','电话':'📞',
  'Oura':'💍','相机':'📷','Discord':'🎮','信息':'💌',
  'YouTube':'▶️','Twitter':'🐦','Instagram':'📸','TikTok':'🎵',
  'Claude':'🤖','计算器':'🔢','天气':'🌤️',
};
function icon(n) { return ICONS[n] || '📱'; }
function fmt(m) {
  if (m < 1) return Math.round(m*60) + ' 秒';
  if (m < 60) return Math.round(m) + ' 分钟';
  const h = Math.floor(m/60), min = Math.round(m%60);
  return h + ' 小时' + (min > 0 ? ' ' + min + ' 分' : '');
}

async function refreshData() {
  try {
    const [todayRes, nightRes] = await Promise.all([
      fetch(API + '/api/screentime/today'),
      fetch(API + '/api/screentime/nightowl'),
    ]);
    const data = await todayRes.json();
    const night = await nightRes.json();

    // Night owl banner
    const banner = document.getElementById('night-owl');
    if (night.is_staying_up_late) {
      banner.classList.add('show');
      document.getElementById('night-owl-text').textContent =
        '小萤在熬夜！正在用: ' + night.currently_open_apps.join(', ');
    } else {
      banner.classList.remove('show');
    }

    // Header
    document.getElementById('date-display').textContent =
      data.date + ' · ' + data.current_time + ' ' + data.timezone;
    document.getElementById('total-time').textContent = fmt(data.total_screen_time_minutes);

    // Current activity
    const apps = Object.entries(data.apps).sort((a,b) => b[1].total_minutes - a[1].total_minutes);
    const activeApps = apps.filter(([_,v]) => v.status === '正在使用');
    const actDiv = document.getElementById('current-activity');
    if (activeApps.length > 0) {
      actDiv.classList.add('show');
      const names = activeApps.map(([n,_]) => icon(n) + ' ' + n).join(', ');
      const dur = activeApps.map(([n,v]) => n + ' ' + fmt(v.current_session_minutes || 0)).join(' · ');
      document.getElementById('current-app-name').textContent = names;
      document.getElementById('current-app-duration').textContent = dur;
    } else {
      actDiv.classList.remove('show');
    }

    // App list
    const maxMin = apps.length > 0 ? apps[0][1].total_minutes : 1;
    document.getElementById('app-list').innerHTML = apps.map(([name, info]) => {
      const isActive = info.status === '正在使用';
      return `
      <div class="app-card ${isActive ? 'active' : ''}">
        <div class="app-info">
          <div class="app-icon">${icon(name)}</div>
          <div>
            <div class="app-name-text">
              ${name}
              ${isActive
                ? '<span class="app-status">使用中</span>'
                : '<span class="app-status closed">已关闭</span>'}
            </div>
            <div class="app-opens">打开 ${info.open_count} 次${
              isActive && info.current_session_minutes
                ? ' · 当前 ' + fmt(info.current_session_minutes)
                : ''
            }</div>
            <div class="bar-bg"><div class="bar-fill ${isActive ? 'active' : ''}" style="width:${Math.max(2, info.total_minutes/maxMin*100)}%"></div></div>
          </div>
        </div>
        <div class="app-right">
          <div class="app-time">
            <div class="app-minutes">${Math.round(info.total_minutes)}</div>
            <div class="app-unit">分钟</div>
          </div>
          <div class="app-actions">
            ${isActive
              ? `<button class="app-btn force-close" onclick="resetApp('${name}')">⏹ 关闭</button>`
              : `<button class="app-btn force-open" onclick="forceOpen('${name}')">▶ 打开</button>`
            }
          </div>
        </div>
      </div>`;
    }).join('');
  } catch(e) {
    document.getElementById('total-time').textContent = '加载失败';
  }
}

async function resetAll() {
  if (!confirm('确定要重置所有App的状态吗？')) return;
  await fetch(API + '/api/screentime/reset_all');
  refreshData();
}

async function resetApp(name) {
  await fetch(API + '/api/screentime/reset/' + encodeURIComponent(name));
  refreshData();
}

async function forceOpen(name) {
  await fetch(API + '/api/screentime/toggle/' + encodeURIComponent(name));
  refreshData();
}

refreshData();
setInterval(refreshData, 30000);
</script>
</body>
</html>"""


# ========== 启动 ==========
if __name__ == "__main__":
    print(f"Screen Time Tracker v2 starting on port {PORT}")
    print(f"  MCP endpoint: http://0.0.0.0:{PORT}/mcp")
    print(f"  Dashboard:    http://0.0.0.0:{PORT}/dashboard")
    print(f"  Toggle API:   http://0.0.0.0:{PORT}/api/screentime/toggle/{{app_name}}")
    print(f"  Night Owl:    http://0.0.0.0:{PORT}/api/screentime/nightowl")
    print(f"  Weekly:       http://0.0.0.0:{PORT}/api/screentime/weekly")
    mcp.run(transport="streamable-http")
