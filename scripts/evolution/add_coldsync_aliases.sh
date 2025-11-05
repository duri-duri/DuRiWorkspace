#!/usr/bin/env bash
# L4.0 .bashrc coldsync 단축키 추가
# Usage: bash scripts/evolution/add_coldsync_aliases.sh
# 목적: coldsync 빠른 점검을 위한 alias 추가

set -euo pipefail

echo "=== L4.0 .bashrc coldsync 단축키 추가 ==="
echo ""

# 백업
echo "1. .bashrc 백업:"
cp ~/.bashrc ~/.bashrc.bak.$(date +%s)
echo "✅ 백업 완료"
echo ""

# 2. 기존 alias 제거 (중복 방지)
echo "2. 기존 coldsync alias 제거:"
sed -i '/^alias cold-/d' ~/.bashrc 2>/dev/null || true
echo "✅ 제거 완료"
echo ""

# 3. 새 alias 추가
echo "3. 새 coldsync alias 추가:"
if ! grep -q "# coldsync quick checks" ~/.bashrc; then
    cat >> ~/.bashrc <<'ALIASES'

# coldsync quick checks
alias cold-log='journalctl --user -u coldsync-install.service -n 20 --no-pager'
alias cold-hash='sha256sum ~/.local/bin/coldsync_hosp_from_usb.sh ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh'
alias cold-run='systemctl --user start coldsync-install.service'
alias cold-status='systemctl --user status coldsync-install.path --no-pager | head -12'
ALIASES
    echo "✅ alias 추가 완료"
else
    echo "✅ alias 이미 존재"
fi
echo ""

# 4. 구문 검사
echo "4. 구문 검사:"
if bash -n ~/.bashrc 2>&1; then
    echo "✅ [OK] bashrc syntax clean"
else
    echo "❌ [FAIL] 구문 오류 발견"
    bash -n ~/.bashrc || true
    exit 1
fi
echo ""

echo "=== alias 추가 완료 ==="
echo ""
echo "적용:"
echo "  source ~/.bashrc"
echo ""
echo "사용:"
echo "  cold-log    # 최근 로그 확인"
echo "  cold-hash   # 해시 확인"
echo "  cold-run    # 수동 동기화"
echo "  cold-status # Path 유닛 상태"

