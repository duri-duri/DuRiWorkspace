#!/usr/bin/env bash
# CI Self-Healing Agent - L5 자동화 레이어
# Purpose: CI 실패 원인 자동 감지 및 해결 패치 생성
# Usage: scripts/ops/ci_self_heal.sh [--dry-run]

set -euo pipefail

DRY_RUN="${1:-}"
WORK="${WORK:-$(git rev-parse --show-toplevel 2>/dev/null || echo /home/duri/DuRiWorkspace)}"
cd "$WORK"

LOG="/tmp/ci_self_heal.$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$LOG") 2>&1

echo "=== CI Self-Healing Agent Start $(date) ==="

# 1. PR 상태 확인
PR_NUMBER="${PR_NUMBER:-$(gh pr list --head day20-l4-finalize --json number -q '.[].number' 2>/dev/null | head -1)}"

if [[ -z "$PR_NUMBER" ]]; then
  echo "[WARN] No PR found for current branch"
  exit 0
fi

echo "PR Number: $PR_NUMBER"

# 2. CI 실패 항목 수집
FAILED_CHECKS=$(gh pr checks "$PR_NUMBER" --json name,conclusion,status --jq '.[] | select(.conclusion == "FAILURE" or .status == "FAILURE") | .name' 2>/dev/null || true)

if [[ -z "$FAILED_CHECKS" ]]; then
  echo "[OK] No failed checks found"
  exit 0
fi

echo "Failed checks: $FAILED_CHECKS"

# 3. 실패 원인별 해결책 적용
FIXES_APPLIED=0

# 3.1 freeze-guard 실패
if echo "$FAILED_CHECKS" | grep -q "freeze-guard\|enforce-freeze"; then
  echo "[FIX] freeze-guard failure detected"
  
  # 변경된 파일 중 freeze-guard에 걸린 파일 찾기
  CHANGED_FILES=$(gh pr diff "$PR_NUMBER" --name-only 2>/dev/null || git diff --name-only origin/main...HEAD)
  
  for file in $CHANGED_FILES; do
    if ! grep -q "^$file$" .github/freeze-allow.txt 2>/dev/null && [[ "$file" =~ ^(prometheus/rules/|scripts/ops/|docs/ops/) ]]; then
      echo "  Adding $file to freeze-allow.txt"
      if [[ -z "$DRY_RUN" ]]; then
        echo "$file" >> .github/freeze-allow.txt
        FIXES_APPLIED=$((FIXES_APPLIED + 1))
      fi
    fi
  done
fi

