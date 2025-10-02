#!/bin/bash
set -Eeuo pipefail
# 📦 delete_old_snapshots.sh
# 30일 지난 DuRi snapshot 디렉토리를 GitHub + 로컬 모두에서 정리합니다.

TARGET_DIR=~/snapshots
cd "$TARGET_DIR" || exit 1

echo "📅 기준일: 30일 이상 경과한 스냅샷 삭제 시작"

# 1️⃣ 오래된 스냅샷 찾기
OLD_DIRS=$(find . -maxdepth 1 -type d -name 'snapshot_*' -mtime +30)

if [ -z "$OLD_DIRS" ]; then
  echo "✅ 삭제할 스냅샷이 없습니다."
  exit 0
fi

# 2️⃣ Git에서 삭제 등록
for dir in $OLD_DIRS; do
  echo "🗑️ Git에서 삭제 예정: $dir"
  git rm -r "$dir"
done

# 3️⃣ 커밋 및 푸시
echo "💾 Git 커밋 및 원격 푸시 중..."
git commit -m "🔥 Removed old snapshots (30+ days)"
git push origin main --tags

# 4️⃣ 로컬 디렉토리 삭제
for dir in $OLD_DIRS; do
  echo "🧹 로컬에서 삭제: $dir"
  rm -rf "$dir"
done

echo "✅ 오래된 스냅샷 정리 완료"
