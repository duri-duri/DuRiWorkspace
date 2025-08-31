import os
import json
from datetime import datetime

def generate_emotion_vector(emotion_keyword):
    base_vector = {
        "joy": 0.0, "anger": 0.0, "fear": 0.0,
        "trust": 0.0, "surprise": 0.0, "sadness": 0.0,
        "anticipation": 0.0, "disgust": 0.0
    }
    if emotion_keyword == "칭찬":
        base_vector["joy"] = 0.8
        base_vector["trust"] = 0.6
    return base_vector

today = datetime.now().strftime("%Y-%m-%d")
target_dir = f"/home/duri/emotion_data/{today}"
os.makedirs(target_dir, exist_ok=True)

emotion = generate_emotion_vector("칭찬")

with open(f"{target_dir}/emotion_vector.json", "w") as f:
    json.dump(emotion, f, indent=2)

with open(f"{target_dir}/delta_emotion_vector.json", "w") as f:
    json.dump({"delta": "stub"}, f)

with open(f"{target_dir}/emotion_change_log.json", "w") as f:
    f.write("감정 변경 기록 시작\n")