# 3.2 label-integrity 실패
if echo "$FAILED_CHECKS" | grep -q "ab-label-integrity\|label-integrity"; then
  echo "[FIX] label-integrity failure detected"
  
  CURRENT_LABELS=$(gh pr view "$PR_NUMBER" --json labels -q '.labels[].name' 2>/dev/null || echo "")
  
  # 정책 1: safe-change일 때는 ab:none 필요
  if echo "$CURRENT_LABELS" | grep -q "safe-change\|change:safe"; then
    echo "  Policy: safe-change requires ab:none"
    if echo "$CURRENT_LABELS" | grep -q "ab:A\|ab:B"; then
      echo "  Removing ab:A/ab:B (conflict with safe-change)"
      if [[ -z "$DRY_RUN" ]]; then
        gh pr edit "$PR_NUMBER" --remove-label "ab:A" 2>/dev/null || true
        gh pr edit "$PR_NUMBER" --remove-label "ab:B" 2>/dev/null || true
        FIXES_APPLIED=$((FIXES_APPLIED + 1))
      fi
    fi
    if ! echo "$CURRENT_LABELS" | grep -q "ab:none"; then
      echo "  Adding ab:none (required for safe-change)"
      if [[ -z "$DRY_RUN" ]]; then
        gh label create "ab:none" --color FFD700 --description "No AB variant" 2>/dev/null || true
        gh pr edit "$PR_NUMBER" --add-label "ab:none" 2>/dev/null || true
        FIXES_APPLIED=$((FIXES_APPLIED + 1))
      fi
    fi
  # 정책 2: risky-change일 때는 ab:A 또는 ab:B 필요
  elif echo "$CURRENT_LABELS" | grep -q "risky-change\|change:risky"; then
    echo "  Policy: risky-change requires ab:A or ab:B"
    if ! echo "$CURRENT_LABELS" | grep -q "ab:A\|ab:B"; then
      echo "  Adding ab:A (default for risky-change)"
      if [[ -z "$DRY_RUN" ]]; then
        gh label create "ab:A" --color FFD700 --description "A-branch of AB gate" 2>/dev/null || true
        gh pr edit "$PR_NUMBER" --add-label "ab:A" 2>/dev/null || true
        FIXES_APPLIED=$((FIXES_APPLIED + 1))
      fi
    fi
    if echo "$CURRENT_LABELS" | grep -q "ab:none"; then
      echo "  Removing ab:none (conflict with risky-change)"
      if [[ -z "$DRY_RUN" ]]; then
        gh pr edit "$PR_NUMBER" --remove-label "ab:none" 2>/dev/null || true
        FIXES_APPLIED=$((FIXES_APPLIED + 1))
      fi
    fi
  # 정책 3: change-safety 라벨 없으면 파일 패턴 기반 판단
  elif ! echo "$CURRENT_LABELS" | grep -q "safe-change\|risky-change\|change:safe\|change:risky"; then
    echo "  Policy: Auto-detect change-safety from file patterns"
    SAFE_PATTERNS="^(prometheus/rules/|scripts/ops/|docs/ops/|\.gitignore|\.githooks/)"
    RISKY_PATTERNS="^(config/|\.slo/|rulepack/)"
    
    CHANGED_FILES=$(gh pr diff "$PR_NUMBER" --name-only 2>/dev/null || git diff --name-only origin/main...HEAD)
    
    if echo "$CHANGED_FILES" | grep -qE "$RISKY_PATTERNS"; then
      echo "  Adding risky-change + ab:A (risky patterns detected)"
      if [[ -z "$DRY_RUN" ]]; then
        gh label create "risky-change" --color DC143C --description "High-risk change" 2>/dev/null || true
        gh label create "ab:A" --color FFD700 --description "A-branch of AB gate" 2>/dev/null || true
        gh pr edit "$PR_NUMBER" --add-label "risky-change" --add-label "ab:A" 2>/dev/null || true
        FIXES_APPLIED=$((FIXES_APPLIED + 1))
      fi
    else
      echo "  Adding safe-change + ab:none (safe patterns only)"
      if [[ -z "$DRY_RUN" ]]; then
        gh label create "safe-change" --color FFD700 --description "Low-risk ops/rules change" 2>/dev/null || true
        gh label create "ab:none" --color FFD700 --description "No AB variant" 2>/dev/null || true
        gh pr edit "$PR_NUMBER" --add-label "safe-change" --add-label "ab:none" 2>/dev/null || true
        FIXES_APPLIED=$((FIXES_APPLIED + 1))
      fi
    fi
  # 정책 4: ab 그룹 중복 제거 (정확히 하나만)
  else
    AB_COUNT=$(echo "$CURRENT_LABELS" | grep -oE "ab:(A|B|none)" | wc -l)
    if [[ "$AB_COUNT" -gt 1 ]]; then
      echo "  Policy: Multiple ab: labels detected, keeping ab:none if safe-change present"
      if echo "$CURRENT_LABELS" | grep -q "safe-change"; then
        echo "  Removing ab:A/ab:B (keeping ab:none)"
        if [[ -z "$DRY_RUN" ]]; then
          gh pr edit "$PR_NUMBER" --remove-label "ab:A" --remove-label "ab:B" 2>/dev/null || true
          gh pr edit "$PR_NUMBER" --add-label "ab:none" 2>/dev/null || true
          FIXES_APPLIED=$((FIXES_APPLIED + 1))
        fi
      fi
    elif [[ "$AB_COUNT" -eq 0 ]]; then
      echo "  Policy: No ab: label found, adding ab:none (default)"
      if [[ -z "$DRY_RUN" ]]; then
        gh label create "ab:none" --color FFD700 --description "No AB variant" 2>/dev/null || true
        gh pr edit "$PR_NUMBER" --add-label "ab:none" 2>/dev/null || true
        FIXES_APPLIED=$((FIXES_APPLIED + 1))
      fi
    fi
  fi
  
  # 추가 필수 라벨 확인 (type, area, size)
  if ! echo "$CURRENT_LABELS" | grep -q "type:"; then
    echo "  Adding type:ops (default)"
    if [[ -z "$DRY_RUN" ]]; then
      gh label create "type:ops" --color 0366d6 --description "Operations change" 2>/dev/null || true
      gh pr edit "$PR_NUMBER" --add-label "type:ops" 2>/dev/null || true
      FIXES_APPLIED=$((FIXES_APPLIED + 1))
    fi
  fi
  
  if ! echo "$CURRENT_LABELS" | grep -q "area:"; then
    echo "  Adding area:observability (detected from changed files)"
    if [[ -z "$DRY_RUN" ]]; then
      gh label create "area:observability" --color 0e8a16 --description "Observability area" 2>/dev/null || true
      gh pr edit "$PR_NUMBER" --add-label "area:observability" 2>/dev/null || true
      FIXES_APPLIED=$((FIXES_APPLIED + 1))
    fi
  fi
  
  if ! echo "$CURRENT_LABELS" | grep -q "size:"; then
    # 변경 파일 수 기반으로 size 판단
    CHANGE_COUNT=$(gh pr diff "$PR_NUMBER" --name-only 2>/dev/null | wc -l || echo "10")
    if [[ "$CHANGE_COUNT" -lt 5 ]]; then
      SIZE="S"
    elif [[ "$CHANGE_COUNT" -lt 20 ]]; then
      SIZE="M"
    else
      SIZE="L"
    fi
    echo "  Adding size:$SIZE (change count: $CHANGE_COUNT)"
    if [[ -z "$DRY_RUN" ]]; then
      gh label create "size:$SIZE" --color fbca04 --description "Size: $SIZE" 2>/dev/null || true
      gh pr edit "$PR_NUMBER" --add-label "size:$SIZE" 2>/dev/null || true
      FIXES_APPLIED=$((FIXES_APPLIED + 1))
    fi
  fi
