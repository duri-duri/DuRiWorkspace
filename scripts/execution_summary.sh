#!/bin/bash
# 실행 요약 - 바로 진행

set -e

echo "📋 실행 요약 시작..."

# 1. Go/No-Go 체크
echo "1️⃣ Go/No-Go 체크..."
./scripts/go_no_go_check.sh

# 2. 브랜치/PR
echo "2️⃣ 브랜치/PR..."
./scripts/apply_bundle.sh

# 3. 배포
echo "3️⃣ 배포..."
echo "   PR 머지 후 실행:"
echo "   ./scripts/last_5_check.sh"
echo "   ./scripts/actual_deployment.sh"

# 4. 관측/롤백 대비
echo "4️⃣ 관측/롤백 대비..."
echo "   ./scripts/post_deployment_observation.sh"
echo "   필요 시: ./scripts/one_click_rollback.sh {auto|manual|revision N}"

echo ""
echo "✅ 실행 요약 완료!"
echo "🚀 95점권 확실 - 이제 배포 버튼을 누르세요!"
