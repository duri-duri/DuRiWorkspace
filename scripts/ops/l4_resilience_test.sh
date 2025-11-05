#!/usr/bin/env bash
# L4 Resilience Test - 강제 종료 시나리오 테스트
# Purpose: 프로세스 강제 종료 시 NDJSON 완전성 및 메트릭 일관성 확인
# Usage: bash scripts/ops/l4_resilience_test.sh

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo /home/duri/DuRiWorkspace)"
cd "${ROOT}"

AUDIT_DIR="${ROOT}/var/audit"
DECISIONS="${AUDIT_DIR}/decisions.ndjson"
TEXTFILE_DIR="${TEXTFILE_DIR:-/tmp/test_textfile_resilience}"
LOG_DIR="${AUDIT_DIR}/logs"
mkdir -p "${LOG_DIR}" "${TEXTFILE_DIR}"

# 백업 원본
if [[ -f "${DECISIONS}" ]]; then
  cp "${DECISIONS}" "${DECISIONS}.backup.$(date +%Y%m%d_%H%M%S)"
fi

# 테스트용 decisions.ndjson 초기화
test_decisions="${AUDIT_DIR}/decisions_test.ndjson"
> "${test_decisions}"

echo "=== L4 Resilience Test: 강제 종료 시나리오 ==="
echo ""

# 1. 병렬 append + 강제 종료 시뮬레이션
echo "1. Running parallel append with forced kill simulation..."
export NODE_EXPORTER_TEXTFILE_DIR="${TEXTFILE_DIR}"

pids=()
for i in $(seq 1 20); do
  summary="${LOG_DIR}/tmp_resilience_${i}.log"
  mkdir -p "$(dirname "$summary")"
  printf "Score: 0.%02d\nDecision: HOLD\n" "$i" > "$summary"
  
  (
    score="0.$i" decision="HOLD" summary="$summary" \
    DECISIONS_NDJSON="${test_decisions}" \
    bash scripts/ops/inc/l4_post_decision.sh &
    pid=$!
    sleep 0.05
    # 50% 확률로 강제 종료
    if [[ $((RANDOM % 2)) -eq 0 ]]; then
      kill -9 "$pid" 2>/dev/null || true
    fi
    wait "$pid" 2>/dev/null || true
  ) &
  pids+=($!)
  sleep 0.1
done

# 모든 프로세스 완료 대기
for pid in "${pids[@]}"; do
  wait "$pid" 2>/dev/null || true
done

echo "  ✅ Parallel append completed"

# 2. NDJSON 무결성 확인
echo ""
echo "2. Checking NDJSON integrity..."
if [[ -f "${test_decisions}" ]]; then
  total_lines=$(wc -l < "${test_decisions}" 2>/dev/null || echo 0)
  valid_json=$(jq -cr 'select(type=="object" and .ts and .decision)' "${test_decisions}" 2>/dev/null | wc -l || echo 0)
  invalid_lines=$((total_lines - valid_json))
  
  echo "  Total lines: ${total_lines}"
  echo "  Valid JSON objects: ${valid_json}"
  echo "  Invalid lines: ${invalid_lines}"
  
  if [[ $invalid_lines -eq 0 ]]; then
    echo "  ✅ All lines are valid JSON (no corruption)"
  else
    echo "  ⚠️  Found ${invalid_lines} invalid lines (may indicate race condition)"
  fi
  
  # 파싱 가능 여부 확인
  if jq -cr '.' "${test_decisions}" >/dev/null 2>&1; then
    echo "  ✅ File is parseable"
  else
    echo "  ❌ File parsing failed"
  fi
else
  echo "  ⚠️  Test decisions file not found"
fi

# 3. 메트릭 파일 일관성 확인
echo ""
echo "3. Checking metric file consistency..."
if [[ -f "${TEXTFILE_DIR}/l4_weekly_decision.prom" ]]; then
  metric_exists=1
  metric_content=$(cat "${TEXTFILE_DIR}/l4_weekly_decision.prom" 2>/dev/null || echo "")
  
  if grep -qE '^l4_weekly_decision' <<< "$metric_content"; then
    echo "  ✅ Metric file exists and contains valid data"
    echo "  Content preview:"
    echo "$metric_content" | head -5 | sed 's/^/    /'
  else
    echo "  ⚠️  Metric file exists but content may be incomplete"
  fi
else
  echo "  ⚠️  Metric file not found (may be expected if NODE_EXPORTER_TEXTFILE_DIR not set)"
fi

# 4. 락 파일 정리 확인
echo ""
echo "4. Checking lock file cleanup..."
lock_file="${AUDIT_DIR}/decisions.lock"
if [[ -f "${lock_file}" ]]; then
  # 락 파일이 남아있는지 확인 (프로세스가 죽어서 남은 경우)
  if lsof "${lock_file}" >/dev/null 2>&1; then
    echo "  ⚠️  Lock file is still held by a process"
  else
    echo "  ✅ Lock file is not held (cleanup successful)"
  fi
else
  echo "  ✅ No lock file found (cleanup successful)"
fi

# 5. 최종 검증: decisions.ndjson 파싱 가능 여부
echo ""
echo "5. Final validation: parsing test decisions..."
if [[ -f "${test_decisions}" ]] && [[ -s "${test_decisions}" ]]; then
  if jq -rs 'length > 0' "${test_decisions}" >/dev/null 2>&1; then
    decision_count=$(jq -rs 'length' "${test_decisions}" 2>/dev/null || echo 0)
    echo "  ✅ Successfully parsed ${decision_count} decisions"
    
    # 최신 결정 확인
    latest=$(jq -rs 'sort_by(.ts) | reverse | .[0].decision // empty' "${test_decisions}" 2>/dev/null || echo "")
    if [[ -n "$latest" ]]; then
      echo "  ✅ Latest decision: ${latest}"
    fi
  else
    echo "  ❌ Failed to parse decisions (corruption detected)"
  fi
fi

# 정리
rm -f "${test_decisions}" "${TEXTFILE_DIR}/l4_weekly_decision.prom" 2>/dev/null || true

echo ""
echo "=== Resilience Test Complete ==="
echo ""
echo "Summary:"
echo "  - NDJSON integrity: $([ $invalid_lines -eq 0 ] && echo 'PASS' || echo 'FAIL')"
echo "  - Metric consistency: $([ -n "${metric_content:-}" ] && echo 'PASS' || echo 'SKIP')"
echo "  - Lock cleanup: $([ ! -f "${lock_file}" ] || ! lsof "${lock_file}" >/dev/null 2>&1 && echo 'PASS' || echo 'FAIL')"

