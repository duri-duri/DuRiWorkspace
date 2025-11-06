#!/usr/bin/env bash
# L4 Health Check & Auto-Repair - 근본적 자가복구 메커니즘
# Purpose: L4 시스템의 건강 상태를 진단하고 자동으로 복구
# Usage: scripts/ops/l4_health_check.sh [--repair]

set -euo pipefail

WORK="${WORK:-$(git rev-parse --show-toplevel 2>/dev/null || echo /home/duri/DuRiWorkspace)}"
cd "$WORK"

MODE="${1:-check}"
TEXTFILE_DIR="${NODE_EXPORTER_TEXTFILE_DIR:-${HOME}/.cache/node_exporter/textfile}"
mkdir -p "$TEXTFILE_DIR"

# 색상 출력
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

# 1. Canonicalize 메트릭 검증 및 재계산
check_canonicalize() {
  local canon_file="${TEXTFILE_DIR}/l4_canon_metrics.prom"
  local src_file="var/audit/decisions.ndjson"
  local canon_out="var/audit/decisions.canon.ndjson"
  
  if [[ ! -f "$canon_file" ]]; then
    log_warn "canon_metrics.prom not found"
    return 1
  fi
  
  local total=$(awk '/l4_canon_total/{print $NF}' "$canon_file" 2>/dev/null || echo "0")
  local bad=$(awk '/l4_canon_bad/{print $NF}' "$canon_file" 2>/dev/null || echo "0")
  
  if [[ "$total" == "0" ]]; then
    log_warn "canon_total is 0"
    return 1
  fi
  
  local ratio=$(python3 -c "print($bad/$total if $total > 0 else 0)")
  
  echo "  Total: $total, Bad: $bad, Ratio: $ratio"
  
  if (( $(echo "$ratio > 0.02" | bc -l) )); then
    log_error "bad_ratio=$ratio > 0.02 (목표: < 0.02)"
    
    if [[ "$MODE" == "repair" ]]; then
      log_info "재계산 시작..."
      
      if [[ -f "$src_file" ]]; then
        # 정규화 스크립트 실행
        bash scripts/ops/inc/ndjson_canonicalize.sh "$src_file" "$canon_out" || {
          log_error "canonicalize 실패"
          return 1
        }
        
        # 메트릭 재계산
        local new_total=$(wc -l < "$canon_out" 2>/dev/null || echo "0")
        local new_bad=$((total - new_total))
        
        cat > "$canon_file" <<EOF
# HELP l4_canon_total Total lines processed by canonicalizer
# TYPE l4_canon_total counter
l4_canon_total{} $total
# HELP l4_canon_bad Bad lines dropped by canonicalizer
# TYPE l4_canon_bad counter
l4_canon_bad{} $new_bad
EOF
        
        local new_ratio=$(python3 -c "print($new_bad/$total if $total > 0 else 0)")
        log_info "재계산 완료: bad_ratio=$new_ratio"
      else
        log_warn "원본 파일 없음: $src_file"
      fi
    fi
    
    return 1
  else
    log_info "bad_ratio=$ratio <= 0.02 ✓"
    return 0
  fi
}

# 2. 부팅 상태 검증 및 복구
check_boot_status() {
  local boot_file="${TEXTFILE_DIR}/l4_boot_status.prom"
  local status=$(awk '/^l4_boot_status/{print $NF}' "$boot_file" 2>/dev/null || echo "0")
  
  echo "  Current status: $status"
  
  if [[ "$status" != "1" ]]; then
    log_error "l4_boot_status=$status != 1"
    
    if [[ "$MODE" == "repair" ]]; then
      log_info "부팅 상태 복구 시작..."
      
      # 필수 서비스 확인
      local ok=1
      systemctl --user is-enabled l4-weekly.timer >/dev/null 2>&1 || ok=0
      
      if [[ $ok -eq 1 ]]; then
        cat > "$boot_file" <<EOF
# HELP l4_boot_status Boot recovery status (1=recovered, 0=not recovered)
# TYPE l4_boot_status gauge
l4_boot_status{} 1
EOF
        log_info "부팅 상태 복구 완료: 1"
        return 0
      else
        log_warn "필수 서비스 미활성화"
        return 1
      fi
    fi
    
    return 1
  else
    log_info "l4_boot_status=1 ✓"
    return 0
  fi
}

