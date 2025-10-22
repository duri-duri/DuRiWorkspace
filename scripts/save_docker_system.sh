#!/usr/bin/env bash
set -Eeuo pipefail

# 스크립트 기준 repo 루트로 이동
cd "$(dirname "$0")/.."

echo "=== 💾 도커 시스템 저장 시작 ==="

BACKUP_DIR="backups"
VOL_DIR="$BACKUP_DIR/volumes"
CFG_DIR="$BACKUP_DIR/configs"
STAMP="$(date +%F_%H%M%S)"

mkdir -p "$VOL_DIR" "$CFG_DIR"

# 1) 상태/설정 백업
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" \
  > "$BACKUP_DIR/docker_system_status_${STAMP}.txt"

cp -f docker-compose*.yml "$CFG_DIR/" 2>/dev/null || true
cp -f .env*              "$CFG_DIR/" 2>/dev/null || true
cp -f prometheus.yml     "$CFG_DIR/" 2>/dev/null || true
cp -rf ops/observability "$CFG_DIR/" 2>/dev/null || true

# 2) 볼륨 아카이브
# 주의: 빈 볼륨도 tar는 생성(재현성 ↑)
while read -r volume; do
  [ -z "$volume" ] && continue
  echo "백업 중: $volume"
  docker run --rm -v "$volume":/data -v "$PWD/$VOL_DIR":/backup alpine \
    sh -c "cd /data && tar -czf /backup/${volume}_${STAMP}.tar.gz . || tar -czf /backup/${volume}_${STAMP}.tar.gz --files-from /dev/null"
done < <(docker volume ls --format "{{.Name}}" | grep -E "^(duriworkspace|duri_core)")

# 3) 무결성 목록
( cd "$VOL_DIR" && ls *.tar.gz >/dev/null 2>&1 && sha256sum *.tar.gz > "../SHA256SUMS_${STAMP}.txt" ) || true

echo "=== ✅ 백업 완료: $BACKUP_DIR ==="
