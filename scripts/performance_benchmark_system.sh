#!/usr/bin/env bash
set -euo pipefail

# 성능 벤치마킹 시스템
# Phase 6: 성능 최적화 + 안정성 강화 + 운영 효율화

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

# === 설정 ===
BENCHMARK_LOGS_DIR="var/logs/performance/benchmark"
BENCHMARK_RESULTS_DIR="var/state/performance_benchmark"
BENCHMARK_CONFIG_FILE="configs/phase6_performance_optimization_plan.yml"
LOCK_FILE="var/state/performance_benchmark_in_progress.lock"

# === 로깅 함수 ===
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [BENCHMARK] $1" | tee -a "$BENCHMARK_LOGS_DIR/benchmark_execution_$(date +%F).log"
}

# === 오류 처리 ===
error_exit() {
    log "ERROR: $1"
    exit 1
}

# === 락 파일 관리 ===
acquire_lock() {
    if [[ -e "$LOCK_FILE" ]]; then
        log "WARN: 다른 벤치마크가 진행 중입니다. 잠시 후 재시도하세요."
        exit 1
    fi
    echo "$$" > "$LOCK_FILE"
    trap 'rm -f "$LOCK_FILE"' EXIT
}

# === 백업 성능 벤치마크 ===
benchmark_backup_performance() {
    local benchmark_name="backup_performance"
    local result_file="$BENCHMARK_RESULTS_DIR/${benchmark_name}_$(date +%F).json"

    log "📊 백업 성능 벤치마크 시작..."

    # 1) 백업 속도 측정
    log "  📋 1단계: 백업 속도 측정"
    local backup_start_time=$(date +%s)

    # 테스트 백업 실행 (var/reports 폴더)
    if [[ -d "var/reports" ]]; then
        local test_backup_dir="var/test_backup_benchmark_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$test_backup_dir"

        # rsync를 사용한 백업 속도 측정
        local rsync_start=$(date +%s.%N)
        rsync -av --stats "var/reports/" "$test_backup_dir/" >/dev/null 2>&1
        local rsync_end=$(date +%s.%N)
        local rsync_duration=$(echo "$rsync_end - $rsync_start" | bc -l 2>/dev/null || echo "0")

        # 백업 크기 측정
        local backup_size=$(du -sb "$test_backup_dir" 2>/dev/null | cut -f1 || echo "0")
        local source_size=$(du -sb "var/reports" 2>/dev/null | cut -f1 || echo "0")

        # 압축률 계산
        local compression_ratio=0
        if [[ $source_size -gt 0 ]]; then
            compression_ratio=$(echo "scale=2; (1 - $backup_size / $source_size) * 100" | bc -l 2>/dev/null || echo "0")
        fi

        # 정리
        rm -rf "$test_backup_dir"

        log "    ✅ 백업 속도: ${rsync_duration}초"
        log "    ✅ 백업 크기: ${backup_size}바이트"
        log "    ✅ 압축률: ${compression_ratio}%"
    else
        log "    ⚠️  var/reports 폴더가 존재하지 않음"
        local rsync_duration=0
        local backup_size=0
        local compression_ratio=0
    fi

    local backup_end_time=$(date +%s)
    local backup_duration=$((backup_end_time - backup_start_time))

    # 2) 리소스 사용량 측정
    log "  📋 2단계: 리소스 사용량 측정"
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    local memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    local disk_io=$(iostat -x 1 1 2>/dev/null | tail -1 | awk '{print $6}' || echo "0")

    # 3) 결과 저장
    cat > "$result_file" <<EOF
{
  "benchmark": {
    "name": "$benchmark_name",
    "timestamp": "$(date -Iseconds)",
    "duration_seconds": $backup_duration
  },
  "backup_performance": {
    "backup_speed_seconds": $rsync_duration,
    "backup_size_bytes": $backup_size,
    "compression_ratio_percent": $compression_ratio,
    "source_size_bytes": $source_size
  },
  "resource_usage": {
    "cpu_usage_percent": $cpu_usage,
    "memory_usage_percent": $memory_usage,
    "disk_io_tps": $disk_io
  },
  "targets": {
    "backup_speed_improvement": "≥20% 향상",
    "backup_size_reduction": "≥15% 감소",
    "resource_usage_limit": "CPU ≤80%, 메모리 ≤70%"
  },
  "analysis": {
    "backup_speed_status": "$(if [[ $(echo "$rsync_duration < 10" | bc -l 2>/dev/null || echo "1") -eq 1 ]]; then echo "GOOD"; else echo "NEEDS_IMPROVEMENT"; fi)",
    "backup_size_status": "$(if [[ $(echo "$compression_ratio > 15" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then echo "GOOD"; else echo "NEEDS_IMPROVEMENT"; fi)",
    "resource_usage_status": "$(if [[ $(echo "$cpu_usage < 80" | bc -l 2>/dev/null || echo "0") -eq 1 && $(echo "$memory_usage < 70" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then echo "GOOD"; else echo "NEEDS_IMPROVEMENT"; fi)"
  }
}
EOF

    log "✅ 백업 성능 벤치마크 완료: $result_file"
    return 0
}

