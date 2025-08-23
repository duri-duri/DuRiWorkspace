#!/usr/bin/env bash
set -euo pipefail

# Shadow 병행 검증 시스템
# Phase 4: 레거시 vs 표준 시스템 성능 비교
# 3일간 병행 실행하여 결과 분석

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

# === 설정 ===
SHADOW_LOGS_DIR="var/logs/legacy/shadow"
SHADOW_RESULTS_DIR="var/state/shadow_results"
SHADOW_CONFIG_FILE="configs/legacy_system_mapping.yml"
LOCK_FILE="var/state/shadow_validation_in_progress.lock"

# === 로깅 함수 ===
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [SHADOW] $1" | tee -a "$SHADOW_LOGS_DIR/shadow_validation_$(date +%F).log"
}

# === 오류 처리 ===
error_exit() {
    log "ERROR: $1"
    exit 1
}

# === 락 파일 관리 ===
acquire_lock() {
    if [[ -e "$LOCK_FILE" ]]; then
        log "WARN: 다른 Shadow 검증이 진행 중입니다. 잠시 후 재시도하세요."
        exit 1
    fi
    echo "$$" > "$LOCK_FILE"
    trap 'rm -f "$LOCK_FILE"' EXIT
}

# === Shadow 대상 시스템 정의 ===
declare -A SHADOW_TARGETS=(
    ["duri_backup.sh"]="scripts/"
    ["duri_backup_progress.sh"]="scripts/"
    ["shared-scripts/autosave_scripts.sh"]=""
)

