#!/usr/bin/env bash
set -euo pipefail

# usage:
#   bash scripts/ops/protection_apply.sh <owner/repo> snapshot  /tmp/snap.json
#   bash scripts/ops/protection_apply.sh <owner/repo> relax     /tmp/snap.json
#   bash scripts/ops/protection_apply.sh <owner/repo> restore   /tmp/snap.json
#
# env:
#   PROTECTION_ADMIN_TOKEN: repo admin 권한 토큰 (필수, 없으면 GITHUB_TOKEN 사용)

REPO="${1:?owner/repo}"; CMD="${2:?snapshot|relax|restore}"; SNAP="${3:?path}"
API="https://api.github.com/repos/${REPO}/branches/main/protection"

TS() { date "+%F %T"; }
log() { echo "[$(TS)] $*"; }
die() { log "[FATAL] $*"; exit 1; }

auth() {
  TOKEN="${PROTECTION_ADMIN_TOKEN:-${GITHUB_TOKEN:-}}"
  if [[ -z "$TOKEN" ]]; then
    die "PROTECTION_ADMIN_TOKEN or GITHUB_TOKEN not set"
  fi
  echo "-H" "Authorization: token ${TOKEN}" "-H" "Accept: application/vnd.github+json"
}

# API 호출 재시도 함수 (지수 백오프)
api_call_with_retry() {
  local method="${1:-GET}"
  local url="$2"
  local data_file="${3:-}"
  local max_retries=5
  local retry=1
  
  while [ $retry -le $max_retries ]; do
    if [ "$method" = "PUT" ] && [ -n "$data_file" ]; then
      if curl -sS -X PUT $(auth) --data @"$data_file" "$url" | jq -e . >/dev/null 2>&1; then
        return 0
      fi
    else
      if curl -sS $(auth) "$url" | jq -e . >/dev/null 2>&1; then
        return 0
      fi
    fi
    
    if [ $retry -lt $max_retries ]; then
      local delay=$((2**retry))
      log "API call failed, retrying in ${delay}s (attempt $retry/$max_retries)..."
      sleep $delay
    fi
    retry=$((retry + 1))
  done
  
  die "API call failed after $max_retries retries"
}

snapshot() {
  log "snapshot -> ${SNAP}"
  api_call_with_retry GET "${API}" > "${SNAP}"
  jq -e . "${SNAP}" >/dev/null || die "invalid snapshot JSON"
  log "snapshot saved"
  cat "${SNAP}" | jq '{approvals: .required_pull_request_reviews.required_approving_review_count, code_owner: .required_pull_request_reviews.require_code_owner_reviews, contexts: .required_status_checks.contexts}'
}

relax() {
  log "relax using ${SNAP}"
  [[ -f "$SNAP" ]] || die "snapshot file not found: ${SNAP}"
  
  # 최소 변경: approvals=0, codeowner=false. 나머지는 스냅샷의 contexts 유지(안전)
  CTX=$(jq -r '.required_status_checks.contexts // []' "${SNAP}")
  ENFORCE_ADMINS=$(jq -r '.enforce_admins.enabled // true' "${SNAP}")
  CONV_RESOLVE=$(jq -r '.required_conversation_resolution.enabled // true' "${SNAP}")
  LINEAR_HIST=$(jq -r '.required_linear_history.enabled // true' "${SNAP}")
  
  cat > /tmp/relax.json <<JSON
{
  "required_status_checks": {"strict": true, "contexts": ${CTX}},
  "enforce_admins": ${ENFORCE_ADMINS},
  "required_pull_request_reviews": {"required_approving_review_count": 0, "require_code_owner_reviews": false},
  "required_conversation_resolution": ${CONV_RESOLVE},
  "required_linear_history": ${LINEAR_HIST},
  "restrictions": null
}
JSON
  
  api_call_with_retry PUT "${API}" "/tmp/relax.json" || die "relax API failed"
  log "relax applied"
  curl -sS $(auth) "${API}" | jq '{approvals: .required_pull_request_reviews.required_approving_review_count, code_owner: .required_pull_request_reviews.require_code_owner_reviews}'
}

restore() {
  log "restore from ${SNAP}"
  [[ -f "$SNAP" ]] || die "snapshot file not found: ${SNAP}"
  
  api_call_with_retry PUT "${API}" "${SNAP}" || die "restore API failed"
  log "protection restored"
  curl -sS $(auth) "${API}" | jq '{approvals: .required_pull_request_reviews.required_approving_review_count, code_owner: .required_pull_request_reviews.require_code_owner_reviews, admins: .enforce_admins.enabled}'
}

case "${CMD}" in
  snapshot) snapshot ;;
  relax)    relax ;;
  restore) restore ;;
  *) die "bad cmd: ${CMD}. Use: snapshot|relax|restore" ;;
esac

