import datetime
import json
import os


def save_emotion_vector(emotion_vector, base_path="/home/duri/emotion_data"):
    today = datetime.date.today().isoformat()
    save_path = os.path.join(base_path, today)
    os.makedirs(save_path, exist_ok=True)

    with open(os.path.join(save_path, "cur.json"), "w") as f:
        json.dump(emotion_vector, f)

    print(f"[✅] 감정 벡터 저장 완료: {save_path}/cur.json")


if __name__ == "__main__":
    # 샘플 감정 벡터 (자유롭게 수정 가능)
    sample_emotion = {"joy": 0.8, "anger": 0.1, "sadness": 0.05}

    save_emotion_vector(sample_emotion)
