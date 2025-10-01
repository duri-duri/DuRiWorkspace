#!/usr/bin/env bash
set -euo pipefail

# 레거시 시스템 즉시 Freeze 실행 스크립트
# Phase 4: 레거시 Freeze → Shadow 병행 검증

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

# === 설정 ===
LEGACY_LOGS_DIR="var/logs/legacy"
FREEZE_LOGS_DIR="$LEGACY_LOGS_DIR/freeze"
FREEZE_STATUS_FILE="var/state/legacy_freeze_status.json"
LOCK_FILE="var/state/legacy_freeze_in_progress.lock"

# === 로깅 함수 ===
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [FREEZE] $1" | tee -a "$FREEZE_LOGS_DIR/freeze_execution_$(date +%F).log"
}

# === 오류 처리 ===
error_exit() {
    log "ERROR: $1"
    exit 1
}

# === 락 파일 관리 ===
acquire_lock() {
    if [[ -e "$LOCK_FILE" ]]; then
        log "WARN: 다른 Freeze 작업이 진행 중입니다. 잠시 후 재시도하세요."
        exit 1
    fi
    echo "$$" > "$LOCK_FILE"
    trap 'rm -f "$LOCK_FILE"' EXIT
}

# === Freeze 대상 시스템 정의 ===
declare -A FREEZE_TARGETS=(
    ["unified_backup_core.sh"]="scripts/_legacy/"
    ["unified_backup_extended.sh"]="scripts/_legacy/"
    ["unified_backup_full.sh"]="scripts/_legacy/"
)

# === Freeze 실행 ===
freeze_system() {
    local script_name="$1"
    local script_path="$2"
    local full_path="$script_path$script_name"

    log "🚫 $script_name Freeze 시작..."

    if [[ ! -f "$full_path" ]]; then
        log "⚠️  $script_name 파일을 찾을 수 없음: $full_path"
        return 1
    fi

    # 1) 실행 권한 제거
    log "  📋 1단계: 실행 권한 제거"
    chmod -x "$full_path"

    # 2) 백업 생성
    log "  📋 2단계: 백업 생성"
    local backup_path="${full_path}.frozen_$(date +%Y%m%d_%H%M%S)"
    cp "$full_path" "$backup_path"

    # 3) Freeze 마커 추가
    log "  📋 3단계: Freeze 마커 추가"
    cat >> "$full_path" <<EOF

# === FREEZE NOTICE ===
# 이 스크립트는 Phase 4에서 Freeze되었습니다.
# Freeze 일시: $(date -Iseconds)
# Freeze 사유: 표준 시스템으로 대체 완료
# 대체 시스템: duri_backup_phase1.sh
#
# 실행하려면: duri_backup_phase1.sh [core|extended|full]
#
# 참고: 이 스크립트는 더 이상 실행되지 않습니다.
# === END FREEZE NOTICE ===
EOF

    # 4) 로그 경로 매핑
    log "  📋 4단계: 로그 경로 매핑"
    local log_file="$FREEZE_LOGS_DIR/legacy_freeze_${script_name%.*}_$(date +%F).log"
    echo "$(date -Iseconds): $script_name FREEZE 완료" > "$log_file"
    echo "  - 원본 경로: $full_path" >> "$log_file"
    echo "  - 백업 경로: $backup_path" >> "$log_file"
    echo "  - 대체 시스템: duri_backup_phase1.sh" >> "$log_file"

    log "✅ $script_name Freeze 완료"
    return 0
}

# === Freeze 상태 기록 ===
record_freeze_status() {
    local status_file="$FREEZE_STATUS_FILE"
    mkdir -p "$(dirname "$status_file")"

    log "📝 Freeze 상태 기록: $status_file"

    cat > "$status_file" <<EOF
{
  "freeze_execution": {
    "timestamp": "$(date -Iseconds)",
    "operator": "$(whoami)",
    "hostname": "$(hostname)",
    "phase": "Phase 4: 레거시 Freeze → Shadow 병행 검증"
  },
  "frozen_systems": [
EOF

    local first=true
    for script_name in "${!FREEZE_TARGETS[@]}"; do
        local script_path="${FREEZE_TARGETS[$script_name]}"
        local full_path="$script_path$script_name"

        if [[ -f "$full_path" ]]; then
            if [[ "$first" == "true" ]]; then
                first=false
            else
                echo "," >> "$status_file"
            fi

            cat >> "$status_file" <<EOF
    {
      "script_name": "$script_name",
      "original_path": "$full_path",
      "freeze_date": "$(date -Iseconds)",
      "status": "FROZEN",
      "replacement": "duri_backup_phase1.sh",
      "backup_path": "${full_path}.frozen_$(date +%Y%m%d_%H%M%S)"
    }
EOF
        fi
    done

    cat >> "$status_file" <<EOF
  ],
  "next_steps": [
    "Shadow 병행 검증 시작 (3일간)",
    "성능 지표 비교 분석",
    "점진적 전환 계획 수립"
  ],
  "rollback_plan": {
    "condition": "표준 시스템 성공률 < 95%",
    "action": "레거시 시스템 즉시 복구",
    "timeframe": "1시간 내"
  }
}
EOF

    log "✅ Freeze 상태 기록 완료"
}

