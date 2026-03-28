"""Screen Time Tracker v3 — Entry point."""

import threading
import time

from src.app import mcp
from src.config import PORT
from src.db import init_db
from src.models import hourly_sleep_check
from src.notify import send_telegram_notification


def background_sleep_checker():
    """Background thread that checks every hour if the user is sleeping/idle."""
    # Wait 5 minutes after startup before first check (let everything settle)
    time.sleep(300)
    while True:
        try:
            result = hourly_sleep_check()
            if result.get("msg_type"):
                send_telegram_notification(result)
                print(f"[sleep-checker] {result['action']}: {result.get('msg_type')} ({result.get('app')} idle {result.get('hours_idle')}h)")
            else:
                print(f"[sleep-checker] check complete: {result.get('action', 'none')}")
        except Exception as e:
            print(f"[sleep-checker] error: {e}")
        time.sleep(3600)  # Sleep 1 hour


if __name__ == "__main__":
    init_db()

    # Start background sleep checker thread
    checker = threading.Thread(target=background_sleep_checker, daemon=True)
    checker.start()
    print(f"[sleep-checker] background thread started (checks every 1 hour)")

    print(f"Screen Time Tracker v3 starting on port {PORT}")
    print(f"  Panel:      http://0.0.0.0:{PORT}/panel")
    print(f"  Toggle API: http://0.0.0.0:{PORT}/api/screentime/toggle/{{app_name}}")
    print(f"  Event API:  http://0.0.0.0:{PORT}/api/event/{{event_type}}")
    print(f"  Health:     http://0.0.0.0:{PORT}/health")
    mcp.run(transport="streamable-http")
