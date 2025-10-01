#!/usr/bin/env python3

from datetime import datetime
import json
import os

BASE_DIR = "/home/duri/emotion_data"
CUR_PATH = os.path.join(BASE_DIR, "cur.json")
LAST_PATH = os.path.join(BASE_DIR, "last_logged_emotion.json")
LOG_PATH = os.path.join(BASE_DIR, "emotion_change_log.json")
THRESHOLD = 0.1  # intensity 변화 기준


def load_json(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return None
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def append_log(entry):
    logs = []
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            try:
                logs = json.load(f)
            except:
                logs = []
    logs.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(logs[-500:], f, indent=2, ensure_ascii=False)  # 최근 500개 유지


def emotion_changed(prev, curr):
    if prev is None:
        return "first_log"
    if prev["emotion"] != curr["emotion"]:
        return "emotion_changed"
    if abs(prev["intensity"] - curr["intensity"]) >= THRESHOLD:
        return "intensity_changed"
    return None


def main():
    cur = load_json(CUR_PATH)
    if not cur:
        return

    last = load_json(LAST_PATH)
    reason = emotion_changed(last, cur)

    if reason:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "prev": last if last else "none",
            "new": cur,
            "reason": reason,
        }
        append_log(log_entry)
        save_json(LAST_PATH, cur)


if __name__ == "__main__":
    main()
