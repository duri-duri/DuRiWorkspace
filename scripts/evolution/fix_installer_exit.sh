#!/usr/bin/env bash
# L4.0 설치기 exit 0 보장 패치 (WSL에서 실행)
# Usage: bash scripts/evolution/fix_installer_exit.sh
# 목적: 변경 없을 때도 0으로 종료하도록 방어

set -euo pipefail

echo "=== L4.0 설치기 exit 0 보장 패치 ==="
echo ""

INSTALLER="/usr/local/sbin/coldsync-install"

# 백업
echo "1. 설치기 백업:"
if [ -f "$INSTALLER" ]; then
    sudo cp "$INSTALLER" "${INSTALLER}.bak.$(date +%s)" 2>/dev/null || true
    echo "✅ 백업 완료"
else
    echo "⚠️  설치기 파일 없음"
fi
echo ""

# 설치기 재작성
echo "2. 설치기 재작성 (exit 0 보장):"
sudo tee "$INSTALLER" >/dev/null <<'SH'
#!/usr/bin/env bash
set -euo pipefail

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

sudo chmod 0755 "$INSTALLER"
echo "✅ 설치기 재작성 완료"
echo ""

# 테스트 실행
echo "3. 설치기 테스트 실행:"
if sudo "$INSTALLER"; then
    echo "✅ 설치기 테스트 성공"
else
    echo "⚠️  설치기 테스트 실패"
fi
echo ""

echo "=== 설치기 패치 완료 ==="
echo ""
echo "다음 단계:"
echo "  bash scripts/evolution/verify_installer_fix.sh   # 검증"

