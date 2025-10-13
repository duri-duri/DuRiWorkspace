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

# 네트워크 정리 (강제 해제 포함)
echo "4. 네트워크 정리..."
# 네트워크에 남은 컨테이너 강제 분리 후 제거
NET=duriworkspace_default
if docker network ls | grep -q "$NET"; then
  echo "   네트워크 $NET 강제 해제..."
  docker network inspect "$NET" --format '{{range $id, $c := .Containers}}{{$id}}{{"\n"}}{{end}}' 2>/dev/null | \
    xargs -r -I{} docker network disconnect -f "$NET" {} 2>/dev/null || true
  docker network rm "$NET" 2>/dev/null || true
fi
docker network prune -f || true

# 볼륨 정리 (선택사항)
echo "5. 볼륨 정리 (선택사항)..."
docker volume prune -f || true

echo "✅ 도커 정리 완료"
