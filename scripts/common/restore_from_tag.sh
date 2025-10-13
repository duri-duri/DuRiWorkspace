#!/bin/bash
set -Eeuo pipefail

TAG=$1
if [ -z "$TAG" ]; then
  echo "❌ 태그 이름을 인자로 넣어주세요. 예: snapshot_2025-06-01_14-00"
  exit 1
fi

GIT_REPOS=(
  "/home/duri/duri-core"
  "/mnt/remote/db_secure"
  "/mnt/remote/de_secure"
)

for REPO in "${GIT_REPOS[@]}"; do
  cd "$REPO" || continue
  git fetch origin --tags
  git checkout "tags/$TAG" -f
done

echo "✅ [$TAG] 기준으로 모든 저장소 롤백 완료"
