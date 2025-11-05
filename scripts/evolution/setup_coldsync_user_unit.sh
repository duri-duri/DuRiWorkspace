#!/usr/bin/env bash
# L4.0 A안: 유저 유닛 + ~/.local/bin (루트 불필요)
# Usage: bash scripts/evolution/setup_coldsync_user_unit.sh
# 목적: VS Code 저장 시 자동 동기화 (p≈0.995)

set -euo pipefail

echo "=== L4.0 A안: 유저 유닛 설정 ==="
echo ""

# 1. 타깃 경로 생성
echo "1. ~/.local/bin 디렉토리 생성:"
mkdir -p ~/.local/bin
echo "✅ 완료"
echo ""

# 2. 초기 복사
echo "2. 초기 파일 복사:"
SRC="$HOME/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST="$HOME/.local/bin/coldsync_hosp_from_usb.sh"
if [ -f "$SRC" ]; then
    cp -f "$SRC" "$DST"
    chmod +x "$DST"
    echo "✅ 초기 복사 완료: $DST"
else
    echo "❌ 소스 파일 없음: $SRC"
    exit 1
fi
echo ""

# 3. user systemd 디렉토리 생성
echo "3. user systemd 디렉토리 생성:"
mkdir -p ~/.config/systemd/user
echo "✅ 완료"
echo ""

# 4. Service 유닛 생성
echo "4. Service 유닛 생성:"
cat > ~/.config/systemd/user/coldsync-install.service <<'UNIT'
[Unit]
Description=Install coldsync script into ~/.local/bin on change

[Service]
Type=oneshot
# 사용자 권한으로 동작 → sudo 불필요
ExecStart=/bin/bash -c '\
  set -Eeuo pipefail; \
  SRC="$HOME/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"; \
  DST="$HOME/.local/bin/coldsync_hosp_from_usb.sh"; \
  if ! [ -r "$SRC" ]; then echo "[ERR] SRC not readable"; exit 2; fi; \
  mkdir -p "$HOME/.local/bin"; \
  if ! [ -f "$DST" ] || ! cmp -s "$SRC" "$DST"; then \
    install -m 0755 "$SRC" "$DST"; \
    echo "[INSTALLED] $(date -Is) -> $DST"; \
  else \
    echo "[up-to-date] $(date -Is)"; \
  fi'
# 과도 실행 억제(동일 파일 잦은 저장 대비): 300ms 디바운스
ExecStartPost=/usr/bin/sleep 0.3
UNIT
echo "✅ Service 유닛 생성 완료"
echo ""

# 5. Path 유닛 생성
echo "5. Path 유닛 생성:"
cat > ~/.config/systemd/user/coldsync-install.path <<'UNIT'
[Unit]
Description=Watch coldsync script and auto-install on change

[Path]
# VS Code의 save 패턴(임시파일→rename, metadata update) 모두 대응
PathChanged=%h/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
PathModified=%h/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
# 디렉터리 단위 변경(파일 rename/moved_to 포함)
PathChanged=%h/DuRiWorkspace/scripts/bin

[Install]
WantedBy=default.target
UNIT
echo "✅ Path 유닛 생성 완료"
echo ""

# 6. 활성화
echo "6. user systemd 활성화:"
systemctl --user daemon-reload
systemctl --user enable --now coldsync-install.path
echo "✅ 활성화 완료"
echo ""

# 7. 상태 확인
echo "7. 상태 확인:"
systemctl --user status coldsync-install.path --no-pager | head -12 || echo "상태 확인 실패"
echo ""

# 8. 초기 동기화
echo "8. 초기 동기화 실행:"
systemctl --user start coldsync-install.service || echo "초기 동기화 실패"
echo ""

# 9. 해시 확인
echo "9. 해시 확인:"
SRC_HASH=$(sha256sum "$SRC" | awk '{print $1}')
DST_HASH=$(sha256sum "$DST" 2>/dev/null | awk '{print $1}' || echo "")
echo "  SRC: $SRC_HASH"
echo "  DST: $DST_HASH"
if [ "$SRC_HASH" = "$DST_HASH" ] && [ -n "$DST_HASH" ]; then
    echo "✅ 해시 동기화 확인"
else
    echo "⚠️  해시 불일치"
fi
echo ""

echo "=== A안 설정 완료 ==="
echo ""
echo "사용 방법:"
echo "  1. VS Code에서 ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh 편집"
echo "  2. 저장 (Ctrl+S)"
echo "  3. 자동으로 ~/.local/bin에 배포됨"
echo ""
echo "검증:"
echo "  journalctl --user -u coldsync-install.service -n 5 --no-pager"
echo "  sha256sum ~/.local/bin/coldsync_hosp_from_usb.sh ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"

