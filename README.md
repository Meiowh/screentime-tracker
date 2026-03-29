# Screen Time Tracker

A real-time iPhone screen time tracking system with an MCP (Model Context Protocol) interface for AI assistants and a live web dashboard.

Three-layer architecture: **iPhone Shortcuts** send toggle signals to a **hosted server**, which exposes data to **Claude** via MCP tools.

---

## Features

- **Real-time toggle tracking** — iPhone Shortcuts hit a single URL to open/close apps
- **Session-based model** — tracks start, end, duration, and close reason for every app session
- **Live dashboard** — dark-themed, auto-refreshing web UI with heatmaps, charts, and session management
- **Night owl detection** — alerts when there is screen activity between 1-6 AM
- **All-nighter detection** — flags continuous usage past 4 AM
- **Sleep inference** — automatically closes sessions when charging starts during night hours with no recent activity
- **Stale session cleanup** — auto-closes sessions open longer than 24 hours
- **Hourly heatmap** — visualize which hours of the day have the most screen time
- **Weekly trends** — 7-day usage comparison
- **Charging & location events** — track when the phone starts/stops charging or leaves/arrives home
- **MCP tools** — 13 tools for AI assistants to query screen time data
- **Session correction** — edit or delete sessions via API or dashboard
- **PostgreSQL storage** — reliable, queryable data persistence

## Architecture

```
+------------------+       GET /api/screentime/toggle/{app}       +------------------+
|                  | ------------------------------------------->  |                  |
|  iPhone          |       GET /api/event/{type}                  |  Server          |
|  Shortcuts       | ------------------------------------------->  |  (Railway/VPS)   |
|                  |                                               |                  |
+------------------+                                               |  Python + FastMCP|
                                                                   |  PostgreSQL      |
+------------------+       MCP (SSE / Streamable HTTP)            |                  |
|                  | <------------------------------------------> |                  |
|  Claude          |       Tools: get_today_screentime,           +------------------+
|  (AI Assistant)  |       whats_she_doing_now, night_owl_check,         |
|                  |       daily_report, weekly_trend, ...               |
+------------------+                                               +------------------+
                                                                   |                  |
+------------------+       GET /panel                             |  Web Dashboard   |
|                  | ------------------------------------------->  |  Auto-refresh    |
|  Browser         |                                               |  Dark theme      |
|                  | <-------------------------------------------  |  Live timer      |
+------------------+       HTML + vanilla JS                      +------------------+
```

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL database (local or hosted)

### Setup

```bash
git clone https://github.com/your-repo/screentime-tracker.git
cd screentime-tracker

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL

# Run
python main.py
```

The server starts on port 8080 by default. Visit `http://localhost:8080/panel` for the web UI.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `PORT` | No | `8080` | Server port |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/screentime/toggle/{app_name}` | Toggle app open/close (iPhone Shortcut target) |
| `GET` | `/api/event/{event_type}` | Record event (charging_start, charging_stop, left_home, arrived_home) |
| `GET` | `/api/screentime/today` | Today's summary JSON |
| `GET` | `/api/screentime/nightowl` | Night owl detection |
| `GET` | `/api/screentime/allnighter` | All-nighter detection |
| `GET` | `/api/screentime/weekly` | 7-day trend |
| `GET` | `/api/screentime/hourly` | Hourly distribution heatmap data |
| `GET` | `/api/screentime/sessions` | Recent sessions list |
| `GET` | `/api/screentime/longest` | Longest session today |
| `POST` | `/api/screentime/correct/{session_id}` | Edit session end time (body: `{"end_ts": "..."}`) |
| `DELETE` | `/api/screentime/session/{session_id}` | Delete a session |
| `GET` | `/api/screentime/reset/{app_name}` | Force close an app |
| `GET` | `/api/screentime/reset_all` | Force close all apps |
| `GET` | `/panel` | Web dashboard |
| `GET` | `/health` | Health check |

## MCP Tools

| Tool | Description |
|------|-------------|
| `get_today_screentime` | Today's full summary with all apps |
| `whats_she_doing_now` | Current active app and duration |
| `night_owl_check` | Late-night activity detection |
| `all_nighter_check` | All-nighter detection |
| `weekly_trend` | 7-day usage trends |
| `get_app_usage(app_name)` | Specific app's usage today |
| `get_recent_activity(limit)` | Recent events list |
| `get_charging_history` | Charging events |
| `get_location_history` | Home/away events |
| `longest_session_today` | Longest continuous session |
| `app_open_count(app_name)` | How many times an app was opened today |
| `daily_report` | Comprehensive daily report |
| `compare_days(date1, date2)` | Compare two dates |

## Deployment

### Railway

1. Create a new project on [Railway](https://railway.app)
2. Add a PostgreSQL addon (the `DATABASE_URL` is set automatically)
3. Connect your GitHub repo or deploy via CLI
4. Railway reads the `Procfile` automatically

### Docker

```bash
docker build -t screentime-tracker .
docker run -e DATABASE_URL=postgresql://... -p 8080:8080 screentime-tracker
```

## Timezone

The tracker supports dynamic timezone configuration so all time-dependent calculations (today filter, night detection, sleep check, hourly distribution, weekly trends) use the correct local time.

**Default**: `America/New_York` (Eastern Time, UTC-4/UTC-5)

### Auto-detection

When the iPhone shortcut sends a charging start event with a `?t=` parameter containing an ISO 8601 timestamp (e.g. `?t=2026-03-29T12:28:00-07:00`), the server automatically extracts the UTC offset and updates the stored timezone if it differs from the current setting. This handles timezone changes when traveling.

### Manual configuration

Open the web dashboard (`/panel`), navigate to the Settings page (last tab), and use the "时区设置" section to set the UTC offset manually. The input accepts values from -12 to +14 (step 0.5 for half-hour timezones like India UTC+5.5).

### API

- `GET /api/settings/timezone` — returns current timezone name, offset, and label
- `POST /api/settings/timezone` — set timezone via JSON body: `{"offset": -7}` or `{"name": "America/Los_Angeles"}` or both

### How it works

Timezone settings are stored in a `settings` table in PostgreSQL. All time-dependent functions in the application read the timezone dynamically on each call, so changes take effect immediately without restarting the server.

## iPhone Shortcut Setup

Create an automation in Apple Shortcuts for each app:

1. **Trigger**: When [App] is opened / closed
2. **Action**: Get Contents of URL
3. **URL**: `https://your-server.com/api/screentime/toggle/AppName`
4. **Method**: GET

