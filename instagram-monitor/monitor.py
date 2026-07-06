#!/usr/bin/env python3
"""
Instagram Follow Monitor
Sleduje změny v followers/following vašeho vlastního účtu
a posílá oznámení o změnách.

Použití:
    python monitor.py              # jednorázová kontrola
    python monitor.py --loop       # běží v cyklu (výchozí interval 30 min)
    python monitor.py --history    # zobrazí historii změn
"""

import argparse
import time
import sys
import os
from datetime import datetime

from dotenv import load_dotenv

from instagram_client import login, fetch_followers, fetch_following
from storage import save_snapshot, load_snapshot, save_history
from notifier import notify


def compare(old_set: set[str], new_set: set[str]) -> tuple[set[str], set[str]]:
    added = new_set - old_set
    removed = old_set - new_set
    return added, removed


def check_once():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Přihlašování k Instagramu...")
    cl, user_id = login()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Přihlášen jako @{os.environ['IG_USERNAME']}")

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Stahuji followers...")
    current_followers = fetch_followers(cl, user_id)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Stahuji following...")
    current_following = fetch_following(cl, user_id)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Followers: {len(current_followers)}, Following: {len(current_following)}")

    previous = load_snapshot()
    events = []

    if previous is None:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] První spuštění — ukládám výchozí snapshot.")
    else:
        old_followers, old_following = previous
        now = datetime.now().isoformat()

        new_followers, lost_followers = compare(old_followers, current_followers)
        new_following, lost_following = compare(old_following, current_following)

        for u in sorted(new_followers):
            events.append({"timestamp": now, "type": "new_follower", "username": u})
        for u in sorted(lost_followers):
            events.append({"timestamp": now, "type": "lost_follower", "username": u})
        for u in sorted(new_following):
            events.append({"timestamp": now, "type": "new_following", "username": u})
        for u in sorted(lost_following):
            events.append({"timestamp": now, "type": "lost_following", "username": u})

        if events:
            notify(events)
            save_history(events)
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Žádné změny.")

    save_snapshot(current_followers, current_following)
    return events


def show_history():
    history_path = os.path.join(os.path.dirname(__file__), "data", "history.jsonl")
    if not os.path.exists(history_path):
        print("Zatím žádná historie.")
        return

    import json
    with open(history_path, encoding="utf-8") as f:
        for line in f:
            event = json.loads(line)
            ts = event["timestamp"][:16].replace("T", " ")
            label = {
                "new_follower": "✅ Nový sledující",
                "lost_follower": "❌ Přestal sledovat",
                "new_following": "➡️  Začal(a) jsi sledovat",
                "lost_following": "⬅️  Přestal(a) jsi sledovat",
            }.get(event["type"], event["type"])
            print(f"  {ts}  {label}: @{event['username']}")


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Instagram Follow Monitor")
    parser.add_argument("--loop", action="store_true", help="Běží v cyklu")
    parser.add_argument("--history", action="store_true", help="Zobrazí historii změn")
    args = parser.parse_args()

    if args.history:
        show_history()
        return

    if not os.environ.get("IG_USERNAME") or not os.environ.get("IG_PASSWORD"):
        print("Chyba: Nastav IG_USERNAME a IG_PASSWORD v souboru .env")
        print("Viz .env.example")
        sys.exit(1)

    if args.loop:
        interval = int(os.environ.get("CHECK_INTERVAL", "30"))
        print(f"Spouštím monitor v cyklu (interval: {interval} min)")
        print("Ctrl+C pro ukončení\n")
        while True:
            try:
                check_once()
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Chyba: {e}")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Další kontrola za {interval} min...\n")
            time.sleep(interval * 60)
    else:
        check_once()


if __name__ == "__main__":
    main()
