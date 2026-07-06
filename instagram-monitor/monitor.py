#!/usr/bin/env python3
"""
Instagram Monitor pro @jana_pirkova_
Sleduje kdo ji začal/přestal sledovat a koho ona začala/přestala sledovat.

Spuštění:
    pip install instagrapi
    python monitor.py
"""

import json
import os
import time
import getpass
from datetime import datetime
from instagrapi import Client

TARGET = "jana_pirkova_"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CREDS_FILE = os.path.join(DATA_DIR, "credentials.json")
SESSION_FILE = os.path.join(DATA_DIR, "session.json")
SNAPSHOT_FILE = os.path.join(DATA_DIR, "snapshot.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.txt")
CHECK_INTERVAL = 30


def ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def get_credentials():
    ensure_dir()
    if os.path.exists(CREDS_FILE):
        with open(CREDS_FILE, encoding="utf-8") as f:
            return json.load(f)

    print("=== Prvni spusteni ===")
    print("Potrebuji tvuj Instagram login (pro pristup k API).")
    print()
    username = input("Instagram username: ").strip()
    password = getpass.getpass("Instagram heslo: ").strip()

    creds = {"username": username, "password": password}
    with open(CREDS_FILE, "w", encoding="utf-8") as f:
        json.dump(creds, f)
    os.chmod(CREDS_FILE, 0o600)
    print("Ulozeno.\n")
    return creds


def ig_login():
    creds = get_credentials()
    cl = Client()

    if os.path.exists(SESSION_FILE):
        cl.load_settings(SESSION_FILE)

    cl.login(creds["username"], creds["password"])
    ensure_dir()
    cl.dump_settings(SESSION_FILE)
    return cl


def fetch_users(cl, user_id, fetch_fn):
    users = fetch_fn(user_id, amount=0)
    return {u.username for u in users.values()}


def load_snapshot():
    if not os.path.exists(SNAPSHOT_FILE):
        return None
    with open(SNAPSHOT_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return set(data["followers"]), set(data["following"])


def save_snapshot(followers, following):
    ensure_dir()
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "followers": sorted(followers),
            "following": sorted(following),
        }, f, ensure_ascii=False, indent=2)


def log_event(text):
    ensure_dir()
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")


def ts():
    return datetime.now().strftime("%H:%M:%S")


def check():
    print(f"[{ts()}] Prihlasuji se...")
    cl = ig_login()

    print(f"[{ts()}] Hledam @{TARGET}...")
    target_info = cl.user_info_by_username(TARGET)
    target_id = str(target_info.pk)

    print(f"[{ts()}] Stahuji followers @{TARGET}...")
    followers = fetch_users(cl, target_id, cl.user_followers)

    print(f"[{ts()}] Stahuji following @{TARGET}...")
    following = fetch_users(cl, target_id, cl.user_following)

    print(f"[{ts()}] @{TARGET} ma {len(followers)} sledujicich, sleduje {len(following)} lidi")

    previous = load_snapshot()

    if previous is None:
        print(f"[{ts()}] Prvni kontrola — ukladam snapshot. Zmeny uvidis priste.")
        save_snapshot(followers, following)
        return

    old_followers, old_following = previous
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    changes = False

    new_followers = followers - old_followers
    lost_followers = old_followers - followers
    new_following = following - old_following
    lost_following = old_following - following

    for u in sorted(new_followers):
        msg = f"[{now}]  +sledujici   @{u} zacal sledovat @{TARGET}"
        print(f"  >>> {msg}")
        log_event(msg)
        changes = True

    for u in sorted(lost_followers):
        msg = f"[{now}]  -sledujici   @{u} prestal sledovat @{TARGET}"
        print(f"  >>> {msg}")
        log_event(msg)
        changes = True

    for u in sorted(new_following):
        msg = f"[{now}]  +sleduje     @{TARGET} zacala sledovat @{u}"
        print(f"  >>> {msg}")
        log_event(msg)
        changes = True

    for u in sorted(lost_following):
        msg = f"[{now}]  -sleduje     @{TARGET} prestala sledovat @{u}"
        print(f"  >>> {msg}")
        log_event(msg)
        changes = True

    if not changes:
        print(f"[{ts()}] Zadne zmeny.")

    save_snapshot(followers, following)


def main():
    print(f"{'=' * 50}")
    print(f"  Instagram Monitor — @{TARGET}")
    print(f"  Kontrola kazdych {CHECK_INTERVAL} minut")
    print(f"  Ctrl+C pro ukonceni")
    print(f"{'=' * 50}")
    print()

    while True:
        try:
            check()
        except KeyboardInterrupt:
            print("\nUkonceno.")
            break
        except Exception as e:
            print(f"[{ts()}] CHYBA: {e}")

        print(f"[{ts()}] Dalsi kontrola za {CHECK_INTERVAL} min...\n")
        try:
            time.sleep(CHECK_INTERVAL * 60)
        except KeyboardInterrupt:
            print("\nUkonceno.")
            break


if __name__ == "__main__":
    main()
