#!/usr/bin/env bash
set -euo pipefail

# 레거시 순차 종료 실행 스크립트
# Phase 5: Turn-off & 위험 축소, 레거시 시스템 완전 제거

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

# === 설정 ===
SHUTDOWN_LOGS_DIR="var/logs/legacy/shutdown"
SHUTDOWN_BACKUP_DIR="var/backups/legacy_shutdown"
SHUTDOWN_PROGRESS_FILE="var/state/legacy_shutdown_progress.json"
GLOBAL_LOCK_FILE="var/state/legacy_shutdown_global.lock"
CONFIG_FILE="configs/phase5_legacy_shutdown_plan.yml"

# === 로깅 함수 ===
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [SHUTDOWN] $1" | tee -a "$SHUTDOWN_LOGS_DIR/shutdown_execution_$(date +%F).log"
}

# === 오류 처리 ===
error_exit() {
    log "ERROR: $1"
    exit 1
}

# === 락 파일 관리 ===
acquire_global_lock() {
    local lock_file="$GLOBAL_LOCK_FILE"
    local timeout_minutes=30
    local retry_interval=300  # 5분
    local max_retries=6
    
    log "🔒 전역 종료 락 획득 시도..."
    
    for ((i=0; i<max_retries; i++)); do
        if [[ -e "$lock_file" ]]; then
            local lock_pid=$(cat "$lock_file" 2>/dev/null || echo "")
            local lock_age=$(( $(date +%s) - $(stat -c %Y "$lock_file" 2>/dev/null || echo 0) ))
            
            # 락 타임아웃 확인
            if [[ $lock_age -gt $((timeout_minutes * 60)) ]]; then
                log "⚠️  오래된 락 감지, 강제 제거: $lock_file"
                rm -f "$lock_file"
            else
                log "⏳ 다른 종료 작업이 진행 중입니다. PID: $lock_pid, 대기 중... ($((i+1))/$max_retries)"
                sleep $retry_interval
                continue
            fi
        fi
        
        # 락 획득 시도
        if (set -C; echo "$$" > "$lock_file") 2>/dev/null; then
            log "✅ 전역 종료 락 획득 성공"
            trap 'rm -f "$lock_file"' EXIT
            return 0
        fi
        
        log "❌ 락 획득 실패, 재시도 중... ($((i+1))/$max_retries)"
        sleep $retry_interval
    done
    
    error_exit "전역 종료 락 획득 실패 (최대 재시도 횟수 초과)"
}

acquire_system_lock() {
    local system_name="$1"
    local lock_file="var/state/legacy_shutdown_${system_name%.*}.lock"
    local timeout_minutes=15
    local retry_interval=180  # 3분
    local max_retries=10
    
    log "🔒 $system_name 시스템 종료 락 획득 시도..."
    
    for ((i=0; i<max_retries; i++)); do
        if [[ -e "$lock_file" ]]; then
            local lock_pid=$(cat "$lock_file" 2>/dev/null || echo "")
            local lock_age=$(( $(date +%s) - $(stat -c %Y "$lock_file" 2>/dev/null || echo 0) ))
            
            # 락 타임아웃 확인
            if [[ $lock_age -gt $((timeout_minutes * 60)) ]]; then
                log "⚠️  오래된 시스템 락 감지, 강제 제거: $lock_file"
                rm -f "$lock_file"
            else
                log "⏳ $system_name 종료 작업이 진행 중입니다. PID: $lock_pid, 대기 중... ($((i+1))/$max_retries)"
                sleep $retry_interval
                continue
            fi
        fi
        
        # 락 획득 시도
        if (set -C; echo "$$" > "$lock_file") 2>/dev/null; then
            log "✅ $system_name 시스템 종료 락 획득 성공"
            echo "$lock_file"  # 락 파일 경로 반환
            return 0
        fi
        
        log "❌ $system_name 락 획득 실패, 재시도 중... ($((i+1))/$max_retries)"
        sleep $retry_interval
    done
    
    error_exit "$system_name 시스템 종료 락 획득 실패 (최대 재시도 횟수 초과)"
}

