#!/usr/bin/env bash
# 도커 네트워크 잔류 방지 스크립트
set -euo pipefail

echo "🧹 도커 네트워크 잔류 방지"

# Compose 서비스 종료 (orphans 포함)
echo "1. Compose 서비스 종료..."
docker compose down --remove-orphans || true

# 실행 중인 컨테이너 모두 정지
echo "2. 실행 중인 컨테이너 정지..."
docker ps -aq | xargs -r docker stop || true

# 모든 컨테이너 제거
echo "3. 모든 컨테이너 제거..."
docker ps -aq | xargs -r docker rm -f || true

# 네트워크 정리
echo "4. 네트워크 정리..."
docker network prune -f || true

# 볼륨 정리 (선택사항)
echo "5. 볼륨 정리 (선택사항)..."
docker volume prune -f || true

echo "✅ 도커 정리 완료"
