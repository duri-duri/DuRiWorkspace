#!/usr/bin/env bash
set -Eeuo pipefail
trap 'echo "[ERROR] line:$LINENO"; exit 1' ERR

ENV_FILE="${ENV_FILE:-$HOME/DuRiWorkspace/ops/.ops.env}"
[ -f "$ENV_FILE" ] && . "$ENV_FILE"

PROJECT_DIR="${PROJECT_DIR:-$HOME/DuRiWorkspace}"
COMPOSE_BASE="${COMPOSE_BASE:-docker-compose.yml}"
COMPOSE_HEALTH="${COMPOSE_HEALTH:-compose.health.overlay.yml}"
DOCKER_SOCK="${DOCKER_SOCK:-/var/run/docker.sock}"
WAIT_DOCKER_SECS="${WAIT_DOCKER_SECS:-180}"
HEALTH_TIMEOUT_SECS="${HEALTH_TIMEOUT_SECS:-180}"

DOCKER_DAEMON_MODE="${DOCKER_DAEMON_MODE:-auto}"
PROM_MODE="${PROM_MODE:-standalone}"
PROM_NAME="${PROM_NAME:-prometheus}"
PROM_PORT="${PROM_PORT:-9090}"
PROM_CONFIG="${PROM_CONFIG:-$PROJECT_DIR/prometheus.yml}"
PROM_RULES="${PROM_RULES:-$PROJECT_DIR/rules.d}"

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

# 0) Preflight 체크
log "preflight checks..."
command -v docker >/dev/null || { echo "❌ docker not found"; exit 3; }
command -v docker compose >/dev/null || { echo "❌ docker compose not found"; exit 3; }

# 0.0) 로그 소음 줄이기 (마무리 하드닝)
export COMPOSE_PROGRESS=quiet

# 0.1) 베이스 이미지 사전 빌드 (logging 충돌 방지)
if ! docker image inspect duri-base:latest >/dev/null 2>&1; then
  log "building base image (logging conflict prevention)..."
  docker build -f docker/Dockerfile.base -t duri-base:latest .
fi

# 0.2) 데몬 보증
ensure_daemon

# 1) 모드 충돌 가드(PROM_MODE=compose면 standalone 잔존 제거)
if [[ "${PROM_MODE}" == "compose" ]]; then
  if docker ps -a --format '{{.Names}}' | grep -qx "$PROM_NAME"; then
    log "remove standalone $PROM_NAME to avoid name conflict"
    docker rm -f "$PROM_NAME" >/dev/null 2>&1 || true
  fi
fi

# 2) Prometheus 볼륨 권한 설정 (권한 문제 방지)
PROM_DATA_DIR="$PROJECT_DIR/data/prometheus"
if [[ -d "$PROM_DATA_DIR" ]]; then
  log "fix prometheus data directory permissions"
  sudo chown -R 65534:65534 "$PROM_DATA_DIR" 2>/dev/null || {
    log "warning: failed to fix prometheus permissions (may need sudo)"
  }
fi

# 2.1) Grafana 권한 설정 (권한 문제 방지)
GRAFANA_DATA_DIR="$PROJECT_DIR/grafana/data"
if [[ -d "$GRAFANA_DATA_DIR" ]]; then
  log "fix grafana data directory permissions"
  # 컨테이너 기반 권한 수정 (sudo 불필요)
  docker run --rm -v "$GRAFANA_DATA_DIR:/var/lib/grafana" alpine \
    sh -c 'chown -R 472:472 /var/lib/grafana && find /var/lib/grafana -type d -exec chmod 755 {} \; && find /var/lib/grafana -type f -exec chmod 644 {} \;' 2>/dev/null || {
    log "warning: failed to fix grafana permissions"
  }
fi

# 3) 인프라 먼저 기동 (의존성 순서 보장)
log "starting infrastructure first..."
docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" up -d duri-postgres duri-redis

# 3.1) 인프라 헬스 대기
log "waiting for infrastructure health..."
timeout 90s bash -c '
  until docker compose ps | grep -E "(duri-postgres|duri-redis).*healthy" -q; do 
    echo "  waiting for postgres/redis..."; sleep 2; 
  done
