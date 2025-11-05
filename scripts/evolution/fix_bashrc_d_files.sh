#!/usr/bin/env bash
# L4.0 .bashrc.d 구문 에러 제거 + alias 충돌 제거
# Usage: bash scripts/evolution/fix_bashrc_d_files.sh
# 목적: .bashrc.d 파일들의 구문 에러 및 alias 충돌 해결

set -euo pipefail

echo "=== L4.0 .bashrc.d 구문 에러 제거 + alias 충돌 제거 ==="
echo ""

# 1) 안전 백업
echo "1. .bashrc.d 파일 백업:"
mkdir -p ~/.bashrc.d
for f in ~/.bashrc.d/*.sh; do
    [ -f "$f" ] && cp -a "$f" "${f}.bak.$(date +%s)" 2>/dev/null || true
done
echo "✅ 백업 완료"
echo ""

# 2) 10-systemd-user.sh 내용 교체
echo "2. systemd --user 헬퍼 재작성:"
cat > ~/.bashrc.d/10-systemd-user.sh <<'EOF'
# --- systemd --user helpers ---
# ensure no alias conflicts
unalias dus 2>/dev/null || true
unalias dstat 2>/dev/null || true
unalias dlog 2>/dev/null || true
unalias drestart 2>/dev/null || true
unalias dmetrics 2>/dev/null || true

# define as bash functions
dus()      { command systemctl --user "$@"; }
dstat()    { command systemctl --user status "${1:-duri-shadow-exporter}" --no-pager; }
drestart() { command systemctl --user restart "${1:-duri-shadow-exporter}"; }
dlog()     { command journalctl --user -u "${1:-duri-shadow-exporter}" -f; }
dmetrics() { command curl -s http://localhost:9109/metrics | grep -E '^duri_shadow_(runs_total|heartbeat_seconds|exporter_up)'; }
EOF
echo "✅ systemd 헬퍼 재작성 완료"
echo ""

# 3) 20-coldsync.sh 내용 교체 (가드 추가)
echo "3. coldsync 헬퍼 재작성:"
cat > ~/.bashrc.d/20-coldsync.sh <<'EOF'
# --- coldsync helpers (functions) ---
cold_log()    { journalctl --user -u coldsync-install.service -n "${1:-20}" --no-pager; }
cold_hash()   { sha256sum "$HOME/.local/bin/coldsync_hosp_from_usb.sh" \
                        "$HOME/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"; }
cold_run()    { systemctl --user start coldsync-install.service; }
cold_status() { systemctl --user status coldsync-install.path --no-pager | head -12; }

# 하이픈 alias (인터랙티브에서만 유효)
alias cold-log='cold_log'
alias cold-hash='cold_hash'
alias cold-run='cold_run'
alias cold-status='cold_status'
EOF
echo "✅ coldsync 헬퍼 재작성 완료"
echo ""

# 3) 모든 bashrc 조각 CRLF/이상문자 정리 + 구문 검사
echo "4. CRLF 및 공백 정리:"
sed -i 's/\r$//' ~/.bashrc.d/*.sh 2>/dev/null || true
sed -i 's/[ \t]\+$//' ~/.bashrc.d/*.sh 2>/dev/null || true
echo "✅ 정리 완료"
echo ""

echo "5. 구문 검사:"
for f in ~/.bashrc.d/*.sh; do
    if [ -f "$f" ]; then
        if bash -n "$f" 2>&1; then
            echo "  ✅ $(basename "$f")"
        else
            echo "  ❌ $(basename "$f") 구문 오류"
            bash -n "$f" || true
            exit 1
        fi
    fi
done
echo ""

# 4) .bashrc도 한 번 더 깨끗이
echo "6. .bashrc 정리:"
sed -i 's/\r$//' ~/.bashrc
sed -i 's/[ \t]\+$//' ~/.bashrc
if bash -n ~/.bashrc 2>&1; then
    echo "✅ [OK] .bashrc syntax clean"
else
    echo "❌ [FAIL] .bashrc syntax error"
    bash -n ~/.bashrc || true
    exit 1
fi
echo ""

# 5) 재적용
echo "7. .bashrc 적용:"
source ~/.bashrc || echo "⚠️  source 실패 (경고 무시 가능)"
echo "✅ 적용 완료"
echo ""

# 6) 확인
echo "8. 함수 확인:"
if type dus dstat dlog drestart dmetrics cold-log cold-hash cold-run cold-status >/dev/null 2>&1; then
    echo "✅ 모든 함수 정의 확인"
    echo ""
    echo "함수 목록:"
    type dus cold-log cold-hash cold-run cold-status 2>/dev/null | head -15 || true
else
    echo "⚠️  일부 함수 미확인"
    echo ""
    echo "확인된 함수:"
    type dus 2>/dev/null || echo "  dus: 없음"
    type cold-log 2>/dev/null || echo "  cold-log: 없음"
fi
echo ""

echo "=== .bashrc.d 파일 정리 완료 ==="
echo ""
echo "생성된 파일:"
echo "  ~/.bashrc.d/10-systemd-user.sh"
echo "  ~/.bashrc.d/20-coldsync.sh"
echo ""
echo "다음 단계:"
echo "  type dus cold-log cold-hash cold-run cold-status"

