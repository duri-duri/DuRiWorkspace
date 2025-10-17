#!/usr/bin/env bash
set -euo pipefail

echo "=== 📝 릴리스 노트 자동화 ==="

# 현재 이미지 라벨에서 정보 추출
VERSION=$(docker inspect duriworkspace-duri_control:latest | jq -r '.[0].Config.Labels."org.opencontainers.image.version"')
GIT_SHA=$(docker inspect duriworkspace-duri_control:latest | jq -r '.[0].Config.Labels."org.opencontainers.image.revision"')
BUILD_DATE=$(docker inspect duriworkspace-duri_control:latest | jq -r '.[0].Config.Labels."org.opencontainers.image.created"')

echo "## DuRi Release Notes" > CHANGELOG.md
echo "" >> CHANGELOG.md
echo "### Version: $VERSION" >> CHANGELOG.md
echo "- **Git SHA**: $GIT_SHA" >> CHANGELOG.md
echo "- **Build Date**: $BUILD_DATE" >> CHANGELOG.md
echo "- **Changes**: [GitHub Compare](https://github.com/your-repo/compare/previous-tag...$GIT_SHA)" >> CHANGELOG.md
echo "" >> CHANGELOG.md

echo "✅ CHANGELOG.md 생성 완료"