The toggle endpoint automatically detects whether to open or close based on the current session state.

---

## 中文使用教程

### iPhone 快捷指令配置教程

#### 基础配置（App 追踪）

每个你想追踪的 App 需要配一个自动化：

1. 打开"快捷指令" App → 自动化 → **+** 新自动化
2. 选择触发条件："App" → 选择一个 App（比如小红书）→ 勾选"已打开"和"已关闭"
3. 添加操作："获取URL的内容"
4. URL 填写：`https://你的服务器地址/api/screentime/toggle/小红书`
5. 方法：GET
6. 关闭"运行前询问"（设为立即运行）
7. 保存

重复以上步骤给每个想追踪的 App。

> **提示**：App 名称可以用中文也可以用英文，比如 `小红书`、`Twitter`、`微信` 都可以。名称会直接显示在 Dashboard 上。

#### 充电追踪（带自动时区检测）

**开始充电的自动化：**

1. 新自动化 → 触发条件："充电器" → "已连接"
2. 添加操作1："日期" → "当前日期"
3. 添加操作2："格式化日期" → 日期格式选"自定义" → 输入 `yyyy-MM-dd'T'HH:mm:ssZZZZZ`
4. 添加操作3："获取URL的内容"
5. URL：`https://你的服务器地址/api/event/charging_start?t=`（在最后拖入上一步的"已格式化的日期"变量）
6. 方法：GET
7. 关闭"运行前询问"

**停止充电的自动化：**

同上，但触发条件改为"已断开"，URL 改成 `/api/event/charging_stop?t=` + 时间变量

> **为什么要带 `?t=` 参数？** 这个参数包含了你手机当前的时区信息。服务器会从中提取 UTC 偏移量，旅行时自动更新时区设置，不需要手动改。

#### 位置追踪

1. **离开家**：新自动化 → "离开" → 选你家位置 → 获取URL `https://你的服务器地址/api/event/left_home`
2. **回到家**：新自动化 → "到达" → 选你家位置 → 获取URL `https://你的服务器地址/api/event/arrived_home`

---

### Dashboard 使用说明

- 访问地址：`https://你的服务器地址/panel`
- 5个页面：**主页** / **应用排行** / **数据分析** / **今日会话** / **设置**
- 左右滑动切换页面，底部图标也可以点击切换
- 设置页可以自定义：时区、应用颜色、背景颜色、水印样式

---

### 时区配置

- 默认东部时间（UTC-4）
- 旅行时自动检测：充电自动化带 `?t=` 参数会自动更新时区
- 手动设置：Dashboard 设置页 → 时区设置 → 输入 UTC 偏移

#### 常见时区对照

| 时区 | UTC 偏移 | 城市 |
|------|---------|------|
| 北京时间 | +8 | 北京、上海、台北 |
| 东部时间（夏令时）| -4 | 纽约、俄亥俄 |
| 东部时间（冬令时）| -5 | 纽约、俄亥俄 |
| 中部时间（夏令时）| -5 | 芝加哥 |
| 太平洋时间（夏令时）| -7 | 洛杉矶、旧金山 |

---

### 睡眠检测说明

系统每小时自动检查一次，根据以下规则判断你是否在睡觉：

- **充电中 + 凌晨 + 2小时没用手机** → 自动关闭 app，Bot 通知
- **充电中 + 白天 + 3小时没操作** → 午睡检测
- **没充电 + 白天 + 4小时没操作** → 自动关闭
- **短时间无操作** → 发提醒但不关闭

---

### 一键部署教程（Railway）

1. Fork 这个仓库到你的 GitHub
2. 登录 [railway.app](https://railway.app)
3. 新建项目 → GitHub Repo → 选择你 fork 的仓库
4. 添加 PostgreSQL 数据库
5. 等待自动部署完成
6. 打开你的 Railway 域名 + `/panel` 查看 Dashboard

---

## License

MIT
