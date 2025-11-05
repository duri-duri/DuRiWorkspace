#!/usr/bin/env bash
# coldsync-install Service 유닛 수정 스크립트
# 문제: ReadWritePaths에 소스 파일 경로가 없어서 읽기 실패

set -euo pipefail

echo "=== coldsync-install.service 수정 ==="
echo ""

# 수정된 Service 유닛 적용
sudo tee /etc/systemd/system/coldsync-install.service <<'UNIT'
[Unit]
Description=Install coldsync script into /usr/local/bin if changed

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/coldsync-install
# 최소 하드닝
PrivateTmp=yes
NoNewPrivileges=yes
ProtectHome=read-only
ProtectHostname=yes
ProtectClock=yes
ProtectControlGroups=yes
ProtectKernelLogs=yes
ProtectKernelModules=yes
ProtectKernelTunables=yes
RestrictSUIDSGID=yes
LockPersonality=yes
MemoryDenyWriteExecute=yes
SystemCallFilter=@system-service
# 소스 파일 읽기 허용 (수정)
ReadOnlyPaths=/home/duri/DuRiWorkspace/scripts/bin
# 쓰기 경로
ReadWritePaths=/usr/local/bin /var/lib/coldsync-hosp /tmp
UNIT

echo "✅ Service 유닛 수정 완료"
echo ""

echo "=== 적용 및 재시작 ==="
sudo systemctl daemon-reload
echo "daemon-reload 완료"
echo ""

echo "=== 테스트 실행 ==="
sudo systemctl start coldsync-install.service
sleep 1
echo ""

echo "=== 상태 확인 ==="
sudo systemctl status coldsync-install.service --no-pager -l || true
echo ""

echo "=== 로그 확인 ==="
sudo journalctl -u coldsync-install.service -n 20 --no-pager || true
echo ""

echo "=== 파일 검증 ==="
ls -lh /usr/local/bin/coldsync_hosp_from_usb.sh 2>/dev/null && echo "✅ 설치 완료" || echo "❌ 설치 실패"
echo ""

echo "=== SHA256 비교 ==="
sha256sum /usr/local/bin/coldsync_hosp_from_usb.sh /home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh 2>/dev/null || echo "파일 비교 실패"