# === 로그 시스템 성능 벤치마크 ===
benchmark_logging_performance() {
    local benchmark_name="logging_performance"
    local result_file="$BENCHMARK_RESULTS_DIR/${benchmark_name}_$(date +%F).json"

    log "📊 로그 시스템 성능 벤치마크 시작..."

    # 1) 로그 쓰기 속도 측정
    log "  📋 1단계: 로그 쓰기 속도 측정"
    local log_file="$BENCHMARK_LOGS_DIR/write_test_$(date +%Y%m%d_%H%M%S).log"
    local write_start=$(date +%s.%N)

    # 대량 로그 쓰기 테스트
    for i in {1..1000}; do
        echo "$(date -Iseconds): Test log entry $i - Performance benchmark test for logging system" >> "$log_file"
    done

    local write_end=$(date +%s.%N)
    local write_duration=$(echo "$write_end - $write_start" | bc -l 2>/dev/null || echo "0")
    local write_speed=$(echo "scale=2; 1000 / $write_duration" | bc -l 2>/dev/null || echo "0")

    log "    ✅ 로그 쓰기 속도: ${write_speed} entries/초"

    # 2) 로그 검색 속도 측정
    log "  📋 2단계: 로그 검색 속도 측정"
    local search_start=$(date +%s.%N)
    local search_results=$(grep -c "Performance benchmark" "$log_file" 2>/dev/null || echo "0")
    local search_end=$(date +%s.%N)
    local search_duration=$(echo "$search_end - $search_start" | bc -l 2>/dev/null || echo "0")

    log "    ✅ 로그 검색 속도: ${search_duration}초 (${search_results}개 결과)"

    # 3) 로그 압축 테스트
    log "  📋 3단계: 로그 압축 테스트"
    local original_size=$(stat -c %s "$log_file" 2>/dev/null || echo "0")
    local compressed_file="${log_file}.gz"

    gzip -c "$log_file" > "$compressed_file" 2>/dev/null || true
    local compressed_size=$(stat -c %s "$compressed_file" 2>/dev/null || echo "0")

    local compression_ratio=0
    if [[ $original_size -gt 0 ]]; then
        compression_ratio=$(echo "scale=2; (1 - $compressed_size / $original_size) * 100" | bc -l 2>/dev/null || echo "0")
    fi

    log "    ✅ 압축률: ${compression_ratio}%"

    # 4) 정리
    rm -f "$log_file" "$compressed_file"

    # 5) 결과 저장
    cat > "$result_file" <<EOF
{
  "benchmark": {
    "name": "$benchmark_name",
    "timestamp": "$(date -Iseconds)"
  },
  "write_performance": {
    "write_speed_entries_per_second": $write_speed,
    "write_duration_seconds": $write_duration,
    "total_entries": 1000
  },
  "search_performance": {
    "search_duration_seconds": $search_duration,
    "search_results_count": $search_results
  },
  "compression_performance": {
    "original_size_bytes": $original_size,
    "compressed_size_bytes": $compressed_size,
    "compression_ratio_percent": $compression_ratio
  },
  "targets": {
    "write_speed_improvement": "≥30% 향상",
    "search_speed_improvement": "≥50% 향상",
    "storage_savings": "≥25% 절약"
  },
  "analysis": {
    "write_speed_status": "$(if [[ $(echo "$write_speed > 100" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then echo "GOOD"; else echo "NEEDS_IMPROVEMENT"; fi)",
    "search_speed_status": "$(if [[ $(echo "$search_duration < 0.1" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then echo "GOOD"; else echo "NEEDS_IMPROVEMENT"; fi)",
    "compression_status": "$(if [[ $(echo "$compression_ratio > 25" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then echo "GOOD"; else echo "NEEDS_IMPROVEMENT"; fi)"
  }
}
EOF

    log "✅ 로그 시스템 성능 벤치마크 완료: $result_file"
    return 0
}