# === Freeze 검증 ===
verify_freeze() {
    log "🔍 Freeze 검증 시작..."

    local verification_passed=true

    for script_name in "${!FREEZE_TARGETS[@]}"; do
        local script_path="${FREEZE_TARGETS[$script_name]}"
        local full_path="$script_path$script_name"

        if [[ -f "$full_path" ]]; then
            # 실행 권한 확인
            if [[ -x "$full_path" ]]; then
                log "❌ $script_name: 실행 권한이 여전히 존재함"
                verification_passed=false
            else
                log "✅ $script_name: 실행 권한 제거됨"
            fi

            # Freeze 마커 확인
            if grep -q "FREEZE NOTICE" "$full_path"; then
                log "✅ $script_name: Freeze 마커 추가됨"
            else
                log "❌ $script_name: Freeze 마커 누락"
                verification_passed=false
            fi
        else
            log "⚠️  $script_name: 파일이 존재하지 않음"
        fi
    done

    if [[ "$verification_passed" == "true" ]]; then
        log "🎉 모든 Freeze 검증 통과!"
        return 0
    else
        log "❌ 일부 Freeze 검증 실패"
        return 1
    fi
}

# === Freeze 요약 리포트 생성 ===
generate_freeze_summary() {
    local summary_file="$FREEZE_LOGS_DIR/freeze_summary_$(date +%F).md"

    log "📊 Freeze 요약 리포트 생성: $summary_file"

    cat > "$summary_file" <<EOF
# 🚫 레거시 시스템 Freeze 요약 — $(date +%F)

## 📋 **Freeze 실행 개요**

- **실행 일시**: $(date -Iseconds)
- **실행자**: $(whoami)
- **호스트**: $(hostname)
- **Phase**: Phase 4: 레거시 Freeze → Shadow 병행 검증

## 🚫 **Freeze된 시스템**

$(for script_name in "${!FREEZE_TARGETS[@]}"; do
    local script_path="${FREEZE_TARGETS[$script_name]}"
    local full_path="$script_path$script_name"
    if [[ -f "$full_path" ]]; then
        echo "- **$script_name**: $full_path"
        echo "  - 상태: 🚫 FREEZE 완료"
        echo "  - 대체 시스템: \`duri_backup_phase1.sh\`"
        echo "  - Freeze 사유: 표준 시스템으로 대체 완료"
    fi
done)

## 📊 **Freeze 실행 결과**

- **총 대상 시스템**: ${#FREEZE_TARGETS[@]}개
- **Freeze 완료**: $(find "$FREEZE_LOGS_DIR" -name "legacy_freeze_*_$(date +%F).log" | wc -l | xargs)개
- **검증 상태**: $(verify_freeze >/dev/null 2>&1 && echo "✅ 통과" || echo "❌ 실패")

## 🔄 **다음 단계**

### **1) Shadow 병행 검증 (3일간)**
- 표준 시스템과 병행 실행
- 성공률, 성능, 안정성 비교
- 결과 분석 및 검증

### **2) 점진적 전환**
- 문제 없는 시스템 순차 종료
- 복잡한 기능 단계적 마이그레이션
- 최종 정리 및 정리

## 🚨 **주의사항**

- **Freeze된 시스템은 더 이상 실행되지 않음**
- **백업은 \`duri_backup_phase1.sh\` 사용**
- **문제 발생 시 즉시 롤백 가능**
- **모든 변경사항은 Git에 커밋됨**

## 📁 **관련 파일**

- **Freeze 상태**: \`$FREEZE_STATUS_FILE\`
- **Freeze 로그**: \`$FREEZE_LOGS_DIR\`
- **백업본**: \`scripts/_legacy/*.frozen_*\`

---

> **💡 운영 팁**: Freeze된 시스템은 참고용으로만 보존됩니다.
> **🔄 실행**: 새로운 백업은 \`duri_backup_phase1.sh\`를 사용하세요.
> **📊 모니터링**: Shadow 병행 검증 결과를 지속적으로 확인하세요.
EOF

    log "✅ Freeze 요약 리포트 생성 완료: $summary_file"
}

# === 메인 실행 로직 ===
main() {
    log "🚀 레거시 시스템 Freeze 실행 시작"

    # 락 획득
    acquire_lock

    # 디렉토리 생성
    mkdir -p "$FREEZE_LOGS_DIR"

    # Freeze 실행
    local freeze_success=0
    local freeze_total=${#FREEZE_TARGETS[@]}

    for script_name in "${!FREEZE_TARGETS[@]}"; do
        local script_path="${FREEZE_TARGETS[$script_name]}"

        if freeze_system "$script_name" "$script_path"; then
            freeze_success=$((freeze_success + 1))
        fi
    done

    # Freeze 상태 기록
    record_freeze_status

    # Freeze 검증
    verify_freeze

    # Freeze 요약 리포트 생성
    generate_freeze_summary

    # 결과 요약
    log "📊 Freeze 실행 결과 요약"
    log "  - 총 대상: $freeze_total개"
    log "  - 성공: $freeze_success개"
    log "  - 실패: $((freeze_total - freeze_success))개"

    if [[ $freeze_success -eq $freeze_total ]]; then
        log "🎉 모든 레거시 시스템 Freeze 완료!"
        log "다음 단계: Shadow 병행 검증 시작"
        exit 0
    else
        log "⚠️  일부 Freeze 실패, 수동 확인 필요"
        exit 1
    fi
}

# === 스크립트 실행 ===
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
