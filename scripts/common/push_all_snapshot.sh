#!/bin/bash

MESSAGE="📸 2025-07-15 DuRi 전체 상태 스냅샷"
BRANCH="dev-2025-07-15-full_snapshot"

# "."은 현재 디렉토리 (DuRiWorkspace)
MODULES=("duri_core" "duri_brain" "duri_evolution" ".")

for dir in "${MODULES[@]}"; do
  DISPLAY_NAME="$dir"
  [ "$dir" = "." ] && DISPLAY_NAME="DuRiWorkspace"
  echo "📁 $DISPLAY_NAME 처리 중..."

  if [ ! -d "$dir/.git" ]; then
    echo "⚠️  $DISPLAY_NAME 은 Git 디렉토리가 아님 → 스킵"
    continue
  fi

  cd "$dir" || { echo "❌ 디렉토리 $dir 없음"; exit 1; }

  git add .
  if git diff --cached --quiet; then
    echo "ℹ️  커밋할 변경 사항 없음 → 건너뜀"
  else
    git commit -m "$MESSAGE ($DISPLAY_NAME)"
  fi

  if git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
    echo "🔁 브랜치 $BRANCH 이미 존재 → checkout만 수행"
    git checkout "$BRANCH"
  else
    git checkout -b "$BRANCH"
  fi

  git push -u origin "$BRANCH"

  cd - >/dev/null  # 원래 디렉토리로 돌아가기 (출력 숨김)
  echo "✅ $DISPLAY_NAME 완료"
done
