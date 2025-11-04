#!/usr/bin/env bash
# L4.0 .bashrc 모듈화 및 구문 에러 원천 차단
# Usage: bash scripts/evolution/modularize_bashrc.sh
# 목적: 함수/별칭을 ~/.bashrc.d/*.sh로 분리하여 구문 에러 파급 방지

set -euo pipefail

echo "=== L4.0 .bashrc 모듈화 및 구문 에러 원천 차단 ==="
echo ""

# 안전 백업
echo "1. .bashrc 백업:"
cp -a ~/.bashrc ~/.bashrc.pre_fix.$(date +%s)
echo "✅ 백업 완료"
echo ""

# 1-1) bashrc.d 디렉토리 도입
echo "2. ~/.bashrc.d 디렉토리 생성:"
mkdir -p ~/.bashrc.d
echo "✅ 디렉토리 생성 완료"
echo ""

# 1-2) coldsync 헬퍼를 전용 파일로 분리
echo "3. coldsync 헬퍼 분리:"
cat > ~/.bashrc.d/20-coldsync.sh <<'EOF'
# --- coldsync helpers (functions) ---
cold-log()    { journalctl --user -u coldsync-install.service -n "${1:-20}" --no-pager; }
cold-hash()   { sha256sum ~/.local/bin/coldsync_hosp_from_usb.sh ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh; }
cold-run()    { systemctl --user start coldsync-install.service; }
cold-status() { systemctl --user status coldsync-install.path --no-pager; }
EOF
chmod +x ~/.bashrc.d/20-coldsync.sh
echo "✅ coldsync 헬퍼 분리 완료"
echo ""

# 1-3) systemd 헬퍼도 외부 파일로 분리
echo "4. systemd --user 헬퍼 분리:"
cat > ~/.bashrc.d/10-systemd-user.sh <<'EOF'
# --- systemd --user helpers ---
dus()      { systemctl --user "$@"; }
dstat()    { systemctl --user status "${1:-duri-shadow-exporter}" --no-pager; }
drestart() { systemctl --user restart "${1:-duri-shadow-exporter}"; }
dlog()     { journalctl --user -u "${1:-duri-shadow-exporter}" -f; }
dmetrics() { curl -s http://localhost:9109/metrics | grep -E '^duri_shadow_(runs_total|heartbeat_seconds|exporter_up)'; }
EOF
chmod +x ~/.bashrc.d/10-systemd-user.sh
echo "✅ systemd 헬퍼 분리 완료"
echo ""

# 1-4) 기존 .bashrc에서 충돌 가능 영역 정리
echo "5. .bashrc 정리 (충돌 영역 제거):"
awk '
BEGIN{skip=0}

{
  # storage.env 강제 source 흔적 제거
  if ($0 ~ /source[[:space:]]+~\/DuRiWorkspace\/etc\/storage\.env/) next;
  
  # 190~220 부근의 중복 alias/함수 블록 제거
  if (NR>=190 && NR<=220) {
    if ($0 ~ /(alias[[:space:]]+(dus|dstat|dlog|drestart|dmetrics)=|^dus\(\)|^dstat\(\)|^dlog\(\)|^drestart\(\)|^dmetrics\(\))/) next;
    # 라인 끝에 붙은 유령 달러기호 제거
    sub(/\$[[:space:]]*$/,"");
  }
  
  print;
}

END{
  print "";
  print "# --- load ~/.bashrc.d fragments ---";
  print "for f in \"$HOME/.bashrc.d\"/*.sh; do";
  print "  [ -r \"$f\" ] && . \"$f\"";
  print "done";
}
' ~/.bashrc > ~/.bashrc.fixed && mv ~/.bashrc.fixed ~/.bashrc

# 1-5) CRLF/불필요 공백 정리
echo "6. CRLF 및 공백 정리:"
sed -i 's/\r$//' ~/.bashrc
sed -i 's/[ \t]\+$//' ~/.bashrc
echo "✅ 정리 완료"
echo ""

# 1-6) 구문 검사
echo "7. 구문 검사:"
if bash -n ~/.bashrc 2>&1; then
    echo "✅ [OK] bashrc syntax clean"
else
    echo "❌ [FAIL] bashrc syntax error"
    bash -n ~/.bashrc || true
    echo ""
    echo "문제 구간 확인:"
    sed -n '190,220p' ~/.bashrc
    exit 1
fi
echo ""

# 1-7) 적용 테스트
echo "8. 적용 테스트:"
source ~/.bashrc || echo "⚠️  source 실패 (경고 무시 가능)"

# 1-8) 확인
echo "9. 함수 확인:"
if type dus dstat dlog drestart dmetrics cold-log cold-hash cold-run cold-status >/dev/null 2>&1; then
    echo "✅ 모든 함수 정의 확인"
    type dus cold-log cold-hash cold-run cold-status 2>/dev/null | head -10 || true
else
    echo "⚠️  일부 함수 미확인 (경고 무시 가능)"
fi
echo ""

echo "=== .bashrc 모듈화 완료 ==="
echo ""
echo "생성된 파일:"
echo "  ~/.bashrc.d/10-systemd-user.sh"
echo "  ~/.bashrc.d/20-coldsync.sh"
echo ""
echo "다음 단계:"
echo "  source ~/.bashrc"
echo "  type cold-log cold-hash cold-run cold-status"

