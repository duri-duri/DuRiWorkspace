#!/usr/bin/env bash
# L4.0 Path 트리거 문제 해결 (PathModified 추가)
# Usage: bash scripts/evolution/fix_path_trigger_complete.sh
# 목적: PathChanged가 작동하지 않을 때 PathModified 추가

set -euo pipefail

echo "=== L4.0 Path 트리거 문제 해결 (PathModified 추가) ==="
echo ""

# 1. 수동 동기화 (즉시 해시 동기화)
echo "1. 수동 동기화:"
sudo systemctl start coldsync-install.service
if [ $? -eq 0 ]; then
    echo "✅ 수동 동기화 완료"
else
    echo "❌ 수동 동기화 실패"
    exit 1
fi
echo ""

# 2. Path 유닛 백업
echo "2. Path 유닛 백업:"
sudo cp /etc/systemd/system/coldsync-install.path /etc/systemd/system/coldsync-install.path.bak.$(date +%s)
echo "✅ 백업 완료"
echo ""

# 3. Path 유닛 수정 (PathModified 추가)
echo "3. Path 유닛 수정 (PathModified 추가):"
sudo tee /etc/systemd/system/coldsync-install.path >/dev/null <<'UNIT'
[Unit]
Description=Watch coldsync script and auto-install on change

[Path]
# 파일 내용 변경 감지
PathChanged=/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
# 파일 메타데이터 변경 감지 (VS Code 저장 등)
PathModified=/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
# 급격한 연속 저장 시 과도 실행 방지
TriggerLimitIntervalSec=10s
TriggerLimitBurst=5

[Install]
WantedBy=multi-user.target
UNIT
echo "✅ Path 유닛 수정 완료"
echo ""

# 4. 데몬 리로드 및 Path 유닛 재시작
echo "4. systemd 데몬 리로드 및 Path 유닛 재시작:"
sudo systemctl daemon-reload
sudo systemctl restart coldsync-install.path
if systemctl is-active --quiet coldsync-install.path 2>/dev/null; then
    echo "✅ Path 유닛 재시작 완료"
else
    echo "❌ Path 유닛 재시작 실패"
    exit 1
fi
echo ""

# 5. Path 트리거 테스트
echo "5. Path 트리거 테스트:"
echo "  파일 수정 중..."
SRC_FILE="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
echo "# Path trigger test $(date)" >> "$SRC_FILE"
sleep 5

TRIGGER_LOG=$(journalctl -u coldsync-install.service -n 5 --no-pager 2>/dev/null | grep -E "INSTALLED|up-to-date" || echo "")
if [ -n "$TRIGGER_LOG" ]; then
    echo "✅ Path 트리거 작동 확인"
    echo "$TRIGGER_LOG" | tail -1
else
    echo "⚠️  Path 트리거 작동하지 않음 (VS Code로 저장 테스트 권장)"
fi
echo ""

# 6. 해시 확인
echo "6. 해시 확인:"
SRC_HASH=$(sha256sum "$SRC_FILE" | awk '{print $1}')
DST_FILE="/usr/local/bin/coldsync_hosp_from_usb.sh"
DST_HASH=$(sha256sum "$DST_FILE" 2>/dev/null | awk '{print $1}' || echo "")

if [ "$SRC_HASH" = "$DST_HASH" ] && [ -n "$DST_HASH" ]; then
    echo "✅ 해시 동기화 확인"
else
    echo "⚠️  해시 불일치 (수동 동기화 필요)"
    echo "  SRC: $SRC_HASH"
    echo "  DST: $DST_HASH"
    echo "  수동 동기화: sudo systemctl start coldsync-install.service"
fi
echo ""

echo "=== Path 트리거 문제 해결 완료 ==="
echo ""
echo "사용 방법:"
echo "  1. VS Code에서 ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh 편집"
echo "  2. 저장 (Ctrl+S)"
echo "  3. 자동으로 /usr/local/bin에 배포됨"
echo ""
echo "테스트:"
echo "  echo '# Test' >> ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
echo "  sleep 3"
echo "  journalctl -u coldsync-install.service -n 3 --no-pager"

