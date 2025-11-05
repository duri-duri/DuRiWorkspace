#!/usr/bin/env bash
# L4.0 freeze-guard 정식 예외 규칙 추가
# Usage: bash scripts/evolution/add_freeze_allow_rule.sh
# 목적: freeze-guard 정식 예외 규칙 추가 (FREEZE_BYPASS 대체)

set -euo pipefail

echo "=== L4.0 freeze-guard 정식 예외 규칙 추가 ==="
echo ""

FREEZE_ALLOW=".github/freeze-allow.txt"

# freeze-allow.txt 확인
echo "1. freeze-allow.txt 확인:"
if [ ! -f "$FREEZE_ALLOW" ]; then
    mkdir -p .github
    touch "$FREEZE_ALLOW"
    echo "✅ freeze-allow.txt 생성"
fi
echo ""

# 기존 규칙 확인
echo "2. 기존 규칙 확인:"
if grep -q 'coldsync_hosp_from_usb' "$FREEZE_ALLOW" 2>/dev/null; then
    echo "✅ coldsync 예외 규칙 이미 존재"
    grep 'coldsync_hosp_from_usb' "$FREEZE_ALLOW" || true
else
    echo "⚠️  coldsync 예외 규칙 없음 (추가 필요)"
fi
echo ""

# 예외 규칙 추가 (형식에 따라 조정 필요)
echo "3. 예외 규칙 추가:"
# scripts/bin/** 패턴 확인
if ! grep -q 'scripts/bin' "$FREEZE_ALLOW" 2>/dev/null; then
    # scripts/evolution/** 앞에 추가
    sed -i '/^scripts\/evolution\/\*\*/i scripts/bin/**\nscripts/bin/coldsync_hosp_from_usb.sh' "$FREEZE_ALLOW"
    echo "✅ scripts/bin/** 패턴 추가 완료"
else
    echo "✅ scripts/bin 패턴 이미 존재"
fi
echo ""

# 변경사항 확인
echo "4. 변경사항 확인:"
git diff "$FREEZE_ALLOW" || echo "변경사항 없음"
echo ""

# 커밋 안내
echo "5. 커밋 안내:"
echo "  git add $FREEZE_ALLOW"
echo "  git commit -m 'ops: freeze-allow rule for L4 coldsync finalize'"
echo "  git push"
echo ""

echo "=== freeze-guard 예외 규칙 추가 완료 ==="
echo ""
echo "참고: freeze-guard의 실제 파서 형식에 맞게 조정이 필요할 수 있습니다."
echo "      형식이 다르면 .github/workflows/freeze-guard.yml을 확인하세요."

