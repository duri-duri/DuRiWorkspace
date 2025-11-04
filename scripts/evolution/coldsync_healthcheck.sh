#!/usr/bin/env bash
# L4.0 coldsync 헬스체크 (최근 10분만 검사, 오탐 제거)
# Usage: bash scripts/evolution/coldsync_healthcheck.sh
# 목적: 최근 10분 로그만 검사하여 과거 로그 오탐 방지

set -euo pipefail

echo "=== L4.0 coldsync 헬스체크 (최근 10분) ==="
echo ""

LOG='coldsync-install.service'
SINCE='-10 min'

# 최근 10분 로그에서 실패/에러 라인 수를 카운트
FAILS="$(
  journalctl --user -u "$LOG" --since "$SINCE" --no-pager -o cat 2>/dev/null \
  | grep -E -i 'fail|error|err|exit[^0-9]*[1-9]|Unknown key name' || true
)"

FAIL_COUNT="$(printf '%s\n' "$FAILS" | sed '/^$/d' | wc -l | tr -cd '0-9')"
FAIL_COUNT="${FAIL_COUNT:-0}"

echo "1) 설치/동기화 로그 샘플 (최근 20줄):"
journalctl --user -u "$LOG" --since "$SINCE" --no-pager -n 20 -o cat || true
echo ""

echo "2) 최근 10분 실패 라인 수: ${FAIL_COUNT}"
if [ "$FAIL_COUNT" -gt 0 ]; then
  echo "❌ [FAIL] 최근 10분 실패 라인 ${FAIL_COUNT}건"
  # 실패 샘플 5줄만 보여주기
  printf '%s\n' "$FAILS" | tail -5
  exit 1
else
  echo "✅ [PASS] 최근 10분 실패 없음"
  exit 0
fi
