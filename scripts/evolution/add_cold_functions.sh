#!/usr/bin/env bash
# L4.0 cold-* 함수 추가 (alias 대체, 모든 셸에서 동작)
# Usage: bash scripts/evolution/add_cold_functions.sh
# 목적: cold-* 명령어를 함수로 추가 (비인터랙티브 셸에서도 동작)

set -euo pipefail

echo "=== L4.0 cold-* 함수 추가 ==="
echo ""

# 백업
echo "1. .bashrc 백업:"
cp ~/.bashrc ~/.bashrc.bak.$(date +%s)
echo "✅ 백업 완료"
echo ""

# 2. 기존 alias/함수 제거 (중복 방지)
echo "2. 기존 cold-* alias/함수 제거:"
sed -i '/^alias cold-/d' ~/.bashrc 2>/dev/null || true
sed -i '/^cold_log()/d' ~/.bashrc 2>/dev/null || true
sed -i '/^cold-log()/d' ~/.bashrc 2>/dev/null || true
sed -i '/^cold_hash()/d' ~/.bashrc 2>/dev/null || true
sed -i '/^cold-hash()/d' ~/.bashrc 2>/dev/null || true
sed -i '/^cold_run()/d' ~/.bashrc 2>/dev/null || true
sed -i '/^cold-run()/d' ~/.bashrc 2>/dev/null || true
sed -i '/^cold_status()/d' ~/.bashrc 2>/dev/null || true
sed -i '/^cold-status()/d' ~/.bashrc 2>/dev/null || true
sed -i '/# coldsync quick/d' ~/.bashrc 2>/dev/null || true
sed -i '/# coldsync helpers/d' ~/.bashrc 2>/dev/null || true
echo "✅ 제거 완료"
echo ""

# 3. 함수 추가
echo "3. cold-* 함수 추가:"
if ! grep -q "# --- coldsync helpers (functions) ---" ~/.bashrc; then
    cat >> ~/.bashrc <<'FUNCTIONS'

# --- coldsync helpers (functions) ---
cold-log()    { journalctl --user -u coldsync-install.service -n "${1:-20}" --no-pager; }
cold-hash()   { sha256sum ~/.local/bin/coldsync_hosp_from_usb.sh ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh; }
cold-run()    { systemctl --user start coldsync-install.service; }
cold-status() { systemctl --user status coldsync-install.path --no-pager | head -12; }
FUNCTIONS
    echo "✅ 함수 추가 완료"
else
    echo "✅ 함수 이미 존재"
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

# 5. 적용 테스트
echo "5. 적용 테스트:"
if bash --login -c 'type cold-log >/dev/null 2>&1 && echo "OK"' 2>&1; then
    echo "✅ 함수 정의 확인"
else
    echo "⚠️  함수 정의 확인 실패 (경고 무시 가능)"
fi
echo ""

echo "=== 함수 추가 완료 ==="
echo ""
echo "적용:"
echo "  source ~/.bashrc"
echo ""
echo "사용:"
echo "  cold-log    # 최근 로그 확인"
echo "  cold-hash   # 해시 확인"
echo "  cold-run    # 수동 동기화"
echo "  cold-status # Path 유닛 상태"

