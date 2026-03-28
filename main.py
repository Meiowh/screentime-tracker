"""Screen Time Tracker v3 — Entry point."""

from src.app import mcp
from src.config import PORT
from src.db import init_db

if __name__ == "__main__":
    init_db()
    print(f"Screen Time Tracker v3 starting on port {PORT}")
    print(f"  Panel:      http://0.0.0.0:{PORT}/panel")
    print(f"  Toggle API: http://0.0.0.0:{PORT}/api/screentime/toggle/{{app_name}}")
    print(f"  Event API:  http://0.0.0.0:{PORT}/api/event/{{event_type}}")
    print(f"  Health:     http://0.0.0.0:{PORT}/health")
    mcp.run(transport="streamable-http")
