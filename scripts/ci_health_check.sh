#!/usr/bin/env bash
set -euo pipefail

echo "🚀 CI 헬스 체크 시작..."

# Docker Compose 서비스 시작
docker compose up -d duri_control duri_brain

# 서비스 시작 대기
sleep 15

# 스모크 테스트 실행
bash ./scripts/smoke_health_metrics.sh

echo "✅ CI 헬스 체크 완료!"
