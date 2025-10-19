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

# --- Prometheus targets gate (타이밍 보정) ----------------------------------------------
PROM_URL="${PROM_URL:-http://localhost:9090}"
# 기대 타깃 (현재 설정에 맞게 업데이트)
EXPECTED_TARGETS=(prometheus node redis postgres cadvisor blackbox dori-dora-exporter)

# --- 유니크 처리
mapfile -t _uniq_targets < <(printf "%s\n" "${EXPECTED_TARGETS[@]}" | awk '!(a[$0]++)')

echo "--- Prometheus targets ---"
down=0; missing=0

# Prometheus 타겟 준비 대기 (최대 2분)
echo "• Waiting for Prometheus targets to be ready..."
for i in {1..30}; do
  if command -v jq >/dev/null 2>&1; then
    up_count=$(curl -fsS "$PROM_URL/api/v1/targets?state=any" 2>/dev/null | jq '[.data.activeTargets[] | select(.health=="up")] | length' 2>/dev/null || echo "0")
  else
    up_count=$(curl -fsS "$PROM_URL/api/v1/targets?state=any" 2>/dev/null | grep -o '"health":"up"' | wc -l || echo "0")
  fi
  
  if [ "$up_count" -ge "${#_uniq_targets[@]}" ]; then
    echo "✓ Prometheus targets ready: $up_count/${#_uniq_targets[@]}"
    break
  fi
  
  if [ "$i" -eq 30 ]; then
    echo "⚠️ Prometheus targets not fully ready after 2 minutes ($up_count/${#_uniq_targets[@]})"
  else
    echo "• Waiting... ($up_count/${#_uniq_targets[@]} ready)"
    sleep 4
  fi
done

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
