# tools/replay_capsule.py
import hashlib
import json

from tools.fusion import MonotoneLogit, crdt_merge


def replay_capsule(capsule_file):
    """캡슐 리플레이: 결정 과정 재현과 출력 해시 일치 확인"""
    cap = json.load(open(capsule_file))
    logit = MonotoneLogit()  # 실제 운용 파라미터 로드 권장

    # 입력 벡터 구성
    x = [
        1 if cap["core"]["tag"] else 0,  # core_hit
        max((d.get("sim", 0) for d in cap["rag"]), default=0),  # similarity
        max((1.0 / (1 + d.get("age_days", 0)) for d in cap["rag"]), default=0),  # recency
        max((d.get("sim", 0) > 0 and 1 or 0 for d in cap["rag"]), default=0),  # provenance
    ]

    # 확률 계산
    p = logit.prob(x)

    # CRDT 병합 재현
    rag_candidates = [{"val": "_", "sim": x[1], "recency": x[2], "prov": x[3]}]
    val, _ = crdt_merge(core_val=None, rag_candidates=rag_candidates)

    print(f"p={round(p,4)} crdt_val={val} out_hash={cap['output']['hash']}")

    # 해시 일치 확인
    expected_hash = cap["output"]["hash"]
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
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 tools/replay_capsule.py <capsule.json>")
        sys.exit(1)

    result = replay_capsule(sys.argv[1])
    print(f"Hash match: {result['hash_match']}")
