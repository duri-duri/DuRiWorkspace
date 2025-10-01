#!/usr/bin/env python3

import json
import os
import shutil
from datetime import datetime

# 🔧 설정
EMOTION_DIR = "/home/duri/emotion_data/2025-05-23"
DELTA_FILE = os.path.join(EMOTION_DIR, "delta.json")
LAST_SENT_FILE = os.path.join(EMOTION_DIR, "last_sent.json")
SEND_LOG = "/home/duri/logs/broadcast.log"
TARGETS = {
    "duri-control": "192.168.0.11",
    "duri-brain": "192.168.0.9",
    "duri-evolution": "192.168.0.20",
}
REMOTE_PATH = "/home/duri/emotion_data/delta.json"


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SEND_LOG, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")


def file_exists_and_valid(path):
    return os.path.isfile(path) and os.path.getsize(path) > 0


def read_json(path):
    with open(path, "r") as f:
        return json.load(f)


def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f)


def send_to_all_nodes():
    for name, ip in TARGETS.items():
        cmd = f"scp {DELTA_FILE} duri@{ip}:{REMOTE_PATH}"
        result = os.system(cmd)
        if result == 0:
            log(f"[📤] 전송 성공 → {name} ({ip})")
        else:
            log(f"[❌] 전송 실패 → {name} ({ip})")


def main():
    if not file_exists_and_valid(DELTA_FILE):
        log("[❌] delta.json 파일 없음 또는 비정상")
        return

    current = read_json(DELTA_FILE)

    if os.path.exists(LAST_SENT_FILE):
        previous = read_json(LAST_SENT_FILE)
        if current == previous:
            log("[⏸️] 변경 없음 → 전송 생략")
            return

    # 변경 감지 → 전송
    send_to_all_nodes()
    shutil.copy2(DELTA_FILE, LAST_SENT_FILE)


if __name__ == "__main__":
    main()
