#!/usr/bin/env python3
import json
import pathlib
import sys

if len(sys.argv) < 3:
    print("usage: bench_guard.py <baseline.json> <now.json> [THRESH_PCT=10]")
    sys.exit(2)

baseline_p = pathlib.Path(sys.argv[1])
now_p = pathlib.Path(sys.argv[2])
thresh = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0  # percent


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# pytest-benchmark JSON 구조 가정:
# {
#   "benchmarks": [
#     {"fullname": "reasoning_math_bench", "stats": {"mean": ...}},
#     ...
#   ]
# }
base = load(baseline_p)
now = load(now_p)


# fullname -> mean 매핑
def to_means(doc):
    out = {}
    for b in doc.get("benchmarks", []):
        name = b.get("fullname") or b.get("name") or ""
        mean = (b.get("stats") or {}).get("mean")
        if name and isinstance(mean, (int, float)):
            out[name] = mean
    return out


bm_base = to_means(base)
bm_now = to_means(now)

missing = [k for k in bm_base.keys() if k not in bm_now]
if missing:
    print(f"[WARN] missing in NOW: {missing}")

worse, better = [], []
for name, base_mean in bm_base.items():
    now_mean = bm_now.get(name)
    if now_mean is None:
        continue
    # mean: 낮을수록 좋음(시간)
    delta_pct = (now_mean - base_mean) / base_mean * 100.0
    if delta_pct > thresh:
        worse.append((name, base_mean, now_mean, delta_pct))
    elif delta_pct < -thresh:
        better.append((name, base_mean, now_mean, delta_pct))

if better:
    print("✅ Improvements (mean↓):")
    for n, b, c, p in better:
        print(f"  - {n}: {b:,.4f} → {c:,.4f}  ({p:+.2f}%)")

if worse:
    print("❌ Regressions (mean↑) beyond threshold:")
    for n, b, c, p in worse:
        print(f"  - {n}: {b:,.4f} → {c:,.4f}  ({p:+.2f}%)")
    sys.exit(1)

print(f"🏁 Guard PASS (threshold ±{thresh:.1f}%, regressions none).")
sys.exit(0)
