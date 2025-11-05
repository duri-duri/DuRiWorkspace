#!/usr/bin/env bash
# L4.0 서비스 유닛 재오염 방지 (pre-commit hook)
# Usage: bash scripts/evolution/setup_precommit_hook.sh
# 목적: 서비스 유닛 파일의 쉘 조각 재오염 방지

set -euo pipefail

echo "=== L4.0 서비스 유닛 재오염 방지 (pre-commit hook) ==="
echo ""

HOOKS_DIR=".githooks"
PRE_COMMIT_HOOK="$HOOKS_DIR/pre-commit-systemd-verify"

# .githooks 디렉토리 생성
echo "1. .githooks 디렉토리 생성:"
mkdir -p "$HOOKS_DIR"
echo "✅ 디렉토리 생성 완료"
echo ""

# pre-commit hook 생성
echo "2. pre-commit hook 생성:"
cat > "$PRE_COMMIT_HOOK" <<'SH'
#!/usr/bin/env bash
set -euo pipefail

# systemd 유닛 파일 검증
verify_systemd_unit() {
    local unit_file="$1"
    if [ -f "$unit_file" ]; then
        # systemd-analyze verify (user unit)
        if ! systemd-analyze --user verify "$unit_file" 2>/dev/null; then
            echo "❌ [FAIL] Invalid systemd unit: $unit_file"
            return 1
        fi
        
        # 쉘 조각 검사 (set -Eeuo, SRC=, DST= 등)
        if grep -qE 'set -Eeuo|SRC=|DST=|^if\s+! cmp' "$unit_file"; then
            echo "❌ [FAIL] Shell fragments detected in unit file: $unit_file"
            echo "   Remove shell fragments from [Service] section"
            return 1
        fi
    fi
    return 0
}

# coldsync 관련 유닛 파일 검증
USER_UNIT_DIR="$HOME/.config/systemd/user"
if [ -d "$USER_UNIT_DIR" ]; then
    ERRORS=0
    
    if [ -f "$USER_UNIT_DIR/coldsync-install.service" ]; then
        verify_systemd_unit "$USER_UNIT_DIR/coldsync-install.service" || ERRORS=$((ERRORS + 1))
    fi
    
    if [ -f "$USER_UNIT_DIR/coldsync-install.path" ]; then
        verify_systemd_unit "$USER_UNIT_DIR/coldsync-install.path" || ERRORS=$((ERRORS + 1))
    fi
    
    if [ "$ERRORS" -gt 0 ]; then
        echo ""
        echo "💡 Fix: bash scripts/evolution/fix_service_unit_final.sh"
        exit 1
    fi
fi

exit 0
SH

chmod +x "$PRE_COMMIT_HOOK"
echo "✅ pre-commit hook 생성 완료"
echo ""

# Git hooks 경로 설정
echo "3. Git hooks 경로 설정:"
if git config core.hooksPath >/dev/null 2>&1; then
    CURRENT_HOOKS=$(git config core.hooksPath)
    if [ "$CURRENT_HOOKS" != ".githooks" ]; then
        echo "⚠️  기존 hooks 경로: $CURRENT_HOOKS"
        echo "   git config core.hooksPath .githooks"
    fi
else
    git config core.hooksPath .githooks
    echo "✅ Git hooks 경로 설정 완료"
fi
echo ""

# 기존 pre-commit hook 병합 (있는 경우)
echo "4. 기존 pre-commit hook 확인:"
if [ -f ".githooks/pre-commit" ] && [ ! -f "$PRE_COMMIT_HOOK" ]; then
    # 기존 hook에 추가
    cat >> ".githooks/pre-commit" <<'APPEND'

# systemd 유닛 검증 (coldsync)
if [ -f ".githooks/pre-commit-systemd-verify" ]; then
    bash .githooks/pre-commit-systemd-verify || exit 1
fi
APPEND
    echo "✅ 기존 hook에 추가 완료"
else
    echo "✅ 새 hook 생성 완료"
fi
echo ""

# 테스트 실행
echo "5. hook 테스트 실행:"
if bash "$PRE_COMMIT_HOOK" 2>&1; then
    echo "✅ Hook 테스트 통과"
else
    echo "⚠️  Hook 테스트 실패 (경고 무시 가능)"
fi
echo ""

echo "=== pre-commit hook 설정 완료 ==="
echo ""
echo "다음 단계:"
echo "  git add .githooks/pre-commit-systemd-verify"
echo "  git commit -m 'ops: Add systemd unit verification pre-commit hook'"

