#!/usr/bin/env bash
# L4.0 B안: 시스템 유닛 유지 + sudo 제거
# Usage: bash scripts/evolution/setup_coldsync_system_unit_fixed.sh
# 목적: 루트 유닛에서 sudo 제거 + Path 유닛 개선 (p≈0.98)

set -euo pipefail

echo "=== L4.0 B안: 시스템 유닛 수정 (sudo 제거 + Path 개선) ==="
echo ""

# 1. 설치기 수정 (sudo 제거)
echo "1. 설치기 수정 (sudo 제거):"
sudo tee /usr/local/sbin/coldsync-install >/dev/null <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail

SRC="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST="/usr/local/bin/coldsync_hosp_from_usb.sh"
STATEDIR="/var/lib/coldsync-hosp"

mkdir -p "$STATEDIR" /usr/local/bin

# 없으면 성공 종료(패스)
if [[ ! -f "$SRC" ]]; then
  echo "[coldsync-install] SRC not found, nothing to do."
  exit 0
fi

src_sha=$(sha256sum "$SRC" | awk '{print $1}')
dst_sha=""
if [[ -f "$DST" ]]; then dst_sha=$(sha256sum "$DST" | awk '{print $1}'); fi

if [[ "$src_sha" != "$dst_sha" ]]; then
  install -o root -g root -m 0755 "$SRC" "$DST"
  echo "[coldsync-install] INSTALLED SRC_SHA=$src_sha DST_SHA=$(sha256sum "$DST" | awk '{print $1}')"
else
  echo "[coldsync-install] up-to-date SRC_SHA=$src_sha"
fi

# 반드시 성공 종료
exit 0
SH
sudo chmod 0755 /usr/local/sbin/coldsync-install
echo "✅ 설치기 수정 완료"
echo ""

# 2. Service 유닛 수정
echo "2. Service 유닛 수정:"
sudo mkdir -p /etc/systemd/system/coldsync-install.service.d
sudo tee /etc/systemd/system/coldsync-install.service.d/override.conf >/dev/null <<'CONF'
[Service]
# ── WSL 최소 하드닝 + 쓰기 허용 경로 지정 ──
ProtectSystem=no
ProtectHome=no
PrivateTmp=yes
NoNewPrivileges=yes

# 대상 쓰기 경로만 개방
ReadWritePaths=/usr/local/bin /var/lib/coldsync-hosp /tmp
# 소스 파일 읽기 허용
ReadOnlyPaths=/home/duri/DuRiWorkspace/scripts/bin
StateDirectory=coldsync-hosp

# ExecStartPre 명시적 제거
ExecStartPre=
CONF
echo "✅ Service 유닛 수정 완료"
echo ""

# 3. Path 유닛 수정 (디렉터리 감시 추가)
echo "3. Path 유닛 수정 (디렉터리 감시 추가):"
sudo cp /etc/systemd/system/coldsync-install.path /etc/systemd/system/coldsync-install.path.bak.$(date +%s) 2>/dev/null || true
sudo tee /etc/systemd/system/coldsync-install.path >/dev/null <<'UNIT'
[Unit]
Description=Watch coldsync script dir and auto-install on change

[Path]
# 1) 특정 파일 변경/교체
PathChanged=/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
# 2) 디렉터리 단위 변경(파일 rename/moved_to 포함)
PathChanged=/home/duri/DuRiWorkspace/scripts/bin
# 3) 메타데이터 변경 감지 (VS Code 저장 등)
PathModified=/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
# 급격한 연속 저장 시 과도 실행 방지
TriggerLimitIntervalSec=10s
TriggerLimitBurst=5

[Install]
WantedBy=multi-user.target
UNIT
echo "✅ Path 유닛 수정 완료"
echo ""

# 4. 데몬 리로드 및 활성화
echo "4. systemd 데몬 리로드 및 활성화:"
sudo systemctl daemon-reload
sudo systemctl enable --now coldsync-install.path
echo "✅ 활성화 완료"
echo ""

# 5. 초기 동기화
echo "5. 초기 동기화 실행:"
sudo systemctl start coldsync-install.service || echo "초기 동기화 실패"
echo ""

# 6. 상태 확인
echo "6. 상태 확인:"
systemctl status coldsync-install.path --no-pager | head -10 || echo "상태 확인 실패"
echo ""

# 7. 해시 확인
echo "7. 해시 확인:"
SRC_FILE="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST_FILE="/usr/local/bin/coldsync_hosp_from_usb.sh"
SRC_HASH=$(sha256sum "$SRC_FILE" | awk '{print $1}')
DST_HASH=$(sha256sum "$DST_FILE" 2>/dev/null | awk '{print $1}' || echo "")
echo "  SRC: $SRC_HASH"
echo "  DST: $DST_HASH"
if [ "$SRC_HASH" = "$DST_HASH" ] && [ -n "$DST_HASH" ]; then
    echo "✅ 해시 동기화 확인"
else
    echo "⚠️  해시 불일치"
fi
echo ""

echo "=== B안 설정 완료 ==="
echo ""
echo "사용 방법:"
echo "  1. VS Code에서 ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh 편집"
echo "  2. 저장 (Ctrl+S)"
echo "  3. 자동으로 /usr/local/bin에 배포됨"
echo ""
echo "검증:"
echo "  journalctl -u coldsync-install.service -n 5 --no-pager"
echo "  sha256sum /usr/local/bin/coldsync_hosp_from_usb.sh ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"

