#!/usr/bin/env python3

import os
import json
from datetime import datetime

DATE = datetime.now().strftime("%Y-%m-%d")
BASE_DIR = f"/home/duri/emotion_data/{DATE}"
DELTA_PATH = os.path.join(BASE_DIR, "delta.json")
CUR_PATH = os.path.join(BASE_DIR, "cur.json")
LOG_PATH = "/home/duri/logs/update_cur.log"

def log(msg):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"[{datetime.now().strftime('%F %T')}] {msg}\n")

def copy_delta_to_cur():
    if not os.path.isfile(DELTA_PATH) or os.path.getsize(DELTA_PATH) == 0:
        log("❌ delta.json 없음 또는 비어있음")
        return

    try:
        with open(DELTA_PATH, "r") as f:
            delta = json.load(f)
        with open(CUR_PATH, "w") as f:
            json.dump(delta, f, indent=2, ensure_ascii=False)
        log("✅ delta.json → cur.json 복사 완료")
    except Exception as e:
        log(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    copy_delta_to_cur()
