#!/usr/bin/env bash
set -Eeuo pipefail
# 운영 전환 모니터링 스크립트 (기존 watch_full_backup.sh 패턴 활용)

ROLLOUT_INTERVAL="${ROLLOUT_INTERVAL:-60}"  # 60초마다 체크
LOG_FILE="var/reports/rollout_monitor_$(date +%Y%m%d).log"

log(){ echo "[$(date '+%F %T')] $*" | tee -a "$LOG_FILE"; }
err(){ echo "[$(date '+%F %T')] [ERR] $*" | tee -a "$LOG_FILE" >&2; }

# 모니터링 함수
check_rollout_health() {
    local rollout_pct="${DURI_UNIFIED_REASONING_ROLLOUT:-0}"
    local mode="${DURI_UNIFIED_REASONING_MODE:-auto}"

    log "체크: ROLLOUT=${rollout_pct}%, MODE=${mode}"

    # 1) 계약 테스트 체크
    if ! pytest -q tests/contracts -k "reasoning" >/dev/null 2>&1; then
        err "계약 테스트 실패 - 롤백 권장"
        return 1
    fi

    # 2) 통합 테스트 체크
    if ! pytest -q tests/contracts_unified -k "unified or rollout" >/dev/null 2>&1; then
        err "통합 테스트 실패 - 롤백 권장"
        return 1
    fi

    # 3) 벤치마크 체크 (25% 이상일 때만)
    if [ "$rollout_pct" -ge 25 ]; then
        if ! scripts/bench_compare.sh >/dev/null 2>&1; then
            err "벤치마크 회귀 감지 - 롤백 권장"
            return 1
        fi
    fi

    log "✅ 모든 체크 통과"
    return 0
}

# 메인 모니터링 루프
main() {
    log "🚀 운영 전환 모니터링 시작 (${ROLLOUT_INTERVAL}초 간격)"
    log "현재 설정: ROLLOUT=${DURI_UNIFIED_REASONING_ROLLOUT:-0}%, MODE=${DURI_UNIFIED_REASONING_MODE:-auto}"

    while true; do
        if ! check_rollout_health; then
            err "건강도 체크 실패 - 모니터링 계속 (수동 롤백 필요)"
        fi

        sleep "$ROLLOUT_INTERVAL"
    done
}

# 신호 처리
trap 'log "모니터링 중단됨"; exit 0' INT TERM

# 로그 디렉토리 생성
mkdir -p "$(dirname "$LOG_FILE")"

# 실행
main
