#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/var/reports/bench_$(date +%Y%m%d_%H%M)"
mkdir -p "$OUT"
echo "[BENCH] init → $OUT"
pytest -q tests/perf --benchmark-save=baseline \
  --benchmark-autosave --benchmark-min-rounds=5 \
  --benchmark-name=short --benchmark-columns=min,mean,stddev,median,ops \
  2>&1 | tee "$OUT/bench_init.log"
echo "$OUT" > "$ROOT/var/reports/LAST_BENCH_DIR"
echo "[OK] baseline saved. dir=$OUT"
