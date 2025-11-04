#!/usr/bin/env bash
# L4.0 .bashrc.d 로더 보증 + cold-* 실행 래퍼 고정 생성
# Usage: bash scripts/evolution/fix_bashrc_loader_and_wrappers.sh
# 목적: .bashrc.d 로더 보증 및 cold-* 실행 파일 고정 생성

set -euo pipefail

echo "=== L4.0 .bashrc.d 로더 보증 + cold-* 실행 래퍼 고정 생성 ==="
echo ""

# 1) .bashrc에 loader 보증
echo "1. .bashrc 로더 보증:"
if ! grep -q 'for f in.*\.bashrc\.d.*\.sh' ~/.bashrc; then
    cat >> ~/.bashrc <<'EOF'

# --- modular loader ---
if [ -d "$HOME/.bashrc.d" ]; then
  for f in "$HOME"/.bashrc.d/*.sh; do
    [ -r "$f" ] && . "$f"
  done
fi
EOF
    echo "✅ 로더 추가 완료"
else
    echo "✅ 로더 이미 존재"
fi
echo ""

# 2) systemd-user 헬퍼: alias 제거 + function 고정
echo "2. systemd --user 헬퍼 재작성:"
cat > ~/.bashrc.d/10-systemd-user.sh <<'EOF'
# --- systemd --user helpers (bash) ---
unalias dus dstat dlog drestart dmetrics 2>/dev/null || true

dus()      { command systemctl --user "$@"; }
dstat()    { command systemctl --user status "${1:-duri-shadow-exporter}" --no-pager; }
drestart() { command systemctl --user restart "${1:-duri-shadow-exporter}"; }
dlog()     { command journalctl --user -u "${1:-duri-shadow-exporter}" -f; }
dmetrics() { command curl -s http://localhost:9109/metrics | grep -E '^duri_shadow_(runs_total|heartbeat_seconds|exporter_up)'; }
EOF
echo "✅ systemd 헬퍼 재작성 완료"
echo ""

# 3) coldsync 헬퍼: 전부 function
echo "3. coldsync 헬퍼 재작성:"
cat > ~/.bashrc.d/20-coldsync.sh <<'EOF'
# --- coldsync helpers (bash) ---
unalias cold-log cold-hash cold-run cold-status 2>/dev/null || true

cold-log()    { command journalctl --user -u coldsync-install.service -n "${1:-20}" --no-pager; }
cold-hash()   { command sha256sum "$HOME/.local/bin/coldsync_hosp_from_usb.sh" "$HOME/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"; }
cold-run()    { command systemctl --user start coldsync-install.service; }
cold-status() { command systemctl --user status coldsync-install.path --no-pager; }
EOF
echo "✅ coldsync 헬퍼 재작성 완료"
echo ""

# 4) cold-* 실행 래퍼 고정 생성
echo "4. cold-* 실행 래퍼 고정 생성:"
mkdir -p ~/.local/bin

cat > ~/.local/bin/cold_log <<'SH'
#!/usr/bin/env bash
journalctl --user -u coldsync-install.service -n "${1:-20}" --no-pager
SH

cat > ~/.local/bin/cold_hash <<'SH'
#!/usr/bin/env bash
sha256sum "$HOME/.local/bin/coldsync_hosp_from_usb.sh" "$HOME/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
SH

cat > ~/.local/bin/cold_run <<'SH'
#!/usr/bin/env bash
systemctl --user start coldsync-install.service
SH

cat > ~/.local/bin/cold_status <<'SH'
#!/usr/bin/env bash
systemctl --user status coldsync-install.path --no-pager
SH

chmod +x ~/.local/bin/cold_*
echo "✅ 실행 래퍼 생성 완료"
echo ""

# 5) CRLF/공백 정리 + 구문 검사
echo "5. CRLF 및 공백 정리:"
sed -i 's/\r$//' ~/.bashrc ~/.bashrc.d/*.sh 2>/dev/null || true
sed -i 's/[ \t]\+$//' ~/.bashrc ~/.bashrc.d/*.sh 2>/dev/null || true
echo "✅ 정리 완료"
echo ""

echo "6. 구문 검사:"
if bash -n ~/.bashrc && bash -n ~/.bashrc.d/10-systemd-user.sh && bash -n ~/.bashrc.d/20-coldsync.sh 2>&1; then
    echo "✅ [OK] 모든 파일 구문 검사 통과"
else
    echo "❌ [FAIL] 구문 오류 발견"
    bash -n ~/.bashrc || true
    bash -n ~/.bashrc.d/10-systemd-user.sh || true
    bash -n ~/.bashrc.d/20-coldsync.sh || true
    exit 1
fi
echo ""

# 7) 재적용
echo "7. .bashrc 적용:"
source ~/.bashrc || echo "⚠️  source 실패 (경고 무시 가능)"
echo "✅ 적용 완료"
echo ""

# 8) 타입 확인
echo "8. 함수 타입 확인:"
if type dus dstat dlog drestart dmetrics cold-log cold-hash cold-run cold-status >/dev/null 2>&1; then
    echo "✅ 모든 함수 정의 확인"
    echo ""
    echo "함수 목록:"
    type dus cold-log cold-hash cold-run cold-status 2>/dev/null | head -20 || true
else
    echo "⚠️  일부 함수 미확인"
    echo ""
    echo "확인된 함수:"
    type dus 2>/dev/null || echo "  dus: 없음"
    type cold-log 2>/dev/null || echo "  cold-log: 없음"
fi
echo ""

# 9) 실행 래퍼 확인
echo "9. 실행 래퍼 확인:"
if [ -x ~/.local/bin/cold_log ] && [ -x ~/.local/bin/cold_hash ] && [ -x ~/.local/bin/cold_run ] && [ -x ~/.local/bin/cold_status ]; then
    echo "✅ 모든 실행 래퍼 확인"
    ls -lh ~/.local/bin/cold_* 2>/dev/null || true
else
    echo "⚠️  일부 실행 래퍼 미확인"
fi
echo ""

echo "=== .bashrc.d 로더 보증 + cold-* 실행 래퍼 고정 생성 완료 ==="
echo ""
echo "생성된 파일:"
echo "  ~/.bashrc.d/10-systemd-user.sh"
echo "  ~/.bashrc.d/20-coldsync.sh"
echo "  ~/.local/bin/cold_log"
echo "  ~/.local/bin/cold_hash"
echo "  ~/.local/bin/cold_run"
echo "  ~/.local/bin/cold_status"
echo ""
echo "다음 단계:"
echo "  type dus cold-log cold-hash cold-run cold-status"
echo "  cold_status"
echo "  cold_hash"

