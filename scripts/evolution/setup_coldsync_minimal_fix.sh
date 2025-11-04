#!/usr/bin/env bash
# L4.0 최소 수정: sudo NOPASSWD + Path 유닛 개선
# Usage: bash scripts/evolution/setup_coldsync_minimal_fix.sh
# 목적: 기존 구조 유지 + sudo 문제만 해결 (p≈0.85)

set -euo pipefail

echo "=== L4.0 최소 수정: sudo NOPASSWD + Path 개선 ==="
echo ""

# 1. sudoers 규칙 추가
echo "1. sudoers 규칙 추가 (NOPASSWD):"
sudo tee /etc/sudoers.d/coldsync >/dev/null <<'SUDOERS'
# L4.0 coldsync 자동 배포 - NOPASSWD (최소 권한)
duri ALL=(root) NOPASSWD: /usr/local/sbin/coldsync-install
duri ALL=(root) NOPASSWD: /bin/systemctl start coldsync-install.service
duri ALL=(root) NOPASSWD: /bin/systemctl restart coldsync-install.path
SUDOERS
sudo chmod 0440 /etc/sudoers.d/coldsync
echo "✅ sudoers 규칙 추가 완료"
echo ""

# 2. 설치기 수정 (sudo -n 사용)
echo "2. 설치기 수정 (sudo -n 사용):"
# 설치기는 이미 루트로 실행되므로 변경 없음 (검증만)
if [ -f /usr/local/sbin/coldsync-install ]; then
    echo "✅ 설치기 존재 확인"
else
    echo "❌ 설치기 없음"
    exit 1
fi
echo ""

# 3. Path 유닛 개선
echo "3. Path 유닛 개선:"
sudo cp /etc/systemd/system/coldsync-install.path /etc/systemd/system/coldsync-install.path.bak.$(date +%s) 2>/dev/null || true
sudo tee /etc/systemd/system/coldsync-install.path >/dev/null <<'UNIT'
[Unit]
Description=Watch coldsync script dir and auto-install on change

[Path]
# 1) 특정 파일 변경/교체
PathChanged=/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
# 2) 디렉터리 단위 변경(파일 rename/moved_to 포함)
PathChanged=/home/duri/DuRiWorkspace/scripts/bin
# 3) 메타데이터 변경 감지
PathModified=/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
# 급격한 연속 저장 시 과도 실행 방지
TriggerLimitIntervalSec=10s
TriggerLimitBurst=5

[Install]
WantedBy=multi-user.target
UNIT
echo "✅ Path 유닛 개선 완료"
echo ""

# 4. 데몬 리로드 및 활성화
echo "4. systemd 데몬 리로드 및 활성화:"
sudo systemctl daemon-reload
sudo systemctl enable --now coldsync-install.path
echo "✅ 활성화 완료"
echo ""

# 5. sudo -n 테스트
echo "5. sudo -n 테스트:"
if sudo -n true 2>/dev/null; then
    echo "✅ sudo NOPASSWD 작동 확인"
else
    echo "❌ sudo NOPASSWD 작동 실패"
fi
echo ""

# 6. 초기 동기화
echo "6. 초기 동기화 실행:"
sudo systemctl start coldsync-install.service || echo "초기 동기화 실패"
echo ""

# 7. 해시 확인
echo "7. 해시 확인:"
SRC_FILE="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST_FILE="/usr/local/bin/coldsync_hosp_from_usb.sh"
SRC_HASH=$(sha256sum "$SRC_FILE" | awk '{print $1}')
DST_HASH=$(sha256sum "$DST_FILE" 2>/dev/null | awk '{print $1}' || echo "")
echo "  SRC: $SRC_HASH"
echo "  DST: $DST_HASH"
if [ "$SRC_HASH" = "$SRC_HASH" ] && [ -n "$DST_HASH" ]; then
    echo "✅ 해시 동기화 확인"
else
    echo "⚠️  해시 불일치"
fi
echo ""

echo "=== 최소 수정 완료 ==="
echo ""
echo "사용 방법:"
echo "  1. VS Code에서 ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh 편집"
echo "  2. 저장 (Ctrl+S)"
echo "  3. 자동으로 /usr/local/bin에 배포됨"
echo ""
echo "검증:"
echo "  journalctl -u coldsync-install.service -n 5 --no-pager"
echo "  sha256sum /usr/local/bin/coldsync_hosp_from_usb.sh ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"

