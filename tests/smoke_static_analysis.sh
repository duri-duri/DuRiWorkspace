#!/usr/bin/env bash
set -euo pipefail

echo "🧪 정적 분석 스모크 테스트"
if command -v shellcheck >/dev/null; then
  echo "📋 shellcheck 실행 중..."
  if shellcheck -x scripts/*.sh tests/*.sh; then
    echo "✅ shellcheck: 모든 스크립트 통과"
  else
    echo "⚠️ shellcheck: 일부 경고 발견 (계속 진행)"
  fi
else
  echo "⚠️ shellcheck 없음 (건너뜀)"
fi
