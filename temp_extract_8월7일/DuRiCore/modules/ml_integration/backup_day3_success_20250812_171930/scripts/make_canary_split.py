#!/usr/bin/env python3
import json, os, hashlib
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(".")
ART  = ROOT / "artifacts_phase1"
ART.mkdir(exist_ok=True)

# 입력 파일(실데이터 CSV)
DATA = ROOT / "test_data.csv"   # 필요시 경로 조정
CANARY_N = 200
RANDOM_STATE = 4242

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

def main():
    assert DATA.exists(), f"data not found: {DATA}"
    df = pd.read_csv(DATA)

    # 캔너리: stratified가 필요하면 타깃 분위로 라벨링 후 층화 가능
    if "target" in df.columns:
        # 분위 기반 간단 층화(5분위)
        y = pd.qcut(df["target"].rank(method="first"), q=5, labels=False)
        canary, _ = train_test_split(df, test_size=len(df)-CANARY_N, random_state=RANDOM_STATE, stratify=y)
    else:
        canary = df.sample(n=CANARY_N, random_state=RANDOM_STATE)

    canary_path = ART / "canary_set.csv"
    canary.to_csv(canary_path, index=False)

    meta = {
        "type": "canary",
        "rows": len(canary),
        "random_state": RANDOM_STATE,
        "data_sha256": sha256_file(DATA),
        "canary_sha256": sha256_file(canary_path),
        "columns": list(canary.columns),
    }
    json.dump(meta, open(ART/"canary_meta.json","w"), ensure_ascii=False, indent=2)
    print(f"[CANARY] saved: {canary_path} ({len(canary)} rows)")
    print(f"[CANARY] meta: {ART/'canary_meta.json'}")

if __name__ == "__main__":
    main()
