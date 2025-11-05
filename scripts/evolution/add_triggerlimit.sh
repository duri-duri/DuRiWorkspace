#!/usr/bin/env bash
# L4.0 Path 유닛 버스트 보호 추가
# Usage: bash scripts/evolution/add_triggerlimit.sh
# 목적: VS Code 연속 저장 시 과다 실행 억제

set -euo pipefail

echo "=== L4.0 Path 유닛 버스트 보호 추가 ==="
echo ""

UNIT_DIR="$HOME/.config/systemd/user"
PATH_UNIT="$UNIT_DIR/coldsync-install.path"

# 1. 백업
echo "1. Path 유닛 백업:"
if [ -f "$PATH_UNIT" ]; then
    cp -a "$PATH_UNIT" "$PATH_UNIT.bak.$(date +%s)"
    echo "✅ 백업 완료"
else
    echo "❌ Path 유닛 없음: $PATH_UNIT"
    exit 1
fi
echo ""

# 2. TriggerLimit 추가
echo "2. TriggerLimit 추가:"
awk '
/^\[Path\]/ {print; seen=1; next}
seen && /^TriggerLimit/ {next}
{print}
END {
  if (seen) {
    print "TriggerLimitIntervalSec=10s"
    print "TriggerLimitBurst=5"
  }
}
' "$PATH_UNIT" > "$PATH_UNIT.tmp" && mv "$PATH_UNIT.tmp" "$PATH_UNIT"
echo "✅ TriggerLimit 추가 완료"
echo ""

# 3. 적용
echo "3. systemd 데몬 리로드 및 재시작:"
systemctl --user daemon-reload
systemctl --user restart coldsync-install.path
echo "✅ 적용 완료"
echo ""

# 4. 상태 확인
echo "4. 상태 확인:"
systemctl --user status coldsync-install.path --no-pager | head -12 || echo "상태 확인 실패"
echo ""

# 5. TriggerLimit 확인
echo "5. TriggerLimit 확인:"
if systemctl --user cat coldsync-install.path 2>/dev/null | grep -q 'TriggerLimit'; then
    echo "✅ TriggerLimit 설정 확인됨"
    systemctl --user cat coldsync-install.path 2>/dev/null | grep -E 'TriggerLimit' || echo "  (표시 안됨)"
else
    echo "❌ TriggerLimit 설정 안됨"
fi
echo ""

echo "=== 버스트 보호 추가 완료 ==="

