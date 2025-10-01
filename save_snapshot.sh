#!/bin/bash

# 📍 사용법: ./save_snapshot.sh "감정시스템_완성"
LABEL=$1
DATE=$(date +%Y-%m-%d)
BASE="/home/duri/snapshots/${DATE}__${LABEL// /_}"

mkdir -p "$BASE"

echo "📦 DuRi snapshot 저장 위치: $BASE"

# duri-core
mkdir -p "$BASE/duri-core"
cp /home/duri/scripts/log_emotion_change.py "$BASE/duri-core/"
cp /home/duri/scripts/broadcast_emotion_if_changed.py "$BASE/duri-core/"
cp /home/duri/scripts/emit_emotion_to_core.py "$BASE/duri-core/"
crontab -l > "$BASE/duri-core/crontab.txt"

# duri-brain
mkdir -p "$BASE/duri-brain"
scp duri@192.168.0.9:/home/duri/scripts/receive_emotion_vector.py "$BASE/duri-brain/" 2>/dev/null

# duri-evolution
mkdir -p "$BASE/duri-evolution"
scp duri@192.168.0.20:/home/duri/scripts/receive_emotion_vector.py "$BASE/duri-evolution/" 2>/dev/null

# snapshot 설명 파일
cat <<EOF > "$BASE/README.md"
# 📦 DuRi Snapshot - $LABEL

- 날짜: $DATE
- 핵심 흐름: 감정 변화 → delta 생성 → 중요도 체크 → 브로드캐스트 → 수신 저장
- 저장한 구성 요소:
  - duri-core: 핵심 감정 처리 및 broadcast
  - duri-brain: 감정 수신
  - duri-evolution: 감정 수신
  - crontab 자동화 설정 포함

> 구조도는 별도로 drawio 또는 png로 추가해주세요.
EOF

echo "✅ 스냅샷 저장 완료: $BASE"
