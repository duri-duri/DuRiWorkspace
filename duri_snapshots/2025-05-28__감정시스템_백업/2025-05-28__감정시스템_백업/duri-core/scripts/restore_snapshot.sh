#!/bin/bash
TAG=$1

if [ -z "$TAG" ]; then
  echo "❗ 사용법: ./restore_snapshot.sh snapshot_YYYY-MM-DD__HH-MM"
  exit 1
fi

cd ~/snapshots
git fetch origin --tags
git checkout tags/$TAG -f

echo "✅ [$TAG] GitHub 스냅샷 체크아웃 완료"

echo "📦 duri-core 복원 중..."
cp -r $TAG/duri-core/* ~/duri-core/

echo "📦 emotion_data 복원 중..."
cp -r $TAG/emotion_data/* ~/emotion_data/

echo "📦 logs 복원 중..."
cp -r $TAG/logs/* ~/logs/

echo "✅ 복원 완료. 시스템 상태가 [$TAG]로 되돌아갔습니다."
