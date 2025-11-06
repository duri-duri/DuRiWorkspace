#!/usr/bin/env bash
# PR Label Auto-Fix - 라벨 정책 자동 적용
# Purpose: PR 라벨을 자동으로 정리하여 ab-label-integrity 통과 보장
# Usage: scripts/ops/ci_fix_label_and_ready.sh [PR_NUMBER]

set -euo pipefail

PR_NUMBER="${1:-${PR_NUMBER:-$(gh pr list --head day20-l4-finalize --json number -q '.[].number' 2>/dev/null | head -1)}}"

if [[ -z "$PR_NUMBER" ]]; then
  echo "[ERROR] PR number required"
  exit 1
fi

echo "=== PR Label Auto-Fix for PR #$PR_NUMBER ==="

# 1. 현재 라벨 확인
CURRENT_LABELS=$(gh pr view "$PR_NUMBER" --json labels -q '.labels[].name' 2>/dev/null || echo "")
echo "Current labels: $CURRENT_LABELS"

# 2. safe-change 확인
if echo "$CURRENT_LABELS" | grep -q "safe-change"; then
  echo "[POLICY] safe-change detected → requires ab:none"
  
  # ab:A/ab:B 제거
  if echo "$CURRENT_LABELS" | grep -q "ab:A\|ab:B"; then
    echo "  Removing ab:A/ab:B"
    gh pr edit "$PR_NUMBER" --remove-label "ab:A" 2>/dev/null || true
    gh pr edit "$PR_NUMBER" --remove-label "ab:B" 2>/dev/null || true
  fi
  
  # ab:none 추가
  if ! echo "$CURRENT_LABELS" | grep -q "ab:none"; then
    echo "  Adding ab:none"
    gh label create "ab:none" --color FFD700 --description "No AB variant" 2>/dev/null || true
    gh pr edit "$PR_NUMBER" --add-label "ab:none"
  fi
fi

# 3. 필수 라벨 확인 및 추가
REQUIRED_LABELS=("type:ops" "area:observability" "size:M")

for label in "${REQUIRED_LABELS[@]}"; do
  if ! echo "$CURRENT_LABELS" | grep -q "$label"; then
    label_name=$(echo "$label" | cut -d: -f1)
    label_value=$(echo "$label" | cut -d: -f2)
    
    case "$label_name" in
      type)
        gh label create "$label" --color 0366d6 --description "Type: $label_value" 2>/dev/null || true
        ;;
      area)
        gh label create "$label" --color 0e8a16 --description "Area: $label_value" 2>/dev/null || true
        ;;
      size)
        gh label create "$label" --color fbca04 --description "Size: $label_value" 2>/dev/null || true
        ;;
    esac
    
    echo "  Adding $label"
    gh pr edit "$PR_NUMBER" --add-label "$label"
  fi
done

# 4. 최종 라벨 확인
FINAL_LABELS=$(gh pr view "$PR_NUMBER" --json labels -q '.labels[].name' 2>/dev/null || echo "")
echo ""
echo "Final labels: $FINAL_LABELS"
echo ""
echo "✅ Label fix complete"

# 5. Draft 해제 제안
PR_STATE=$(gh pr view "$PR_NUMBER" --json isDraft -q '.isDraft' 2>/dev/null || echo "false")
if [[ "$PR_STATE" == "true" ]]; then
  echo ""
  echo "💡 PR is in Draft state. To make it ready for review:"
  echo "   gh pr ready $PR_NUMBER"
fi