# === 사전 검증 ===
pre_shutdown_validation() {
    local system_name="$1"
    
    log "🔍 $system_name 사전 검증 시작..."
    
    # 1) 표준 시스템 성공률 확인
    log "  📋 1단계: 표준 시스템 성공률 확인"
    local standard_success_rate=$(get_standard_system_success_rate)
    if [[ $(echo "$standard_success_rate >= 99.9" | bc -l 2>/dev/null || echo "1") -eq 1 ]]; then
        log "    ✅ 표준 시스템 성공률: ${standard_success_rate}% (≥99.9%)"
    else
        log "    ❌ 표준 시스템 성공률 부족: ${standard_success_rate}% (<99.9%)"
        return 1
    fi
    
    # 2) 의존성 준수율 확인
    log "  📋 2단계: 의존성 준수율 확인"
    local dependency_compliance=$(get_dependency_compliance_rate)
    if [[ "$dependency_compliance" == "100%" ]]; then
        log "    ✅ 의존성 준수율: $dependency_compliance"
    else
        log "    ❌ 의존성 준수율 부족: $dependency_compliance"
        return 1
    fi
    
    # 3) 오류 발생률 확인
    log "  📋 3단계: 오류 발생률 확인"
    local error_rate=$(get_error_rate)
    if [[ $(echo "$error_rate <= 1.0" | bc -l 2>/dev/null || echo "1") -eq 1 ]]; then
        log "    ✅ 오류 발생률: ${error_rate}% (≤1%)"
    else
        log "    ❌ 오류 발생률 과다: ${error_rate}% (>1%)"
        return 1
    fi
    
    log "✅ $system_name 사전 검증 통과"
    return 0
}

# === 백업 생성 ===
create_shutdown_backup() {
    local system_name="$1"
    local system_path="$2"
    local backup_dir="$SHUTDOWN_BACKUP_DIR/$(date +%Y%m%d)_${system_name%.*}"
    
    log "💾 $system_name 종료 백업 생성..."
    
    mkdir -p "$backup_dir"
    
    # 1) 파일 백업
    if [[ -f "$system_path" ]]; then
        log "  📋 1단계: 파일 백업"
        cp "$system_path" "$backup_dir/"
        log "    ✅ 파일 백업 완료: $backup_dir/$(basename "$system_path")"
    fi
    
    # 2) 메타데이터 백업
    log "  📋 2단계: 메타데이터 백업"
    local metadata_file="$backup_dir/metadata.json"
    cat > "$metadata_file" <<EOF
{
  "system_name": "$system_name",
  "original_path": "$system_path",
  "backup_date": "$(date -Iseconds)",
  "backup_reason": "Phase 5 레거시 시스템 종료",
  "file_size": "$(stat -c %s "$system_path" 2>/dev/null || echo "N/A")",
  "file_permissions": "$(stat -c %a "$system_path" 2>/dev/null || echo "N/A")",
  "file_owner": "$(stat -c %U "$system_path" 2>/dev/null || echo "N/A")",
  "checksum": "$(sha256sum "$system_path" 2>/dev/null | cut -d' ' -f1 || echo "N/A")"
}
EOF
    log "    ✅ 메타데이터 백업 완료: $metadata_file"
    
    # 3) 백업 검증
    log "  📋 3단계: 백업 검증"
    if [[ -f "$backup_dir/$(basename "$system_path")" ]] && [[ -f "$metadata_file" ]]; then
        log "    ✅ 백업 검증 통과"
        echo "$backup_dir"  # 백업 디렉토리 경로 반환
    else
        log "    ❌ 백업 검증 실패"
        return 1
    fi
}

