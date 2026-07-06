import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _path(filename):
    return os.path.join(DATA_DIR, filename)


def save_snapshot(followers: set[str], following: set[str]):
    _ensure_dir()
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "followers": sorted(followers),
        "following": sorted(following),
    }
    with open(_path("latest.json"), "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)


def load_snapshot() -> tuple[set[str], set[str]] | None:
    path = _path("latest.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return set(data["followers"]), set(data["following"])


def save_history(events: list[dict]):
    _ensure_dir()
    path = _path("history.jsonl")
    with open(path, "a", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
