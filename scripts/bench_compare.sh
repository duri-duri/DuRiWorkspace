#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/var/reports/bench_$(date +%Y%m%d_%H%M)"
mkdir -p "$OUT"
echo "[BENCH] compare → $OUT"

# 기준선 없으면 안내
if [ ! -d "$ROOT/.benchmarks" ]; then
  echo "[WARN] no .benchmarks baseline found. run scripts/bench_init.sh first."
  exit 2
fi

# 현재 측정
pytest -q tests/perf --benchmark-compare --benchmark-compare-fail=mean:10% \
  --benchmark-min-rounds=5 \
  --benchmark-name=short --benchmark-columns=min,mean,stddev,median,ops \
  2>&1 | tee "$OUT/bench_compare.log"

# 결과 로그에 회귀 문구가 있으면 실패 처리
if grep -qi "FAILED benchmark" "$OUT/bench_compare.log"; then
  echo "[FAIL] regression detected (>10% mean slowdown). See $OUT/bench_compare.log"
  exit 1
fi

echo "$OUT" > "$ROOT/var/reports/LAST_BENCH_DIR"
echo "[OK] no regression. artifacts at $OUT"
