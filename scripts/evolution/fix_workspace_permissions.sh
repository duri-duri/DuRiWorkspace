#!/usr/bin/env bash
# L4.0 워크트리 권한/해시 드리프트 고정 (WSL에서 실행)
# Usage: bash scripts/evolution/fix_workspace_permissions.sh
# 목적: 재발 방지

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

SRC_FILE="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"

echo "=== L4.0 워크트리 권한/해시 드리프트 고정 ==="
echo ""

# 3-1) 소유권 고정
echo "1. 소유권 고정:"
sudo chown duri:duri "$SRC_FILE"
echo "✅ 소유권 설정 완료"
echo ""

# 3-2) 실행권한/라인엔딩
echo "2. 실행권한/라인엔딩:"
chmod 0755 "$SRC_FILE"
echo "✅ 실행권한 설정 완료"

if command -v dos2unix >/dev/null 2>&1; then
    dos2unix "$SRC_FILE" 2>/dev/null || true
    echo "✅ 라인엔딩 변환 완료"
else
    echo "ℹ️  dos2unix 없음 (스킵)"
fi
echo ""

# 3-3) 3점 스냅샷
echo "3. 3점 스냅샷:"
echo ""
echo "== working =="
sha256sum "$SRC_FILE" 2>/dev/null || echo "워킹트리 파일 없음"

echo "== installed =="
sha256sum /usr/local/bin/coldsync_hosp_from_usb.sh 2>/dev/null || echo "설치본 파일 없음"

echo "== git HEAD =="
git show HEAD:scripts/bin/coldsync_hosp_from_usb.sh 2>/dev/null | sha256sum || echo "git HEAD 없음"
echo ""

# 권고: 설치본이 정답이라면
DST_FILE="/usr/local/bin/coldsync_hosp_from_usb.sh"
if [ -f "$DST_FILE" ]; then
    echo "4. 설치본 기준 정렬 (선택):"
    read -p "설치본을 워크트리로 복사하시겠습니까? (yes/no): " CONFIRM
    if [ "$CONFIRM" = "yes" ]; then
        sudo install -m 0755 "$DST_FILE" "$SRC_FILE"
        sudo chown duri:duri "$SRC_FILE"
        echo "✅ 설치본을 워크트리로 복사 완료"
        echo ""
        echo "📋 Git 커밋 권장:"
        echo "  git add scripts/bin/coldsync_hosp_from_usb.sh"
        echo "  git commit -m 'fix(coldsync): align workspace script to installed (WSL-safe, LF)'"
    else
        echo "ℹ️  스킵"
    fi
fi
echo ""

echo "=== 워크트리 권한/해시 드리프트 고정 완료 ==="

