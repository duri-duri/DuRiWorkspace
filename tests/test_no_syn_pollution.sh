#!/usr/bin/env bash
# 하드닝 #4: SYN 오염 영구 차단 테스트
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== SYN 오염 차단 테스트 ==="
echo ""

bash scripts/ab_pvalue_stats.sh "2 hours" >/tmp/ab.out 2>&1 || true

if grep -q '\-SYN' /tmp/ab.out 2>/dev/null; then
    echo "[FAIL] SYN 포함 발견"
    grep '\-SYN' /tmp/ab.out
    exit 1
else
    echo "[OK] SYN 제외 확인"
fi

echo ""

