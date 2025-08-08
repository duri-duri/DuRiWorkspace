#!/bin/bash

cd ~/snapshots
git fetch origin --tags > /dev/null 2>&1

echo "📜 사용 가능한 복원 태그 목록:"
echo "-------------------------------"
git tag --list | sort
echo "-------------------------------"

read -p "⏪ 복원할 태그 이름을 정확히 입력하세요: " TAG

if [ -z "$TAG" ]; then
  echo "❌ 태그 이름이 입력되지 않았습니다. 종료합니다."
  exit 1
fi

git checkout tags/$TAG -f

echo "✅ [$TAG] GitHub 스냅샷 체크아웃 완료"

echo "📦 duri-core 복원 중..."
cp -r $TAG/duri-core/* ~/duri-core/

echo "📦 emotion_data 복원 중..."
cp -r $TAG/emotion_data/* ~/emotion_data/

echo "📦 logs 복원 중..."
cp -r $TAG/logs/* ~/logs/

echo "✅ 복원 완료. 시스템 상태가 [$TAG]로 되돌아갔습니다."

