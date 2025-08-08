

#!/usr/bin/env python3

import os
import json
import requests
from datetime import datetime
import yaml

# 📌 경로 설정
DATE = datetime.now().strftime("%Y-%m-%d")
CUR_EMOTION_PATH = f'/home/duri/emotion_data/{DATE}/emotion_vector.json'
QUEUE_PATH = '/home/duri/emotion_queue/pending_emotions.json'
POLICY_PATH = '/home/duri/../config/importance_policy.yaml'

# 📌 전송 대상 (REST API)
DEST_URL = 'http://192.168.0.15:8080/emotion'

# 🔧 중요도 기준 불러오기
def load_importance_threshold(default=0.3):
    try:
        with open(POLICY_PATH, 'r') as f:
            return yaml.safe_load(f).get("importance_threshold", default)
    except:
        return default

# 📥 감정 불러오기
def load_emotion(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None

# 📤 감정 전송
def send_emotion(data):
    try:
        res = requests.post(DEST_URL, json=data)
        if res.status_code != 200:
            raise Exception(f"HTTP {res.status_code}")
        print(f"[✓] 전송 성공: {data['emotion']} ({data['importance_score']:.2f})")
    except Exception as e:
        print(f"[!] 전송 실패: {e} → 큐에 저장")
        os.makedirs(os.path.dirname(QUEUE_PATH), exist_ok=True)
        with open(QUEUE_PATH, 'a') as q:
            q.write(json.dumps(data) + '\n')

# 🚀 실행 로직
def main():
    emotion = load_emotion(CUR_EMOTION_PATH)
    if not emotion:
        print("[!] 감정 데이터 없음 또는 파싱 실패")
        return

    threshold = load_importance_threshold()
    score = emotion.get('importance_score', 0)
    if score >= threshold:
        send_emotion(emotion)
    else:
        print(f"[-] importance_score 낮음 ({score:.2f}) → 전송 생략")

if __name__ == "__main__":
    main()
