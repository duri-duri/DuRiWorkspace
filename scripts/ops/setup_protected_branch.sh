#!/usr/bin/env bash
# Protected Branch 강제 적용 스크립트 (JSON 방식)
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

# JSON 파일 생성
TMP_JSON=$(mktemp)
cat > "$TMP_JSON" <<EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "obs-lint",
      "sandbox-smoke-60s",
      "promql-unit",
      "dr-rehearsal-24h-pass",
      "canary-quorum-pass",
      "error-budget-burn-ok"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "require_code_owner_reviews": true,
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_linear_history": true
}
EOF

# Protected Branch 설정 강제 적용
log "Applying Protected Branch settings..."
if gh api \
  -X PUT "repos/$OWNER/$REPO/branches/$BR/protection" \
  -H "Accept: application/vnd.github+json" \
  --input "$TMP_JSON" >/dev/null 2>&1; then
  log "[OK] Protected Branch settings applied"
  rm -f "$TMP_JSON"
else
  log "[WARN] Protected Branch API call failed. Using manual method."
  log ""
  log "Please run manually:"
  log "  gh api -X PUT 'repos/$OWNER/$REPO/branches/$BR/protection' \\"
  log "    -H 'Accept: application/vnd.github+json' \\"
  log "    --input <(cat <<'JSON'"
  cat "$TMP_JSON"
  log "JSON"
  log ")"
  rm -f "$TMP_JSON"
  exit 1
fi

# 확인
log ""
log "=== Verification ==="
VERIFICATION=$(gh api "repos/$OWNER/$REPO/branches/$BR/protection" 2>/dev/null || echo "{}")

echo "$VERIFICATION" | jq '{enforce_admins, required_status_checks: .required_status_checks.contexts}' 2>/dev/null || echo "$VERIFICATION"

CONTEXTS=$(echo "$VERIFICATION" | jq -r '.required_status_checks.contexts[]? // empty' 2>/dev/null || echo "")
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
  log ""
  log "Note: If you don't have admin permissions, please configure Protected Branch manually:"
  log "  Settings → Branches → Add rule → main"
  exit 1
fi
