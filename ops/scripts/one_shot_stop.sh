#!/usr/bin/env bash
set -Eeuo pipefail

ENV_FILE="${ENV_FILE:-$HOME/DuRiWorkspace/ops/.ops.env}"
[ -f "$ENV_FILE" ] && . "$ENV_FILE"

PROJECT_DIR="${PROJECT_DIR:-$HOME/DuRiWorkspace}"
COMPOSE_BASE="${COMPOSE_BASE:-docker-compose.yml}"
COMPOSE_HEALTH="${COMPOSE_HEALTH:-compose.health.overlay.yml}"
DOCKER_SOCK="${DOCKER_SOCK:-/var/run/docker.sock}"
PROM_MODE="${PROM_MODE:-standalone}"
PROM_NAME="${PROM_NAME:-prometheus}"

LOG_DIR="$PROJECT_DIR/var/logs"; mkdir -p "$LOG_DIR"
log(){ echo "[$(date '+%F %T')] $*"; }
cd "$PROJECT_DIR"

# 0) Docker 데몬 확인
if [ ! -S "$DOCKER_SOCK" ] || ! pgrep -x dockerd >/dev/null 2>&1; then
  log "dockerd not running → skip"
  exit 0
fi

# 1) Prometheus 컨테이너 정리 (standalone 모드)
if [[ "$PROM_MODE" == "standalone" ]]; then
  if docker ps -a --format '{{.Names}}' | grep -qx "$PROM_NAME"; then
    log "stop standalone prometheus"
    docker stop "$PROM_NAME" >/dev/null || true
    docker rm "$PROM_NAME" >/dev/null || true
  fi
fi

# 2) Compose down (+health overlay)
log "compose down"
docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" down

# 3) Orphan 컨테이너 정리
log "cleanup orphan containers"
docker container prune -f >/dev/null || true

# 4) 네트워크 정리
log "cleanup networks"
docker network prune -f >/dev/null || true

# 5) Summary
echo "=== Docker System Stopped ==="
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | head -10

log "Docker system stopped successfully"
exit 0


