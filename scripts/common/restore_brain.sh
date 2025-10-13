#!/bin/bash
set -Eeuo pipefail

# 📌 사용법: ./restore_brain.sh <commit_hash>
# 예시: ./restore_brain.sh 8436469

# ====== 설정값 ======
REPO_PATH="$HOME/local_git_repos/duri-brain"
TARGET_COMMIT="$1"
REMOTE_USER="duri"
REMOTE_HOST="192.168.0.9"
REMOTE_PATH="/srv/db_secure/"

# ====== 검증 ======
if [ -z "$TARGET_COMMIT" ]; then
  echo "❌ 커밋 해시를 입력하세요. 예: ./restore_brain.sh <commit_hash>"
  exit 1
fi

echo "🔄 [1/3] duri-brain 저장소로 이동"
cd "$REPO_PATH" || { echo "❌ 경로 오류: $REPO_PATH"; exit 1; }

echo "🔁 [2/3] Git 커밋 롤백: $TARGET_COMMIT"
git fetch origin
git checkout "$TARGET_COMMIT" || { echo "❌ checkout 실패"; exit 1; }

echo "🚀 [3/3] rsync로 duri-brain 배포"
rsync -av --delete ./ "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH"

echo "✅ duri-brain 롤백 및 배포 완료"
