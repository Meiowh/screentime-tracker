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
+------------------+       GET /dashboard                         |  Web Dashboard   |
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

The server starts on port 8080 by default. Visit `http://localhost:8080/dashboard` for the web UI.

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
| `GET` | `/dashboard` | Web dashboard |
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

## License

MIT
