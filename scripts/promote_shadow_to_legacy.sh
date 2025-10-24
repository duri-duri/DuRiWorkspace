#!/usr/bin/env bash
# SSH → Legacy 프로모션 스크립트 (듀얼 트랙용)
# 사용법: REQUIRE_TESTS=1 DRY_RUN=1 bash scripts/promote_shadow_to_legacy.sh duri_core

set -euo pipefail

REPO_NAME="${1:-duri_core}"   # duri_core | duri_brain | duri_evolution | duri_control
SRC_DIR="${REPO_NAME}_ssh"
DST_DIR="${REPO_NAME}_legacy"
MAIN_BRANCH="main"

REQUIRE_TESTS=${REQUIRE_TESTS:-1}
REQUIRE_LINT=${REQUIRE_LINT:-0}
DRY_RUN=${DRY_RUN:-0}

timestamp="$(date +%Y%m%d-%H%M%S)"
tag="shadow-${timestamp}"
pr_branch="pr/${tag}-${REPO_NAME}"

[[ -d "$SRC_DIR/.git" ]] || { echo "missing $SRC_DIR"; exit 1; }
[[ -d "$DST_DIR/.git" ]] || { echo "missing $DST_DIR"; exit 1; }

# (선택) shadow 브랜치명 정책 가드
git -C "$SRC_DIR" rev-parse --abbrev-ref HEAD >/dev/null

if [[ "$REQUIRE_TESTS" -eq 1 ]]; then
  echo "[gate] pytest"; pytest -q || { echo "tests failed"; exit 1; }
fi
if [[ "$REQUIRE_LINT" -eq 1 ]]; then
  echo "[gate] ruff"; ruff .    || { echo "lint failed";  exit 1; }
fi

git -C "$SRC_DIR" fetch --tags
git -C "$SRC_DIR" tag -f "$tag"
[[ "$DRY_RUN" -eq 0 ]] && git -C "$SRC_DIR" push origin "refs/tags/$tag" -f

git -C "$DST_DIR" fetch origin "$MAIN_BRANCH" --tags
git -C "$DST_DIR" switch -c "$pr_branch" "origin/$MAIN_BRANCH"

# 변경 동기화 (대량 삭제 보호 위해 첫 운용은 --dry-run 권장)
rsync -a --delete --exclude ".git" "$SRC_DIR"/ "$DST_DIR"/

git -C "$DST_DIR" add -A
if git -C "$DST_DIR" diff --cached --quiet; then
  echo "no change to promote"; exit 0
fi

git -C "$DST_DIR" commit -m "promo(${REPO_NAME}): ${tag} → legacy"

if [[ "$DRY_RUN" -eq 0 ]]; then
  git -C "$DST_DIR" push -u origin "$pr_branch"
  gh pr create -R "duri-duri/${REPO_NAME}" -H "$pr_branch" -B "$MAIN_BRANCH" \
     -t "Promotion: ${tag}" \
     -b "Auto promotion from shadow (SSH) to legacy (HTTPS)."
  gh pr merge --auto --squash
fi

echo "✓ Promotion prepared for ${REPO_NAME} (${tag})"
