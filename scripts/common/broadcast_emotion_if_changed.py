#!/usr/bin/env python3

import json
import os
from datetime import datetime

import yaml

# 🔧 경로 설정
DATE = datetime.now().strftime("%Y-%m-%d")
BASE_DIR = "/home/duri/emotion_data"
EMOTION_DIR = os.path.join(BASE_DIR, DATE)
DELTA_FILE = os.path.join(EMOTION_DIR, "delta.json")
LAST_SENT_FILE = os.path.join(EMOTION_DIR, "last_sent.json")
SEND_LOG = "/home/duri/../logs/broadcast.log"
BROADCAST_JSON_LOG = os.path.join(EMOTION_DIR, "broadcast_log.json")
POLICY_PATH = "/home/duri/../config/importance_policy.yaml"
QUEUE_PATH = "/home/duri/emotion_queue/queue.json"
REMOTE_PATH = os.path.join(BASE_DIR, DATE, "delta_from_remote.json")

TARGETS = {
    "duri-brain": "192.168.0.9",
    "duri-control": "192.168.0.11",
    "duri-evolution": "192.168.0.20",
}


# 📋 로그 기록
def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(SEND_LOG), exist_ok=True)
    with open(SEND_LOG, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")


# 📋 JSON 이력 로그 기록
def append_broadcast_json_log(entry):
    logs = []
    if os.path.exists(BROADCAST_JSON_LOG):
        with open(BROADCAST_JSON_LOG, "r") as f:
            try:
                logs = json.load(f)
            except:  # noqa: E722
                logs = []
    logs.append(entry)
    with open(BROADCAST_JSON_LOG, "w") as f:
        json.dump(logs[-500:], f, indent=2, ensure_ascii=False)


# 📋 JSON 파일 다루기
def file_exists_and_valid(path):
    return os.path.isfile(path) and os.path.getsize(path) > 0


def read_json(path):
    with open(path, "r") as f:
        return json.load(f)


def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)


# 📋 중요도 기준 불러오기
def load_importance_threshold(default=0.3):
    try:
        with open(POLICY_PATH, "r") as f:
            return yaml.safe_load(f).get("importance_threshold", default)
    except:  # noqa: E722
        log("[⚠️] importance_policy.yaml 읽기 실패, 기본값 사용")
        return default


# 📋 실패 시 큐에 백업
def backup_failed_emotion(data):
    os.makedirs(os.path.dirname(QUEUE_PATH), exist_ok=True)
    with open(QUEUE_PATH, "a") as f:
        f.write(json.dumps(data) + "\n")


# 📤 대상 노드로 전송
def send_to_all_targets(data):
    for name, ip in TARGETS.items():
        cmd = f"scp -q {DELTA_FILE} duri@{ip}:{REMOTE_PATH}"
        result = os.system(cmd)
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "target": name,
            "ip": ip,
            "emotion": data,
        }

        if result == 0:
            log(f"[📤] 전송 성공 → {name} ({ip})")
            log_entry["status"] = "success"
        else:
            log(f"[❌] 전송 실패 → {name} ({ip})")
            log_entry["status"] = "failure"
            log_entry["error"] = f"scp exit code: {result}"
            backup_failed_emotion(data)

        append_broadcast_json_log(log_entry)


# 🚀 메인 로직
def main():
    if not file_exists_and_valid(DELTA_FILE):
        log("[❌] delta.json 없음 또는 비정상")
        return

    try:
        current_delta = read_json(DELTA_FILE)
    except Exception as e:
        log(f"[⚠️] delta.json 읽기 오류: {e}")
        return

    threshold = load_importance_threshold()
    importance = current_delta.get("importance_score", 0)

    if importance < threshold:
        log(f"[⏹️] 중요도 낮음 ({importance} < {threshold}) → 전송 생략")
        return

    if not file_exists_and_valid(LAST_SENT_FILE):
        log("[📢] 최초 전송 - 기록 없음")
        send_to_all_targets(current_delta)
        write_json(LAST_SENT_FILE, current_delta)
        return

    try:
        last_sent = read_json(LAST_SENT_FILE)
    except Exception as e:
        log(f"[⚠️] last_sent.json 읽기 오류: {e}")
        return

    if json.dumps(current_delta, sort_keys=True) != json.dumps(last_sent, sort_keys=True):
        log("[📢] 변화 감지됨 - 전송 실행")
        send_to_all_targets(current_delta)
        write_json(LAST_SENT_FILE, current_delta)
    else:
        log("[⏸️] 변화 없음 - 전송 생략")


if __name__ == "__main__":
    main()
