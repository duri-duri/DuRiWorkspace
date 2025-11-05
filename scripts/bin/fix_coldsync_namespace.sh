#!/usr/bin/env bash
# coldsync-install Service 유닛 수정 스크립트 (mount namespace 문제 해결)
# 문제: /var/lib/coldsync-hosp 디렉토리가 없어서 mount namespace 설정 실패

set -euo pipefail

echo "=== coldsync-install.service 수정 (mount namespace 문제 해결) ==="
echo ""

echo "1. 디렉토리 미리 생성:"
sudo mkdir -p /var/lib/coldsync-hosp
sudo chown root:root /var/lib/coldsync-hosp
sudo chmod 755 /var/lib/coldsync-hosp
echo "✅ 디렉토리 생성 완료"
echo ""

echo "2. Service 유닛 수정:"
sudo tee /etc/systemd/system/coldsync-install.service > /dev/null <<'UNIT'
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
# 소스 파일 읽기 허용
ReadOnlyPaths=/home/duri/DuRiWorkspace/scripts/bin
# 쓰기 경로 (디렉토리는 미리 생성됨)
ReadWritePaths=/usr/local/bin /var/lib/coldsync-hosp /tmp
UNIT

echo "✅ Service 유닛 수정 완료"
echo ""

echo "3. systemd 재로드 및 테스트:"
sudo systemctl daemon-reload
echo "daemon-reload 완료"
echo ""

echo "4. 수동 트리거 테스트:"
sudo systemctl start coldsync-install.service
sleep 1
echo ""

echo "5. 상태 확인:"
sudo systemctl status coldsync-install.service --no-pager -l | head -30 || true
echo ""

echo "6. 로그 확인:"
sudo journalctl -u coldsync-install.service -n 20 --no-pager || true
echo ""

echo "7. 파일 동기화 확인:"
SRC="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST="/usr/local/bin/coldsync_hosp_from_usb.sh"

if [ -f "$SRC" ] && [ -f "$DST" ]; then
    SHA_SRC=$(sha256sum "$SRC" | awk '{print $1}')
    SHA_DST=$(sha256sum "$DST" | awk '{print $1}')
    
    if [ "$SHA_SRC" = "$SHA_DST" ]; then
        echo "✅ 파일 동기화 OK (해시 일치)"
    else
        echo "⚠️  파일 동기화 안됨 (해시 불일치)"
        echo "  소스: $SHA_SRC"
        echo "  대상: $SHA_DST"
    fi
else
    echo "❌ 파일 확인 실패"
fi
echo ""

echo "=== 수정 완료 ==="
echo ""
echo "이제 저장 트리거 테스트:"
echo "  echo '# Test \$(date)' >> ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
echo "  sleep 2"
echo "  sudo journalctl -u coldsync-install.service -n 10 --no-pager"

