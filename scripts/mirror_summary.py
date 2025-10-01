import json
import math
import pathlib
import sys

path = pathlib.Path("var/reports/mirror/samples.jsonl")
n = agree = 0
if path.exists():
    for line in path.open(encoding="utf-8"):
        n += 1
        try:
            rec = json.loads(line)
            # 새로운 데이터 구조에 맞게 수정: base, unified, agree 필드 사용
            agree += 1 if rec.get("agree") else 0
        except:
            pass
acc = (agree / n * 100) if n else 0.0
print(f"mirror_samples={n}, agree={agree} ({acc:.1f}%)")
