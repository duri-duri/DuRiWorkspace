#!/usr/bin/env bash
set -euo pipefail

# === Day 61 Pre-Phase3 Gate Check ===
# 모든 하드닝 포인트를 한 번에 검증하는 스크립트

echo "🚀 Day 61 Pre-Phase3 Gate Check 시작"
echo "=================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 결과 추적
TOTAL_CHECKS=0
PASSED_CHECKS=0

check_result() {
    local check_name="$1"
    local result="$2"
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if [[ "$result" == "PASS" ]]; then
        echo -e "${GREEN}✅ $check_name${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${RED}❌ $check_name${NC}"
        echo "   $result"
    fi
}

# 1) 자가코딩 루프 드라이런
echo "1. 자가코딩 루프 (Day21) 검증..."
if [[ -f "tools/auto_code_loop_beta.sh" ]]; then
    check_result "자가코딩 루프 스크립트" "PASS"
else
    check_result "자가코딩 루프 스크립트" "FAIL: 스크립트 파일 없음"
fi

# 2) 학습 큐레이터
echo "2. 학습 큐레이터 (Day25) 검증..."
if python3 - <<'PY' >/dev/null 2>&1; then
import sys; sys.path.append('.')
from DuRiCore.adaptive_learning_system import AdaptiveLearningSystem
als = AdaptiveLearningSystem()
print("OK")
PY
    check_result "학습 큐레이터 초기화" "PASS"
else
    check_result "학습 큐레이터 초기화" "FAIL: import 또는 초기화 오류"
fi

# 3) HITL SLA 모니터링
echo "3. HITL SLA 모니터링 (Day27) 검증..."
if curl -sG http://localhost:9090/api/v1/query --data-urlencode 'query=avg_over_time(scrape_duration_seconds[10m])' | jq -e '.data.result | length > 0' >/dev/null 2>&1; then
    check_result "Prometheus 메트릭 수집" "PASS"
else
    check_result "Prometheus 메트릭 수집" "FAIL: 메트릭 쿼리 실패"
fi

# 4) PoU 파일럿 모니터링
echo "4. PoU 파일럿 모니터링 검증..."
if python3 - <<'PY' >/dev/null 2>&1; then
import sys; sys.path.append('.')
from DuRi_Day11_15_starter.pou_pilot_manager import PoUPilotManager
pou = PoUPilotManager()
print("OK")
PY
    check_result "PoU 모니터링 시스템" "PASS"
else
    check_result "PoU 모니터링 시스템" "FAIL: import 또는 초기화 오류"
fi

# 5) Prometheus 안정성
echo "5. Prometheus 안정성 검증..."
UP_COUNT=$(curl -sG http://localhost:9090/api/v1/query --data-urlencode 'query=sum by (job)(up)' | jq -r '.data.result[] | select(.value[1] == "1") | .metric.job' | wc -l)
if [[ "$UP_COUNT" -ge 6 ]]; then
    check_result "Prometheus 타겟 가용률" "PASS"
else
    check_result "Prometheus 타겟 가용률" "FAIL: $UP_COUNT/6 타겟만 up"
fi

# 6) CI 규칙 검증
echo "6. CI 규칙 검증..."
if gh api repos/duri-duri/DuRiWorkspace/rulesets/7261445 --jq '.rules[] | select(.type=="required_status_checks") | .parameters.required_status_checks[].context' 2>/dev/null | grep -q "guard"; then
    check_result "GitHub Ruleset 설정" "PASS"
else
    check_result "GitHub Ruleset 설정" "FAIL: Ruleset 확인 불가"
fi

# 결과 요약
echo ""
echo "=================================="
echo "📊 검증 결과 요약"
echo "=================================="
echo "총 검증 항목: $TOTAL_CHECKS"
echo "통과 항목: $PASSED_CHECKS"
echo "실패 항목: $((TOTAL_CHECKS - PASSED_CHECKS))"

if [[ "$PASSED_CHECKS" -eq "$TOTAL_CHECKS" ]]; then
    echo -e "${GREEN}🎉 모든 검증 통과! Phase 3 진입 준비 완료!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  일부 검증 실패. Phase 3 진입 전 수정 필요.${NC}"
    exit 1
fi
