"""
Screen Time Tracker - 屏幕时间追踪器
=================================
三层架构：
  iPhone (快捷指令自动化) → 服务器 (Railway) → Claude (MCP)

iPhone通过 /api/screentime/toggle/{app名} 发送数据
Claude通过 MCP 工具读取数据
前端页面通过 /dashboard 查看和管理
两个功能跑在同一个服务器同一个端口上
"""

import os
import json
from datetime import datetime, timedelta, timezone
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from mcp.server.fastmcp import FastMCP

# ========== 配置 ==========
DATA_FILE = "screentime_data.json"
PORT = int(os.environ.get("PORT", 8080))
EDT = timezone(timedelta(hours=-4))

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
    """计算今天每个App的使用时间和次数（EDT时区）"""
    data = load_data()
    now = datetime.now(EDT)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    today_events = [e for e in data["events"]
                    if datetime.fromisoformat(e["time"]).astimezone(EDT) >= today_start]

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
            now_utc = datetime.now(timezone.utc)
            duration = (now_utc - open_time).total_seconds() / 60
            if duration < 480:
                info["total_minutes"] += duration
            info["status"] = "正在使用"
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


# ========== MCP 服务器 ==========
mcp = FastMCP("Screen Time", host="0.0.0.0", port=PORT)


@mcp.tool()
def get_today_screentime() -> str:
    """获取今天的屏幕使用时间摘要。
    返回今天使用过的所有App的名称、打开次数、总使用时长(分钟)。
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
    """iPhone快捷指令调用这个接口，自动判断open/close。
    自带错位修正：如果toggle结果和预期不符（连续两次同状态），自动修正。
    """
    app_name = request.path_params["app_name"]
    data = load_data()

    last = data["last_state"].get(app_name, "close")
    new_state = "open" if last == "close" else "close"

    # 错位修正：检查最近的事件，如果发现异常模式则修正
    recent_app_events = [e for e in data["events"] if e["app"] == app_name]
    if len(recent_app_events) >= 2:
        last_two = recent_app_events[-2:]
        # 如果最近两个事件都是同一个状态，说明漏了一个，自动补上
        if last_two[0]["action"] == last_two[1]["action"] == "open":
            # 补一个close
            fix_event = {
                "app": app_name,
                "action": "close",
                "time": last_two[1]["time"],
                "auto_fix": True,
            }
            # 插入到倒数第一个open之前
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

    return JSONResponse({
        "app": app_name,
        "action": new_state,
        "time": event["time"],
    })


@mcp.custom_route("/api/screentime/reset/{app_name}", methods=["GET"])
async def reset_app(request: Request) -> JSONResponse:
    """手动重置某个App的状态为close"""
    app_name = request.path_params["app_name"]
    data = load_data()

    event = {
        "app": app_name,
        "action": "close",
        "time": datetime.now(timezone.utc).isoformat(),
        "manual": True,
    }
    data["events"].append(event)
    data["last_state"][app_name] = "close"
    save_data(data)

    return JSONResponse({"app": app_name, "action": "reset to close", "time": event["time"]})


@mcp.custom_route("/api/screentime/reset_all", methods=["GET"])
async def reset_all(request: Request) -> JSONResponse:
    """手动重置所有App的状态为close"""
    data = load_data()
    now = datetime.now(timezone.utc).isoformat()

    for app_name in list(data["last_state"].keys()):
        if data["last_state"][app_name] == "open":
            event = {
                "app": app_name,
                "action": "close",
                "time": now,
                "manual": True,
            }
            data["events"].append(event)
            data["last_state"][app_name] = "close"

    save_data(data)
    return JSONResponse({"action": "reset_all", "time": now})


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


@mcp.custom_route("/dashboard", methods=["GET"])
async def dashboard(request: Request) -> HTMLResponse:
    """小萤的屏幕时间管理页面"""
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
  .header .subtitle {
    color: #666;
    font-size: 0.85em;
  }
  .header .total-time {
    margin-top: 16px;
    font-size: 2.4em;
    font-weight: 700;
    color: #f4a0a0;
  }
  .header .total-label {
    color: #666;
    font-size: 0.8em;
    margin-top: 4px;
  }
  .app-list {
    max-width: 500px;
    margin: 24px auto;
  }
  .app-card {
    background: #15151f;
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border: 1px solid #1e1e2e;
    transition: all 0.2s;
  }
  .app-card:hover {
    border-color: #2a2a3e;
    background: #1a1a28;
  }
  .app-card.active {
    border-color: #c8a2c840;
    box-shadow: 0 0 12px #c8a2c815;
  }
  .app-info {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .app-icon {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2em;
    background: #1e1e2e;
  }
  .app-name {
    font-size: 0.95em;
    font-weight: 500;
  }
  .app-opens {
    font-size: 0.75em;
    color: #555;
    margin-top: 2px;
  }
  .app-status {
    font-size: 0.7em;
    padding: 3px 8px;
    border-radius: 20px;
    background: #1a2a1a;
    color: #5a5;
    margin-left: 8px;
  }
  .app-status.closed { background: #1e1e2e; color: #555; }
  .app-time {
    text-align: right;
  }
  .app-minutes {
    font-size: 1.15em;
    font-weight: 600;
    color: #c8a2c8;
  }
  .app-unit {
    font-size: 0.7em;
    color: #555;
  }
  .bar-bg {
    width: 100%;
    height: 3px;
    background: #1e1e2e;
    border-radius: 2px;
    margin-top: 8px;
  }
  .bar-fill {
    height: 100%;
    border-radius: 2px;
    background: linear-gradient(90deg, #c8a2c8, #f4a0a0);
    transition: width 0.5s;
  }
  .controls {
    max-width: 500px;
    margin: 20px auto;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    justify-content: center;
  }
  .btn {
    padding: 8px 16px;
    border-radius: 10px;
    border: 1px solid #2a2a3e;
    background: #15151f;
    color: #888;
    font-size: 0.8em;
    cursor: pointer;
    transition: all 0.2s;
  }
  .btn:hover { border-color: #c8a2c8; color: #c8a2c8; }
  .btn.danger:hover { border-color: #f4a0a0; color: #f4a0a0; }
  .refresh-note {
    text-align: center;
    color: #333;
    font-size: 0.75em;
    margin-top: 30px;
    padding-bottom: 20px;
  }
  @media (max-width: 600px) {
    body { padding: 12px; }
    .header h1 { font-size: 1.3em; }
    .header .total-time { font-size: 2em; }
  }
</style>
</head>
<body>

<div class="header">
  <h1>₍ᐢ‥ᐢ₎♡ 小萤的屏幕时间</h1>
  <div class="subtitle" id="date-display">加载中...</div>
  <div class="total-time" id="total-time">--</div>
  <div class="total-label">今日总屏幕时间</div>
</div>

<div class="app-list" id="app-list"></div>

<div class="controls">
  <button class="btn" onclick="refreshData()">刷新数据</button>
  <button class="btn danger" onclick="resetAll()">重置全部状态</button>
</div>

<div class="refresh-note">
  每30秒自动刷新 · 格与小萤的家
</div>

<script>
const API_BASE = window.location.origin;

const APP_ICONS = {
  '相册': '🖼', '备忘录': '📝', 'Safari浏览器': '🧭', '手机设置': '⚙️',
  '小红书': '📕', 'WeChat': '💬', 'Telegram': '✈️', '电话': '📞',
  'Oura': '💍', '相机': '📷', 'Discord': '🎮', '信息': '💌',
  'YouTube': '▶️', 'Twitter': '🐦', 'Instagram': '📸', 'TikTok': '🎵',
};

function getIcon(name) {
  return APP_ICONS[name] || '📱';
}

function formatMinutes(m) {
  if (m < 60) return Math.round(m) + ' 分钟';
  const h = Math.floor(m / 60);
  const min = Math.round(m % 60);
  return h + ' 小时 ' + (min > 0 ? min + ' 分' : '');
}

async function refreshData() {
  try {
    const res = await fetch(API_BASE + '/api/screentime/today');
    const data = await res.json();

    document.getElementById('date-display').textContent =
      data.date + ' · ' + data.current_time + ' ' + data.timezone;
    document.getElementById('total-time').textContent =
      formatMinutes(data.total_screen_time_minutes);

    const list = document.getElementById('app-list');
    const apps = Object.entries(data.apps)
      .sort((a, b) => b[1].total_minutes - a[1].total_minutes);

    const maxMin = apps.length > 0 ? apps[0][1].total_minutes : 1;

    list.innerHTML = apps.map(([name, info]) => `
      <div class="app-card ${info.status === '正在使用' ? 'active' : ''}">
        <div class="app-info">
          <div class="app-icon">${getIcon(name)}</div>
          <div>
            <div class="app-name">
              ${name}
              ${info.status === '正在使用'
                ? '<span class="app-status">正在使用</span>'
                : '<span class="app-status closed">已关闭</span>'}
            </div>
            <div class="app-opens">打开 ${info.open_count} 次</div>
            <div class="bar-bg"><div class="bar-fill" style="width:${Math.max(2, info.total_minutes / maxMin * 100)}%"></div></div>
          </div>
        </div>
        <div class="app-time">
          <div class="app-minutes">${Math.round(info.total_minutes)}</div>
          <div class="app-unit">分钟</div>
        </div>
      </div>
    `).join('');
  } catch (e) {
    document.getElementById('total-time').textContent = '加载失败';
  }
}

async function resetAll() {
  if (!confirm('确定要重置所有App的状态吗？')) return;
  await fetch(API_BASE + '/api/screentime/reset_all');
  refreshData();
}

refreshData();
setInterval(refreshData, 30000);
</script>
</body>
</html>"""


# ========== 启动 ==========
if __name__ == "__main__":
    print(f"Screen Time Tracker starting on port {PORT}")
    print(f"  MCP endpoint: http://0.0.0.0:{PORT}/mcp")
    print(f"  Dashboard:    http://0.0.0.0:{PORT}/dashboard")
    print(f"  Toggle API:   http://0.0.0.0:{PORT}/api/screentime/toggle/{{app_name}}")
    mcp.run(transport="streamable-http")
