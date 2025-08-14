#!/usr/bin/env bash
set -euo pipefail
RUNS=${1:-3}
TS=$(date +%Y%m%d_%H%M%S)
LOGDIR="artifacts_phase1/repro_${TS}"
mkdir -p "$LOGDIR"

echo "== Repro loop: ${RUNS} runs =="
for i in $(seq 1 $RUNS); do
  echo "--- Run #$i ---"
  LOGF="$LOGDIR/run_${i}.log"
  # 필요 시 프로그램이 읽는 cfg 병합 경로를 CLI/env로 전달 (프로젝트 관례에 맞게 조정)
  OVERRIDE="configs/evolve_override.yaml"
  export DURI_EVOLVE_OVERRIDE="$OVERRIDE"
  python3 auto_evolve_guarded.py | tee "$LOGF"

  # league_summary.csv에 run_id/thresholds 주석 라인 남기기 (간단 추적)
  if [ -f artifacts_phase1/league_summary.csv ]; then
    echo "# repro_ts=${TS}, run=${i}, override=${OVERRIDE}" >> artifacts_phase1/league_summary.csv
  fi
done

echo "== Repro finished. Logs: $LOGDIR =="
# quick stats
grep -h "→ testR2=" "$LOGDIR"/*.log | sed 's/^[[:space:]]*//' | sort | uniq -c

