#!/usr/bin/env bash
set -Eeuo pipefail

ENV_FILE="${ENV_FILE:-$HOME/DuRiWorkspace/ops/.ops.env}"
[ -f "$ENV_FILE" ] && . "$ENV_FILE"

PROJECT_DIR="${PROJECT_DIR:-$HOME/DuRiWorkspace}"
COMPOSE_BASE="${COMPOSE_BASE:-docker-compose.yml}"
COMPOSE_HEALTH="${COMPOSE_HEALTH:-compose.health.overlay.yml}"
DOCKER_SOCK="${DOCKER_SOCK:-/var/run/docker.sock}"
WAIT_DOCKER_SECS="${WAIT_DOCKER_SECS:-180}"
HEALTH_TIMEOUT_SECS="${HEALTH_TIMEOUT_SECS:-150}"

DOCKER_DAEMON_MODE="${DOCKER_DAEMON_MODE:-auto}"
PROM_MODE="${PROM_MODE:-standalone}"
PROM_NAME="${PROM_NAME:-prometheus}"
PROM_PORT="${PROM_PORT:-9090}"
PROM_CONFIG="${PROM_CONFIG:-$PROJECT_DIR/prometheus.yml}"
PROM_RULES="${PROM_RULES:-$PROJECT_DIR/prometheus_rules.yml}"

LOG_DIR="$PROJECT_DIR/var/logs"; mkdir -p "$LOG_DIR"
log(){ echo "[$(date '+%F %T')] $*"; }
cd "$PROJECT_DIR"

have_sock(){ [ -S "$DOCKER_SOCK" ] && docker version >/dev/null 2>&1; }

start_desktop(){
  # WSL에서 Windows Docker Desktop 기동
  log "try Docker Desktop…"
  ( command -v powershell.exe >/dev/null 2>&1 && \
    powershell.exe -NoProfile -Command "Start-Process -WindowStyle Hidden -FilePath '$env:ProgramFiles\Docker\Docker\Docker Desktop.exe'" \
  ) >/dev/null 2>&1 || true

  # 소켓/daemon 대기
  for _ in $(seq 1 "$WAIT_DOCKER_SECS"); do
    have_sock && return 0
    sleep 1
  done
  return 1
}

start_native(){
  log "try native dockerd…"
  nohup dockerd --host=unix://$DOCKER_SOCK >>"$LOG_DIR/dockerd.log" 2>&1 &

  for _ in $(seq 1 25); do
    have_sock && return 0
    sleep 1
  done
  return 1
}

start_sudo_native(){
  log "try sudo dockerd…"
  if command -v sudo >/dev/null 2>&1; then
    sudo -n true >/dev/null 2>&1 || true   # 캐시 없으면도 시도
    nohup sudo dockerd --host=unix://$DOCKER_SOCK >>"$LOG_DIR/dockerd.log" 2>&1 &
    for _ in $(seq 1 25); do
      have_sock && return 0
      sleep 1
    done
  fi
  return 1
}

ensure_daemon(){
  have_sock && { log "docker daemon ready"; return; }

  case "$DOCKER_DAEMON_MODE" in
    desktop)
      start_desktop || { echo "⛔ Desktop start failed"; exit 2; }
      ;;
    native)
      start_native || { echo "⛔ native dockerd start failed"; exit 2; }
      ;;
    sudo-native)
      start_sudo_native || { echo "⛔ sudo dockerd start failed"; exit 2; }
      ;;
    auto|*)
      # Desktop → sudo-native → native 순으로 시도
      start_desktop || start_sudo_native || start_native || {
        echo "⛔ failed to start any docker daemon (Desktop/native)"; exit 2;
      }
      ;;
  esac

  have_sock || { echo "⛔ docker still not ready"; exit 2; }
}

# 0) 데몬 보증
ensure_daemon

# 1) 모드 충돌 가드(PROM_MODE=compose면 standalone 잔존 제거)
if [[ "${PROM_MODE}" == "compose" ]]; then
  if docker ps -a --format '{{.Names}}' | grep -qx "$PROM_NAME"; then
    log "remove standalone $PROM_NAME to avoid name conflict"
    docker rm -f "$PROM_NAME" >/dev/null 2>&1 || true
  fi
fi

# 2) Compose up (+ health overlay)
log "compose up -d (+health overlay)"
docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" up -d

# 3) Prometheus (standalone 모드면 별도 보증)
if [[ "$PROM_MODE" == "standalone" ]]; then
  if ! docker ps -a --format '{{.Names}}' | grep -qx "$PROM_NAME"; then
    log "run $PROM_NAME (standalone + /-/ready)"
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

# 4) Healthy 게이팅
log "wait-until-healthy (≤ ${HEALTH_TIMEOUT_SECS}s)"
start_ts=$(date +%s)
while :; do
  mapfile -t CIDS < <(docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" ps -q | sed '/^$/d')
  [[ "$PROM_MODE" == "standalone" ]] && CIDS+=("$(docker ps -aqf "name=^${PROM_NAME}$")")
  (( ${#CIDS[@]} )) || { echo "⛔ no containers"; exit 3; }

  bad=0
  for id in "${CIDS[@]}"; do
    [[ -z "$id" ]] && continue
    st=$(docker inspect "$id" --format '{{.State.Status}}')
    hs=$(docker inspect "$id" --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}no-health{{end}}')
    [[ "$st" != "running" ]] && { bad=1; break; }
    [[ "$hs" == "unhealthy" ]] && { bad=1; break; }
    [[ "$hs" != "no-health" && "$hs" != "healthy" ]] && { bad=1; break; }
  done

  (( bad==0 )) && break
  (( $(date +%s) - start_ts > HEALTH_TIMEOUT_SECS )) && { echo "⛔ health timeout"; break; }
  sleep 2
done

# 5) 요약 & 종료코드
echo "=== Container Summary ==="
docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" ps --format "table {{.Name}}\t{{.State}}\t{{.Publishers}}"
[[ "$PROM_MODE" == "standalone" ]] && docker ps --filter "name=^${PROM_NAME}$" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || true

rc=0
while read -r name state; do [[ "$state" =~ unhealthy|Exited|dead|paused ]] && rc=4; done \
  < <(docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" ps --format "{{.Name}} {{.State}}")
if [[ "$PROM_MODE" == "standalone" ]] && docker ps -a --format '{{.Names}}' | grep -qx "$PROM_NAME"; then
  pst=$(docker inspect "$PROM_NAME" --format '{{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{else}}no-health{{end}}')
  [[ "$pst" =~ unhealthy|Exited|dead|paused ]] && rc=4
fi
(( rc!=0 )) && echo "⛔ some containers not healthy/running"
exit "$rc"