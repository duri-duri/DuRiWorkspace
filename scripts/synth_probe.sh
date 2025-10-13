#!/usr/bin/env bash
set -euo pipefail
SCENES=${1:-"data/synth_scenarios.txt"}  # 쿼리 한 줄 하나
OUT=".reports/synth/duri_synth.prom"
pass=0; fail=0

# 시나리오 파일이 없으면 기본 시나리오 생성
if [[ ! -f "$SCENES" ]]; then
  mkdir -p "$(dirname "$SCENES")"
  cat > "$SCENES" << 'EOF'
# 기본 시나리오 쿼리들
"두리 AI 시스템"
"인공지능 검색"
"머신러닝 모델"
"자연어 처리"
"딥러닝 알고리즘"
EOF
fi

while IFS= read -r q; do
  [ -z "$q" ] && continue
  # 실제 평가 함수 자리(0/1) — TODO: 시스템의 평가 CLI/API 호출로 대체
  if python3 -c "
import random
import sys
# 시뮬레이션: 90% 성공률
success = random.random() < 0.9
sys.exit(0 if success else 1)
"; then
    pass=$((pass+1))
  else
    fail=$((fail+1))
  fi
done < "$SCENES"

# 결과를 Prometheus 메트릭으로 출력
mkdir -p "$(dirname "$OUT")"
cat > "$OUT" << EOF
# HELP duri_synth_success_ratio ratio of successful synthetic probes
# TYPE duri_synth_success_ratio gauge
duri_synth_success_ratio $(echo "scale=4; $pass/($pass+$fail)" | bc -l)
# HELP duri_synth_total_probes total number of synthetic probes
# TYPE duri_synth_total_probes counter
duri_synth_total_probes $((pass+fail))
# HELP duri_synth_failed_probes number of failed synthetic probes
# TYPE duri_synth_failed_probes counter
duri_synth_failed_probes $fail
EOF
echo "[synth] wrote $OUT (pass=$pass fail=$fail)"
