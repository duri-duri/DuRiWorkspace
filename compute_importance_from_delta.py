#!/usr/bin/env python3
import json
import os
from datetime import datetime, timedelta

# 📌 경로 설정
TODAY = datetime.now().strftime("%Y-%m-%d")
YESTERDAY = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

today_path = f"/home/duri/emotion_data/{TODAY}/emotion_vector.json"
yesterday_path = f"/home/duri/emotion_data/{YESTERDAY}/emotion_vector.json"


def load_vector(path):
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def compute_delta_importance(current, previous):
    if current is None or previous is None:
        return 0.0  # 비교할 대상이 없으면 중요도 없음
    delta = sum(
        abs(current.get(emotion, 0.0) - previous.get(emotion, 0.0)) for emotion in current.keys()
    )
    return round(delta / len(current), 4)


# 실행부
current_vec = load_vector(today_path)
previous_vec = load_vector(yesterday_path)

score = compute_delta_importance(current_vec, previous_vec)
print(f"[+] importance_score = {score}")
