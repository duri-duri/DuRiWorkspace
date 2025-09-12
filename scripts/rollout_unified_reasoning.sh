#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
run_step() {
  PCT="$1"
  echo "[ROLLOUT] → ${PCT}%"
  DURI_UNIFIED_REASONING_ROLLOUT="$PCT" DURI_UNIFIED_REASONING_MODE=auto \
    bash -lc "source $ROOT/env/dev_env.sh && pytest -q tests/contracts tests/contracts_unified -k 'reasoning' && scripts/bench_compare.sh"
}
run_step 0   # 기준 검증
run_step 25
run_step 50
run_step 100
echo "[OK] rollout path passed."
