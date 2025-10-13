#!/bin/bash
set -Eeuo pipefail
# 리팩토링 25% 전환 모니터링 스크립트
# 사용법: bash scripts/monitor_rollout.sh [간격초수]

INTERVAL=${1:-900}  # 기본 15분 (900초)
LOG_FILE="var/reports/rollout_monitor_$(date +%Y%m%d_%H%M%S).log"

echo "🚀 리팩토링 25% 전환 모니터링 시작"
echo "📊 간격: ${INTERVAL}초 (${INTERVAL}s)"
echo "📝 로그: $LOG_FILE"
echo "⏹️  중단: Ctrl+C"
echo ""

# 로그 파일 초기화
echo "# 리팩토링 25% 전환 모니터링 로그" > "$LOG_FILE"
echo "# 시작: $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$TIMESTAMP] 상태 체크"

    # 1. 롤아웃 상태
    echo "  📊 롤아웃 상태:"
    ROLLOUT_STATUS=$(bash scripts/rollout_ops.sh status 2>/dev/null | head -n 5)
    echo "$ROLLOUT_STATUS" | sed 's/^/    /'

    # 2. 에러 로그 스캔
    echo "  🔍 에러 로그 스캔:"
    ERROR_CHECK=$(grep -Eri "error|fail|traceback" var/reports/final_verify_*/*.log 2>/dev/null || echo "OK")
    if [ "$ERROR_CHECK" = "OK" ]; then
        echo "    ✅ 에러 없음"
    else
        echo "    ❌ 에러 발견:"
        echo "$ERROR_CHECK" | sed 's/^/      /'
    fi

    # 3. 테스트 상태 (간단 체크)
    echo "  🧪 테스트 상태:"
    if [ -f "var/reports/pytest-report.xml" ]; then
        echo "    ✅ pytest 리포트 존재"
    else
        echo "    ⚠️  pytest 리포트 없음"
    fi

    # 4. 시스템 리소스 (간단 체크)
    echo "  💻 시스템 리소스:"
    MEMORY_USAGE=$(free -h | grep "Mem:" | awk '{print $3"/"$2}')
    echo "    📊 메모리: $MEMORY_USAGE"

    # 로그 파일에 기록
    {
        echo "[$TIMESTAMP]"
        echo "ROLLOUT_STATUS:"
        echo "$ROLLOUT_STATUS"
        echo "ERROR_CHECK: $ERROR_CHECK"
        echo "MEMORY: $MEMORY_USAGE"
        echo "---"
    } >> "$LOG_FILE"

    echo ""
    echo "⏰ 다음 체크까지 ${INTERVAL}초 대기... (Ctrl+C로 중단)"
    sleep "$INTERVAL"
done
