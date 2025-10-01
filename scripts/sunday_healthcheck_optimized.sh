#!/usr/bin/env bash
set -euo pipefail

# ===== DuRi 일요일 시스템 안정성 점검 (최적화 버전) =====
# 사용법: ./sunday_healthcheck_optimized.sh [--fast|--full|--compare]

ROOT="${ROOT:-$HOME/DuRiWorkspace}"
ARCHIVE_ROOT="${ARCHIVE_ROOT:-/mnt/hdd/ARCHIVE}"
FULL_DIR="${FULL_DIR:-$ARCHIVE_ROOT/FULL}"
INCR_DIR="${INCR_DIR:-$ARCHIVE_ROOT/INCR}"

# 로그 설정
LOG_FILE="$ROOT/var/logs/sunday_healthcheck_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$(dirname "$LOG_FILE")"

# 색상 출력 함수
banner(){ printf "\n\033[1;34m== %s ==\033[0m\n" "$*"; }
ok(){ printf "\033[1;32m[OK]\033[0m %s\n" "$*"; }
ng(){ printf "\033[1;31m[NG]\033[0m %s\n" "$*"; }
warn(){ printf "\033[1;33m[WARN]\033[0m %s\n" "$*"; }
info(){ printf "\033[1;36m[INFO]\033[0m %s\n" "$*"; }

# 로그 함수
log() {
    echo "[$(date +'%F %T %Z')] $1" | tee -a "$LOG_FILE"
}

# 성능 측정 함수
measure_performance() {
    local start_time=$(date +%s.%N)
    "$@"
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l)
    echo "$duration"
}

# 시스템 부하 측정
get_system_load() {
    uptime | awk -F'load average:' '{print $2}' | tr -d ' '
}

# 메모리 사용량 측정
get_memory_usage() {
    free -m | awk 'NR==2{printf "%.1f%%", $3*100/$2}'
}

# 디스크 사용량 측정
get_disk_usage() {
    df -h "$ROOT" | awk 'NR==2{print $5}' | tr -d '%'
}

# ---- 1) 시스템 기본 상태 점검 ----
check_system_basics() {
    banner "1) 시스템 기본 상태 점검"

    # 시스템 부하 확인
    local load=$(get_system_load)
    local memory=$(get_memory_usage)
    local disk=$(get_disk_usage)

    log "시스템 부하: $load"
    log "메모리 사용량: $memory"
    log "디스크 사용량: $disk%"

    # 임계값 체크 (부동소수 안전 비교)
    load1="$(cut -d' ' -f1 /proc/loadavg)"
    threshold="${LOAD_THRESHOLD:-2.0}"
    if awk -v l="$load1" -v t="$threshold" 'BEGIN{exit !(l>t)}'; then
        warn "시스템 부하가 높습니다: $load"
    else
        ok "시스템 부하 정상: $load"
    fi

    if awk -v m="${memory%.*}" 'BEGIN{exit !(m>80)}'; then
        warn "메모리 사용량이 높습니다: $memory"
    else
        ok "메모리 사용량 정상: $memory"
    fi

    if awk -v d="$disk" 'BEGIN{exit !(d>85)}'; then
        warn "디스크 사용량이 높습니다: $disk%"
    else
        ok "디스크 사용량 정상: $disk%"
    fi
}

# ---- 2) 핵심 스크립트 존재 확인 ----
check_core_scripts() {
    banner "2) 핵심 스크립트 존재 확인"

    local scripts=(
        "scripts/duri_backup_phase1.sh"
        "scripts/run_health_and_mark.sh"
        "scripts/morning_check_and_recover.sh"
        "scripts/smoke_restore_test.sh"
        "scripts/hdd_verify_backups.sh"
        "scripts/ops_alert.sh"
        "tools/canary_guard.py"
    )

    local missing=0
    for script in "${scripts[@]}"; do
        if [[ -f "$ROOT/$script" ]]; then
            ok "$script 존재"
        else
            ng "$script 없음"
            ((missing++))
        fi
    done

    if [[ $missing -eq 0 ]]; then
        ok "모든 핵심 스크립트 존재"
    else
        ng "$missing개 스크립트 누락"
        return 1
    fi
}

