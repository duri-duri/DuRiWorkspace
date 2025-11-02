#!/usr/bin/env bash
# Protected Branch 강제 적용 스크립트
# Purpose: GitHub API로 Protected Branch 설정 강제 적용
# Usage: bash scripts/ops/setup_protected_branch.sh

set -euo pipefail

OWNER="${OWNER:-duri-duri}"
REPO="${REPO:-DuRiWorkspace}"
BR="${BR:-main}"

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*" >&2
}

log "=== Protected Branch 강제 적용 ==="
log "Repository: $OWNER/$REPO"
log "Branch: $BR"

if ! command -v gh >/dev/null 2>&1; then
  log "[FAIL] GitHub CLI (gh) not found. Install: https://cli.github.com/"
  exit 1
fi

# Protected Branch 설정 강제 적용
log "Applying Protected Branch settings..."
gh api \
  -X PUT "repos/$OWNER/$REPO/branches/$BR/protection" \
  -H "Accept: application/vnd.github+json" \
  -f required_status_checks='{"strict":true,"contexts":["obs-lint","sandbox-smoke-60s","promql-unit","dr-rehearsal-24h-pass","canary-quorum-pass","error-budget-burn-ok"]}' \
  -f enforce_admins=true \
  -f required_pull_request_reviews='{"require_code_owner_reviews":true,"required_approving_review_count":1}' \
  -f allow_force_pushes=false \
  -f allow_deletions=false \
  -f required_linear_history=true

log "[OK] Protected Branch settings applied"

# 확인
log ""
log "=== Verification ==="
VERIFICATION=$(gh api "repos/$OWNER/$REPO/branches/$BR/protection" | jq '{enforce_admins, required_status_checks: .required_status_checks.contexts}')

echo "$VERIFICATION" | jq '.'

CONTEXTS=$(echo "$VERIFICATION" | jq -r '.required_status_checks[] // empty')
REQUIRED_LIST=("obs-lint" "sandbox-smoke-60s" "promql-unit" "dr-rehearsal-24h-pass" "canary-quorum-pass" "error-budget-burn-ok")

log ""
log "Checking required checks..."
MISSING=0
for check in "${REQUIRED_LIST[@]}"; do
  if echo "$CONTEXTS" | grep -q "^${check}$"; then
    log "  ✅ $check"
  else
    log "  ❌ $check (MISSING)"
    MISSING=1
  fi
done

if [ "$MISSING" -eq 0 ]; then
  log "[OK] All 6 required checks configured"
  exit 0
else
  log "[FAIL] Some required checks missing"
  exit 1
fi

