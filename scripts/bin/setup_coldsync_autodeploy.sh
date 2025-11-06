#!/usr/bin/env bash
# systemd Path 트리거 기반 자동 배포 설정 스크립트
# Usage: bash scripts/bin/setup_coldsync_autodeploy.sh

set -euo pipefail

echo "=== 0) 전제 확인 ==="
uname -a
echo ""
systemctl --version || { echo "systemd not available"; exit 1; }
echo ""
echo "WSL 확인:"
grep -qEi 'microsoft|wsl' /proc/version && echo "WSL detected" && systemctl is-system-running 2>&1 || echo "systemd check complete"
echo ""

echo "=== 1) 루트 설치기 작성 ==="
sudo tee /usr/local/sbin/coldsync-install <<'SH'
#!/usr/bin/env bash
set -euo pipefail

SRC="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST="/usr/local/bin/coldsync_hosp_from_usb.sh"
STATE="/var/lib/coldsync-hosp/.last.sha256"
TMP="$(mktemp -p /tmp coldsync.XXXXXX)"

log() { printf '[%s] %s\n' "$(date +'%F %T')" "$*" ; }

# 기본 검증
[ -f "$SRC" ] || { log "ERR: src not found: $SRC"; exit 1; }
head -1 "$SRC" | grep -qE '^#!' || { log "ERR: no shebang"; exit 1; }
# bash 문법 점검(있으면)
if command -v bash >/dev/null 2>&1; then
  bash -n "$SRC" || { log "ERR: bash -n failed"; exit 1; }
fi

mkdir -p /var/lib/coldsync-hosp
CUR=$(sha256sum "$SRC" | awk '{print $1}')
PREV=$(cat "$STATE" 2>/dev/null || true)

if [ "$CUR" = "$PREV" ] && [ -f "$DST" ]; then
  log "SKIP: no change (sha256=$CUR)"
  exit 0
fi

# 원자적 설치
install -o root -g root -m 0755 "$SRC" "$TMP"
mv -f "$TMP" "$DST"
sync

# 상태 갱신 + 보고
printf '%s\n' "$CUR" > "$STATE"
log "INSTALLED: $SRC -> $DST"
sha256sum "$SRC" "$DST" || true
SH

sudo chmod 0755 /usr/local/sbin/coldsync-install
echo "✅ 설치기 생성 완료"
ls -lh /usr/local/sbin/coldsync-install
echo ""

echo "=== 2) systemd Service 유닛 작성 ==="
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
# /usr/local/bin 쓸 수 있게 허용
ReadWritePaths=/usr/local/bin /var/lib/coldsync-hosp /tmp
UNIT
echo "✅ Service 유닛 생성 완료"
echo ""

echo "=== 2) systemd Path 유닛 작성 ==="
sudo tee /etc/systemd/system/coldsync-install.path <<'UNIT'
[Unit]
Description=Watch coldsync script and auto-install on change

[Path]
# 작업본이 바뀌면 트리거
PathChanged=/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh

[Install]
WantedBy=multi-user.target
UNIT
echo "✅ Path 유닛 생성 완료"
echo ""

echo "=== systemd 적용 ==="
sudo systemctl daemon-reload
echo "daemon-reload 완료"
sudo systemctl enable --now coldsync-install.path
echo ""
echo "✅ coldsync-install.path 활성화 완료"
sudo systemctl status coldsync-install.path --no-pager -l || true
echo ""

echo "=== 3) 즉시 수동 트리거 검증 ==="
sudo systemctl start coldsync-install.service
sleep 1
echo ""
echo "Service 상태:"
sudo systemctl status coldsync-install.service --no-pager -l || true
echo ""
echo "로그 (최근 50줄):"
sudo journalctl -u coldsync-install.service -n 50 --no-pager || true
echo ""

echo "=== 파일 검증 ==="
echo ""
echo "1. 설치된 파일:"
ls -lh /usr/local/bin/coldsync_hosp_from_usb.sh
echo ""
echo "2. 작업본:"
ls -lh /home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
echo ""
echo "3. SHA256 비교:"
sha256sum /usr/local/bin/coldsync_hosp_from_usb.sh /home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
echo ""
echo "✅ 파일 동기화 확인 완료"
echo ""

echo "=== 4) 저장 트리거 검증 ==="
echo ""
echo "작업본에 더미 변경 추가 (테스트용):"
echo "# Auto-install test $(date)" >> /home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
echo "변경 완료. Path 감지 대기 중..."
sleep 2
echo ""
echo "Path 유닛 상태:"
sudo systemctl status coldsync-install.path --no-pager -l | head -20 || true
echo ""
echo "Service 로그 (최근 20줄):"
sudo journalctl -u coldsync-install.service -n 20 --no-pager || true
echo ""

echo "=== ✅ 설정 완료! ==="
echo ""
echo "📋 사용법:"
echo "  1. VS Code에서 편집:"
echo "     code ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
echo ""
echo "  2. 저장하면 자동으로 /usr/local/bin에 배포됩니다."
echo ""
echo "📋 주요 명령어:"
echo "  - 로그 실시간 확인: sudo journalctl -u coldsync-install.service -f"
echo "  - 수동 설치: sudo /usr/local/sbin/coldsync-install"
echo "  - Path 상태: sudo systemctl status coldsync-install.path"
echo "  - 비활성화: sudo systemctl disable --now coldsync-install.path"
echo ""

