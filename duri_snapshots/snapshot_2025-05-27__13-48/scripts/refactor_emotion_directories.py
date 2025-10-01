import json
import os
import shutil
from datetime import datetime, timedelta

import yaml

with open("/home/duri/config/DuRi-memory-policy.yaml", "r") as f:
    policy = yaml.safe_load(f)["memory_policy"]

root = "/home/duri/emotion_data"
cutoff = datetime.today() - timedelta(days=policy["archive_after_days"])
compressed_dir = os.path.join(root, "compressed")
os.makedirs(compressed_dir, exist_ok=True)


# 중요도 계산 함수 (delta 기준)
def calc_importance_from_delta(delta_path):
    try:
        with open(delta_path, "r") as f:
            delta = json.load(f)
        delta_sum = sum(abs(v) for v in delta.values())
        importance = delta_sum / len(delta) if delta else 0
        return importance
    except Exception as e:
        print(f"[❌] 중요도 계산 실패: {delta_path}, 이유: {e}")
        return 0


for subdir in os.listdir(root):
    subpath = os.path.join(root, subdir)
    if not os.path.isdir(subpath) or subdir == "compressed":
        continue  # "compressed" 폴더는 건너뛰기

    try:
        d = datetime.strptime(subdir, "%Y-%m-%d")
        if d < cutoff:
            delta_path = os.path.join(subpath, "delta.json")
            if not os.path.exists(delta_path):
                print(f"[📭] delta.json 없음: {delta_path}")

            importance = calc_importance_from_delta(delta_path)
            print(f"[ℹ️] 중요도: {importance:.4f} | 경로: {subpath}")

            if importance < policy["importance_threshold"]:
                shutil.rmtree(subpath)
                print(f"[🗑️] 삭제됨 (중요도 낮음): {subpath}")
            else:
                shutil.move(subpath, os.path.join(compressed_dir, subdir))
                print(f"[📦] 압축 이동: {subpath}")
    except Exception as e:
        print(f"[⚠️] 디렉토리 처리 오류: {subpath}, 이유: {e}")
