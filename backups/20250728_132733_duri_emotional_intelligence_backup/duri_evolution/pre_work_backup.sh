#!/bin/bash
DATE_TAG="snapshot_$(date '+%Y-%m-%d__%H-%M')"
SNAPSHOT_DIR=~/snapshots/$DATE_TAG

echo "🔄 백업 디렉토리 생성: $SNAPSHOT_DIR"
mkdir -p "$SNAPSHOT_DIR"

echo "📦 파일 백업 중..."
cp -r ~/scripts "$SNAPSHOT_DIR/scripts"
cp -r ~/emotion_data "$SNAPSHOT_DIR/emotion_data"
cp -r ~/logs "$SNAPSHOT_DIR/logs"
[ -d ~/models ] && cp -r ~/models "$SNAPSHOT_DIR/models"

echo "📤 GitHub 푸시 중..."
cd ~/snapshots
git add .
git commit -m "📦 [$HOSTNAME] 백업: $DATE_TAG"
git tag "$DATE_TAG"
git push origin main --tags

echo "✅ [$HOSTNAME] 백업 완료"


