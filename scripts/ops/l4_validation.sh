#!/usr/bin/env bash
# L4 Validation Routines
# Purpose: 5-minute smoke test for L4 automation hardening

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo /home/duri/DuRiWorkspace)"
cd "${ROOT}"

AUDIT_DIR="${ROOT}/var/audit"
DECISIONS="${AUDIT_DIR}/decisions.ndjson"
TEXTFILE_DIR="${TEXTFILE_DIR:-/tmp/test_textfile}"

echo "=== L4 Validation Routines ==="
echo ""

# 1. HOLD→메트릭 반영 테스트
echo "1. Testing HOLD→metric reflection..."
export NODE_EXPORTER_TEXTFILE_DIR="${TEXTFILE_DIR}"
mkdir -p "${NODE_EXPORTER_TEXTFILE_DIR}"

summary="${AUDIT_DIR}/logs/test_hold.log"
mkdir -p "$(dirname "$summary")"
printf "Score: 0.00\nDecision: HOLD\n" > "$summary"

score=0 decision=HOLD summary="$summary" bash scripts/ops/inc/l4_post_decision.sh || true

if grep -qE '^l4_weekly_decision -1$' "${TEXTFILE_DIR}/l4_weekly_decision.prom" 2>/dev/null; then
  echo "  ✅ HOLD metric correctly reflected (-1)"
else
  echo "  ❌ HOLD metric not found or incorrect"
fi

# 2. NDJSON 라인 무결성 테스트
echo ""
echo "2. Testing NDJSON line integrity..."
if [[ -f "${DECISIONS}" ]]; then
  line_count=$(wc -l < "${DECISIONS}" 2>/dev/null || echo 0)
  echo "  Total lines: ${line_count}"
  
  # 첫 번째 유효한 JSON 라인 확인
  first_ts=$(jq -cr 'select(type=="object" and .ts)|.ts' "${DECISIONS}" 2>/dev/null | head -1 || echo "")
  if [[ -n "$first_ts" ]]; then
    echo "  ✅ First valid timestamp: ${first_ts}"
  else
    echo "  ⚠️  No valid timestamps found"
  fi
  
  # 모든 라인이 유효한 JSON인지 확인
  invalid_count=$(jq -cr 'select(type!="object")' "${DECISIONS}" 2>/dev/null | wc -l || echo 0)
  if [[ $invalid_count -eq 0 ]]; then
    echo "  ✅ All lines are valid JSON objects"
  else
    echo "  ⚠️  Found ${invalid_count} invalid lines"
  fi
else
  echo "  ⚠️  decisions.ndjson not found (initial state)"
fi

# 3. 타임스탬프 정렬 테스트 (ts,seq) 2중 키 기준
echo ""
echo "3. Testing timestamp sorting (ts,seq) dual-key..."
if [[ -f "${DECISIONS}" ]]; then
  sorted_count=$(jq -rs 'sort_by([.ts, (.seq // 0)]) | length' "${DECISIONS}" 2>/dev/null || echo 0)
  unsorted_count=$(wc -l < "${DECISIONS}" 2>/dev/null || echo 0)
  
  if [[ $sorted_count -eq $unsorted_count ]]; then
    echo "  ✅ All ${sorted_count} entries sortable by (ts,seq)"
  else
    echo "  ⚠️  Sorting mismatch: sorted=${sorted_count}, total=${unsorted_count}"
  fi
  
  # (ts,seq) 기준 정렬 위반 검사
  violation_count=$(jq -cr 'select(type=="object" and .ts and .seq)|[.ts,.seq]|@tsv' "${DECISIONS}" 2>/dev/null | \
    awk 'BEGIN{prev_ts=""; prev_seq=-1; violations=0}
    {
      ts=$1; seq=$2+0;
      if (prev_ts!="" && (ts<prev_ts || (ts==prev_ts && seq<prev_seq))) { violations++ }
      prev_ts=ts; prev_seq=seq
    }
    END{print violations}' || echo 0)
  
  if [[ $violation_count -eq 0 ]]; then
    echo "  ✅ No sorting violations detected (ts,seq)"
  else
    echo "  ❌ Found ${violation_count} sorting violations"
  fi
  
  # 최신 결정 확인
  latest=$(jq -rs 'sort_by([.ts, (.seq // 0)]) | reverse | .[0].decision // empty' "${DECISIONS}" 2>/dev/null || echo "")
  if [[ -n "$latest" ]]; then
    echo "  ✅ Latest decision: ${latest}"
  else
    echo "  ⚠️  Could not extract latest decision"
  fi
else
  echo "  ⚠️  decisions.ndjson not found (initial state)"
fi

# 4. 원자적 쓰기 테스트 (간단 버전)
echo ""
echo "4. Testing atomic write (textfile metrics)..."
if [[ -f "${TEXTFILE_DIR}/l4_weekly_decision.prom" ]]; then
  # 파일이 완전한지 확인 (마지막 줄이 비어있지 않음)
  if tail -1 "${TEXTFILE_DIR}/l4_weekly_decision.prom" | grep -qE '^l4_weekly_decision_info'; then
    echo "  ✅ Metric file appears complete"
  else
    echo "  ⚠️  Metric file may be incomplete"
  fi
else
  echo "  ⚠️  Metric file not found (may be expected if not configured)"
fi

# 5. 타이머 오케스트레이션 확인
echo ""
echo "5. Checking timer orchestration..."
timer_count=$(systemctl --user list-timers --all 2>/dev/null | grep -cE 'l4-(daily-quick|daily|shadow-replay|weekly)' || echo 0)
if [[ $timer_count -ge 3 ]]; then
  echo "  ✅ Found ${timer_count} L4 timers"
  systemctl --user list-timers --all 2>/dev/null | grep -E 'l4-(daily-quick|daily|shadow-replay|weekly)' || true
else
  echo "  ⚠️  Expected at least 3 timers, found ${timer_count}"
fi

echo ""
echo "=== Validation Complete ==="

