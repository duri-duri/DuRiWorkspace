#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."

echo "=== 🔄 도커 시스템 복원 시작 ==="

CFG_DIR="backups/configs"
VOL_DIR="backups/volumes"

# 1) 설정 복원(있을 때만)
if [ -d "$CFG_DIR" ]; then
  cp -f "$CFG_DIR"/docker-compose*.yml . 2>/dev/null || true
  cp -f "$CFG_DIR"/.env*              . 2>/dev/null || true
  cp -f "$CFG_DIR"/prometheus.yml     . 2>/dev/null || true
  cp -rf "$CFG_DIR"/ops               . 2>/dev/null || true
fi

# 2) 볼륨 복원
if [ -d "$VOL_DIR" ]; then
  for tgz in "$VOL_DIR"/*.tar.gz; do
    [ ! -f "$tgz" ] && continue
    vol="$(basename "$tgz" | sed "s/_20.*$//")"
    echo "복원 중: $vol"
    docker volume create "$vol" >/dev/null 2>&1 || true
    docker run --rm -v "$vol":/data -v "$PWD":/host alpine \
      sh -c "cd /data && tar -xzf /host/$tgz || true"
  done
fi

# 3) 서비스 시작
docker compose -p duriworkspace up -d

# 4) 모니터링 스택 (파일 있을 때)
[ -f docker-compose.monitoring.yml ] && \
  docker compose -p duriworkspace -f docker-compose.yml -f docker-compose.monitoring.yml --profile monitoring up -d || true

# 5) 상태 확인
sleep 8
docker compose -p duriworkspace ps
echo "=== ✅ 복원 완료 ==="
