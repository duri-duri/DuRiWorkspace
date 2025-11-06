#!/usr/bin/env bash
# L4 Operational Checklist
# Purpose: Quick checklist for operational readiness
# Usage: bash scripts/ops/l4_operational_checklist.sh

set -euo pipefail

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*"
}

check_item() {
  local name="$1"
  local cmd="$2"
  
  echo -n "  [ ] $name: "
  if eval "$cmd" >/dev/null 2>&1; then
    echo "✅"
    return 0
  else
    echo "❌"
    return 1
  fi
}

log "=== L4 Operational Checklist ==="
log ""

PASS=0
TOTAL=0

log "1. 시크릿 설정:"
TOTAL=$((TOTAL + 1))
if check_item "PROMETHEUS_URL 설정" \
  "[ -n \"\${PROMETHEUS_URL:-}\" ] || gh secret list | grep -q PROMETHEUS_URL"; then
  PASS=$((PASS + 1))
fi

TOTAL=$((TOTAL + 1))
if check_item "SLO 설정 파일 존재" \
  "[ -f .slo/auto_relax.yml ]"; then
  PASS=$((PASS + 1))
fi

log ""
log "2. 워크플로우 파일:"
TOTAL=$((TOTAL + 1))
if check_item "l4-post-merge-quality-watch.yml" \
  "[ -f .github/workflows/l4-post-merge-quality-watch.yml ]"; then
  PASS=$((PASS + 1))
fi

TOTAL=$((TOTAL + 1))
if check_item "l4-auto-rollback.yml" \
  "[ -f .github/workflows/l4-auto-rollback.yml ]"; then
  PASS=$((PASS + 1))
fi

TOTAL=$((TOTAL + 1))
if check_item "policy-learning-loop.yml" \
  "[ -f .github/workflows/policy-learning-loop.yml ]"; then
  PASS=$((PASS + 1))
fi

log ""
log "3. 스크립트 실행 권한:"
TOTAL=$((TOTAL + 1))
if check_item "prom_query.sh 실행 가능" \
  "[ -x scripts/ops/prom_query.sh ]"; then
  PASS=$((PASS + 1))
fi

TOTAL=$((TOTAL + 1))
if check_item "policy_learning_loop.py 실행 가능" \
  "[ -x scripts/evolution/policy_learning_loop.py ]"; then
  PASS=$((PASS + 1))
fi

log ""
log "4. Rulepack 구조:"
TOTAL=$((TOTAL + 1))
if check_item "rulepack 디렉토리 존재" \
  "[ -d rulepack ]"; then
  PASS=$((PASS + 1))
fi

TOTAL=$((TOTAL + 1))
if check_item "rulepack 시나리오 파일" \
  "[ -f rulepack/safe-docs.yml ]"; then
  PASS=$((PASS + 1))
fi

log ""
log "5. 감사 디렉토리:"
TOTAL=$((TOTAL + 1))
if check_item "audit 디렉토리 존재" \
  "[ -d docs/ops/audit ]"; then
  PASS=$((PASS + 1))
fi

log ""
log "=== 체크리스트 결과 ==="
log "통과: $PASS/$TOTAL"

if [ $PASS -eq $TOTAL ]; then
  log "✅ 모든 체크리스트 항목 통과"
  exit 0
else
  log "⚠️  일부 항목 실패 ($((TOTAL - PASS))개)"
  exit 1
fi