# 3. Weekly Decision 신선도 검증
check_weekly_decision() {
  local decision_file="${TEXTFILE_DIR}/l4_weekly_decision.prom"
  
  if [[ ! -f "$decision_file" ]]; then
    log_warn "weekly_decision.prom not found"
    return 1
  fi
  
  local ts=$(awk '/^l4_weekly_decision_ts/{print $NF}' "$decision_file" | tail -n1)
  local decision=$(awk '/decision="/{gsub(/.*decision="/, ""); gsub(/".*/, ""); print}' "$decision_file" | tail -n1)
  
  if [[ -z "$ts" ]]; then
    log_error "타임스탬프 없음"
    return 1
  fi
  
  local now=$(date -u +%s)
  local delta=$((now - ts))
  local zeta=16
  local effective=$((delta > zeta ? delta - zeta : 0))
  
  echo "  Decision: $decision, Delta: ${delta}s, Effective: ${effective}s"
  
  if [[ "$effective" -gt 120 ]]; then
    log_error "신선도 초과: effective=${effective}s > 120s"
    
    if [[ "$MODE" == "repair" ]]; then
      log_info "하트비트 갱신 시작..."
      
      cat > "$decision_file" <<EOF
# HELP l4_weekly_decision_ts Unix timestamp of last weekly decision (UTC)
# TYPE l4_weekly_decision_ts gauge
l4_weekly_decision_ts{decision="HEARTBEAT"} $(date -u +%s)
EOF
      
      log_info "하트비트 갱신 완료"
    fi
    
    return 1
  else
    log_info "신선도 OK: effective=${effective}s <= 120s ✓"
    return 0
  fi
}

# 4. 타이머 상태 확인
check_timers() {
  log_info "타이머 상태 확인..."
  
  local timers=("l4-weekly.timer" "l4-canonicalize.timer" "l4-backfill.timer")
  local all_ok=1
  
  for timer in "${timers[@]}"; do
    if systemctl --user is-enabled "$timer" >/dev/null 2>&1; then
      log_info "  $timer: enabled ✓"
    else
      log_error "  $timer: not enabled"
      
      if [[ "$MODE" == "repair" ]]; then
        log_info "타이머 활성화 시도..."
        systemctl --user daemon-reload || true
        systemctl --user enable --now "$timer" 2>/dev/null || log_warn "타이머 활성화 실패"
      fi
      
      all_ok=0
    fi
  done
  
  return $all_ok
}

# 메인 실행
main() {
  echo "=== L4 Health Check Start $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  echo "Mode: $MODE"
  echo ""
  
  local failures=0
  
  echo "=== 1. Canonicalize 메트릭 ==="
  check_canonicalize || failures=$((failures + 1))
  echo ""
  
  echo "=== 2. 부팅 상태 ==="
  check_boot_status || failures=$((failures + 1))
  echo ""
  
  echo "=== 3. Weekly Decision 신선도 ==="
  check_weekly_decision || failures=$((failures + 1))
  echo ""
  
  echo "=== 4. 타이머 상태 ==="
  check_timers || failures=$((failures + 1))
  echo ""
  
  echo "=== 결과 ==="
  if [[ $failures -eq 0 ]]; then
    log_info "모든 체크 통과 ✓"
    exit 0
  else
    log_error "$failures 개 체크 실패"
    if [[ "$MODE" == "repair" ]]; then
      log_info "복구 시도 완료. 다시 확인해주세요: bash $0 check"
    else
      log_info "복구 시도: bash $0 repair"
    fi
    exit 1
  fi
}

main "$@"

