#!/bin/bash
set -euo pipefail

echo "🚨 수동 롤백 핫스위치 실행..."

# 현재 상태 백업
echo "📦 현재 상태 백업..."
docker compose ps > rollback_backup_$(date +%Y%m%d_%H%M%S).txt

# 서비스 중지
echo "🛑 서비스 중지..."
docker compose down

# 이전 안정 태그로 롤백 (예시)
echo "🔄 이전 안정 태그로 롤백..."
# git checkout v1.0.0-lock  # 실제 태그로 변경 필요

# 서비스 재시작
echo "🚀 서비스 재시작..."
docker compose up -d --build

# 스모크 테스트
echo "🧪 스모크 테스트..."
sleep 15
bash scripts/smoke_health_metrics.sh

echo "✅ 롤백 완료!"
