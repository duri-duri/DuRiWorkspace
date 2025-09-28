#!/usr/bin/env bash
set -Eeuo pipefail
ENV_FILE="${ENV_FILE:-$HOME/DuRiWorkspace/ops/.ops.env}"
[ -f "$ENV_FILE" ] && . "$ENV_FILE"

PROJECT_DIR="${PROJECT_DIR:-$HOME/DuRiWorkspace}"
COMPOSE_BASE="${COMPOSE_BASE:-docker-compose.yml}"
COMPOSE_HEALTH="${COMPOSE_HEALTH:-compose.health.overlay.yml}"
PROM_MODE="${PROM_MODE:-standalone}"
PROM_NAME="${PROM_NAME:-prometheus}"
DOCKER_SOCK="${DOCKER_SOCK:-/var/run/docker.sock}"

cd "$PROJECT_DIR"
echo "=== Docker Container Health Check ==="
echo "Timestamp: $(date -Is)"

# 데몬 준비 대기(최대 30s)
for _ in {1..30}; do
  docker version >/dev/null 2>&1 && break
  echo "• Waiting for Docker daemon…"
  sleep 1
done
docker version >/dev/null 2>&1 || { echo "⛔ Docker daemon not ready"; exit 2; }

echo "* Container Status:"
docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" ps --format "table {{.Name}}\t{{.State}}\t{{.Publishers}}" || true

bad=0
while read -r id; do
  [[ -z "$id" ]] && continue
  s=$(docker inspect "$id" --format '{{.State.Status}}')
  h=$(docker inspect "$id" --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}no-health{{end}}')
  if [[ "$s" != "running" || "$h" == "unhealthy" ]]; then
    n=$(docker inspect "$id" --format '{{.Name}}' | sed 's#^/##')
    echo "!! $n => status=$s health=$h"
    bad=1
  fi
done < <(docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" ps -q)

# Prometheus 상태(있으면)
if [[ "$PROM_MODE" == "standalone" ]] && docker ps -a --format '{{.Names}}' | grep -qx "$PROM_NAME"; then
  echo "* Prometheus:"
  pst=$(docker inspect "$PROM_NAME" --format '{{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{else}}no-health{{end}}')
  echo "  - $PROM_NAME => $pst"
  [[ "$pst" =~ unhealthy|Exited|dead|paused ]] && bad=1
fi

# 옵션: Prometheus API quick health
if docker ps --format '{{.Names}}' | grep -qx "$PROM_NAME"; then
  ready=$(curl -fsS "http://localhost:${PROM_PORT}/-/ready" >/dev/null && echo READY || echo NOT_READY)
  echo "* Prometheus READY: $ready"
fi

# --- Prometheus targets gate ----------------------------------------------
PROM_URL="${PROM_URL:-http://localhost:9090}"
# 기대 타깃 (원래 배열 유지)
EXPECTED_TARGETS=(redis postgres node cadvisor blackbox self)

# --- 유니크 처리
mapfile -t _uniq_targets < <(printf "%s\n" "${EXPECTED_TARGETS[@]}" | awk '!(a[$0]++)')

echo "--- Prometheus targets ---"
down=0; missing=0

if command -v jq >/dev/null 2>&1; then
  json="$(curl -fsS "$PROM_URL/api/v1/targets?state=active" || true)"
  for job in "${_uniq_targets[@]}"; do
    has=$(echo "$json" | jq -r --arg j "$job" '.data.activeTargets[] | select(.labels.job==$j) | .health' | wc -l)
    if [ "$has" -eq 0 ]; then
      echo "✗ target:$job -> MISSING"; missing=1
    elif echo "$json" | jq -e --arg j "$job" '.data.activeTargets[] | select(.labels.job==$j and .health=="up")' >/dev/null; then
      echo "✓ target:$job -> UP"
    else
      echo "✗ target:$job -> DOWN"; down=1
    fi
  done
else
  json="$(curl -fsS "$PROM_URL/api/v1/targets?state=active" || true)"
  for job in "${_uniq_targets[@]}"; do
    if ! echo "$json" | grep -q "\"job\":\"$job\""; then
      echo "✗ target:$job -> MISSING"; missing=1
    elif echo "$json" | grep -q "\"job\":\"$job\".*\"health\":\"up\""; then
      echo "✓ target:$job -> UP"
    else
      echo "✗ target:$job -> DOWN"; down=1
    fi
  done
fi

if [ "$down" -ne 0 ] || [ "$missing" -ne 0 ]; then
  echo "NG: Prometheus targets failing (down=$down missing=$missing)"
  exit 2
fi

(( bad==0 )) && { echo "=== All Health checks PASSED ==="; exit 0; } || { echo "=== Health check FAILED ==="; exit 1; }