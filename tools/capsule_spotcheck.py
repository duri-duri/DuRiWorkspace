import hashlib

MIN_N = 200  # 최소 샘플 수
# tools/capsule_spotcheck.py
import json
import math
from pathlib import Path
import random
import sys


def wilson(p, n, z=3.29):  # ~99.9% CI
    if n == 0:
        return (0, 1)
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt((p * (1 - p) / n) + (z * z / (4 * n * n))) / denom
    return (max(0, center - margin), min(1, center + margin))


def spotcheck_capsules():
    """캡슐 재현 스팟체크: 윌슨 CI 포함"""
    import psycopg2
    from psycopg2.extras import RealDictCursor

    # DB 연결
    conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5433/postgres")

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # 캡슐 샘플링
        cur.execute(
            "SELECT capsule FROM answer_ledger ORDER BY created_at DESC LIMIT 1000"
        )
        capsules = [row["capsule"] for row in cur.fetchall()]

        # 샘플 크기: max(200, 총응답의 0.5%)
        sample_size = min(max(200, len(capsules) // 200), len(capsules))
        sample = random.sample(capsules, k=sample_size)

        ok = 0
        for c in sample:
            # 실제 리플레이 검증 로직 연결 (해시/seed 일치 등)
            result = replay_capsule_from_dict(c)
            if result["hash_match"]:
                ok += 1

        p = ok / len(sample) if sample else 0
        lo, hi = wilson(p, len(sample))

        print(f"repro={p:.5f} n={len(sample)} CI99.9%=[{lo:.5f},{hi:.5f}]")

        # 목표 달성 확인
        success = p >= 0.999 and lo >= 0.995
        print(f"목표 달성: {'✅' if success else '❌'}")

        return success


def replay_capsule_from_dict(capsule):
    """캡슐 딕셔너리에서 직접 재현"""
    from tools.fusion import MonotoneLogit, crdt_merge

    logit = MonotoneLogit()

    # 입력 벡터 구성
    x = [
        1 if capsule["core"]["tag"] else 0,  # core_hit
        max((d.get("sim", 0) for d in capsule["rag"]), default=0),  # similarity
        max(
            (1.0 / (1 + d.get("age_days", 0)) for d in capsule["rag"]), default=0
        ),  # recency
        max(
            (d.get("sim", 0) > 0 and 1 or 0 for d in capsule["rag"]), default=0
        ),  # provenance
    ]

    # 확률 계산
    p = logit.prob(x)

    # CRDT 병합 재현
    rag_candidates = [{"val": "_", "sim": x[1], "recency": x[2], "prov": x[3]}]
    val, _ = crdt_merge(core_val=None, rag_candidates=rag_candidates)

    # 해시 일치 확인
    expected_hash = capsule["output"]["hash"]
    actual_hash = hashlib.sha256(str(val).encode()).hexdigest()
    match = expected_hash == actual_hash

    return {
        "probability": p,
        "crdt_value": val,
        "expected_hash": expected_hash,
        "actual_hash": actual_hash,
        "hash_match": match,
    }


if __name__ == "__main__":
    success = spotcheck_capsules()
    sys.exit(0 if success else 1)
