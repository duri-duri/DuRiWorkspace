#!/usr/bin/env bash
# L4 Evaluation Script - 현재 상태 평가
# Purpose: Auto Relax Merge Restore 워크플로우의 L4 준수도 평가
# Usage: bash scripts/ops/l4_evaluation.sh

set -euo pipefail

REPO="${REPO:-$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "duri-duri/DuRiWorkspace")}"
BASE_BRANCH="${BASE_BRANCH:-main}"

# 색상 출력
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*"
}

check() {
  local name="$1"
  local desc="$2"
  local cmd="$3"
  
  echo -n "  [ ] $name: "
  if eval "$cmd" >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} $desc"
    return 0
  else
    echo -e "${RED}✗${NC} $desc"
    return 1
  fi
}

log "=== L4 Evaluation: Auto Relax Merge Restore ==="
log "Repository: $REPO"
log ""

# L4 최소충분조건 체크
PASS=0
TOTAL=0

log "1. 정합성 게이트 (Hard Gates):"
TOTAL=$((TOTAL + 1))
if check "6중 게이트" "라벨, base, status, merge state, 경로, contexts 검증" \
  "grep -q 'Hard gate.*validate conditions' .github/workflows/auto-relax-merge-restore.yml"; then
  PASS=$((PASS + 1))
fi

TOTAL=$((TOTAL + 1))
if check "경로 allowlist" "docs/, prometheus/rules/, scripts/ops/, scripts/bin/, .github/workflows/ 검증" \
  "grep -q 'Path allowlist check' .github/workflows/auto-relax-merge-restore.yml"; then
  PASS=$((PASS + 1))
fi

TOTAL=$((TOTAL + 1))
if check "Fork PR 차단" "isCrossRepository 확인" \
  "grep -q 'Deny forked PR' .github/workflows/auto-relax-merge-restore.yml"; then
  PASS=$((PASS + 1))
fi

TOTAL=$((TOTAL + 1))
if check "Actor 화이트리스트" "코멘트 트리거 권한 확인" \
  "grep -q 'Comment author allowlist' .github/workflows/auto-relax-merge-restore.yml"; then
  PASS=$((PASS + 1))
fi

log ""
log "2. 실행 원자성 (Atomicity):"
TOTAL=$((TOTAL + 1))
if check "3중 복원" "trap + always() + final safety net" \
  "grep -c 'if: always()' .github/workflows/auto-relax-merge-restore.yml | grep -q '^[3-9]'"; then
  PASS=$((PASS + 1))
fi

TOTAL=$((TOTAL + 1))
if check "Idempotency 가드" "이미 머지/닫힌 PR 스킵" \
  "grep -q 'Idempotency guard' .github/workflows/auto-relax-merge-restore.yml"; then
  PASS=$((PASS + 1))
fi

TOTAL=$((TOTAL + 1))
if check "Concurrency 그룹" "동시 실행 방지" \
  "grep -q 'concurrency:' .github/workflows/auto-relax-merge-restore.yml"; then
  PASS=$((PASS + 1))
fi

log ""
log "3. 사후 검증 (Post-Verification):"
TOTAL=$((TOTAL + 1))
if check "머지 검증" "merge commit 확인" \
  "grep -q 'Verify merge.*protection restore' .github/workflows/auto-relax-merge-restore.yml"; then
  PASS=$((PASS + 1))
fi

TOTAL=$((TOTAL + 1))
if check "보호 설정 검증" "approvals 복원 확인" \
  "grep -q 'Verify restored' .github/workflows/auto-relax-merge-restore.yml"; then
  PASS=$((PASS + 1))
fi

log ""
log "4. 감사/재현 (Audit/Reproducibility):"
TOTAL=$((TOTAL + 1))
if check "Artifact 업로드" "스냅샷 artifact 저장" \
  "grep -q 'Upload snapshot artifact' .github/workflows/auto-relax-merge-restore.yml"; then
  PASS=$((PASS + 1))
fi

TOTAL=$((TOTAL + 1))
if check "감사 디렉토리" "docs/ops/audit/ 존재" \
  "[ -d docs/ops/audit ]"; then
  PASS=$((PASS + 1))
fi

TOTAL=$((TOTAL + 1))
if check "결과 코멘트" "PR에 결과 코멘트 남김" \
  "grep -q 'Mark PR.*comment' .github/workflows/auto-relax-merge-restore.yml"; then
  PASS=$((PASS + 1))
fi

log ""
log "5. 네트워크 안정성 (Network Resilience):"
TOTAL=$((TOTAL + 1))
if check "재시도 로직" "지수 백오프 재시도" \
  "grep -q 'api_call_with_retry\|retry' scripts/ops/protection_apply.sh"; then
  PASS=$((PASS + 1))
