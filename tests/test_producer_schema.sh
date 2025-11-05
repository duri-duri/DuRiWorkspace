#!/usr/bin/env bash
# P-FIX#2: 계약 테스트(스키마 회귀 방지)
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== 프로듀서 스키마 계약 테스트 ==="
echo ""

# 임시 파일 생성
TEST_FILE="VAR.jsonl"
trap "rm -f $TEST_FILE VAR.jsonl.tmp 2>/dev/null" EXIT

# Python 스크립트로 writer 함수 테스트
python3 <<'PY'
import sys
import os
sys.path.insert(0, 'duri_producer')
from writer import append_ev

# 테스트 데이터 기록 (절대 경로 사용)
test_file = os.path.abspath("VAR.jsonl")
append_ev(test_file, "EV-TEST", "A", "loss", 0.12, 1)
append_ev(test_file, "EV-TEST", "B", "loss", 0.34, 1)
print("[OK] append_ev 호출 완료")
PY

# 6키 검증
if ! grep -qE '"schema_version".*"ts".*"cycle_id".*"variant".*"metric".*"n"' VAR.jsonl 2>/dev/null; then
    echo "[FAIL] 6키 검증 실패"
    exit 1
fi
echo "[OK] 6키 검증 통과"

# 집계 파이프 전체 연동 테스트
ev_id="EV-$(date -u +%Y%m%d-%H%M%S)-TEST"
mkdir -p "var/evolution/${ev_id}"
mv VAR.jsonl "var/evolution/${ev_id}/evolution.${ev_id}.jsonl"

echo "[INFO] evidence_bundle 실행 중..."
# evidence_bundle.sh는 --ev 옵션을 받지만 실제로는 새 EV를 생성합니다
# 따라서 최신 EV를 찾아서 확인해야 합니다
bash scripts/evolution/evidence_bundle.sh --ev "${ev_id}" --force >/dev/null 2>&1 || true

# 최신 ab_eval.prom 파일 찾기
latest_prom=$(find var/evolution -name "ab_eval.prom" -newermt "-1 minute" | head -1)

if [ -n "$latest_prom" ] && [ -f "$latest_prom" ]; then
    # 하드닝: p-value 라인 확인 (최대 10s 리트라이로 플랩 제로화)
    # CI 환경에서 타이밍 이슈 완화: 500ms × 20회 = 10초
    found=0
    for i in $(seq 1 20); do
        if grep -q '^duri_ab_p_value{' "$latest_prom" 2>/dev/null; then
            found=1
            break
        fi
        sleep 0.5
    done
    
    if [ "$found" -eq 1 ]; then
        echo "[OK] ab_eval.prom에 p-value 라인 생성 확인 ($latest_prom)"
    else
        echo "[FAIL] ab_eval.prom에 p-value 라인 없음 (10s 리트라이 후에도)"
        echo "[DEBUG] ab_eval.prom 내용:"
        cat "$latest_prom"
        echo "[INFO] 타이밍/플러시 문제일 수 있습니다. Issue #83 참고."
        exit 1
    fi
else
    echo "[FAIL] ab_eval.prom 파일을 찾을 수 없음"
    exit 1
fi

echo ""
echo "[OK] 프로듀서 스키마 계약 테스트 통과"