' || { echo "❌ infrastructure health timeout"; exit 4; }

# 3.2) 서비스 빌드 & 기동 (logging 충돌 방지)
log "building services (dependency-first)..."
docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" build duri_core duri_evolution
docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" up -d duri_core duri_evolution

# 3.3) 나머지 서비스들
log "starting remaining services..."
docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" up -d --remove-orphans

# 4) Prometheus (standalone 모드면 별도 보증)
if [[ "$PROM_MODE" == "standalone" ]]; then
  if ! docker ps -a --format '{{.Names}}' | grep -qx "$PROM_NAME"; then
    log "run $PROM_NAME (standalone + /-/ready)"
    docker run -d --name "$PROM_NAME" -p "$PROM_PORT:$PROM_PORT" \
      --health-cmd="wget -qO- http://localhost:$PROM_PORT/-/ready >/dev/null 2>&1 || exit 1" \
      --health-interval=15s --health-timeout=5s --health-retries=5 --health-start-period=45s \
      -v "$PROM_CONFIG":/etc/prometheus/prometheus.yml:ro \
      -v "$PROM_RULES":/etc/prometheus/rules.d:ro \
      prom/prometheus >/dev/null
  else
    docker start "$PROM_NAME" >/dev/null || true
  fi
fi

# 5) Healthy 게이팅
log "wait-until-healthy (≤ ${HEALTH_TIMEOUT_SECS}s)"
start_ts=$(date +%s)
while :; do
  mapfile -t CIDS < <(docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" ps -q | sed '/^$/d')
  [[ "$PROM_MODE" == "standalone" ]] && CIDS+=("$(docker ps -aqf "name=^${PROM_NAME}$")")
  (( ${#CIDS[@]} )) || { echo "⛔ no containers"; exit 3; }

  bad=0
  for id in "${CIDS[@]}"; do
    [[ -z "$id" ]] && continue
    name=$(docker inspect "$id" --format '{{.Name}}' | sed 's/^\/\(.*\)$/\1/')
    st=$(docker inspect "$id" --format '{{.State.Status}}')
    hs=$(docker inspect "$id" --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}no-health{{end}}')
    
    if [[ "$st" != "running" ]] || [[ "$hs" == "unhealthy" ]] || [[ "$hs" != "no-health" && "$hs" != "healthy" ]]; then
      echo "  ⚠️  $name: status=$st, health=$hs"
      bad=1
    fi
  done

  (( bad==0 )) && break
  (( $(date +%s) - start_ts > HEALTH_TIMEOUT_SECS )) && { echo "⛔ health timeout"; break; }
  sleep 2
done

# 6) 요약 & 종료코드
echo "=== Container Summary ==="
docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" ps --format "table {{.Name}}\t{{.State}}\t{{.Publishers}}"
[[ "$PROM_MODE" == "standalone" ]] && docker ps --filter "name=^${PROM_NAME}$" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || true

# 6.1) 빠른 검증 실행 (ChatGPT 제안사항)
log "running quick verification..."
if [[ -f "$PROJECT_DIR/ops/scripts/quick_verify.sh" ]]; then
  bash "$PROJECT_DIR/ops/scripts/quick_verify.sh" && {
    log "✅ 모든 시스템 검증 통과"
  } || {
    log "⚠️ 일부 검증 실패 (시스템은 정상 작동 중일 수 있음)"
  }
else
  log "⚠️ quick_verify.sh 없음 - 기본 헬스체크만 실행"
fi

rc=0
while read -r name state; do [[ "$state" =~ unhealthy|Exited|dead|paused ]] && rc=4; done \
  < <(docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" ps --format "{{.Name}} {{.State}}")
if [[ "$PROM_MODE" == "standalone" ]] && docker ps -a --format '{{.Names}}' | grep -qx "$PROM_NAME"; then
  pst=$(docker inspect "$PROM_NAME" --format '{{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{else}}no-health{{end}}')
  [[ "$pst" =~ unhealthy|Exited|dead|paused ]] && rc=4
fi
(( rc!=0 )) && echo "⛔ some containers not healthy/running"
exit "$rc"