fi

log ""
log "6. 사후 품질 감시 (Post-Merge Quality Watch):"
TOTAL=$((TOTAL + 1))
if check "SLO 감시" "머지 후 SLO 모니터링" \
  "grep -q 'SLO\|error.*budget\|post.*merge.*quality' .github/workflows/auto-relax-merge-restore.yml"; then
  PASS=$((PASS + 1))
else
  echo -e "  ${YELLOW}⚠${NC} 미구현: 머지 후 SLO 감시 필요"
fi

TOTAL=$((TOTAL + 1))
if check "자동 롤백" "SLO 위반 시 자동 롤백" \
  "grep -q 'auto.*rollback\|rollback.*workflow' .github/workflows/auto-relax-merge-restore.yml"; then
  PASS=$((PASS + 1))
else
  echo -e "  ${YELLOW}⚠${NC} 미구현: 자동 롤백 메커니즘 필요"
fi

log ""
log "6. 사후 품질 감시 (Post-Merge Quality Watch):"
TOTAL=$((TOTAL + 1))
if check "SLO 감시" "머지 후 SLO 모니터링" \
  "[ -f .github/workflows/l4-post-merge-quality-watch.yml ]"; then
  PASS=$((PASS + 1))
else
  echo -e "  ${YELLOW}⚠${NC} 미구현: 머지 후 SLO 감시 필요"
fi

TOTAL=$((TOTAL + 1))
if check "자동 롤백" "SLO 위반 시 자동 롤백" \
  "[ -f .github/workflows/l4-auto-rollback.yml ]"; then
  PASS=$((PASS + 1))
else
  echo -e "  ${YELLOW}⚠${NC} 미구현: 자동 롤백 메커니즘 필요"
fi

log ""
log "7. 정책 러닝 루프 (Policy Learning Loop):"
TOTAL=$((TOTAL + 1))
if check "정책 러닝 루프" "실패 분류 및 정책 업데이트" \
  "[ -f .github/workflows/policy-learning-loop.yml ]"; then
  PASS=$((PASS + 1))
else
  echo -e "  ${YELLOW}⚠${NC} 미구현: 정책 러닝 루프 필요"
fi

log ""
log "8. 다중 시나리오 일반화 (Multi-Scenario Generalization):"
TOTAL=$((TOTAL + 1))
if check "룰팩 구조" "rulepack/*.yml 파일 존재" \
  "[ -d rulepack ] && ls rulepack/*.yml >/dev/null 2>&1"; then
  PASS=$((PASS + 1))
else
  echo -e "  ${YELLOW}⚠${NC} 미구현: rulepack 구조 필요"
fi

TOTAL=$((TOTAL + 1))
if check "룰팩 통합" "게이트에서 rulepack 적용" \
  "grep -q 'Load rulepack\|rulepack' .github/workflows/auto-relax-merge-restore.yml"; then
  PASS=$((PASS + 1))
else
  echo -e "  ${YELLOW}⚠${NC} 미구현: 게이트에서 rulepack 통합 필요"
fi

log ""
log "7. 정책 러닝 루프 (Policy Learning Loop):"
TOTAL=$((TOTAL + 1))
if check "실패 분류" "실패 원인 자동 분류" \
  "grep -q 'failure.*classification\|label.*failure' .github/workflows/auto-relax-merge-restore.yml"; then
  PASS=$((PASS + 1))
else
  echo -e "  ${YELLOW}⚠${NC} 미구현: 실패 분류 및 정책 업데이트 필요"
fi

log ""
log "=== 평가 결과 ==="
SCORE=$(echo "scale=2; $PASS * 100 / $TOTAL" | bc)
log "통과: $PASS/$TOTAL"
log "점수: ${SCORE}%"

if (( $(echo "$SCORE >= 90" | bc -l) )); then
  log -e "${GREEN}판정: L4 준수 (단일 시나리오)${NC}"
elif (( $(echo "$SCORE >= 70" | bc -l) )); then
  log -e "${YELLOW}판정: L3.9 (L4 근접, 단일 시나리오)${NC}"
elif (( $(echo "$SCORE >= 50" | bc -l) )); then
  log -e "${YELLOW}판정: L3.5-3.8 (부분 준수)${NC}"
else
  log -e "${RED}판정: L3 이하 (보강 필요)${NC}"
fi

log ""
log "=== 다음 단계 제안 ==="
if (( $(echo "$SCORE < 90" | bc -l) )); then
  log "1. 사후 품질 SLO 감시 + 자동 롤백 구현"
  log "2. 정책 러닝 루프 구현"
  log "3. 다중 시나리오 일반화"
fi

exit 0

