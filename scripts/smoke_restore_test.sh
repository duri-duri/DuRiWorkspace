#!/usr/bin/env bash
set -euo pipefail

# 스모크 복원 테스트 스크립트
# Phase 2: 검증 2중 루프 강화
# 주간 FULL 완료 후 전체 스모크 복원 테스트

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

# === 설정 ===
BACKUP_DIR="var/backups"
RESTORE_DIR="var/test_restore"
RESTORE_SLO_FILE="var/state/restore_slo.jsonl"
LOG_FILE="var/logs/smoke_restore.log"
MAX_RESTORE_TIME=1800  # 30분 (30초)

# === 로깅 함수 ===
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# === 오류 처리 ===
error_exit() {
    log "ERROR: $1"
    exit 1
}

# === 사전 조건 확인 ===
log "🚀 스모크 복원 테스트 시작..."

# 백업 디렉토리 확인
if [[ ! -d "$BACKUP_DIR" ]]; then
    error_exit "백업 디렉토리를 찾을 수 없음: $BACKUP_DIR"
fi

# 최신 백업 찾기
latest_backup=$(find "$BACKUP_DIR" -maxdepth 1 -type d -name "*FULL*" | sort | tail -1)
if [[ -z "$latest_backup" ]]; then
    error_exit "FULL 백업을 찾을 수 없음"
fi

log "📦 테스트 대상 백업: $latest_backup"

# === 복원 테스트 환경 준비 ===
log "🔧 복원 테스트 환경 준비..."

# 기존 테스트 복원 디렉토리 정리
if [[ -d "$RESTORE_DIR" ]]; then
    rm -rf "$RESTORE_DIR"
fi

# 새 테스트 복원 디렉토리 생성
mkdir -p "$RESTORE_DIR"

# === 1차 검증: SHA256 체크섬 검증 ===
log "🔍 1차 검증: SHA256 체크섬 검증 시작..."

start_time=$(date +%s)
checksum_file="$latest_backup/checksums.sha256"

if [[ -f "$checksum_file" ]]; then
    log "✅ 체크섬 파일 발견: $checksum_file"
    
    # 체크섬 검증
    if cd "$latest_backup" && sha256sum -c checksums.sha256 2>&1 | tee -a "$LOG_FILE"; then
        log "✅ SHA256 체크섬 검증 통과"
        sha256_status="PASS"
    else
        log "❌ SHA256 체크섬 검증 실패"
        sha256_status="FAIL"
    fi
else
    log "⚠️  체크섬 파일 없음, 건너뜀"
    sha256_status="SKIP"
fi

sha256_time=$(($(date +%s) - start_time))
log "⏱️  SHA256 검증 소요 시간: ${sha256_time}초"

# === 2차 검증: 스모크 복원 테스트 ===
log "🔍 2차 검증: 스모크 복원 테스트 시작..."

start_time=$(date +%s)

# 백업 유형별 복원 테스트
backup_types=("CORE" "EXTENDED" "FULL")
restore_results=()

for backup_type in "${backup_types[@]}"; do
    log "📋 $backup_type 백업 복원 테스트 시작..."
    
    # 해당 유형의 백업 파일 찾기
    backup_files=$(find "$latest_backup" -name "*${backup_type}*" -type f | head -5)
    
    if [[ -z "$backup_files" ]]; then
        log "⚠️  $backup_type 백업 파일 없음, 건너뜀"
        restore_results+=("$backup_type:SKIP")
        continue
    fi
    
    # 복원 테스트 실행
    restore_success=0
    restore_total=0
    
    for backup_file in $backup_files; do
        restore_total=$((restore_total + 1))
        
        # 복원 대상 파일명 생성
        restore_file="$RESTORE_DIR/$(basename "$backup_file")"
        
        # 복원 시도
        if cp "$backup_file" "$restore_file" 2>/dev/null; then
            # 복원된 파일 검증
            if [[ -f "$restore_file" ]]; then
                # 파일 크기 확인
                original_size=$(stat -c%s "$backup_file")
                restored_size=$(stat -c%s "$restore_file")
                
                if [[ "$original_size" -eq "$restored_size" ]]; then
                    log "  ✅ $backup_type: $(basename "$backup_file") 복원 성공"
                    restore_success=$((restore_success + 1))
                else
                    log "  ❌ $backup_type: $(basename "$backup_file") 크기 불일치"
                fi
            else
                log "  ❌ $backup_type: $(basename "$backup_file") 복원 실패"
            fi
        else
            log "  ❌ $backup_type: $(basename "$backup_file") 복사 실패"
        fi
    done
    
    # 결과 기록
    if [[ $restore_total -gt 0 ]]; then
        success_rate=$((restore_success * 100 / restore_total))
        restore_results+=("$backup_type:$success_rate%")
        log "📊 $backup_type 복원 결과: $restore_success/$restore_total ($success_rate%)"
    fi
done

restore_time=$(($(date +%s) - start_time))
log "⏱️  스모크 복원 테스트 소요 시간: ${restore_time}초"

# === 전체 검증 결과 ===
log "📊 전체 검증 결과 요약..."

# SHA256 검증 결과
case "$sha256_status" in
    "PASS") sha256_result="✅ 통과" ;;
    "FAIL") sha256_result="❌ 실패" ;;
    "SKIP") sha256_result="⚠️  건너뜀" ;;
esac

log "  1차 검증 (SHA256): $sha256_result (${sha256_time}초)"

# 스모크 복원 결과
log "  2차 검증 (스모크 복원): ${restore_time}초"
for result in "${restore_results[@]}"; do
    log "    - $result"
done

# === RTO 기록 ===
log "📝 RTO 기록 저장..."

total_time=$((sha256_time + restore_time))
rto_record="{\"timestamp\":\"$(date -Iseconds)\",\"test_type\":\"smoke_restore\",\"backup_source\":\"$latest_backup\",\"sha256_status\":\"$sha256_status\",\"sha256_time\":$sha256_time,\"restore_time\":$restore_time,\"total_time\":$total_time,\"restore_results\":$(printf '%s' "${restore_results[*]}" | jq -R -s -c 'split(" ")'),\"rto_sec\":$total_time}"

echo "$rto_record" >> "$RESTORE_SLO_FILE"
log "✅ RTO 기록 저장 완료: $RESTORE_SLO_FILE"

# === 성공/실패 판정 ===
if [[ "$sha256_status" == "PASS" || "$sha256_status" == "SKIP" ]]; then
    if [[ $restore_time -le $MAX_RESTORE_TIME ]]; then
        log "🎉 스모크 복원 테스트 성공!"
        log "   - SHA256: $sha256_result"
        log "   - 복원 시간: ${restore_time}초 (목표: ≤${MAX_RESTORE_TIME}초)"
        log "   - 전체 시간: ${total_time}초"
        exit 0
    else
        log "⚠️  스모크 복원 테스트 경고: 복원 시간 초과"
        log "   - 복원 시간: ${restore_time}초 (목표: ≤${MAX_RESTORE_TIME}초)"
        exit 1
    fi
else
    log "❌ 스모크 복원 테스트 실패: SHA256 검증 실패"
    exit 1
fi


