#!/usr/bin/env bash
# L4.0 TriggerLimit 경고 해결 (섹션 위치 수정)
# Usage: bash scripts/evolution/fix_triggerlimit_section.sh
# 목적: TriggerLimit을 [Path] 섹션으로 이동

set -euo pipefail

echo "=== L4.0 TriggerLimit 경고 해결 ==="
echo ""

UNIT="$HOME/.config/systemd/user/coldsync-install.path"

# 1. 백업
echo "1. Path 유닛 백업:"
if [ -f "$UNIT" ]; then
    cp -a "$UNIT" "$UNIT.bak.$(date +%s)"
    echo "✅ 백업 완료"
else
    echo "❌ Path 유닛 없음: $UNIT"
    exit 1
fi
echo ""

# 2. 올바른 내용으로 재작성
echo "2. Path 유닛 재작성 ([Path] 섹션에 TriggerLimit 포함):"
cat > "$UNIT" <<'UNIT'
[Unit]
Description=Watch coldsync script and auto-install on change

[Path]
# 내용/메타데이터 변경 모두 감지
PathChanged=%h/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
PathModified=%h/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
# VS Code 연속 저장 버스트 보호
TriggerLimitIntervalSec=10s
TriggerLimitBurst=5

[Install]
WantedBy=default.target
UNIT
echo "✅ 재작성 완료"
echo ""

# 3. 적용
echo "3. systemd 데몬 리로드 및 재시작:"
systemctl --user daemon-reload
systemctl --user restart coldsync-install.path
echo "✅ 적용 완료"
echo ""

# 4. 상태 확인
echo "4. 상태 확인:"
systemctl --user status coldsync-install.path --no-pager | head -15 || echo "상태 확인 실패"
echo ""

# 5. TriggerLimit 확인
echo "5. TriggerLimit 확인:"
if systemctl --user cat coldsync-install.path 2>/dev/null | grep -A 5 '\[Path\]' | grep -q 'TriggerLimit'; then
    echo "✅ TriggerLimit이 [Path] 섹션에 정상 위치"
    systemctl --user cat coldsync-install.path 2>/dev/null | grep -A 5 '\[Path\]' | grep 'TriggerLimit'
else
    echo "❌ TriggerLimit 확인 실패"
fi
echo ""

# 6. 경고 확인
echo "6. 경고 확인:"
WARNINGS=$(systemctl --user status coldsync-install.path --no-pager 2>&1 | grep -iE 'unknown key|triggerlimit' || echo "")
if [ -z "$WARNINGS" ]; then
    echo "✅ 경고 없음"
else
    echo "⚠️  경고 발견:"
    echo "$WARNINGS"
fi
echo ""

echo "=== TriggerLimit 경고 해결 완료 ==="

