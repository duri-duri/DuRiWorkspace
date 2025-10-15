#!/bin/bash
# 적용 순서 - 복붙

set -e

echo "📋 적용 순서 시작..."

# Git 브랜치 생성 및 파일 추가
echo "1️⃣ Git 브랜치 생성 및 파일 추가..."
git checkout -b harden/ops-6pack

# 파일들 추가
git add -A

# 커밋
git commit -m "feat(ops): harden bundle (digest pin, token rotation, NP, schema, gate, cron alerts)"

# 푸시
git push -u origin harden/ops-6pack

echo "✅ Git 브랜치 생성 및 푸시 완료"
echo "📋 다음 단계:"
echo "   1. PR 생성"
echo "   2. CI 통과 확인"
echo "   3. PR 머지"
echo ""
echo "PR 머지 후 실행할 명령어:"
echo "   # 60초 프리플라이트"
echo "   ./scripts/last_5_check.sh"
echo ""
echo "   # 실제 집행"
echo "   ./scripts/actual_deployment.sh"
echo ""
echo "   # 포스트 배포 5줄 관측"
echo "   ./scripts/post_deployment_observation.sh"
echo ""
echo "🚀 적용 순서 완료!"