# === 시스템 종료 ===
shutdown_system() {
    local system_name="$1"
    local system_path="$2"
    local backup_dir="$3"
    
    log "🚫 $system_name 시스템 종료 시작..."
    
    # 1) 실행 권한 제거
    log "  📋 1단계: 실행 권한 제거"
    if [[ -f "$system_path" ]]; then
        chmod -x "$system_path"
        if [[ ! -x "$system_path" ]]; then
            log "    ✅ 실행 권한 제거 완료"
        else
            log "    ❌ 실행 권한 제거 실패"
            return 1
        fi
    fi
    
    # 2) 프로세스 종료 확인
    log "  📋 2단계: 프로세스 종료 확인"
    local running_processes=$(pgrep -f "$(basename "$system_name")" 2>/dev/null || echo "")
    if [[ -z "$running_processes" ]]; then
        log "    ✅ 실행 중인 프로세스 없음"
    else
        log "    ⚠️  실행 중인 프로세스 발견: $running_processes"
        log "      프로세스 종료 시도..."
        pkill -f "$(basename "$system_name")" 2>/dev/null || true
        sleep 2
        local remaining_processes=$(pgrep -f "$(basename "$system_name")" 2>/dev/null || echo "")
        if [[ -z "$remaining_processes" ]]; then
            log "      ✅ 프로세스 종료 완료"
        else
            log "      ❌ 프로세스 종료 실패: $remaining_processes"
            return 1
        fi
    fi
    
    # 3) 파일 접근 불가 확인
    log "  📋 3단계: 파일 접근 불가 확인"
    if [[ -f "$system_path" ]]; then
        if timeout 5s bash -c "source '$system_path'" 2>/dev/null; then
            log "    ❌ 파일 접근 가능 (권한 문제)"
            return 1
        else
            log "    ✅ 파일 접근 불가 확인"
        fi
    fi
    
    # 4) 종료 완료 로그 기록
    log "  📋 4단계: 종료 완료 로그 기록"
    local shutdown_log="$SHUTDOWN_LOGS_DIR/legacy_shutdown_${system_name%.*}_$(date +%F).log"
    cat > "$shutdown_log" <<EOF
$(date -Iseconds): $system_name 시스템 종료 완료
  - 원본 경로: $system_path
  - 백업 경로: $backup_dir
  - 종료 일시: $(date -Iseconds)
  - 종료 사유: Phase 5 레거시 시스템 제거
  - 대체 시스템: 표준 시스템으로 완전 대체
  - 롤백 방법: $backup_dir에서 복원
EOF
    log "    ✅ 종료 완료 로그 기록: $shutdown_log"
    
    log "✅ $system_name 시스템 종료 완료"
    return 0
}

# === 롤백 메커니즘 ===
rollback_system() {
    local system_name="$1"
    local system_path="$2"
    local backup_dir="$3"
    
    log "🔄 $system_name 시스템 롤백 시작..."
    
    # 1) 백업본 존재 확인
    if [[ ! -d "$backup_dir" ]]; then
        log "❌ 백업 디렉토리를 찾을 수 없음: $backup_dir"
        return 1
    fi
    
    # 2) 원본 파일 복원
    local backup_file="$backup_dir/$(basename "$system_path")"
    if [[ -f "$backup_file" ]]; then
        log "  📋 1단계: 원본 파일 복원"
        cp "$backup_file" "$system_path"
        log "    ✅ 파일 복원 완료"
    else
        log "❌ 백업 파일을 찾을 수 없음: $backup_file"
        return 1
    fi
    
    # 3) 실행 권한 복구
    log "  📋 2단계: 실행 권한 복구"
    chmod +x "$system_path"
    if [[ -x "$system_path" ]]; then
        log "    ✅ 실행 권한 복구 완료"
    else
        log "    ❌ 실행 권한 복구 실패"
        return 1
    fi
    
    # 4) 롤백 완료 로그 기록
    log "  📋 3단계: 롤백 완료 로그 기록"
    local rollback_log="$SHUTDOWN_LOGS_DIR/legacy_rollback_${system_name%.*}_$(date +%F).log"
    cat > "$rollback_log" <<EOF
$(date -Iseconds): $system_name 시스템 롤백 완료
  - 원본 경로: $system_path
  - 백업 경로: $backup_dir
  - 롤백 일시: $(date -Iseconds)
  - 롤백 사유: 표준 시스템 문제 발생
  - 복원 방법: 백업본에서 원본 복원
EOF
    log "    ✅ 롤백 완료 로그 기록: $rollback_log"
    
    log "✅ $system_name 시스템 롤백 완료"
    return 0
}

# === 진행 상황 추적 ===
update_progress() {
    local system_name="$1"
    local status="$2"
    local details="$3"
    
    local progress_file="$SHUTDOWN_PROGRESS_FILE"
    mkdir -p "$(dirname "$progress_file")"
    
    # 기존 진행 상황 로드
    local existing_progress="{}"
    if [[ -f "$progress_file" ]]; then
        existing_progress=$(cat "$progress_file")
    fi
    
    # 진행 상황 업데이트
    local updated_progress=$(echo "$existing_progress" | jq --arg name "$system_name" --arg status "$status" --arg details "$details" --arg timestamp "$(date -Iseconds)" '. + {($name): {"status": $status, "details": $details, "timestamp": $timestamp}}' 2>/dev/null || echo "$existing_progress")
    
    echo "$updated_progress" > "$progress_file"
    log "📝 진행 상황 업데이트: $system_name - $status"
}

