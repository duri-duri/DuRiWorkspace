#!/usr/bin/env bash
# L4.0 TriggerLimit 제거 + 서비스 측 디바운스(버스트 보호)
# Usage: bash scripts/evolution/fix_triggerlimit_debounce.sh
# 목적: Path 유닛 TriggerLimit 제거 + 서비스 실행 시 디바운스 적용

set -euo pipefail

echo "=== L4.0 TriggerLimit 제거 + 디바운스 적용 ==="
echo ""

# 2-1) Path 유닛에서 TriggerLimit 라인 완전 제거
echo "1. Path 유닛 TriggerLimit 제거:"
UNIT="$HOME/.config/systemd/user/coldsync-install.path"
if [ -f "$UNIT" ]; then
    cp -a "$UNIT" "$UNIT.bak.$(date +%s)"
    sed -i '/^TriggerLimitIntervalSec=/d;/^TriggerLimitBurst=/d' "$UNIT"
    echo "✅ TriggerLimit 제거 완료"
else
    echo "⚠️  Path 유닛 없음: $UNIT"
fi
echo ""

# 2-2) 디바운스 래퍼 추가
echo "2. 디바운스 래퍼 생성:"
mkdir -p ~/.local/bin

cat > ~/.local/bin/coldsync_install_debounced.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

umask 022

WIN=10               # 최소 간격(초)
STAMP_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/coldsync"
STAMP="$STAMP_DIR/.last"
LOCK="$STAMP_DIR/.lock"

mkdir -p "$STAMP_DIR"

# flock으로 중복 실행 방지
exec 9>"$LOCK"
flock -n 9 || exit 0

now=$(date +%s)
last=0
[ -f "$STAMP" ] && last=$(cat "$STAMP" 2>/dev/null || echo 0)

# 최소 간격 미만이면 조용히 스킵
if [ "$((now-last))" -lt "$WIN" ]; then
  exit 0
fi

echo "$now" > "$STAMP"

# 실제 설치 로직: SRC→DST 비교 후 필요 시 설치
# 인자로 전달되면 사용, 없으면 기본값 사용
SRC="${1:-$HOME/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh}"
DST="${2:-$HOME/.local/bin/coldsync_hosp_from_usb.sh}"

if ! cmp -s "$SRC" "$DST" 2>/dev/null; then
  install -m 0755 "$SRC" "$DST"
  echo "[INSTALLED] $(date --iso-8601=seconds) -> $DST"
else
  echo "[up-to-date] $(date --iso-8601=seconds)"
fi
EOF

chmod +x ~/.local/bin/coldsync_install_debounced.sh
echo "✅ 디바운스 래퍼 생성 완료"
echo ""

# 2-3) Service 유닛이 래퍼를 호출하도록 수정
echo "3. Service 유닛 수정:"
SERVICE="$HOME/.config/systemd/user/coldsync-install.service"
if [ -f "$SERVICE" ]; then
    cp -a "$SERVICE" "$SERVICE.bak.$(date +%s)"
    
    # ExecStart 라인을 래퍼로 교체
    if grep -q '^ExecStart=' "$SERVICE"; then
        sed -i 's#^ExecStart=.*#ExecStart=%h/.local/bin/coldsync_install_debounced.sh#' "$SERVICE"
    else
        # ExecStart가 없을 경우 추가
        sed -i '/^\[Service\]/a ExecStart=%h/.local/bin/coldsync_install_debounced.sh' "$SERVICE"
    fi
    
    echo "✅ Service 유닛 수정 완료"
else
    echo "⚠️  Service 유닛 없음: $SERVICE"
fi
echo ""

# 2-4) 반영
echo "4. systemd 데몬 리로드 및 재시작:"
systemctl --user daemon-reload
systemctl --user restart coldsync-install.path
systemctl --user restart coldsync-install.service || true
echo "✅ 반영 완료"
echo ""

# 2-5) 상태 확인
echo "5. 상태 확인:"
systemctl --user status coldsync-install.path --no-pager | head -12 || true
echo ""

# 2-6) 경고 확인
echo "6. 경고 확인:"
WARNINGS=$(systemctl --user status coldsync-install.path --no-pager 2>&1 | grep -iE 'unknown key|triggerlimit' || echo "")
if [ -z "$WARNINGS" ]; then
    echo "✅ 경고 없음"
else
    echo "⚠️  경고 발견:"
    echo "$WARNINGS"
fi
echo ""

echo "=== TriggerLimit 제거 + 디바운스 적용 완료 ==="
echo ""
echo "다음 단계:"
echo "  # 디바운스 테스트"
echo "  printf '\n# test1 %s\n' \"\$(date)\" >> ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
echo "  sleep 1"
echo "  printf '\n# test2 %s\n' \"\$(date)\" >> ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
echo "  sleep 3"
echo "  cold-log | grep -E 'INSTALLED|up-to-date'"

