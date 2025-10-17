# /home/duri/DuRiWorkspace/ops/shadow_off.sh
#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="/home/duri/DuRiWorkspace"
PROJECT_NAME="duriworkspace"
DOCKER_BIN="${DOCKER_BIN:-$(command -v docker || echo /usr/bin/docker)}"
DC="$DOCKER_BIN compose -p $PROJECT_NAME --project-directory $PROJECT_DIR --ansi never"
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
cd "$PROJECT_DIR"

echo "=== 🌙 Shadow 훈련장 중지 ==="
echo "실행 시간: $(date)"

echo
echo "🛑 카나리 비율 0으로 설정 중..."
$DC exec -T duri-redis redis-cli SET canary:ratio 0 >/dev/null
echo "OK"

echo "🔒 Shadow 비활성화 중..."
$DC exec -T duri-redis redis-cli SET shadow:enabled 0 >/dev/null
echo "OK"

echo "⏹️ Shadow 훈련 서비스만 중지 중..."
# 밤에는 core/brain/evolution/control OFF, DB/Redis/worker 유지
$DC stop duri_core duri_brain duri_evolution duri_control || true

echo "📋 서비스 상태 확인..."
$DC ps | grep -E "(duri-postgres|duri-redis)"

echo
echo "✅ Shadow 훈련장 중지 완료"
echo "🎯 다음 단계:"
echo "   - 내일 아침: ./ops/shadow_on.sh"
echo "   - duri_head는 계속 실행 중 (DB/Redis/aggregation_worker)"
echo "⏰ 실행 시간: $(date)"