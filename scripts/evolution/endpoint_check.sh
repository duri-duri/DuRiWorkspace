#!/usr/bin/env bash
# L4.0 끝점 체크 원라이너
# Usage: bash scripts/evolution/endpoint_check.sh

set -euo pipefail

echo "=== L4.0 끝점 체크 ==="
echo ""

bash scripts/bin/status_coldsync_oneline.sh
echo ""

if bash scripts/bin/verify_coldsync_final.sh; then
    echo "[GO] namespace/해시/유닛 OK"
    exit 0
else
    echo "[NO-GO] fix namespace (mkdir /var/lib/coldsync-hosp) & retry" >&2
    echo ""
    echo "📋 복구:"
    echo "  bash scripts/evolution/fix_namespace_error.sh   # 즉시 핫픽스"
    echo "  bash scripts/evolution/fix_namespace_permanent.sh # 영구 수정"
    exit 1
fi

