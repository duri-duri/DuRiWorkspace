#!/usr/bin/env bash
# 브랜치 보호 설정 완화/복원 원자화 스크립트
# Usage: bash scripts/ops/protection_apply.sh <owner/repo> <relax|restore> [snapshot_path]
set -euo pipefail

REPO="${1:?owner/repo required}"
MODE="${2:?relax|restore required}"
SNAPSHOT="${3:-/tmp/protection_snapshot_latest.json}"

BRANCH="${BRANCH:-main}"

# restore 모드는 사전 스냅샷 필수
if [[ "$MODE" == "restore" ]]; then
  if [[ ! -s "$SNAPSHOT" ]]; then
    echo "[ERROR] restore에는 pre-relax 스냅샷이 필요합니다: $SNAPSHOT" >&2
    echo "[ERROR] relax 전에 생성한 스냅샷 경로를 3번째 인자로 전달하세요." >&2
    exit 3
  fi
fi

# relax 모드는 항상 새로운 스냅샷 생성 (사전 상태 보존)
if [[ "$MODE" == "relax" ]]; then
  echo "[INFO] Creating pre-relax snapshot: $SNAPSHOT"
  gh api "repos/${REPO}/branches/${BRANCH}/protection" > "$SNAPSHOT"
fi

# 목적별 구성 생성
TMP_JSON="/tmp/protection_apply_$$.json"
case "$MODE" in
  relax)
    echo "[INFO] Creating relax payload..."
    jq '{
      required_status_checks: { strict: true, contexts: (.required_status_checks.contexts // []) },
      enforce_admins: true,
      required_pull_request_reviews: {
        required_approving_review_count: 0,
        require_code_owner_reviews: false
      },
      required_conversation_resolution: true,
      required_linear_history: true,
      restrictions: null
    }' "$SNAPSHOT" > "$TMP_JSON"
    ;;
  restore)
    echo "[INFO] Creating restore payload from snapshot: $SNAPSHOT"
    jq '{
      required_status_checks: { strict: true, contexts: (.required_status_checks.contexts // []) },
      enforce_admins: (.enforce_admins.enabled // true),
      required_pull_request_reviews: {
        # 최소 1명 하한 보장 (스냅샷이 0이어도 안전)
        required_approving_review_count: ((.required_pull_request_reviews.required_approving_review_count // 1) | if . < 1 then 1 else . end),
        require_code_owner_reviews: (.required_pull_request_reviews.require_code_owner_reviews // true)
      },
      required_conversation_resolution: (.required_conversation_resolution.enabled // true),
      required_linear_history: (.required_linear_history.enabled // true),
      restrictions: null
    }' "$SNAPSHOT" > "$TMP_JSON"
    ;;
  *)
    echo "Usage: $0 <owner/repo> <relax|restore> [snapshot_path]"
    exit 2
    ;;
esac

# 적용
echo "[INFO] Applying $MODE to ${REPO}/branches/${BRANCH}..."
OUTPUT=$(gh api "repos/${REPO}/branches/${BRANCH}/protection" -X PUT --input "$TMP_JSON")
echo "$OUTPUT" | jq '{
      required_pull_request_reviews: {
        required_approving_review_count: .required_pull_request_reviews.required_approving_review_count,
        require_code_owner_reviews: .required_pull_request_reviews.require_code_owner_reviews
      },
      enforce_admins: .enforce_admins.enabled,
      required_conversation_resolution: .required_conversation_resolution.enabled,
      required_linear_history: .required_linear_history.enabled
    }'

# 검증: 기대값 확인
APPROVALS=$(echo "$OUTPUT" | jq -r '.required_pull_request_reviews.required_approving_review_count')
if [[ "$MODE" == "relax" && "$APPROVALS" != "0" ]]; then
  echo "[ERROR] Protection relax verification failed (approvals=$APPROVALS, expected=0)" >&2
  rm -f "$TMP_JSON"
  exit 1
elif [[ "$MODE" == "restore" && "$APPROVALS" -lt 1 ]]; then
  echo "[ERROR] Protection restore verification failed (approvals=$APPROVALS, expected>=1)" >&2
  rm -f "$TMP_JSON"
  exit 1
fi

rm -f "$TMP_JSON"
echo "[OK] Protection $MODE completed and verified"

