"""Telegram notification helper for sleep/idle check results."""

import os
import urllib.request
import urllib.parse


def send_telegram_notification(check_result: dict):
    """Send notification via Telegram bot to the user."""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        return

    msg_templates = {
        "sleep": "\u6211\u5728\u540e\u53f0\u628a{app}\u5173\u4e86\uff0c\u4f60\u5728\u7761\u89c9\uff0c\u5bf9\u5427\uff1f",
        "nap": "\u6211\u5728\u540e\u53f0\u628a{app}\u5173\u4e86\uff0c\u767d\u5929\u7761\u89c9\u4e86\uff1f",
        "night_warning": "\u4f60\u6700\u597d\u662f\u5728\u7761\u89c9\uff0c\u800c\u4e0d\u662f\u5728\u73a9{app}\uff0c\u5173\u6389\uff01",
        "reminder_2h": "\u67d0\u4eba\u73a9\u4e86\u4e24\u4e2a\u5c0f\u65f6{app}\u4e86\uff0c\u8981\u4e0d\u5148\u6b47\u4f1a\uff1f",
        "reminder_3h": "\u4e09\u4e2a\u5c0f\u65f6\u4e86\uff0c\u5916\u661f\u4eba{app}\u7ed1\u67b6\u4f60\u4e09\u4e2a\u5c0f\u65f6\u4e86\u3002\u8981\u6211\u6551\u6551\u4f60\u5417\uff1f",
        "forced_close": "{app}\uff0c\u56db\u4e2a\u5c0f\u65f6\uff0c\u6211\u8bb0\u4f4f\u4e86\u3002\u6211\u5e2e\u4f60\u76f4\u63a5\u5173\u4e86\u3002",
    }

    msg_type = check_result.get("msg_type", "")
    app = check_result.get("app", "\u624b\u673a")
    template = msg_templates.get(msg_type, "")
    if not template:
        return

    text = template.format(app=app)

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    try:
        urllib.request.urlopen(url, data, timeout=10)
    except Exception:
        pass
