#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-v1.0.1}"                    # e.g. v1.0.1c
BASE_REF="${2:-$(git describe --tags --abbrev=0 2>/dev/null || echo '')}"
NAME="ops-lock-${VERSION}"
TAG="${VERSION}-opslock"
PUSH_TAG="${PUSH_TAG:-true}"

echo "🚀 Build ${NAME} (base: ${BASE_REF:-<none>})…"

# 0) 사전 스모크
bash scripts/smoke_health_metrics.sh

# 1) 커밋(있으면) — 없으면 스킵
git add -A
git commit -m "chore(ops): ${NAME} bundle" || echo "ℹ️ no changes to commit"

mkdir -p dist

# 2) 범위 계산 (태그가 있으면 태그..HEAD, 없으면 HEAD~1..HEAD, 초기 커밋은 show)
HEAD_COMMIT="$(git rev-parse HEAD)"
if [[ -n "${BASE_REF}" ]] && git rev-parse -q --verify "${BASE_REF}" >/dev/null; then
  DIFF_RANGE="${BASE_REF}..${HEAD_COMMIT}"
elif git rev-parse -q --verify HEAD~1 >/dev/null; then
  DIFF_RANGE="HEAD~1..HEAD"
else
  DIFF_RANGE=""  # 초기 커밋
fi

# 3) mbox (권장)
git format-patch -1 "${HEAD_COMMIT}" --stdout > "dist/${NAME}.mbox"

# 4) raw patch (git apply 용)
if [[ -n "${DIFF_RANGE}" ]]; then
  git diff --binary ${DIFF_RANGE} > "dist/${NAME}.patch"
else
  git show --binary -1 --format=email "${HEAD_COMMIT}" > "dist/${NAME}.patch"
fi

# 5) 재현 가능한 tar.gz (정렬/타임스탬프/소유자 고정)
export TZ=UTC
export LC_ALL=C
SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-$(git show -s --format=%ct ${HEAD_COMMIT})}"
tar --sort=name \
    --mtime="@${SOURCE_DATE_EPOCH}" \
    --owner=0 --group=0 --numeric-owner \
    -czf "dist/${NAME}.tar.gz" \
    .pre-commit-config.yaml Makefile .github/workflows/ci.yml \
    alerting/rules.yml RUNBOOK.md \
    scripts/smoke_health_metrics.sh scripts/ci_health_check.sh scripts/rollback_now.sh scripts/release_ops_lock.sh

# 6) 체크섬
sha256sum "dist/${NAME}.tar.gz" "dist/${NAME}.mbox" "dist/${NAME}.patch" > "dist/${NAME}.sha256"

# 7) 태그(기본 push, 끄려면 PUSH_TAG=false)
if git rev-parse -q --verify "refs/tags/${TAG}" >/dev/null; then
  echo "ℹ️ tag ${TAG} exists (skip create)"
else
  git tag -a "${TAG}" -m "Ops-Lock bundle ${VERSION}"
fi
[[ "${PUSH_TAG}" == "true" ]] && git push origin "refs/tags/${TAG}" || true

echo "✅ Done:" && ls -lh dist/${NAME}.*
