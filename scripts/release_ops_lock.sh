#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-v1.0.1}"                    # 예: v1.0.1a
BASE_REF="${2:-$(git describe --tags --abbrev=0 2>/dev/null || echo '')}"
NAME="ops-lock-${VERSION}"

echo "🚀 Build ${NAME} (base: ${BASE_REF:-<none>})…"

# 0) 사전 스모크
bash scripts/smoke_health_metrics.sh

# 1) 커밋(있으면) — 없으면 스킵
git add -A
git diff --cached --quiet || git commit -m "chore(ops): ${NAME} bundle"

# 2) 변경 범위 산출
if [[ -n "${BASE_REF}" ]]; then
  RANGE="${BASE_REF}..HEAD"
else
  # 태그가 전혀 없다면 최근 1커밋 범위
  RANGE="HEAD~1..HEAD"
fi

# 변경이 없으면 종료
if git diff --quiet ${RANGE}; then
  echo "ℹ️ 변경 사항 없음: ${RANGE}"
  exit 0
fi

mkdir -p dist

# 3) 산출물 생성
# 3-1) mbox (권장)
git format-patch ${RANGE} --stdout > "dist/${NAME}.mbox"

# 3-2) 직패치 (이진 안전)
git diff --binary ${RANGE} > "dist/${NAME}.patch"

# 3-3) tar.gz 번들
tar -czf "dist/${NAME}.tar.gz" \
  .pre-commit-config.yaml Makefile .github/workflows/ci.yml \
  alerting/rules.yml RUNBOOK.md \
  scripts/smoke_health_metrics.sh scripts/ci_health_check.sh scripts/rollback_now.sh

# 4) 체크섬
sha256sum "dist/${NAME}.tar.gz" "dist/${NAME}.mbox" "dist/${NAME}.patch" > "dist/${NAME}.sha256"

# 5) 태그(보호 기본) — 실수 방지 위해 강제 푸시 금지
TAG="${VERSION}-opslock"
if git rev-parse -q --verify "refs/tags/${TAG}" >/dev/null; then
  echo "ℹ️ 태그 ${TAG}는 이미 존재합니다. (강제 덮어쓰기 생략)"
else
  git tag -a "${TAG}" -m "Ops-Lock bundle ${VERSION}"
  git push origin "refs/tags/${TAG}"
fi

echo "✅ Done:"
ls -lh dist/${NAME}.*
