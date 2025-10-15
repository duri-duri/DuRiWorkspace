#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-v1.0.1}"
NAME="ops-lock-${VERSION}"

echo "🚀 Build ${NAME}…"

# 1) 사전검증(스모크)
bash scripts/smoke_health_metrics.sh

# 2) 패치/mbox 생성
git add -A
git commit -m "chore(ops): ${NAME} bundle" || echo "ℹ️ no changes to commit"
mkdir -p dist
git format-patch -1 HEAD --stdout > "dist/${NAME}.mbox"
git diff --binary --staged > "dist/${NAME}.patch"

# 3) tar.gz 번들
tar -czf "dist/${NAME}.tar.gz" \
  .pre-commit-config.yaml Makefile .github/workflows/ci.yml \
  alerting/rules.yml RUNBOOK.md \
  scripts/smoke_health_metrics.sh scripts/ci_health_check.sh scripts/rollback_now.sh

# 4) 체크섬
sha256sum "dist/${NAME}.tar.gz" "dist/${NAME}.mbox" "dist/${NAME}.patch" > "dist/${NAME}.sha256"

# 5) 태그(옵션)
git tag -f "${VERSION}-opslock" && git push -f --tags

echo "✅ Done:"
ls -lh dist/${NAME}.*