# === 모니터링 성능 벤치마크 ===
benchmark_monitoring_performance() {
    local benchmark_name="monitoring_performance"
    local result_file="$BENCHMARK_RESULTS_DIR/${benchmark_name}_$(date +%F).json"

    log "📊 모니터링 성능 벤치마크 시작..."

    # 1) 메트릭 수집 속도 측정
    log "  📋 1단계: 메트릭 수집 속도 측정"
    local collection_start=$(date +%s.%N)

    # 시스템 메트릭 수집
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    local memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    local disk_usage=$(df . | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    local load_average=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')

    local collection_end=$(date +%s.%N)
    local collection_duration=$(echo "$collection_end - $collection_start" | bc -l 2>/dev/null || echo "0")

    log "    ✅ 메트릭 수집 속도: ${collection_duration}초"

    # 2) 모니터링 응답 시간 측정
    log "  📋 2단계: 모니터링 응답 시간 측정"
    local response_start=$(date +%s.%N)

    # 모니터링 시스템 응답 테스트 (enhanced_summary_report.sh)
    if [[ -f "ops/summary/enhanced_summary_report.sh" ]]; then
        timeout 10s bash "ops/summary/enhanced_summary_report.sh" >/dev/null 2>&1
        local response_end=$(date +%s.%N)
        local response_duration=$(echo "$response_end - $response_start" | bc -l 2>/dev/null || echo "0")
        log "    ✅ 모니터링 응답 시간: ${response_duration}초"
    else
        log "    ⚠️  enhanced_summary_report.sh를 찾을 수 없음"
        local response_duration=0
    fi

    # 3) 메트릭 처리 효율성 측정
    log "  📋 3단계: 메트릭 처리 효율성 측정"
    local processing_start=$(date +%s.%N)

    # 메트릭 처리 시뮬레이션
    for i in {1..100}; do
        local test_metric="test_metric_$i"
        local test_value=$((RANDOM % 100))
        echo "$test_metric:$test_value" >/dev/null
    done

    local processing_end=$(date +%s.%N)
    local processing_duration=$(echo "$processing_end - $processing_start" | bc -l 2>/dev/null || echo "0")
    local processing_efficiency=$(echo "scale=2; 100 / $processing_duration" | bc -l 2>/dev/null || echo "0")

    log "    ✅ 메트릭 처리 효율성: ${processing_efficiency} metrics/초"

    # 4) 결과 저장
    cat > "$result_file" <<EOF
{
  "benchmark": {
    "name": "$benchmark_name",
    "timestamp": "$(date -Iseconds)"
  },
  "collection_performance": {
    "collection_duration_seconds": $collection_duration,
    "metrics_collected": 4
  },
  "response_performance": {
    "response_duration_seconds": $response_duration
  },
  "processing_performance": {
    "processing_duration_seconds": $processing_duration,
    "processing_efficiency_metrics_per_second": $processing_efficiency,
    "total_metrics_processed": 100
  },
  "collected_metrics": {
    "cpu_usage_percent": $cpu_usage,
    "memory_usage_percent": $memory_usage,
    "disk_usage_percent": $disk_usage,
    "load_average": $load_average
  },
  "targets": {
    "monitoring_response_time": "≤5초",
    "metric_collection_efficiency": "≥40% 향상"
  },
  "analysis": {
    "response_time_status": "$(if [[ $(echo "$response_duration < 5" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then echo "GOOD"; else echo "NEEDS_IMPROVEMENT"; fi)",
    "collection_efficiency_status": "$(if [[ $(echo "$collection_duration < 1" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then echo "GOOD"; else echo "NEEDS_IMPROVEMENT"; fi)",
    "processing_efficiency_status": "$(if [[ $(echo "$processing_efficiency > 10" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then echo "GOOD"; else echo "NEEDS_IMPROVEMENT"; fi)"
  }
}
EOF

    log "✅ 모니터링 성능 벤치마크 완료: $result_file"
    return 0
}

# === 종합 성능 분석 ===
analyze_overall_performance() {
    log "📊 종합 성능 분석 시작..."

    local analysis_file="$BENCHMARK_RESULTS_DIR/overall_performance_analysis_$(date +%F).json"

    # 각 벤치마크 결과 수집
    local backup_file="$BENCHMARK_RESULTS_DIR/backup_performance_$(date +%F).json"
    local logging_file="$BENCHMARK_RESULTS_DIR/logging_performance_$(date +%F).json"
    local monitoring_file="$BENCHMARK_RESULTS_DIR/monitoring_performance_$(date +%F).json"

    local overall_score=0
    local total_metrics=0
    local passed_metrics=0

    # 백업 성능 분석
    if [[ -f "$backup_file" ]]; then
        local backup_speed_status=$(grep -o '"backup_speed_status": "[^"]*"' "$backup_file" | cut -d'"' -f4)
        local backup_size_status=$(grep -o '"backup_size_status": "[^"]*"' "$backup_file" | cut -d'"' -f4)
        local resource_status=$(grep -o '"resource_usage_status": "[^"]*"' "$backup_file" | cut -d'"' -f4)

        total_metrics=$((total_metrics + 3))
        if [[ "$backup_speed_status" == "GOOD" ]]; then passed_metrics=$((passed_metrics + 1)); fi
        if [[ "$backup_size_status" == "GOOD" ]]; then passed_metrics=$((passed_metrics + 1)); fi
        if [[ "$resource_status" == "GOOD" ]]; then passed_metrics=$((passed_metrics + 1)); fi
    fi

    # 로깅 성능 분석
    if [[ -f "$logging_file" ]]; then
        local write_status=$(grep -o '"write_speed_status": "[^"]*"' "$logging_file" | cut -d'"' -f4)
        local search_status=$(grep -o '"search_speed_status": "[^"]*"' "$logging_file" | cut -d'"' -f4)
        local compression_status=$(grep -o '"compression_status": "[^"]*"' "$logging_file" | cut -d'"' -f4)

        total_metrics=$((total_metrics + 3))
        if [[ "$write_status" == "GOOD" ]]; then passed_metrics=$((passed_metrics + 1)); fi
        if [[ "$search_status" == "GOOD" ]]; then passed_metrics=$((passed_metrics + 1)); fi
        if [[ "$compression_status" == "GOOD" ]]; then passed_metrics=$((passed_metrics + 1)); fi
    fi

    # 모니터링 성능 분석
    if [[ -f "$monitoring_file" ]]; then
        local response_status=$(grep -o '"response_time_status": "[^"]*"' "$monitoring_file" | cut -d'"' -f4)
        local collection_status=$(grep -o '"collection_efficiency_status": "[^"]*"' "$monitoring_file" | cut -d'"' -f4)
        local processing_status=$(grep -o '"processing_efficiency_status": "[^"]*"' "$monitoring_file" | cut -d'"' -f4)

        total_metrics=$((total_metrics + 3))
        if [[ "$response_status" == "GOOD" ]]; then passed_metrics=$((passed_metrics + 1)); fi
        if [[ "$collection_status" == "GOOD" ]]; then passed_metrics=$((passed_metrics + 1)); fi
        if [[ "$processing_status" == "GOOD" ]]; then passed_metrics=$((passed_metrics + 1)); fi
    fi

    # 전체 점수 계산
    if [[ $total_metrics -gt 0 ]]; then
        overall_score=$(echo "scale=1; $passed_metrics * 100 / $total_metrics" | bc -l 2>/dev/null || echo "0")
    fi

    # 종합 분석 결과 저장
    cat > "$analysis_file" <<EOF
{
  "overall_analysis": {
    "timestamp": "$(date -Iseconds)",
    "total_metrics": $total_metrics,
    "passed_metrics": $passed_metrics,
    "overall_score_percent": $overall_score,
    "performance_grade": "$(if [[ $(echo "$overall_score >= 80" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then echo "A"; elif [[ $(echo "$overall_score >= 60" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then echo "B"; elif [[ $(echo "$overall_score >= 40" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then echo "C"; else echo "D"; fi)"
  },
  "performance_summary": {
    "backup_performance": "$(if [[ -f "$backup_file" ]]; then echo "측정 완료"; else echo "측정 필요"; fi)",
    "logging_performance": "$(if [[ -f "$logging_file" ]]; then echo "측정 완료"; else echo "측정 필요"; fi)",
    "monitoring_performance": "$(if [[ -f "$monitoring_file" ]]; then echo "측정 완료"; else echo "측정 필요"; fi)"
  },
  "recommendations": [
    "$(if [[ $(echo "$overall_score < 80" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then echo "성능 최적화가 필요합니다"; else echo "현재 성능이 양호합니다"; fi)",
    "$(if [[ $passed_metrics -lt $total_metrics ]]; then echo "개선이 필요한 영역이 있습니다"; else echo "모든 영역이 목표를 달성했습니다"; fi)",
    "Phase 6 성능 최적화 계획에 따라 단계적 개선을 진행하세요"
  ],
  "next_steps": [
    "성능 벤치마크 결과 분석",
    "개선 우선순위 설정",
    "최적화 계획 수립 및 실행"
  ]
}
EOF

    log "✅ 종합 성능 분석 완료: $analysis_file"
    log "📊 전체 성능 점수: ${overall_score}% (${passed_metrics}/${total_metrics} 통과)"

    return 0
}

# === 벤치마크 요약 리포트 생성 ===
generate_benchmark_summary() {
    local summary_file="$BENCHMARK_LOGS_DIR/benchmark_summary_$(date +%F).md"

    log "📊 벤치마크 요약 리포트 생성: $summary_file"

    # 분석 결과 로드
    local overall_score="N/A"
    local performance_grade="N/A"
    if [[ -f "$BENCHMARK_RESULTS_DIR/overall_performance_analysis_$(date +%F).json" ]]; then
        overall_score=$(grep -o '"overall_score_percent": [0-9.]*' "$BENCHMARK_RESULTS_DIR/overall_performance_analysis_$(date +%F).json" | cut -d' ' -f2)
        performance_grade=$(grep -o '"performance_grade": "[^"]*"' "$BENCHMARK_RESULTS_DIR/overall_performance_analysis_$(date +%F).json" | cut -d'"' -f4)
    fi

    cat > "$summary_file" <<EOF
# 📊 Phase 6 성능 벤치마크 요약 — $(date +%F)

## 📋 **벤치마크 개요**

- **실행 일시**: $(date -Iseconds)
- **실행자**: $(whoami)
- **호스트**: $(hostname)
- **Phase**: Phase 6: 성능 최적화 + 안정성 강화 + 운영 효율화

## 🚀 **벤치마크 결과 요약**

- **전체 성능 점수**: ${overall_score}%
- **성능 등급**: ${performance_grade}
- **측정 완료 영역**: 3개 (백업, 로깅, 모니터링)

## 📊 **영역별 성능 측정 결과**

### **1) 백업 성능**
- **상태**: $(if [[ -f "$BENCHMARK_RESULTS_DIR/backup_performance_$(date +%F).json" ]]; then echo "✅ 측정 완료"; else echo "⚠️  측정 필요"; fi)
- **결과 파일**: \`$BENCHMARK_RESULTS_DIR/backup_performance_$(date +%F).json\`
- **목표**: 백업 속도 ≥20% 향상, 백업 크기 ≥15% 감소

### **2) 로깅 성능**
- **상태**: $(if [[ -f "$BENCHMARK_RESULTS_DIR/logging_performance_$(date +%F).json" ]]; then echo "✅ 측정 완료"; else echo "⚠️  측정 필요"; fi)
- **결과 파일**: \`$BENCHMARK_RESULTS_DIR/logging_performance_$(date +%F).json\`
- **목표**: 로그 처리 속도 ≥30% 향상, 검색 속도 ≥50% 향상

### **3) 모니터링 성능**
- **상태**: $(if [[ -f "$BENCHMARK_RESULTS_DIR/monitoring_performance_$(date +%F).json" ]]; then echo "✅ 측정 완료"; else echo "⚠️  측정 필요"; fi)
- **결과 파일**: \`$BENCHMARK_RESULTS_DIR/monitoring_performance_$(date +%F).json\`
- **목표**: 응답 시간 ≤5초, 메트릭 수집 효율성 ≥40% 향상

## 🎯 **성능 최적화 우선순위**

### **높은 우선순위**
- 백업 성능 개선 (속도 및 크기 최적화)
- 로그 시스템 최적화 (쓰기/검색 속도 향상)
- 모니터링 응답 시간 단축

### **중간 우선순위**
- 리소스 사용량 최적화
- 메트릭 수집 효율성 개선
- 압축률 향상

### **낮은 우선순위**
- 시스템 안정성 유지
- 운영 효율성 개선
- 문서화 및 지식 관리

## 📈 **다음 단계**

### **Week 1: 성능 최적화 (2025-09-02 ~ 2025-09-08)**
1. 벤치마크 결과 상세 분석
2. 개선 우선순위 설정
3. 최적화 계획 수립
4. 단계적 최적화 실행

### **Week 2: 안정성 및 효율성 (2025-09-09 ~ 2025-09-15)**
1. 안정성 강화 시스템 구축
2. 운영 효율성 개선
3. 최종 성능 검증
4. Phase 6 완료

## 🚨 **주의사항**

- **성능 최적화는 안정성을 해치지 않는 범위에서 진행**
- **모든 개선사항은 충분한 테스트 후 적용**
- **점진적 적용으로 위험 최소화**
- **지속적인 모니터링으로 개선 효과 검증**

## 📁 **관련 파일**

- **벤치마크 결과**: \`$BENCHMARK_RESULTS_DIR\`
- **벤치마크 로그**: \`$BENCHMARK_LOGS_DIR\`
- **종합 분석**: \`overall_performance_analysis_*.json\`
- **설정 파일**: \`$BENCHMARK_CONFIG_FILE\`

---

> **💡 운영 팁**: 벤치마크 결과를 바탕으로 체계적인 성능 최적화를 진행하세요.
> **📊 모니터링**: 최적화 과정에서 시스템 안정성을 지속적으로 모니터링하세요.
> **🔄 반복**: 정기적인 벤치마크로 최적화 효과를 검증하고 추가 개선을 진행하세요.
EOF

    log "✅ 벤치마크 요약 리포트 생성 완료: $summary_file"
}

# === 메인 실행 로직 ===
main() {
    log "🚀 Phase 6 성능 벤치마킹 시스템 시작"

    # 락 획득
    acquire_lock

    # 디렉토리 생성
    mkdir -p "$BENCHMARK_LOGS_DIR" "$BENCHMARK_RESULTS_DIR"

    # 1) 백업 성능 벤치마크
    if ! benchmark_backup_performance; then
        log "❌ 백업 성능 벤치마크 실패"
    fi

    # 2) 로그 시스템 성능 벤치마크
    if ! benchmark_logging_performance; then
        log "❌ 로그 시스템 성능 벤치마크 실패"
    fi

    # 3) 모니터링 성능 벤치마크
    if ! benchmark_monitoring_performance; then
        log "❌ 모니터링 성능 벤치마크 실패"
    fi

    # 4) 종합 성능 분석
    if ! analyze_overall_performance; then
        log "❌ 종합 성능 분석 실패"
    fi

    # 5) 벤치마크 요약 리포트 생성
    generate_benchmark_summary

    log "🎉 Phase 6 성능 벤치마킹 완료!"
    log "다음 단계: 벤치마크 결과 분석 및 최적화 계획 수립"
}

# === 스크립트 실행 ===
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
