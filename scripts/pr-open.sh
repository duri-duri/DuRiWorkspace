#!/usr/bin/env bash
set -Eeuo pipefail

cur=$(git rev-parse --abbrev-ref HEAD)
case "$cur" in main|release/*)
  echo "❌ protected: $cur"; exit 2;;
esac

echo "⏫ pushing $cur to origin..."
# 푸시 실패 시 훅 메시지까지 보여주고 종료
if ! out=$(git push -u origin HEAD 2>&1); then
  echo "$out"
  echo
  echo "🔎 freeze-preflight:"
  if [[ -x scripts/freeze-preflight.sh ]]; then
    REV=$(git rev-parse HEAD) scripts/freeze-preflight.sh || true
  fi
  exit 1
fi

# PR 있으면 번호만 출력, 없으면 생성 후 번호 출력
if ! num=$(gh pr view --json number -q .number 2>/dev/null); then
  gh pr create --fill --base main --head "$cur" >/dev/null
  num=$(gh pr view --json number -q .number)
fi

echo "✅ PR #$num"