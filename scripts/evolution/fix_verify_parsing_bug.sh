#!/usr/bin/env bash
# L4.0 검증 스크립트 정수 파싱 버그 핫픽스
# Usage: bash scripts/evolution/fix_verify_parsing_bug.sh
# 목적: integer expression expected 에러 제거

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

VERIFY_SCRIPT="scripts/evolution/verify_namespace_fix.sh"

echo "=== L4.0 검증 스크립트 정수 파싱 버그 핫픽스 ==="
echo ""

if [ ! -f "$VERIFY_SCRIPT" ]; then
    echo "⚠️  파일 없음: $VERIFY_SCRIPT"
    exit 0
fi

# 백업
echo "1. 백업:"
cp "$VERIFY_SCRIPT" "${VERIFY_SCRIPT}.bak.$(date +%s)" || true
echo "✅ 백업 완료"
echo ""

# 패치 적용
echo "2. 정수 파싱 버그 수정:"
sed -i \
    -e 's/\r$//' \
    -e 's/NAMESPACE_ERRORS=$(.*| grep -cE/count=$(journalctl -xeu coldsync-install.service -n 200 --no-pager 2\/dev\/null | grep -cE "NAMESPACE|Failed to set up mount namespacing" || echo "0")/' \
    -e 's/\$NAMESPACE_ERRORS/\${count:-0}/g' \
    -e 's/\[ "\$NAMESPACE_ERRORS" -eq 0 \]/\[ ${count:-0} -eq 0 ]/' \
    "$VERIFY_SCRIPT"

# tr -d로 공백 제거 추가 (wc -l 사용하는 부분)
sed -i \
    -e 's/wc -l | awk/wc -l | tr -d "[:space:]" | awk/g' \
    -e 's/awk '\''{print \$1}'\''/awk '\''{print \$1}'\'' | tr -d "[:space:]"/g' \
    "$VERIFY_SCRIPT" 2>/dev/null || true

echo "✅ 패치 적용 완료"
echo ""

# 문법 검사
echo "3. 문법 검사:"
if bash -n "$VERIFY_SCRIPT" 2>/dev/null; then
    echo "✅ 문법 검사 통과"
else
    echo "⚠️  문법 검사 실패"
    bash -n "$VERIFY_SCRIPT" 2>&1 | head -5
fi
echo ""

echo "=== 핫픽스 완료 ==="
echo ""
echo "다음 단계:"
echo "  bash scripts/evolution/verify_namespace_fix.sh   # 재검증"