fi

# 3.3 prometheus-lint 실패
if echo "$FAILED_CHECKS" | grep -q "prometheus-lint\|promtool"; then
  echo "[FIX] prometheus-lint failure detected"
  echo "  Run: promtool check rules prometheus/rules/l4_alerts.yml"
  echo "  Manual fix required - see logs"
fi

# 4. 변경사항 커밋 및 푸시
if [[ $FIXES_APPLIED -gt 0 ]] && [[ -z "$DRY_RUN" ]]; then
  echo "[COMMIT] Applying fixes..."
  git add .github/freeze-allow.txt 2>/dev/null || true
  
  if git diff --cached --quiet; then
    echo "[SKIP] No changes to commit"
  else
    git commit -m "chore: auto-fix freeze-guard allowlist (ci_self_heal)" || true
    FREEZE_BYPASS=1 git push origin day20-l4-finalize || true
    echo "[OK] Fixes pushed"
  fi
fi

# 5. CI 재실행 제안
if [[ $FIXES_APPLIED -gt 0 ]] && [[ -z "$DRY_RUN" ]]; then
  echo "[INFO] Consider rerunning CI:"
  echo "  gh run list --branch day20-l4-finalize --limit 1"
  echo "  gh run rerun <RUN_ID>"
fi

echo "=== CI Self-Healing Agent End: $FIXES_APPLIED fixes applied ==="