# ---- 3) 학습 엔진 성능 테스트 ----
test_learning_engine() {
    banner "3) 학습 엔진 성능 테스트"

    if [[ ! -f "$ROOT/test_learning_engine.py" ]]; then
        ng "test_learning_engine.py 없음"
        return 1
    fi

    local start_time=$(date +%s)
    cd "$ROOT"

    # 성능 측정
    local duration=$(measure_performance python3 test_learning_engine.py > /dev/null 2>&1)
    local exit_code=$?

    if [[ $exit_code -eq 0 ]]; then
        ok "학습 엔진 테스트 성공 (${duration}s)"
        log "학습 엔진 실행 시간: ${duration}초"
    else
        ng "학습 엔진 테스트 실패"
        return 1
    fi
}

# ---- 4) 백업 시스템 상태 확인 ----
check_backup_system() {
    banner "4) 백업 시스템 상태 확인"

    # 최근 백업 파일 확인
    local latest_full=$(find "$FULL_DIR" -name "FULL__*.tar.*" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
    local latest_incr=$(find "$INCR_DIR" -name "INCR__*.tar.*" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)

    if [[ -n "$latest_full" ]]; then
        local full_age=$(( $(date +%s) - $(stat -c %Y "$latest_full") ))
        local full_age_hours=$(( full_age / 3600 ))

        if [[ $full_age_hours -lt 48 ]]; then
            ok "최근 FULL 백업 존재 (${full_age_hours}시간 전)"
        else
            warn "FULL 백업이 오래됨 (${full_age_hours}시간 전)"
        fi
    else
        ng "FULL 백업 파일 없음"
    fi

    if [[ -n "$latest_incr" ]]; then
        local incr_age=$(( $(date +%s) - $(stat -c %Y "$latest_incr") ))
        local incr_age_hours=$(( incr_age / 3600 ))

        if [[ $incr_age_hours -lt 24 ]]; then
            ok "최근 INCR 백업 존재 (${incr_age_hours}시간 전)"
        else
            warn "INCR 백업이 오래됨 (${incr_age_hours}시간 전)"
        fi
    else
        ng "INCR 백업 파일 없음"
    fi
}

# ---- 5) Canary 시스템 상태 확인 ----
check_canary_system() {
    banner "5) Canary 시스템 상태 확인"

    if [[ ! -f "$ROOT/tools/canary_guard.py" ]]; then
        ng "canary_guard.py 없음"
        return 1
    fi

    # Canary 시스템 테스트
    local duration=$(measure_performance python3 "$ROOT/tools/canary_guard.py" > /dev/null 2>&1)
    local exit_code=$?

    if [[ $exit_code -eq 0 ]]; then
        ok "Canary 시스템 정상 (${duration}s)"
    else
        ng "Canary 시스템 오류"
        return 1
    fi
}

# ---- 6) 메일 라우팅 테스트 ----
test_mail_routing() {
    banner "6) 메일 라우팅 테스트"

    # msmtp 설정 확인
    if ! command -v msmtp >/dev/null 2>&1; then
        warn "msmtp 명령어 없음 (메일 테스트 스킵)"
        return 0
    fi

    # 간단한 테스트 메일 전송
    local test_subject="[HEALTHCHECK] $(date +%F_%H%M%S)"
    local test_body="DuRi 시스템 안정성 점검 테스트"

    echo "Subject: $test_subject" > /tmp/test_mail.txt
    echo "" >> /tmp/test_mail.txt
    echo "$test_body" >> /tmp/test_mail.txt

    # 테스트 전송 (실제 전송은 하지 않고 설정만 확인)
    if msmtp --serverinfo > /dev/null 2>&1; then
        ok "메일 서버 연결 정상"
    else
        warn "메일 서버 연결 실패"
    fi
}

# ---- 7) 통합 성능 측정 ----
measure_integrated_performance() {
    banner "7) 통합 성능 측정"

    # 전체 시스템 초기화 시간 측정
    local start_time=$(date +%s.%N)

    # 주요 모듈들 로드 테스트
    cd "$ROOT"
    python3 -c "
import sys
sys.path.append('DuRiCore')
try:
    from DuRiCore.DuRiCore.modules.learning_engine import LearningEngine
    engine = LearningEngine()
    print('LearningEngine 로드 성공')
except Exception as e:
    print(f'LearningEngine 로드 실패: {e}')
    sys.exit(1)
" > /dev/null 2>&1

    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l)

    if [[ $? -eq 0 ]]; then
        ok "통합 시스템 로드 성공 (${duration}s)"
        log "통합 시스템 로드 시간: ${duration}초"
    else
        ng "통합 시스템 로드 실패"
        return 1
    fi
}