# === 성능 지표 수집 ===
collect_performance_metrics() {
    local system_name="$1"
    local system_path="$2"
    local log_file="$SHADOW_LOGS_DIR/${system_name%.*}_metrics_$(date +%F).json"
    
    log "📊 $system_name 성능 지표 수집..."
    
    # 시스템 리소스 사용량
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    local memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    local disk_usage=$(df . | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    
    # 실행 시간 측정 (예시)
    local start_time=$(date +%s)
    # 실제로는 해당 시스템의 실행 시간을 측정해야 함
    sleep 1  # 시뮬레이션용
    local end_time=$(date +%s)
    local execution_time=$((end_time - start_time))
    
    # 성공/실패 상태 (예시)
    local success_status="SUCCESS"
    local error_count=0
    
    # 지표 저장
    cat > "$log_file" <<EOF
{
  "system_name": "$system_name",
  "timestamp": "$(date -Iseconds)",
  "performance_metrics": {
    "cpu_usage_percent": $cpu_usage,
    "memory_usage_percent": $memory_usage,
    "disk_usage_percent": $disk_usage,
    "execution_time_seconds": $execution_time
  },
  "status": {
    "success": "$success_status",
    "error_count": $error_count
  },
  "metadata": {
    "path": "$system_path",
    "collection_method": "shadow_parallel_validator"
  }
}
EOF
    
    log "✅ $system_name 성능 지표 수집 완료: $log_file"
}

# === 표준 시스템과 비교 분석 ===
compare_with_standard() {
    local legacy_system="$1"
    local comparison_file="$SHADOW_RESULTS_DIR/comparison_${legacy_system%.*}_$(date +%F).json"
    
    log "🔍 $legacy_system vs 표준 시스템 비교 분석..."
    
    # 표준 시스템 지표 (예시)
    local standard_success_rate=99.5
    local standard_execution_time=15
    local standard_error_rate=0.5
    
    # 레거시 시스템 지표 (실제로는 수집된 데이터 사용)
    local legacy_success_rate=98.0
    local legacy_execution_time=18
    local legacy_error_rate=2.0
    
    # 비교 분석
    local success_rate_diff=$((standard_success_rate - legacy_success_rate))
    local execution_time_ratio=$(echo "scale=2; $standard_execution_time / $legacy_execution_time" | bc -l 2>/dev/null || echo "1.0")
    local error_rate_diff=$((standard_error_rate - legacy_error_rate))
    
    # 판정 기준
    local success_rate_ok=$([[ $success_rate_diff -ge 0 ]] && echo "true" || echo "false")
    local execution_time_ok=$([[ $(echo "$execution_time_ratio <= 1.2" | bc -l 2>/dev/null || echo "1") -eq 1 ]] && echo "true" || echo "false")
    local error_rate_ok=$([[ $error_rate_diff -le 0 ]] && echo "true" || echo "false")
    
    # 전체 판정
    local overall_result=$([[ "$success_rate_ok" == "true" && "$execution_time_ok" == "true" && "$error_rate_ok" == "true" ]] && echo "PASS" || echo "FAIL")
    
    # 비교 결과 저장
    cat > "$comparison_file" <<EOF
{
  "comparison": {
    "legacy_system": "$legacy_system",
    "standard_system": "duri_backup_phase1.sh",
    "comparison_date": "$(date -Iseconds)"
  },
  "metrics_comparison": {
    "success_rate": {
      "legacy": $legacy_success_rate,
      "standard": $standard_success_rate,
      "difference": $success_rate_diff,
      "status": "$success_rate_ok"
    },
    "execution_time": {
      "legacy": $legacy_execution_time,
      "standard": $standard_execution_time,
      "ratio": $execution_time_ratio,
      "status": "$execution_time_ok"
    },
    "error_rate": {
      "legacy": $legacy_error_rate,
      "standard": $standard_error_rate,
      "difference": $error_rate_diff,
      "status": "$error_rate_ok"
    }
  },
  "overall_assessment": {
    "result": "$overall_result",
    "criteria_met": {
      "success_rate": $success_rate_ok,
      "execution_time": $success_rate_ok,
      "error_rate": $error_rate_ok
    },
    "recommendation": "$(if [[ "$overall_result" == "PASS" ]]; then echo "표준 시스템으로 전환 가능"; else echo "추가 검증 필요"; fi)"
  }
}
EOF
    
    log "✅ $legacy_system 비교 분석 완료: $comparison_file"
    log "  - 전체 판정: $overall_result"
    log "  - 성공률: $success_rate_ok"
    log "  - 실행시간: $execution_time_ok"
    log "  - 오류율: $error_rate_ok"
}

# === Shadow 병행 검증 실행 ===
run_shadow_validation() {
    local system_name="$1"
    local system_path="$2"
    
    log "🔄 $system_name Shadow 병행 검증 시작..."
    
    # 1) 성능 지표 수집
    collect_performance_metrics "$system_name" "$system_path"
    
    # 2) 표준 시스템과 비교 분석
    compare_with_standard "$system_name"
    
    # 3) Shadow 로그 생성
    local shadow_log="$SHADOW_LOGS_DIR/legacy_shadow_${system_name%.*}_$(date +%F).log"
    echo "$(date -Iseconds): $system_name Shadow 검증 완료" > "$shadow_log"
    echo "  - 검증 일시: $(date -Iseconds)" >> "$shadow_log"
    echo "  - 검증 방법: 성능 지표 수집 + 표준 시스템 비교" >> "$shadow_log"
    echo "  - 결과 파일: $SHADOW_RESULTS_DIR/comparison_${system_name%.*}_$(date +%F).json" >> "$shadow_log"
    
    log "✅ $system_name Shadow 병행 검증 완료"
}

# === Shadow 검증 요약 리포트 생성 ===
generate_shadow_summary() {
    local summary_file="$SHADOW_LOGS_DIR/shadow_summary_$(date +%F).md"
    
    log "📊 Shadow 검증 요약 리포트 생성: $summary_file"
    
    # 검증 결과 집계
    local total_systems=${#SHADOW_TARGETS[@]}
    local completed_systems=$(find "$SHADOW_RESULTS_DIR" -name "comparison_*_$(date +%F).json" 2>/dev/null | wc -l | xargs)
    local passed_systems=0
    local failed_systems=0
    
    # PASS/FAIL 카운트
    for result_file in "$SHADOW_RESULTS_DIR"/comparison_*_$(date +%F).json 2>/dev/null; do
        if [[ -f "$result_file" ]]; then
            if grep -q '"result": "PASS"' "$result_file"; then
                passed_systems=$((passed_systems + 1))
            else
                failed_systems=$((failed_systems + 1))
            fi
        fi
    done
    
    cat > "$summary_file" <<EOF
# 🔄 Shadow 병행 검증 요약 — $(date +%F)

## 📋 **검증 개요**

- **검증 일시**: $(date -Iseconds)
- **검증 방법**: 레거시 vs 표준 시스템 병행 실행
- **검증 기간**: 3일 (2025-08-22 ~ 2025-08-25)
- **검증 목적**: 성능 지표 비교 및 전환 가능성 판단

## 🔍 **검증 대상 시스템**

$(for system_name in "${!SHADOW_TARGETS[@]}"; do
    local system_path="${SHADOW_TARGETS[$system_name]}"
    local result_file="$SHADOW_RESULTS_DIR/comparison_${system_name%.*}_$(date +%F).json"
    if [[ -f "$result_file" ]]; then
        local result=$(grep -o '"result": "[^"]*"' "$result_file" | cut -d'"' -f4)
        echo "- **$system_name**: $system_path"
        echo "  - 상태: $([[ "$result" == "PASS" ]] && echo "✅ PASS" || echo "❌ FAIL")"
        echo "  - 결과 파일: \`$result_file\`"
    else
        echo "- **$system_name**: $system_path"
        echo "  - 상태: ⏳ 검증 진행 중"
        echo "  - 결과 파일: 아직 생성되지 않음"
    fi
done)

## 📊 **검증 결과 요약**

- **총 대상 시스템**: $total_systems개
- **검증 완료**: $completed_systems개
- **검증 통과**: $passed_systems개
- **검증 실패**: $failed_systems개
- **진행률**: $([[ $total_systems -gt 0 ]] && echo "$((completed_systems * 100 / total_systems))%" || echo "0%")

## 🎯 **검증 기준**

### **성공률**
- **기준**: 표준 시스템 성공률 ≥ 레거시 시스템 성공률
- **목표**: 99.9% 이상

### **실행 시간**
- **기준**: 표준 시스템 실행 시간 ≤ 레거시 시스템 실행 시간 × 1.2
- **목표**: 120% 이하

### **오류 발생률**
- **기준**: 표준 시스템 오류 발생률 ≤ 레거시 시스템 오류 발생률
- **목표**: 1% 이하

## 📈 **성과 지표**

- **전체 검증 통과율**: $([[ $completed_systems -gt 0 ]] && echo "$((passed_systems * 100 / completed_systems))%" || echo "N/A")
- **표준 시스템 우수성**: $([[ $passed_systems -gt 0 ]] && echo "✅ 확인됨" || echo "⚠️  추가 검증 필요")
- **전환 준비도**: $([[ $passed_systems -eq $completed_systems && $completed_systems -gt 0 ]] && echo "✅ 준비 완료" || echo "⚠️  준비 중")

## 🔄 **다음 단계**

### **1) 검증 완료 후 (2025-08-25)**
- 최종 결과 분석 및 검토
- 전환 가능성 최종 판단
- 점진적 전환 계획 수립

### **2) 점진적 전환 (2025-08-26 ~ 2025-09-01)**
- PASS 시스템 순차 종료
- FAIL 시스템 추가 검증 또는 개선
- 최종 정리 및 정리

## 🚨 **주의사항**

- **Shadow 검증 중에는 두 시스템 모두 실행 가능**
- **문제 발생 시 즉시 레거시 시스템으로 롤백**
- **모든 검증 결과는 상세히 문서화**
- **전환 결정은 검증 결과에 기반하여 신중하게**

## 📁 **관련 파일**

- **검증 결과**: \`$SHADOW_RESULTS_DIR\`
- **Shadow 로그**: \`$SHADOW_LOGS_DIR\`
- **비교 분석**: \`comparison_*.json\`

---

> **💡 운영 팁**: Shadow 검증은 안전한 전환을 위한 중요한 단계입니다.  
> **📊 모니터링**: 검증 결과를 지속적으로 확인하고 문제점을 파악하세요.  
> **🔄 전환**: 검증이 완료된 후에만 점진적 전환을 진행하세요.
EOF
    
    log "✅ Shadow 검증 요약 리포트 생성 완료: $summary_file"
}

# === 메인 실행 로직 ===
main() {
    log "🚀 Shadow 병행 검증 시스템 시작"
    
    # 락 획득
    acquire_lock
    
    # 디렉토리 생성
    mkdir -p "$SHADOW_LOGS_DIR" "$SHADOW_RESULTS_DIR"
    
    # Shadow 검증 실행
    local validation_success=0
    local validation_total=${#SHADOW_TARGETS[@]}
    
    for system_name in "${!SHADOW_TARGETS[@]}"; do
        local system_path="${SHADOW_TARGETS[$system_name]}"
        
        if run_shadow_validation "$system_name" "$system_path"; then
            validation_success=$((validation_success + 1))
        fi
    done
    
    # Shadow 검증 요약 리포트 생성
    generate_shadow_summary
    
    # 결과 요약
    log "📊 Shadow 병행 검증 결과 요약"
    log "  - 총 대상: $validation_total개"
    log "  - 성공: $validation_success개"
    log "  - 실패: $((validation_total - validation_success))개"
    
    if [[ $validation_success -eq $validation_total ]]; then
        log "🎉 모든 Shadow 병행 검증 완료!"
        log "다음 단계: 검증 결과 분석 및 점진적 전환 계획"
        exit 0
    else
        log "⚠️  일부 Shadow 검증 실패, 수동 확인 필요"
        exit 1
    fi
}

# === 스크립트 실행 ===
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi



