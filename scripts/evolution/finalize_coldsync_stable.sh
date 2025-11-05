#!/usr/bin/env bash
# L4.0 A안 마무리: 유저 유닛 영구화 및 안정성 확보
# Usage: bash scripts/evolution/finalize_coldsync_stable.sh
# 목적: 장기 안정성 확보 (linger, system unit 충돌 방지, 문서화)

set -euo pipefail

echo "=== L4.0 A안 마무리: 장기 안정성 확보 ==="
echo ""

# 1. 유저 유닛 영구화 (linger)
echo "1. 유저 유닛 영구화 (linger):"
if loginctl enable-linger "$USER" 2>/dev/null; then
    echo "✅ linger 활성화 완료 (재부팅 후에도 user manager 활성)"
else
    echo "⚠️  linger 활성화 실패 (권한 문제일 수 있음)"
fi
echo ""

# 2. 과거 system unit 충돌 방지
echo "2. 과거 system unit 충돌 방지:"
if systemctl list-units --type=path --all | grep -q 'coldsync-install.path'; then
    echo "  system unit 발견, 비활성화/마스크 중..."
    sudo systemctl stop coldsync-install.path coldsync-install.service 2>/dev/null || true
    sudo systemctl disable coldsync-install.path coldsync-install.service 2>/dev/null || true
    sudo systemctl mask coldsync-install.path coldsync-install.service 2>/dev/null || true
    echo "✅ system unit 비활성화/마스크 완료"
else
    echo "✅ system unit 없음 (충돌 없음)"
fi
echo ""

# 3. User 유닛 재확인
echo "3. User 유닛 재확인:"
systemctl --user daemon-reload
if systemctl --user is-enabled --quiet coldsync-install.path 2>/dev/null; then
    echo "✅ user unit 활성화됨"
    systemctl --user status coldsync-install.path --no-pager | head -12
else
    echo "❌ user unit 비활성화 (활성화 필요)"
    systemctl --user enable --now coldsync-install.path
fi
echo ""

# 4. Path 유닛 버스트 보호 확인
echo "4. Path 유닛 버스트 보호 확인:"
if systemctl --user cat coldsync-install.path 2>/dev/null | grep -q 'TriggerLimit'; then
    echo "✅ TriggerLimit 설정됨"
else
    echo "⚠️  TriggerLimit 없음 (수동 설정 필요)"
fi
echo ""

# 5. 해시 확인
echo "5. 해시 확인:"
SRC_FILE="$HOME/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST_FILE="$HOME/.local/bin/coldsync_hosp_from_usb.sh"
if [ -f "$DST_FILE" ]; then
    SRC_HASH=$(sha256sum "$SRC_FILE" | awk '{print $1}')
    DST_HASH=$(sha256sum "$DST_FILE" | awk '{print $1}')
    if [ "$SRC_HASH" = "$DST_HASH" ]; then
        echo "✅ 해시 동기화 확인"
    else
        echo "⚠️  해시 불일치 (수동 동기화 필요)"
    fi
else
    echo "⚠️  대상 파일 없음 (초기 동기화 필요)"
    systemctl --user start coldsync-install.service || true
fi
echo ""

echo "=== 마무리 완료 ==="
echo ""
echo "다음 단계:"
echo "  bash scripts/evolution/coldsync_healthcheck.sh   # 헬스체크"
echo "  bash scripts/evolution/coldsync_regression.sh     # 회귀 테스트"

