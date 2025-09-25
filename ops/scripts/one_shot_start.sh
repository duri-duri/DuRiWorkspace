#!/usr/bin/env bash
set -Eeuo pipefail

ENV_FILE="${ENV_FILE:-$HOME/DuRiWorkspace/ops/.ops.env}"
[ -f "$ENV_FILE" ] && . "$ENV_FILE"

PROJECT_DIR="${PROJECT_DIR:-$HOME/DuRiWorkspace}"
COMPOSE_BASE="${COMPOSE_BASE:-docker-compose.yml}"
COMPOSE_HEALTH="${COMPOSE_HEALTH:-compose.health.overlay.yml}"
DOCKER_SOCK="${DOCKER_SOCK:-/var/run/docker.sock}"
WAIT_DOCKER_SECS="${WAIT_DOCKER_SECS:-25}"
HEALTH_TIMEOUT_SECS="${HEALTH_TIMEOUT_SECS:-150}"
PROM_MODE="${PROM_MODE:-standalone}"
PROM_NAME="${PROM_NAME:-prometheus}"
PROM_PORT="${PROM_PORT:-9090}"
PROM_CONFIG="${PROM_CONFIG:-$PROJECT_DIR/prometheus.yml}"
PROM_RULES="${PROM_RULES:-$PROJECT_DIR/prometheus_rules.yml}"

LOG_DIR="$PROJECT_DIR/var/logs"; mkdir -p "$LOG_DIR"
log(){ echo "[$(date '+%F %T')] $*"; }
cd "$PROJECT_DIR"

# 0) Docker 데몬 보증(모드별 처리)
if [[ "${DOCKER_DAEMON_MODE:-desktop}" == "native" ]]; then
  if [ ! -S "$DOCKER_SOCK" ] || ! pgrep -x dockerd >/dev/null 2>&1; then
    log "dockerd not running → start (native mode)"
    if command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null; then
      nohup sudo dockerd --host=unix://$DOCKER_SOCK >>"$LOG_DIR/dockerd.log" 2>&1 &
    else
      nohup dockerd --host=unix://$DOCKER_SOCK >>"$LOG_DIR/dockerd.log" 2>&1 &
    fi
  fi
else
  log "WSL/Desktop mode: won't start dockerd; waiting for Docker Desktop socket..."
fi

# 공통 대기(Desktop이면 단순 '응답 대기', Native면 '기동+대기')
for _ in $(seq 1 "$WAIT_DOCKER_SECS"); do docker version >/dev/null 2>&1 && break; sleep 1; done
docker version >/dev/null 2>&1 || { echo "⛔ Docker 데몬 미응답: Desktop 실행(또는 native 설정) 필요"; exit 2; }

# 1) Prometheus 모드 전환에 따른 이름 충돌 가드
if [[ "$PROM_MODE" == "compose" ]]; then
  if docker ps -a --format '{{.Names}}' | grep -qx "$PROM_NAME"; then
    log "remove standalone prometheus to avoid name conflict (compose uses same name)"
    docker rm -f "$PROM_NAME" >/dev/null || true
  fi
fi

# 2) Compose up (+health overlay)
log "compose up -d (+health overlay)"
docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" up -d

# 3) Prometheus (standalone only)
if [[ "$PROM_MODE" == "standalone" ]]; then
  if ! docker ps -a --format '{{.Names}}' | grep -qx "$PROM_NAME"; then
    log "run prometheus (standalone + /-/ready health)"
    docker run -d --name "$PROM_NAME" -p "$PROM_PORT:$PROM_PORT" \
      --health-cmd="wget -qO- http://localhost:$PROM_PORT/-/ready >/dev/null 2>&1 || exit 1" \
      --health-interval=15s --health-timeout=5s --health-retries=5 --health-start-period=45s \
      -v "$PROM_CONFIG":/etc/prometheus/prometheus.yml:ro \
      -v "$PROM_RULES":/etc/prometheus/rules/prometheus_rules.yml:ro \
      prom/prometheus >/dev/null
  else
    docker start "$PROM_NAME" >/dev/null || true
  fi
fi

# 4) Healthy 게이팅(모든 컨테이너 + prom(해당 시))
log "wait-until-healthy (≤ ${HEALTH_TIMEOUT_SECS}s)"
start=$(date +%s)
while :; do
  mapfile -t CIDS < <(docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" ps -q | sed '/^$/d')
  if [[ "$PROM_MODE" == "standalone" ]] && docker ps -a --format '{{.Names}}' | grep -qx "$PROM_NAME"; then
    CIDS+=("$(docker ps -aqf "name=^${PROM_NAME}$")")
  fi
  (( ${#CIDS[@]} > 0 )) || { echo "⛔ 컨테이너 없음"; exit 3; }

  bad=0
  for id in "${CIDS[@]}"; do
    s=$(docker inspect "$id" --format '{{.State.Status}}')
    h=$(docker inspect "$id" --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}no-health{{end}}')
    [[ "$s" != "running" ]] && { bad=1; break; }
    [[ "$h" == "unhealthy" ]] && { bad=1; break; }
    [[ "$h" != "no-health" && "$h" != "healthy" ]] && { bad=1; break; }
  done

  (( bad==0 )) && break
  (( $(date +%s) - start > HEALTH_TIMEOUT_SECS )) && { echo "⛔ health timeout"; break; }
  sleep 2
done

# 5) Summary & 반환코드
echo "=== Container Summary ==="
docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" ps --format "table {{.Name}}\t{{.State}}\t{{.Publishers}}"
[[ "$PROM_MODE" == "standalone" ]] && docker ps --filter "name=^${PROM_NAME}$" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || true

code=0
while read -r name state; do [[ "$state" =~ unhealthy|Exited|dead|paused ]] && code=4; done \
  < <(docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" ps --format "{{.Name}} {{.State}}")
if [[ "$PROM_MODE" == "standalone" ]] && docker ps -a --format '{{.Names}}' | grep -qx "$PROM_NAME"; then
  pst=$(docker inspect "$PROM_NAME" --format '{{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{else}}no-health{{end}}')
  [[ "$pst" =~ unhealthy|Exited|dead|paused ]] && code=4
fi
(( code!=0 )) && echo "⛔ some containers not healthy/running"
exit "$code"
