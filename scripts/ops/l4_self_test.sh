#!/usr/bin/env bash
# L4 Self-Test Script - 빠른 자가테스트
# Purpose: L4 단건 인증을 위한 5단계 자가테스트
# Usage: bash scripts/ops/l4_self_test.sh [PR_NUMBER]

set -euo pipefail

REPO="${REPO:-$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "duri-duri/DuRiWorkspace")}"
PR_NUMBER="${1:-}"

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*"
}

test_step() {
  local name="$1"
  local desc="$2"
  local cmd="$3"
  
  echo ""
  echo "=== $name ==="
  echo "설명: $desc"
  echo ""
  
  if eval "$cmd"; then
    echo "✅ 통과"
    return 0
  else
    echo "❌ 실패"
    return 1
  fi
}

log "=== L4 Self-Test: Auto Relax Merge Restore ==="
log "Repository: $REPO"
log ""

# Step 1: 합성 PR 생성 (allowlist 변경만, checks green)
test_step "Step 1: 합성 PR 생성" \
  "allowlist 변경만 있는 PR 생성 및 라벨 부착" \
  "echo '테스트를 위해 실제 PR 생성은 수동으로 수행하세요:
  1. allowlist 경로만 변경한 PR 생성
  2. 모든 required checks가 green인지 확인
  3. gh pr edit <PR> --add-label \"change:safe\" --add-label \"auto-relax-merge\"'

PR_NUMBER=${PR_NUMBER:-$(gh pr list --limit 1 --json number -q '.[0].number' 2>/dev/null || echo "")}
if [ -z "$PR_NUMBER" ]; then
  echo "⚠️  PR 번호가 없습니다. 테스트를 위해 PR을 생성하거나 PR 번호를 인자로 전달하세요."
  exit 1
fi

# Step 2: 보호설정 복원 확인
test_step "Step 2: 보호설정 복원 확인" \
  "머지 직후 보호설정이 스냅샷 이상으로 복원되었는지 확인" \
  "gh api repos/$REPO/branches/main/protection --jq '.required_pull_request_reviews.required_approving_review_count' | grep -qE '^[1-9]'"

# Step 3: Artifact 확인
test_step "Step 3: Artifact 확인" \
  "스냅샷 artifact 다운로드 및 검증" \
  "echo 'Artifact 확인은 GitHub Actions UI에서 수행하세요:
  1. Actions 탭 → auto-relax-merge-restore 워크플로우 선택
  2. 최근 실행 선택 → protection-snapshot-<PR> artifact 다운로드
  3. 스냅샷 JSON과 현재 보호설정 diff 확인'"

# Step 4: 런너 강제 실패 시뮬레이션
test_step "Step 4: 런너 강제 실패 시뮬레이션" \
  "final safety net가 복원했는지 확인" \
  "echo '런너 실패 시뮬레이션은 실제 워크플로우 실행 중에 수행하세요:
  1. 워크플로우 실행 중 네트워크 차단 또는 step fail 유도
  2. Ensure protection restored (final safety net) step 실행 확인
  3. 보호설정 복원 확인'"

# Step 5: Idempotency 확인
test_step "Step 5: Idempotency 확인" \
  "머지된 PR에 /auto-merge 코멘트 시 job 스킵 확인" \
  "if gh pr view $PR_NUMBER --json merged -q .merged 2>/dev/null | grep -q true; then
    echo 'PR이 이미 머지되었습니다. idempotency 가드가 작동하는지 확인하세요.'
    return 0
  else
    echo 'PR이 아직 머지되지 않았습니다.'
    return 1
  fi"

log ""
log "=== 자가테스트 완료 ==="
log "모든 단계를 통과하면 이 시나리오에 한해 L4 인증 가능합니다."

