#!/usr/bin/env bash
set -Eeuo pipefail
ENV_FILE="${ENV_FILE:-$HOME/DuRiWorkspace/ops/.ops.env}"
[ -f "$ENV_FILE" ] && . "$ENV_FILE"

PROJECT_DIR="${PROJECT_DIR:-$HOME/DuRiWorkspace}"
COMPOSE_BASE="${COMPOSE_BASE:-docker-compose.yml}"
COMPOSE_HEALTH="${COMPOSE_HEALTH:-compose.health.overlay.yml}"
PROM_MODE="${PROM_MODE:-standalone}"
PROM_NAME="${PROM_NAME:-prometheus}"

cd "$PROJECT_DIR"

echo "=== Running (compose) ==="
docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" ps || true

case "${1:-}" in
  --down)
    echo "--- compose down (remove orphans + volumes + network) ---"
    docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" down --remove-orphans -v
    ;;
  *)
    echo "--- stop compose project ---"
    ids=$(docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" ps -q | tr '\n' ' ')
    [[ -n "$ids" ]] && docker stop $ids || echo "no compose containers"
    ;;
esac

if [[ "$PROM_MODE" == "standalone" ]] && docker ps -a --format '{{.Names}}' | grep -qx "$PROM_NAME"; then
  echo "--- stop prometheus (standalone) ---"
  docker stop "$PROM_NAME" >/dev/null || true
fi

echo "=== Done ==="