# ---- 8) 최종 안정성 평가 ----
evaluate_stability() {
    banner "8) 최종 안정성 평가"

    local total_checks=7
    local passed_checks=0
    local failed_checks=0

    # 각 섹션 결과 집계
    if [[ $system_basics_ok -eq 1 ]]; then ((passed_checks++)); else ((failed_checks++)); fi
    if [[ $core_scripts_ok -eq 1 ]]; then ((passed_checks++)); else ((failed_checks++)); fi
    if [[ $learning_engine_ok -eq 1 ]]; then ((passed_checks++)); else ((failed_checks++)); fi
    if [[ $backup_system_ok -eq 1 ]]; then ((passed_checks++)); else ((failed_checks++)); fi
    if [[ $canary_system_ok -eq 1 ]]; then ((passed_checks++)); else ((failed_checks++)); fi
    if [[ $mail_routing_ok -eq 1 ]]; then ((passed_checks++)); else ((failed_checks++)); fi
    if [[ $integrated_performance_ok -eq 1 ]]; then ((passed_checks++)); else ((failed_checks++)); fi

    local stability_score=$(echo "scale=2; $passed_checks / $total_checks" | bc -l)
    local stability_percentage=$(echo "scale=0; $stability_score * 100" | bc -l)

    log "통과한 검사: $passed_checks/$total_checks"
    log "안정성 점수: $stability_score ($stability_percentage%)"

    if [[ $stability_percentage -ge 95 ]]; then
        ok "시스템 안정성 우수: $stability_percentage%"
        echo "🎉 안정성 ≥ 0.95 → 90일 계획 재개 GO!"
        return 0
    elif [[ $stability_percentage -ge 85 ]]; then
        warn "시스템 안정성 양호: $stability_percentage%"
        echo "⚠️ 안정성 0.85-0.94 → 추가 점검 필요"
        return 1
    else
        ng "시스템 안정성 부족: $stability_percentage%"
        echo "❌ 안정성 < 0.85 → 시스템 안정화 필요"
        return 1
    fi
}

# ---- 메인 실행 함수 ----
main() {
    local mode="${1:---full}"

    log "=== DuRi 일요일 시스템 안정성 점검 시작 ==="
    log "모드: $mode, 시간: $(date)"

    # 결과 변수 초기화
    system_basics_ok=0
    core_scripts_ok=0
    learning_engine_ok=0
    backup_system_ok=0
    canary_system_ok=0
    mail_routing_ok=0
    integrated_performance_ok=0

    # 각 섹션 실행 및 결과 저장
    check_system_basics && system_basics_ok=1
    check_core_scripts && core_scripts_ok=1
    test_learning_engine && learning_engine_ok=1
    check_backup_system && backup_system_ok=1
    check_canary_system && canary_system_ok=1
    test_mail_routing && mail_routing_ok=1
    measure_integrated_performance && integrated_performance_ok=1

    # 최종 평가
    evaluate_stability
    local final_result=$?

    log "=== DuRi 일요일 시스템 안정성 점검 완료 ==="
    log "최종 결과: $([ $final_result -eq 0 ] && echo '성공' || echo '실패')"

    return $final_result
}

# 스크립트 실행
main "$@"
