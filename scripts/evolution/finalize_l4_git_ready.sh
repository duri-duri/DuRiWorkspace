#!/usr/bin/env bash
# L4.0 최종 완료 및 Git 준비 통합 실행
# Usage: bash scripts/evolution/finalize_l4_git_ready.sh
# 목적: ExecStart 인자 부여, 함수 의존성 제거, Git 준비

set -euo pipefail

echo "=== L4.0 최종 완료 및 Git 준비 통합 실행 ==="
echo ""

# 1. ExecStart 인자 부여 + 즉시 동기화
echo "=== 1단계: ExecStart 인자 부여 + 즉시 동기화 ==="
bash scripts/evolution/fix_execstart_args.sh
echo ""

# 2. 스크립트 함수 의존성 제거
echo "=== 2단계: 스크립트 함수 의존성 제거 ==="
bash scripts/evolution/fix_script_wrapper_deps.sh
echo ""

# 3. 즉시 조치 확인 (래퍼 사용)
echo "=== 3단계: 즉시 조치 확인 ==="
bash scripts/evolution/coldsync_immediate_check.sh
echo ""

# 4. Git hooks 설정 확인
echo "=== 4단계: Git hooks 설정 확인 ==="
if [ -f ".githooks/pre-commit-systemd-verify" ]; then
    echo "✅ pre-commit hook 존재"
    git config core.hooksPath .githooks
    echo "✅ Git hooks 경로 설정 완료"
else
    echo "⚠️  pre-commit hook 없음 (선택적)"
fi
echo ""

# 5. 최종 검증
echo "=== 5단계: 최종 검증 ==="
# 해시 확인
SRC_HASH=$(sha256sum "$HOME/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh" 2>/dev/null | awk '{print $1}' || echo "")
DST_HASH=$(sha256sum "$HOME/.local/bin/coldsync_hosp_from_usb.sh" 2>/dev/null | awk '{print $1}' || echo "")

if [ "$SRC_HASH" = "$DST_HASH" ] && [ -n "$SRC_HASH" ]; then
    echo "✅ 해시 일치: ${SRC_HASH:0:8}..."
else
    echo "⚠️  해시 불일치:"
    echo "   SRC: ${SRC_HASH:0:8}..."
    echo "   DST: ${DST_HASH:0:8}..."
fi

# ExecStart 확인
EXEC_START=$(systemctl --user cat coldsync-install.service 2>/dev/null | grep -E '^ExecStart=' | head -1 || echo "")
if echo "$EXEC_START" | grep -q 'coldsync_hosp_from_usb.sh'; then
    echo "✅ ExecStart 인자 포함 확인"
else
    echo "⚠️  ExecStart 인자 미포함"
fi

# 경고 확인
WARNINGS=$(journalctl --user -u coldsync-install.service --since "5 min ago" --no-pager 2>&1 | grep -i 'Unknown key name' || echo "")
if [ -z "$WARNINGS" ]; then
    echo "✅ 최근 5분 경고 없음"
else
    echo "⚠️  경고 발견"
fi
echo ""

echo "=== 최종 완료 및 Git 준비 완료 ==="
echo ""
echo "다음 단계:"
echo "  1. 브랜치 생성 및 푸시"
echo "     git switch -c feat/l4-coldsync-final-$(date +%Y%m%d)"
echo "     git add scripts/evolution/*.sh docs/ops/L4_COLDSYNC_FINAL.md .githooks/"
echo "     git commit -m 'ops: L4 coldsync finalized; ExecStart args; wrapper deps removed'"
echo "     git push -u origin HEAD"
echo ""
echo "  2. PR 생성 (gh CLI 사용 시)"
echo "     gh pr create --title 'L4 coldsync: finalize + ExecStart args + wrapper deps' --fill"

