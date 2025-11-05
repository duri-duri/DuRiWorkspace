#!/usr/bin/env bash
# L4.0 coldsync 설치 원자성 보강 (해시 드리프트 방지)
# Usage: bash scripts/evolution/fix_atomic_install.sh
# 목적: tmp→atomic mv로 일시적 해시 불일치 방지

set -euo pipefail

echo "=== L4.0 coldsync 설치 원자성 보강 ==="
echo ""

WRAPPER="$HOME/.local/bin/coldsync_install_debounced.sh"

# 백업
echo "1. 디바운스 래퍼 백업:"
if [ -f "$WRAPPER" ]; then
    cp -a "$WRAPPER" "$WRAPPER.bak.$(date +%s)"
    echo "✅ 백업 완료"
else
    echo "❌ 디바운스 래퍼 없음: $WRAPPER"
    exit 1
fi
echo ""

# 디바운스 윈도 12초로 조정 (권장)
echo "2. 디바운스 윈도 조정 (10→12초):"
if grep -q '^WIN=10' "$WRAPPER"; then
    sed -i 's/^WIN=10/WIN=12/' "$WRAPPER"
    echo "✅ 디바운스 윈도 12초로 조정 완료"
else
    echo "✅ 디바운스 윈도 이미 설정됨"
fi
echo ""

# 설치 로직을 atomic mv로 교체
echo "3. 설치 로직 atomic mv로 교체:"
cat > "$WRAPPER" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

umask 022

WIN=12               # 최소 간격(초, 저장 폭주 방지)
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

# 실제 설치 로직: SRC→DST 비교 후 필요 시 atomic 설치
# 인자로 전달되면 사용, 없으면 기본값 사용
SRC="${1:-$HOME/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh}"
DST="${2:-$HOME/.local/bin/coldsync_hosp_from_usb.sh}"

# 파일 비교
if ! cmp -s "$SRC" "$DST" 2>/dev/null; then
  # atomic install: tmp → sync → atomic mv
  TMP="$(mktemp "${DST}.XXXXXX")"
  chmod 0755 "$SRC"
  cp -f "$SRC" "$TMP"
  sync
  mv -f "$TMP" "$DST"   # atomic move
  sync
  echo "[INSTALLED] $(date --iso-8601=seconds) -> $DST"
else
  echo "[up-to-date] $(date --iso-8601=seconds)"
fi
EOF

chmod +x "$WRAPPER"
echo "✅ atomic install 로직 적용 완료"
echo ""

# Path 유닛 이중화 (PathChanged + PathModified)
echo "4. Path 유닛 이중화:"
PATH_UNIT="$HOME/.config/systemd/user/coldsync-install.path"
if [ -f "$PATH_UNIT" ]; then
    cp -a "$PATH_UNIT" "$PATH_UNIT.bak.$(date +%s)"
    
    # 절대 경로로 확정
    SRC_ABS="$HOME/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
    
    cat > "$PATH_UNIT" <<EOF
[Unit]
Description=Watch coldsync script and auto-install on change

[Path]
# 변경/수정 모두 트리거 (이중화)
PathChanged=${SRC_ABS}
PathModified=${SRC_ABS}

[Install]
WantedBy=default.target
EOF
    
    echo "✅ Path 유닛 이중화 완료"
else
    echo "⚠️  Path 유닛 없음: $PATH_UNIT"
fi
echo ""

# 반영
echo "5. systemd 데몬 리로드 및 재시작:"
systemctl --user daemon-reload
systemctl --user restart coldsync-install.path
systemctl --user restart coldsync-install.service || true
echo "✅ 반영 완료"
echo ""

# 확인
echo "6. Path 유닛 확인:"
systemctl --user cat coldsync-install.path | grep -E '^(PathChanged|PathModified|Unit)=' || true
echo ""

echo "=== 원자성 보강 완료 ==="
echo ""
echo "다음 단계:"
echo "  ${HOME}/.local/bin/cold_status"
echo "  ${HOME}/.local/bin/cold_hash"

