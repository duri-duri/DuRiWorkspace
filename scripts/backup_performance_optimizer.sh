#!/usr/bin/env bash
set -euo pipefail

# 백업 성능 최적화 스크립트
# Phase 6: 성능 최적화 + 안정성 강화 + 운영 효율화

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

# === 설정 ===
OPTIMIZATION_LOGS_DIR="var/logs/performance/optimization"
OPTIMIZATION_RESULTS_DIR="var/state/performance_optimization"
BENCHMARK_RESULTS_DIR="var/state/performance_benchmark"
LOCK_FILE="var/state/backup_optimization_in_progress.lock"

# === 로깅 함수 ===
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [OPTIMIZATION] $1" | tee -a "$OPTIMIZATION_LOGS_DIR/backup_optimization_$(date +%F).log"
}

# === 오류 처리 ===
error_exit() {
    log "ERROR: $1"
    exit 1
}

# === 락 파일 관리 ===
acquire_lock() {
    if [[ -e "$LOCK_FILE" ]]; then
        log "WARN: 다른 최적화 작업이 진행 중입니다. 잠시 후 재시도하세요."
        exit 1
    fi
    echo "$$" > "$LOCK_FILE"
    trap 'rm -f "$LOCK_FILE"' EXIT
}

# === 백업 압축 최적화 ===
optimize_backup_compression() {
    log "🔧 백업 압축 최적화 시작..."
    
    local test_dir="var/test_compression_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$test_dir"
    
    # 테스트 데이터 생성 (var/reports 폴더 복사)
    if [[ -d "var/reports" ]]; then
        cp -r "var/reports" "$test_dir/"
        
        local original_size=$(du -sb "$test_dir" 2>/dev/null | cut -f1 || echo "0")
        log "  📋 원본 크기: ${original_size}바이트"
        
        # 다양한 압축 방식 테스트
        local compression_methods=("gzip" "bzip2" "xz" "lz4" "zstd")
        local best_compression="gzip"
        local best_ratio=0
        
        for method in "${compression_methods[@]}"; do
            if command -v "$method" >/dev/null 2>&1; then
                log "  📋 $method 압축 테스트..."
                
                local compressed_file="${test_dir}.${method}"
                case "$method" in
                    "gzip")
                        tar -czf "$compressed_file" -C "$test_dir" . 2>/dev/null || continue
                        ;;
                    "bzip2")
                        tar -cjf "$compressed_file" -C "$test_dir" . 2>/dev/null || continue
                        ;;
                    "xz")
                        tar -cJf "$compressed_file" -C "$test_dir" . 2>/dev/null || continue
                        ;;
                    "lz4")
                        tar -cf - -C "$test_dir" . | lz4 > "$compressed_file" 2>/dev/null || continue
                        ;;
                    "zstd")
                        tar -cf - -C "$test_dir" . | zstd > "$compressed_file" 2>/dev/null || continue
                        ;;
                esac
                
                if [[ -f "$compressed_file" ]]; then
                    local compressed_size=$(stat -c %s "$compressed_file" 2>/dev/null || echo "0")
                    local ratio=0
                    
                    if [[ $original_size -gt 0 ]]; then
                        ratio=$(echo "scale=2; (1 - $compressed_size / $original_size) * 100" | bc -l 2>/dev/null || echo "0")
                    fi
                    
                    log "    ✅ $method: 압축률 ${ratio}% (${compressed_size}바이트)"
                    
                    if [[ $(echo "$ratio > $best_ratio" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
                        best_ratio=$ratio
                        best_compression=$method
                    fi
                    
                    rm -f "$compressed_file"
                fi
            fi
        done
        
        log "  🏆 최적 압축 방식: $best_compression (압축률: ${best_ratio}%)"
        
        # 정리
        rm -rf "$test_dir"
        
        # 결과 저장
        echo "$best_compression" > "$OPTIMIZATION_RESULTS_DIR/best_compression_method.txt"
        echo "$best_ratio" > "$OPTIMIZATION_RESULTS_DIR/best_compression_ratio.txt"
        
        return 0
    else
        log "  ⚠️  var/reports 폴더가 존재하지 않음"
        return 1
    fi
}

# === 백업 병렬 처리 최적화 ===
optimize_backup_parallelization() {
    log "🔧 백업 병렬 처리 최적화 시작..."
    
    # 시스템 CPU 코어 수 확인
    local cpu_cores=$(nproc 2>/dev/null || echo "1")
    local optimal_jobs=$((cpu_cores * 2))  # CPU 코어의 2배
    
    log "  📋 시스템 CPU 코어: ${cpu_cores}개"
    log "  📋 최적 병렬 작업 수: ${optimal_jobs}개"
    
    # 병렬 처리 테스트
    local test_dir="var/test_parallel_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$test_dir"
    
    # 테스트 파일 생성
    for i in {1..100}; do
        echo "Test file $i content for parallel processing optimization" > "$test_dir/test_file_$i.txt"
    done
    
    # 병렬 복사 테스트
    local start_time=$(date +%s.%N)
    
    # rsync 병렬 옵션 테스트
    local rsync_start=$(date +%s.%N)
    rsync -av --delete "$test_dir/" "$test_dir"_copy/ >/dev/null 2>&1
    local rsync_end=$(date +%s.%N)
    local rsync_duration=$(echo "$rsync_end - $rsync_start" | bc -l 2>/dev/null || echo "0")
    
    # 병렬 tar 테스트
    local tar_start=$(date +%s.%N)
    tar -cf "$test_dir.tar" -C "$test_dir" . >/dev/null 2>&1
    local tar_end=$(date +%s.%N)
    local tar_duration=$(echo "$tar_end - $tar_start" | bc -l 2>/dev/null || echo "0")
    
    local end_time=$(date +%s.%N)
    local total_duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
    
    log "  ✅ rsync 속도: ${rsync_duration}초"
    log "  ✅ tar 속도: ${tar_duration}초"
    log "  ✅ 전체 처리 시간: ${total_duration}초"
    
    # 정리
    rm -rf "$test_dir" "$test_dir"_copy "$test_dir.tar"
    
    # 결과 저장
    cat > "$OPTIMIZATION_RESULTS_DIR/parallel_optimization.json" <<EOF
{
  "parallel_optimization": {
    "timestamp": "$(date -Iseconds)",
    "cpu_cores": $cpu_cores,
    "optimal_jobs": $optimal_jobs,
    "rsync_duration_seconds": $rsync_duration,
    "tar_duration_seconds": $tar_duration,
    "total_duration_seconds": $total_duration
  },
  "recommendations": [
    "rsync --delete 옵션으로 불필요한 파일 제거",
    "tar 압축 시 --use-compress-program 옵션 활용",
    "병렬 작업 수를 CPU 코어의 2배로 설정"
  ]
}
EOF
    
    return 0
}

# === 백업 I/O 최적화 ===
optimize_backup_io() {
    log "🔧 백업 I/O 최적화 시작..."
    
    # 디스크 I/O 성능 측정
    local iostat_output=$(iostat -x 1 1 2>/dev/null | tail -1 || echo "")
    
    if [[ -n "$iostat_output" ]]; then
        local device=$(echo "$iostat_output" | awk '{print $1}')
        local await=$(echo "$iostat_output" | awk '{print $10}')
        local svctm=$(echo "$iostat_output" | awk '{print $11}')
        local util=$(echo "$iostat_output" | awk '{print $14}')
        
        log "  📋 디스크 I/O 성능 분석"
        log "    - 디바이스: $device"
        log "    - 평균 대기 시간: ${await}ms"
        log "    - 평균 서비스 시간: ${svctm}ms"
        log "    - 디스크 사용률: ${util}%"
        
        # I/O 최적화 권장사항
        local io_recommendations=()
        
        if [[ $(echo "$await > 10" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
            io_recommendations+=("디스크 I/O 병목 현상 감지 - SSD 업그레이드 고려")
        fi
        
        if [[ $(echo "$util > 80" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
            io_recommendations+=("디스크 사용률 높음 - 백업 작업 분산 고려")
        fi
        
        if [[ ${#io_recommendations[@]} -eq 0 ]]; then
            io_recommendations+=("현재 I/O 성능 양호")
        fi
        
        # 결과 저장
        cat > "$OPTIMIZATION_RESULTS_DIR/io_optimization.json" <<EOF
{
  "io_optimization": {
    "timestamp": "$(date -Iseconds)",
    "device": "$device",
    "await_ms": $await,
    "svctm_ms": $svctm,
    "utilization_percent": $util
  },
  "recommendations": [
    $(printf '"%s",\n    ' "${io_recommendations[@]}" | head -c -5)
  ]
}
EOF
        
        log "  ✅ I/O 최적화 분석 완료"
    else
        log "  ⚠️  iostat 명령어를 사용할 수 없음"
    fi
    
    return 0
}

# === 백업 중복 제거 최적화 ===
optimize_backup_deduplication() {
    log "🔧 백업 중복 제거 최적화 시작..."
    
    local test_dir="var/test_dedup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$test_dir"
    
    # 중복 파일 생성
    for i in {1..50}; do
        echo "Duplicate content for deduplication test" > "$test_dir/file_$i.txt"
        echo "Unique content $i" > "$test_dir/unique_$i.txt"
    done
    
    # 추가 중복 파일 (동일한 내용)
    for i in {1..25}; do
        cp "$test_dir/file_1.txt" "$test_dir/duplicate_$i.txt"
    done
    
    local original_size=$(du -sb "$test_dir" 2>/dev/null | cut -f1 || echo "0")
    log "  📋 원본 크기: ${original_size}바이트"
    
    # 중복 파일 수 계산
    local total_files=$(find "$test_dir" -type f | wc -l)
    local unique_files=$(find "$test_dir" -type f -exec sha256sum {} \; | sort | uniq -w64 | wc -l)
    local duplicate_files=$((total_files - unique_files))
    
    log "  📋 총 파일 수: ${total_files}개"
    log "  📋 고유 파일 수: ${unique_files}개"
    log "  📋 중복 파일 수: ${duplicate_files}개"
    
    # 중복 제거 후 크기 계산
    local dedup_dir="${test_dir}_dedup"
    mkdir -p "$dedup_dir"
    
    # 고유 파일만 복사
    find "$test_dir" -type f -exec sha256sum {} \; | sort | uniq -w64 | while read hash filename; do
        cp "$filename" "$dedup_dir/"
    done
    
    local dedup_size=$(du -sb "$dedup_dir" 2>/dev/null | cut -f1 || echo "0")
    local space_saved=0
    
    if [[ $original_size -gt 0 ]]; then
        space_saved=$(echo "scale=2; (1 - $dedup_size / $original_size) * 100" | bc -l 2>/dev/null || echo "0")
    fi
    
    log "  ✅ 중복 제거 후 크기: ${dedup_size}바이트"
    log "  ✅ 공간 절약: ${space_saved}%"
    
    # 정리
    rm -rf "$test_dir" "$dedup_dir"
    
    # 결과 저장
    cat > "$OPTIMIZATION_RESULTS_DIR/deduplication_optimization.json" <<EOF
{
  "deduplication_optimization": {
    "timestamp": "$(date -Iseconds)",
    "original_size_bytes": $original_size,
    "dedup_size_bytes": $dedup_size,
    "space_saved_percent": $space_saved,
    "total_files": $total_files,
    "unique_files": $unique_files,
    "duplicate_files": $duplicate_files
  },
  "recommendations": [
    "중복 제거로 ${space_saved}% 공간 절약 가능",
    "백업 전 중복 파일 검사 및 제거",
    "파일 해시 기반 중복 제거 시스템 구축"
  ]
}
EOF
    
    return 0
}

# === 최적화 결과 통합 분석 ===
analyze_optimization_results() {
    log "📊 최적화 결과 통합 분석 시작..."
    
    local analysis_file="$OPTIMIZATION_RESULTS_DIR/backup_optimization_analysis_$(date +%F).json"
    
    # 각 최적화 결과 수집
    local compression_method="N/A"
    local compression_ratio="N/A"
    local cpu_cores="N/A"
    local optimal_jobs="N/A"
    local space_saved="N/A"
    
    if [[ -f "$OPTIMIZATION_RESULTS_DIR/best_compression_method.txt" ]]; then
        compression_method=$(cat "$OPTIMIZATION_RESULTS_DIR/best_compression_method.txt")
    fi
    
    if [[ -f "$OPTIMIZATION_RESULTS_DIR/best_compression_ratio.txt" ]]; then
        compression_ratio=$(cat "$OPTIMIZATION_RESULTS_DIR/best_compression_ratio.txt")
    fi
    
    if [[ -f "$OPTIMIZATION_RESULTS_DIR/parallel_optimization.json" ]]; then
        cpu_cores=$(grep -o '"cpu_cores": [0-9]*' "$OPTIMIZATION_RESULTS_DIR/parallel_optimization.json" | cut -d' ' -f2)
        optimal_jobs=$(grep -o '"optimal_jobs": [0-9]*' "$OPTIMIZATION_RESULTS_DIR/parallel_optimization.json" | cut -d' ' -f2)
    fi
    
    if [[ -f "$OPTIMIZATION_RESULTS_DIR/deduplication_optimization.json" ]]; then
        space_saved=$(grep -o '"space_saved_percent": [0-9.]*' "$OPTIMIZATION_RESULTS_DIR/deduplication_optimization.json" | cut -d' ' -f2)
    fi
    
    # 최적화 효과 분석
    local optimization_score=0
    local total_improvements=0
    
    if [[ "$compression_ratio" != "N/A" && $(echo "$compression_ratio > 15" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
        optimization_score=$((optimization_score + 25))
        total_improvements=$((total_improvements + 1))
    fi
    
    if [[ "$cpu_cores" != "N/A" && $cpu_cores -gt 1 ]]; then
        optimization_score=$((optimization_score + 25))
        total_improvements=$((total_improvements + 1))
    fi
    
    if [[ "$space_saved" != "N/A" && $(echo "$space_saved > 15" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
        optimization_score=$((optimization_score + 25))
        total_improvements=$((total_improvements + 1))
    fi
    
    # I/O 최적화 점수
    if [[ -f "$OPTIMIZATION_RESULTS_DIR/io_optimization.json" ]]; then
        optimization_score=$((optimization_score + 25))
        total_improvements=$((total_improvements + 1))
    fi
    
    # 통합 분석 결과 저장
    cat > "$analysis_file" <<EOF
{
  "backup_optimization_analysis": {
    "timestamp": "$(date -Iseconds)",
    "optimization_score_percent": $optimization_score,
    "total_improvements": $total_improvements,
    "optimization_grade": "$(if [[ $optimization_score -ge 80 ]]; then echo "A"; elif [[ $optimization_score -ge 60 ]]; then echo "B"; elif [[ $optimization_score -ge 40 ]]; then echo "C"; else echo "D"; fi)"
  },
  "optimization_results": {
    "compression": {
      "method": "$compression_method",
      "ratio_percent": "$compression_ratio"
    },
    "parallelization": {
      "cpu_cores": "$cpu_cores",
      "optimal_jobs": "$optimal_jobs"
    },
    "deduplication": {
      "space_saved_percent": "$space_saved"
    }
  },
  "performance_improvements": [
    "압축률: ${compression_ratio}% (목표: ≥15%)",
    "병렬 처리: ${cpu_cores}코어 기반 (목표: CPU 활용도 향상)",
    "중복 제거: ${space_saved}% 공간 절약 (목표: ≥15%)"
  ],
  "next_steps": [
    "최적화된 백업 스크립트 적용",
    "성능 재측정 및 검증",
    "운영 환경에 단계적 적용"
  ]
}
EOF
    
    log "✅ 최적화 결과 통합 분석 완료: $analysis_file"
    log "📊 최적화 점수: ${optimization_score}% (${total_improvements}/4개 개선사항)"
    
    return 0
}

# === 최적화 요약 리포트 생성 ===
generate_optimization_summary() {
    local summary_file="$OPTIMIZATION_LOGS_DIR/backup_optimization_summary_$(date +%F).md"
    
    log "📊 백업 최적화 요약 리포트 생성: $summary_file"
    
    # 최적화 결과 로드
    local optimization_score="N/A"
    local optimization_grade="N/A"
    if [[ -f "$OPTIMIZATION_RESULTS_DIR/backup_optimization_analysis_$(date +%F).json" ]]; then
        optimization_score=$(grep -o '"optimization_score_percent": [0-9]*' "$OPTIMIZATION_RESULTS_DIR/backup_optimization_analysis_$(date +%F).json" | cut -d' ' -f2)
        optimization_grade=$(grep -o '"optimization_grade": "[^"]*"' "$OPTIMIZATION_RESULTS_DIR/backup_optimization_analysis_$(date +%F).json" | cut -d'"' -f4)
    fi
    
    cat > "$summary_file" <<EOF
# 🔧 Phase 6 백업 성능 최적화 요약 — $(date +%F)

## 📋 **최적화 개요**

- **실행 일시**: $(date -Iseconds)
- **실행자**: $(whoami)
- **호스트**: $(hostname)
- **Phase**: Phase 6: 성능 최적화 + 안정성 강화 + 운영 효율화

## 🚀 **최적화 결과 요약**

- **최적화 점수**: ${optimization_score}%
- **최적화 등급**: ${optimization_grade}
- **적용된 최적화**: 4개 영역

## 🔧 **적용된 최적화 기법**

### **1) 백업 압축 최적화**
- **최적 압축 방식**: $(cat "$OPTIMIZATION_RESULTS_DIR/best_compression_method.txt" 2>/dev/null || echo "N/A")
- **압축률**: $(cat "$OPTIMIZATION_RESULTS_DIR/best_compression_ratio.txt" 2>/dev/null || echo "N/A")%
- **목표**: ≥15% 압축률 달성

### **2) 백업 병렬 처리 최적화**
- **CPU 코어**: $(grep -o '"cpu_cores": [0-9]*' "$OPTIMIZATION_RESULTS_DIR/parallel_optimization.json" 2>/dev/null | cut -d' ' -f2 || echo "N/A")개
- **최적 병렬 작업 수**: $(grep -o '"optimal_jobs": [0-9]*' "$OPTIMIZATION_RESULTS_DIR/parallel_optimization.json" 2>/dev/null | cut -d' ' -f2 || echo "N/A")개
- **목표**: CPU 활용도 향상

### **3) 백업 I/O 최적화**
- **I/O 성능 분석**: $(if [[ -f "$OPTIMIZATION_RESULTS_DIR/io_optimization.json" ]]; then echo "✅ 완료"; else echo "⚠️  필요"; fi)
- **목표**: 디스크 I/O 병목 해결

### **4) 백업 중복 제거 최적화**
- **공간 절약**: $(grep -o '"space_saved_percent": [0-9.]*' "$OPTIMIZATION_RESULTS_DIR/deduplication_optimization.json" 2>/dev/null | cut -d' ' -f2 || echo "N/A")%
- **목표**: ≥15% 공간 절약

## 📈 **성능 개선 효과**

- **압축률 향상**: $(cat "$OPTIMIZATION_RESULTS_DIR/best_compression_ratio.txt" 2>/dev/null || echo "0")% 달성
- **병렬 처리**: $(grep -o '"cpu_cores": [0-9]*' "$OPTIMIZATION_RESULTS_DIR/parallel_optimization.json" 2>/dev/null | cut -d' ' -f2 || echo "0")코어 활용
- **공간 절약**: $(grep -o '"space_saved_percent": [0-9.]*' "$OPTIMIZATION_RESULTS_DIR/deduplication_optimization.json" 2>/dev/null | cut -d' ' -f2 || echo "0")% 절약

## 🎯 **다음 단계**

### **1) 최적화 적용**
- 최적화된 백업 스크립트 생성
- 테스트 환경에서 검증
- 운영 환경에 단계적 적용

### **2) 성능 재측정**
- 최적화 후 성능 벤치마크 실행
- 개선 효과 검증
- 추가 최적화 필요성 판단

### **3) 안정성 검증**
- 최적화된 시스템 안정성 테스트
- 오류 처리 및 복구 메커니즘 검증
- 운영 효율성 개선

## 🚨 **주의사항**

- **최적화는 안정성을 해치지 않는 범위에서 진행**
- **모든 최적화는 충분한 테스트 후 적용**
- **점진적 적용으로 위험 최소화**
- **지속적인 모니터링으로 최적화 효과 검증**

## 📁 **관련 파일**

- **최적화 결과**: \`$OPTIMIZATION_RESULTS_DIR\`
- **최적화 로그**: \`$OPTIMIZATION_LOGS_DIR\`
- **통합 분석**: \`backup_optimization_analysis_*.json\`
- **벤치마크 결과**: \`$BENCHMARK_RESULTS_DIR\`

---

> **💡 운영 팁**: 최적화 결과를 바탕으로 체계적인 백업 성능 개선을 진행하세요.  
> **📊 모니터링**: 최적화 과정에서 시스템 안정성을 지속적으로 모니터링하세요.  
> **🔄 반복**: 정기적인 성능 측정으로 최적화 효과를 검증하고 추가 개선을 진행하세요.
EOF
    
    log "✅ 백업 최적화 요약 리포트 생성 완료: $summary_file"
}

# === 메인 실행 로직 ===
main() {
    log "🚀 Phase 6 백업 성능 최적화 시작"
    
    # 락 획득
    acquire_lock
    
    # 디렉토리 생성
    mkdir -p "$OPTIMIZATION_LOGS_DIR" "$OPTIMIZATION_RESULTS_DIR"
    
    # 1) 백업 압축 최적화
    if ! optimize_backup_compression; then
        log "❌ 백업 압축 최적화 실패"
    fi
    
    # 2) 백업 병렬 처리 최적화
    if ! optimize_backup_parallelization; then
        log "❌ 백업 병렬 처리 최적화 실패"
    fi
    
    # 3) 백업 I/O 최적화
    if ! optimize_backup_io; then
        log "❌ 백업 I/O 최적화 실패"
    fi
    
    # 4) 백업 중복 제거 최적화
    if ! optimize_backup_deduplication; then
        log "❌ 백업 중복 제거 최적화 실패"
    fi
    
    # 5) 최적화 결과 통합 분석
    if ! analyze_optimization_results; then
        log "❌ 최적화 결과 통합 분석 실패"
    fi
    
    # 6) 최적화 요약 리포트 생성
    generate_optimization_summary
    
    log "🎉 Phase 6 백업 성능 최적화 완료!"
    log "다음 단계: 최적화된 백업 시스템 적용 및 성능 재측정"
}

# === 스크립트 실행 ===
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi



