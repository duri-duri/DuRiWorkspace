# P-FIX#1: 프로듀서 6키 스키마 실구현
# duri_producer/writer.py

from datetime import datetime
import json
import os

SCHEMA_VERSION = os.getenv("DURI_SCHEMA_VERSION", "1")


def append_ev(path, ev_id: str, variant: str, metric_name: str, metric_value: float, n: int):
    """
    프로듀서 측 evolution.jsonl 기록 함수
    
    최소 의미론 6키: schema_version, ts, cycle_id, variant(A/B), metric{name,value}, n
    
    Args:
        path: 대상 jsonl 파일 경로
        ev_id: EV ID (예: "EV-20251102-030924-45")
        variant: A/B 변이 ("A" | "B")
        metric_name: 메트릭 이름 (예: "loss", "score")
        metric_value: 메트릭 값 (float)
        n: 샘플 수 (int, >=1이면 p 라인 생성 대상)
    
    Returns:
        None
    """
    assert variant in ("A", "B"), f"variant must be 'A' or 'B', got: {variant}"
    assert n >= 0, f"n must be >= 0, got: {n}"
    
    # n==0이면 쓰지 않음 (p 라인 생성 금지)
    if n == 0:
        return
    
    rec = {
        "schema_version": SCHEMA_VERSION,
        "ts": datetime.utcnow().isoformat() + "Z",
        "cycle_id": ev_id,
        "variant": variant,
        "metric": {"name": metric_name, "value": float(metric_value)},
        "n": int(n)
    }
    
    # 원자적 쓰기: tmp → fsync → rename
    dir_path = os.path.dirname(path)
    if dir_path:  # 디렉토리 경로가 비어있지 않으면 생성
        os.makedirs(dir_path, exist_ok=True)
    tmp = path + ".tmp"
    
    with open(tmp, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    
    os.replace(tmp, path)  # 원자적 교체 (Python 3.3+)


# 사용 예시:
# append_ev("var/evolution/EV-20251102-030924-45/evolution.EV-20251102-030924.jsonl",
#            "EV-20251102-030924-45", "A", "loss", 0.321, 1)
# append_ev("var/evolution/EV-20251102-030924-45/evolution.EV-20251102-030924.jsonl",
#            "EV-20251102-030924-45", "B", "loss", 0.123, 1)

