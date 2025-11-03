#!/usr/bin/env bash
# (6) CI에 라벨 정합 단위 테스트 추가 (빠른 실패)
set -euo pipefail

cd "$(dirname "$0")/.."

bad=$(grep -Rlh '^duri_ab_p_value ' var/evolution 2>/dev/null | wc -l || echo 0)
if [ "$bad" -gt 0 ]; then
  echo "FAIL: unlabeled p-lines=$bad"
  grep -Rlh '^duri_ab_p_value ' var/evolution 2>/dev/null | head -5
  exit 1
else
  echo "PASS: no unlabeled p-lines"
  exit 0
fi

