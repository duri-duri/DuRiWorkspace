#!/usr/bin/env python3

import json
import os
from datetime import datetime

from flask import Flask, jsonify, request

# 📌 설정
LOG_DIR = "/home/duri/logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "emotion_receive.log")

# 📥 수신 이력 기록 로그 설정
RECEIVE_JSON_LOG = "/home/duri/emotion_data/receive_log.json"


def append_receive_json_log(entry):
    logs = []
    if os.path.exists(RECEIVE_JSON_LOG):
        with open(RECEIVE_JSON_LOG, "r") as f:
            try:
                logs = json.load(f)
            except:
                logs = []
    logs.append(entry)
    with open(RECEIVE_JSON_LOG, "w") as f:
        json.dump(logs[-500:], f, indent=2, ensure_ascii=False)


app = Flask(__name__)


# 📥 감정 수신 엔드포인트
@app.route("/emotion", methods=["POST"])
def receive_emotion():
    try:
        data = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    log_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 감정 수신: {json.dumps(data, ensure_ascii=False)}\n"

    # 수신 이력 기록
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "emotion": data,
        "status": "success",
    }
    append_receive_json_log(log_entry)

    with open(LOG_FILE, "a") as f:
        f.write(log_msg)

    print(log_msg.strip())  # 콘솔 출력도

    # ⏩ 감정 수신 후 cur.json 갱신 실행
    os.system("python3 /home/duri/scripts/update_cur_from_delta.py")

    return jsonify({"status": "received"}), 200


# 🚀 서버 실행
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
