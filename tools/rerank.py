#!/usr/bin/env python3
import argparse
import json
import sys

p = argparse.ArgumentParser()
p.add_argument("--query", default="")
p.add_argument("--top-k", type=int, default=3)
p.add_argument("--input", required=True)
p.add_argument("--alpha", type=float, default=0.5)
args = p.parse_args()


def load_items(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    # NDJSON or ids-only fallback
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            s = line.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
                if isinstance(obj, dict):
                    items.append(obj)
                    continue
            except Exception:
                pass
            items.append({"id": s, "rank": i})
    return items


items = load_items(args.input)


def score(doc):
    bm25 = doc.get("bm25_score")
    dense = doc.get("dense_score")
    if isinstance(bm25, (int, float)) and isinstance(dense, (int, float)):
        return args.alpha * bm25 + (1 - args.alpha) * dense
    for key in ("combined_score", "score", "rerank_score", "ce_score"):
        v = doc.get(key)
        if isinstance(v, (int, float)):
            return float(v)
    return None


# 점수 필드 존재 여부 확인
scores = [score(d) for d in items]
has_signal = any(v is not None for v in scores)

if not has_signal:
    # 점수 정보가 없으면 원래 순서를 유지한 채 상위 K만
    out = items[: args.top_k]
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(0)

# 점수 계산 및 tie-break: 기존 rank(또는 인덱스) 보존
for d, sc in zip(items, scores):
    d["combined_score"] = float(sc if sc is not None else 0.0)
for idx, d in enumerate(items):
    d.setdefault("rank", idx)

items.sort(key=lambda x: (-x.get("combined_score", 0.0), x.get("rank", 1e9)))
print(json.dumps(items[: args.top_k], ensure_ascii=False))
