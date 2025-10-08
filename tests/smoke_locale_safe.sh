#!/usr/bin/env bash
set -euo pipefail

echo "🧪 로케일 안전성 스모크 테스트"

# C 로케일 테스트
echo "== LC_ALL=C =="
LC_ALL=C scripts/rag_search_fusion_v1.sh "요통" ---rank --k 3 --format ids | awk 'END{exit (NR==3?0:1)}'
if [[ $? -eq 0 ]]; then
  echo "✅ LC_ALL=C: 3줄 ID-only 출력 확인"
else
  echo "❌ LC_ALL=C: 출력 줄 수 오류"
  exit 1
fi

# ko_KR.UTF-8 로케일 테스트 (존재 여부 확인 후)
echo "== LC_ALL=ko_KR.UTF-8 =="
if locale -a 2>/dev/null | grep -qx 'ko_KR\.UTF-8'; then
  LC_ALL=ko_KR.UTF-8 scripts/rag_search_fusion_v1.sh "요통" ---rank --k 3 --format ids 2>/dev/null | awk 'END{exit (NR==3?0:1)}'
  if [[ $? -eq 0 ]]; then
    echo "✅ LC_ALL=ko_KR.UTF-8: 3줄 ID-only 출력 확인"
  else
    echo "❌ LC_ALL=ko_KR.UTF-8: 출력 줄 수 오류"
    exit 1
  fi
else
  echo "⚠️ ko_KR.UTF-8 미설치 — C 로케일로 테스트"
  LC_ALL=C scripts/rag_search_fusion_v1.sh "요통" ---rank --k 3 --format ids | awk 'END{exit (NR==3?0:1)}'
  if [[ $? -eq 0 ]]; then
    echo "✅ LC_ALL=C (fallback): 3줄 ID-only 출력 확인"
  else
    echo "❌ LC_ALL=C (fallback): 출력 줄 수 오류"
    exit 1
  fi
fi

echo "✅ locale-safe"