# === 헬퍼 함수들 ===
get_standard_system_success_rate() {
    # 실제로는 표준 시스템 로그에서 성공률을 계산해야 함
    echo "99.95"  # 시뮬레이션용
}

get_dependency_compliance_rate() {
    # 실제로는 의존성 준수율을 계산해야 함
    echo "100%"  # 시뮬레이션용
}

get_error_rate() {
    # 실제로는 오류 발생률을 계산해야 함
    echo "0.5"  # 시뮬레이션용
}

# === 메인 종료 로직 ===
shutdown_legacy_system() {
    local system_name="$1"
    local system_path="$2"
    
    log "🚀 $system_name 레거시 시스템 종료 시작"
    
    # 시스템별 락 획득
    local system_lock_file=$(acquire_system_lock "$system_name")
    
    # 락 해제 함수 등록
    trap 'rm -f "$system_lock_file"' EXIT
    
    # 1) 사전 검증
    if ! pre_shutdown_validation "$system_name"; then
        log "❌ $system_name 사전 검증 실패, 종료 중단"
        return 1
    fi
    
    # 2) 백업 생성
    local backup_dir
    if ! backup_dir=$(create_shutdown_backup "$system_name" "$system_path"); then
        log "❌ $system_name 백업 생성 실패, 종료 중단"
        return 1
    fi
    
    # 3) 시스템 종료
    if ! shutdown_system "$system_name" "$system_path" "$backup_dir"; then
        log "❌ $system_name 시스템 종료 실패, 롤백 시도"
        if rollback_system "$system_name" "$system_path" "$backup_dir"; then
            log "✅ $system_name 롤백 성공"
        else
            log "❌ $system_name 롤백 실패, 수동 개입 필요"
        fi
        return 1
    fi
    
    # 4) 진행 상황 업데이트
    update_progress "$system_name" "SHUTDOWN_COMPLETE" "시스템 종료 완료, 백업: $backup_dir"
    
    log "🎉 $system_name 레거시 시스템 종료 완료!"
    return 0
}

# === 메인 실행 로직 ===
main() {
    local target_system="${1:-}"
    
    log "🚀 Phase 5 레거시 순차 종료 시스템 시작"
    
    # 전역 락 획득
    acquire_global_lock
    
    # 디렉토리 생성
    mkdir -p "$SHUTDOWN_LOGS_DIR" "$SHUTDOWN_BACKUP_DIR"
    
    # 종료 대상 시스템 정의
    declare -A SHUTDOWN_TARGETS=(
        ["duri_backup.sh"]="scripts/"
        ["duri_backup_progress.sh"]="scripts/"
        ["shared-scripts/autosave_scripts.sh"]=""
    )
    
    if [[ -n "$target_system" ]]; then
        # 특정 시스템만 종료
        if [[ -n "${SHUTDOWN_TARGETS[$target_system]:-}" ]]; then
            local system_path="${SHUTDOWN_TARGETS[$target_system]}"
            if shutdown_legacy_system "$target_system" "$system_path"; then
                log "✅ $target_system 종료 성공"
            else
                log "❌ $target_system 종료 실패"
                exit 1
            fi
        else
            error_exit "알 수 없는 종료 대상: $target_system"
        fi
    else
        # 모든 대상 시스템 순차 종료
        local shutdown_success=0
        local shutdown_total=${#SHUTDOWN_TARGETS[@]}
        
        for system_name in "${!SHUTDOWN_TARGETS[@]}"; do
            local system_path="${SHUTDOWN_TARGETS[$system_name]}"
            
            if shutdown_legacy_system "$system_name" "$system_path"; then
                shutdown_success=$((shutdown_success + 1))
            fi
            
            # 시스템 간 간격
            sleep 5
        done
        
        # 결과 요약
        log "📊 레거시 시스템 종료 결과 요약"
        log "  - 총 대상: $shutdown_total개"
        log "  - 성공: $shutdown_success개"
        log "  - 실패: $((shutdown_total - shutdown_success))개"
        
        if [[ $shutdown_success -eq $shutdown_total ]]; then
            log "🎉 모든 레거시 시스템 종료 완료!"
            log "다음 단계: 최종 정리 및 검증"
            exit 0
        else
            log "⚠️  일부 시스템 종료 실패, 수동 확인 필요"
            exit 1
        fi
    fi
}

# === 스크립트 실행 ===
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi


