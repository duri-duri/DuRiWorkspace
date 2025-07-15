#!/bin/bash

# 📸 공통 커밋 메시지 및 브랜치명
MESSAGE="📸 2025-07-15 DuRi 전체 상태 스냅샷"
BRANCH="dev-2025-07-15-full_snapshot"

# 📂 Git으로 관리되는 모든 모듈 포함
MODULES=("duri_core" "duri_brain" "duri_evolution" "DuRiWorkspace")

for dir in "${MODULES[@]}"; do
  echo "📁 $dir 처리 중..."

  # Git 디렉토리 여부 확인
  if [ ! -d "$dir/.git" ]; then
    echo "⚠️  $dir 은 Git 디렉토리가 아님 → 스킵"
    continue
  fi

  cd "$dir" || { echo "❌ 디렉토리 $dir 없음"; exit 1; }

  # 변경 사항이 있는 경우에만 커밋
  git add .
  if git diff --cached --quiet; then
    echo "ℹ️  커밋할 변경 사항 없음 → 건너뜀"
  else
    git commit -m "$MESSAGE ($dir)"
  fi

  # 브랜치가 이미 있으면 생략
  if git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
    echo "🔁 브랜치 $BRANCH 이미 존재 → checkout만 수행"
    git checkout "$BRANCH"
  else
    git checkout -b "$BRANCH"
  fi

  git push -u origin "$BRANCH"

  cd ..
  echo "✅ $dir 완료"
done
