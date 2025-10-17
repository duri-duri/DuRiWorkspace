# /home/duri/DuRiWorkspace/ops/shadow_on.sh
#!/usr/bin/env bash
set -Eeuo pipefail

# --- fixed docker compose wrapper ---
PROJECT_DIR="/home/duri/DuRiWorkspace"
PROJECT_NAME="duriworkspace"
DOCKER_BIN="${DOCKER_BIN:-$(command -v docker || echo /usr/bin/docker)}"
DC="$DOCKER_BIN compose -p $PROJECT_NAME --project-directory $PROJECT_DIR --ansi never"
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
cd "$PROJECT_DIR"

echo "=== 🌅 Shadow 훈련장 시작 ==="
echo "실행 시간: $(date)"

echo
echo "🚀 Shadow 훈련 서비스 시작 중..."
# 필수 베이스 먼저(이미 떠있으면 no-op)
$DC up -d --remove-orphans duri-postgres duri-redis aggregation_worker

# 의존성 대기(최대 60s)
for i in {1..60}; do
  PG=$($DC ps --format '{{.Name}} {{.Status}}' | grep duri-postgres || true)
  RD=$($DC ps --format '{{.Name}} {{.Status}}' | grep duri-redis || true)
  if echo "$PG" | grep -qi healthy && echo "$RD" | grep -qi healthy; then break; fi
  sleep 1
done

# 주간 구성 기동
$DC up -d --remove-orphans duri_control duri_core duri_brain duri_evolution

echo "🔄 Shadow 활성화 중..."
$DC exec -T duri-redis redis-cli SET shadow:enabled 1 >/dev/null
echo "OK"

echo "📊 카나리 비율 10% 설정 중..."

CUR=$($DC exec -T duri-redis redis-cli GET canary:ratio 2>/dev/null | tr -d '\r' || echo "")
EN_CANARY=$($DC exec -T duri-redis redis-cli GET canary:enabled 2>/dev/null | tr -d '\r' || echo "1")

if [ "${EN_CANARY:-1}" = "1" ]; then
  # 비어있거나 0(또는 ~0)에 가까우면 0.10으로 올림
  if [ -z "${CUR}" ] || awk "BEGIN{exit !(${CUR:-0} < 0.001)}"; then
    $DC exec -T duri-redis redis-cli SET canary:ratio 0.10 >/dev/null
    echo "OK (set -> 0.10)"
  else
    echo "OK (keep -> ${CUR})"
  fi
else
  echo "SKIP (canary:enabled=${EN_CANARY})"
fi

echo "📋 서비스 상태 확인..."
$DC ps | grep -E "(duri-postgres|duri-redis|duri_core|duri_brain|duri_evolution|duri_control|aggregation_worker)"

# 최근성 헬스(선택)
if $DC ps | grep -q aggregation_worker; then
  if ! $DC logs --since=5m --tail=200 aggregation_worker 2>/dev/null | grep -qiE 'snapshot#|guard=True'; then
    echo "⚠️ aggregation_worker: 최근 5분 내 heartbeat 미탐지"
  else
    echo "✅ aggregation_worker: heartbeat OK (<=5m)"
  fi
fi

echo
echo "✅ Shadow 훈련장 시작 완료"
echo "🎯 다음 단계:"
echo "   - 10분 후: ./check_srm_and_guard.sh"
echo "   - 30분 후: ./run_promote_canary.sh 0.50"
echo "   - 저녁 퇴근 시: ./ops/shadow_off.sh"
echo "⏰ 실행 시간: $(date)"