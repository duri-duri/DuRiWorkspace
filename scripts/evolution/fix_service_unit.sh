#!/usr/bin/env bash
# L4.0 coldsync-install.service 정규화 (쉘 스니펫 누수 제거)
# Usage: bash scripts/evolution/fix_service_unit.sh
# 목적: 서비스 유닛에서 쉘 스니펫이 키로 해석되는 문제 해결

set -euo pipefail

echo "=== L4.0 coldsync-install.service 정규화 ==="
echo ""

SERVICE="$HOME/.config/systemd/user/coldsync-install.service"

# 백업
echo "1. 서비스 유닛 백업:"
if [ -f "$SERVICE" ]; then
    cp -a "$SERVICE" "$SERVICE.bak.$(date +%s)"
    echo "✅ 백업 완료"
else
    echo "⚠️  서비스 유닛 없음: $SERVICE"
fi
echo ""

# 유해 라인 정리: set -Eeuo..., SRC=..., DST=... 등 쉘 변수/명령 흔적 제거
echo "2. 유해 라인 제거:"
if [ -f "$SERVICE" ]; then
    sed -i \
      -e '/set -Eeuo pipefail/d' \
      -e 's#^SRC=.*##' \
      -e 's#^DST=.*##' \
      -e 's#^\s*if\s\+! cmp -s .*##' \
      -e 's#^\s*install -m .*##' \
      -e 's#^\s*echo \[INSTALLED\].*##' \
      -e 's#^\s*echo \[up-to-date\].*##' \
      -e '/^$/d' \
      "$SERVICE"
    echo "✅ 유해 라인 제거 완료"
else
    echo "⚠️  서비스 유닛 없음, 건너뜀"
fi
echo ""

# 서비스 유닛 재작성 (깨끗한 버전)
echo "3. 서비스 유닛 재작성:"
cat > "$SERVICE" <<'UNIT'
[Unit]
Description=Install coldsync script into ~/.local/bin on change
Wants=coldsync-install.path

[Service]
Type=oneshot
# 소스/타깃 경로를 명시적으로 환경변수로 주입
Environment=SRC=%h/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
Environment=DST=%h/.local/bin/coldsync_hosp_from_usb.sh
# 안전: 대상 디렉토리 없으면 생성
ExecStartPre=/usr/bin/mkdir -p %h/.local/bin
# 디바운스 래퍼로 실행 (인자 전달형)
ExecStart=/bin/bash -lc '%h/.local/bin/coldsync_install_debounced.sh "$SRC" "$DST"'
# 로그가 길어져도 문제없음
StandardOutput=journal
StandardError=journal
UNIT
echo "✅ 서비스 유닛 재작성 완료"
echo ""

# 디바운스 래퍼가 인자를 받도록 수정
echo "4. 디바운스 래퍼 확인/수정:"
WRAPPER="$HOME/.local/bin/coldsync_install_debounced.sh"
if [ -f "$WRAPPER" ]; then
    # 인자 지원 확인
    if ! grep -q 'SRC="${1:-' "$WRAPPER"; then
        cp -a "$WRAPPER" "$WRAPPER.bak.$(date +%s)"
        # SRC/DST를 인자로 받도록 수정
        sed -i 's|SRC="$HOME/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"|SRC="${1:-$HOME/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh}"|' "$WRAPPER"
        sed -i 's|DST="$HOME/.local/bin/coldsync_hosp_from_usb.sh"|DST="${2:-$HOME/.local/bin/coldsync_hosp_from_usb.sh}"|' "$WRAPPER"
        echo "✅ 디바운스 래퍼 인자 지원 추가 완료"
    else
        echo "✅ 디바운스 래퍼 이미 인자 지원"
    fi
else
    echo "⚠️  디바운스 래퍼 없음: $WRAPPER"
fi
echo ""

# 반영
echo "5. systemd 데몬 리로드 및 재시작:"
systemctl --user daemon-reload
systemctl --user restart coldsync-install.path || true
systemctl --user restart coldsync-install.service || true
echo "✅ 반영 완료"
echo ""

# 확인
echo "6. 경고 확인:"
WARNINGS=$(journalctl --user -u coldsync-install.service -n 20 --no-pager 2>&1 | grep -i 'Unknown key name' || echo "")
if [ -z "$WARNINGS" ]; then
    echo "✅ 경고 없음"
else
    echo "⚠️  경고 발견:"
    echo "$WARNINGS"
fi
echo ""

# 최근 로그 확인
echo "7. 최근 로그 확인:"
journalctl --user -u coldsync-install.service -n 8 --no-pager || true
echo ""

echo "=== 서비스 유닛 정규화 완료 ==="
echo ""
echo "다음 단계:"
echo "  # 해시 확인"
echo "  cold-hash"
echo "  # 디바운스 테스트"
echo "  printf '\n# test %s\n' \"\$(date)\" >> ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
echo "  sleep 3"
echo "  cold-log | grep -E 'INSTALLED|up-to-date'"

