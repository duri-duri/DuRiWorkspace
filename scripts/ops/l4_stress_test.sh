#!/usr/bin/env bash
# L4 Parallel Append Stress Test
# Purpose: 병렬 append 스트레스 테스트로 동시성 제어 검증
# Usage: bash scripts/ops/l4_stress_test.sh [iterations] [parallelism]

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo /home/duri/DuRiWorkspace)"
cd "${ROOT}"

ITERATIONS="${1:-1000}"
PARALLELISM="${2:-10}"
AUDIT_DIR="${ROOT}/var/audit"
TEST_DECISIONS="${AUDIT_DIR}/decisions_stress_test.ndjson"
LOG_DIR="${AUDIT_DIR}/logs"
TEXTFILE_DIR="${TEXTFILE_DIR:-/tmp/test_textfile_stress}"

mkdir -p "${LOG_DIR}" "${TEXTFILE_DIR}"

# 백업 및 초기화
if [[ -f "${TEST_DECISIONS}" ]]; then
  mv "${TEST_DECISIONS}" "${TEST_DECISIONS}.backup.$(date +%Y%m%d_%H%M%S)"
fi
> "${TEST_DECISIONS}"

echo "=== L4 Parallel Append Stress Test ==="
echo "Iterations: ${ITERATIONS}"
echo "Parallelism: ${PARALLELISM}"
echo ""

export NODE_EXPORTER_TEXTFILE_DIR="${TEXTFILE_DIR}"

start_time=$(date +%s)

# 병렬 append 실행
for i in $(seq 1 "${ITERATIONS}"); do
  summary="${LOG_DIR}/stress_${i}.log"
  printf "Score: 0.%04d\nDecision: CONTINUE\n" "$i" > "$summary"
  
  (
    score="0.$(printf "%04d" "$i")" decision="CONTINUE" summary="$summary" \
    DECISIONS_NDJSON="${TEST_DECISIONS}" \
    bash scripts/ops/inc/l4_post_decision.sh >/dev/null 2>&1 || true
  ) &
  
  # 병렬도 제어
  if [[ $((i % PARALLELISM)) -eq 0 ]]; then
    wait
  fi
done

# 남은 프로세스 대기
wait

end_time=$(date +%s)
duration=$((end_time - start_time))

echo "✅ Stress test completed in ${duration} seconds"
echo ""

# 결과 검증
echo "=== Validation ==="

# 1. 라인 수 확인
total_lines=$(wc -l < "${TEST_DECISIONS}" 2>/dev/null || echo 0)
echo "Total lines written: ${total_lines}"

# 2. 유효한 JSON 확인
valid_json=$(jq -cr 'select(type=="object" and .ts and .decision)' "${TEST_DECISIONS}" 2>/dev/null | wc -l || echo 0)
invalid_lines=$((total_lines - valid_json))

echo "Valid JSON objects: ${valid_json}"
echo "Invalid lines: ${invalid_lines}"

# 3. 파싱 가능 여부
if jq -rs 'length > 0' "${TEST_DECISIONS}" >/dev/null 2>&1; then
  echo "✅ File is parseable"
else
  echo "❌ File parsing failed"
fi

# 4. 중복 확인 (같은 ts가 여러 개인지)
duplicate_count=$(jq -rs 'group_by(.ts) | map(select(length > 1)) | length' "${TEST_DECISIONS}" 2>/dev/null || echo 0)
if [[ $duplicate_count -eq 0 ]]; then
  echo "✅ No duplicate timestamps detected"
else
  echo "⚠️  Found ${duplicate_count} duplicate timestamp groups"
fi

# 5. 타임스탬프 정렬 확인
sorted_count=$(jq -rs 'sort_by(.ts) | length' "${TEST_DECISIONS}" 2>/dev/null || echo 0)
if [[ $sorted_count -eq $total_lines ]]; then
  echo "✅ All entries are sortable by timestamp"
else
  echo "⚠️  Sorting mismatch: sorted=${sorted_count}, total=${total_lines}"
fi

# 6. 성공률 계산
success_rate=$(awk -v v="$valid_json" -v t="$ITERATIONS" 'BEGIN{printf "%.2f", (v/t)*100}')
echo ""
echo "Success rate: ${success_rate}% (${valid_json}/${ITERATIONS})"

# 정리
rm -f "${TEST_DECISIONS}" "${TEXTFILE_DIR}/l4_weekly_decision.prom" 2>/dev/null || true

echo ""
echo "=== Stress Test Complete ==="

