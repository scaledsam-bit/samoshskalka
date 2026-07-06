import os
import requests
from datetime import datetime


def _telegram_send(message: str):
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=10)


def notify(events: list[dict]):
    if not events:
        return

    lines = [f"Instagram Monitor — {datetime.now().strftime('%d.%m.%Y %H:%M')}"]
    lines.append("")

    for e in events:
        icon = {
            "new_follower": "+👤",
            "lost_follower": "-👤",
            "new_following": "+👁",
            "lost_following": "-👁",
        }.get(e["type"], "•")

        label = {
            "new_follower": "Nový sledující",
            "lost_follower": "Přestal sledovat",
            "new_following": "Začal(a) jsi sledovat",
            "lost_following": "Přestal(a) jsi sledovat",
        }.get(e["type"], e["type"])

        lines.append(f"  {icon} {label}: @{e['username']}")

    message = "\n".join(lines)

    print(message)
    print()

    _telegram_send(message)
