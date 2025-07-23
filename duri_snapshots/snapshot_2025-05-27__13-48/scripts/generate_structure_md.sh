#!/bin/bash

LABEL=$1
DATE=$(date +%Y-%m-%d)
TARGET="/home/duri/snapshots/${DATE}__${LABEL// /_}/structure.md"

cat <<EOF > "$TARGET"
# 🧠 DuRi 시스템 구조도 ($DATE 기준)

\`\`\`
📁 DuRi System Root
├── 📦 GitHub Repository (Remote)
│   ├── /scripts/
│   ├── /duri-checker/
│   ├── /memory_system/
│   ├── /config/
│   └── deploy_all.sh
│
├── 🧠 duri-core (main brain)
│   ├── emotion_data/
│   ├── scripts/
│   ├── logs/
│   ├── config/
│   └── crontab 설정
│
├── 🧬 duri-evolution (학습/추론 전용)
│   ├── emotion_data/
│   ├── scripts/
│   └── logs/
│
├── 🧠 duri-brain (판단/판단 트리거)
│   ├── emotion_data/
│   ├── scripts/
│   └── logs/
│
└── 🛰️ 배포 자동화
    └── duri-head
        └── deploy_all.sh → 모든 노드로 배포
\`\`\`

> 본 구조는 감정 흐름 기반 판단 시스템으로 완성됨.
> 각 노드는 역할 분리되고 crontab으로 자동화됨.
EOF

echo "✅ 구조도 저장 완료 → $TARGET"
