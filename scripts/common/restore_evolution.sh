#!/bin/bash
set -Eeuo pipefail

# 📌 사용법: ./restore_evolution.sh <commit_hash>
# 예시: ./restore_evolution.sh 2d4da61

# ====== 설정값 ======
REPO_PATH="$HOME/local_git_repos/duri-evolution"
TARGET_COMMIT="$1"
REMOTE_USER="duri"
REMOTE_HOST="192.168.0.20"
REMOTE_PATH="/srv/de_secure/"

# ====== 검증 ======
if [ -z "$TARGET_COMMIT" ]; then
  echo "❌ 커밋 해시를 입력하세요. 예: ./restore_evolution.sh <commit_hash>"
  exit 1
fi

echo "🔄 [1/3] duri-evolution 저장소로 이동"
cd "$REPO_PATH" || { echo "❌ 경로 오류: $REPO_PATH"; exit 1; }

echo "🔁 [2/3] Git 커밋 롤백: $TARGET_COMMIT"
git fetch origin
git checkout "$TARGET_COMMIT" || { echo "❌ checkout 실패"; exit 1; }

echo "🚀 [3/3] rsync로 duri-evolution 배포"
rsync -av --delete --no-perms --no-group --exclude=".git" ./ "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH"

echo "✅ duri-evolution 롤백 및 배포 완료"
