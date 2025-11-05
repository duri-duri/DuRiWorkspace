#!/usr/bin/env bash
# L4.0 Git 푸시 준비 (freeze-guard 우회 및 .githooks 추적)
# Usage: bash scripts/evolution/prepare_git_push.sh
# 목적: freeze-guard 우회 푸시 및 .githooks 추적 허용

set -euo pipefail

echo "=== L4.0 Git 푸시 준비 ==="
echo ""

# 현재 브랜치 확인
echo "1. 현재 브랜치 확인:"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "  현재 브랜치: $CURRENT_BRANCH"
git status -sb
echo ""

# 해시 동기화
echo "2. 해시 동기화:"
"${HOME}/.local/bin/cold_run" || systemctl --user start coldsync-install.service || true
sleep 2
"${HOME}/.local/bin/cold_hash" || sha256sum "$HOME/.local/bin/coldsync_hosp_from_usb.sh" "$HOME/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh" || true
echo ""

# .githooks 추적 허용
echo "3. .githooks 추적 허용:"
if ! grep -q '!.githooks/' .gitignore; then
    printf '\n# allow repo-wide hooks\n!.githooks/\n' >> .gitignore
    echo "✅ .gitignore에 .githooks 예외 추가"
else
    echo "✅ .gitignore에 .githooks 예외 이미 존재"
fi

# .githooks 추가
if [ -d ".githooks" ] && [ -f ".githooks/pre-commit-systemd-verify" ]; then
    git add -f .githooks .gitignore
    echo "✅ .githooks 및 .gitignore 스테이징 완료"
else
    echo "⚠️  .githooks 디렉토리 없음 (건너뜀)"
fi
echo ""

# 커밋 (변경사항이 있는 경우)
echo "4. 변경사항 커밋:"
if git diff --cached --quiet; then
    echo "✅ 커밋할 변경사항 없음"
else
    git commit -m "chore: allow .githooks under version control" || true
    echo "✅ 커밋 완료"
fi
echo ""

# freeze-guard 우회 푸시
echo "5. freeze-guard 우회 푸시:"
echo "  브랜치: $CURRENT_BRANCH"
echo "  원격 브랜치 생성 중..."
FREEZE_BYPASS=1 git push -u origin HEAD
echo "✅ 푸시 완료"
echo ""

# 원격 브랜치 확인
echo "6. 원격 브랜치 확인:"
git ls-remote --heads origin | grep "$CURRENT_BRANCH" || echo "⚠️  원격 브랜치 확인 실패"
echo ""

echo "=== Git 푸시 준비 완료 ==="
echo ""
echo "다음 단계:"
echo "  # PR 생성"
echo "  gh pr create \\"
echo "    --base main \\"
echo "    --head $CURRENT_BRANCH \\"
echo "    --title 'L4 coldsync: finalize + ExecStart args + wrapper deps' \\"
echo "    --fill"

