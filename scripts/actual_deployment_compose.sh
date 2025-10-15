#!/bin/bash
set -euo pipefail

echo "🚀 실제 집행(Compose 폴백) 시작..."

# 1) 시작 훅(있으면 실행)
[ -x ./scripts/deploy_start.sh ] && ./scripts/deploy_start.sh || true

# 2) 이미지 리빌드/롤링 재시작 (핵심 4개)
echo "🔄 서비스 재배포(빌드→재기동)..."
docker compose build duri_core duri_brain duri_evolution duri_control
docker compose up -d --no-deps duri_core duri_brain duri_evolution duri_control

# 3) 헬스 스모크 (HEAD→GET 폴백)
check() {
  local port=$1
  local head=$(curl -sI "http://localhost:$port/health" | head -1 || true)
  if echo "$head" | grep -E " 200 | 204 " >/dev/null; then
    echo ":$port HEAD ok -> $head"
  else
    local body=$(curl -s "http://localhost:$port/health" || true)
    [ -n "$body" ] || { echo "❌ :$port health FAIL"; exit 1; }
    echo ":$port GET ok -> $(echo "$body" | head -c 80)"
  fi
}
for p in 8080 8081 8082 8083; do check $p; done
echo "✅ 앱 헬스 스모크 통과"

# 4) 무결성 스모크
echo "🧪 무결성 스모크..."
python3 - <<'PY'
from DuRiCore.deployment.deployment_integrity import deployment_integrity as d
res=d.verify_integrity()
assert res["integrity_verified"], f"Integrity failed: {res}"
print("OK:", res["summary"])
PY
curl -fsS http://localhost:9090/-/healthy >/dev/null && echo "✅ Prometheus healthy"

# 5) 성공 훅(있으면 실행)
[ -x ./scripts/deploy_success.sh ] && ./scripts/deploy_success.sh || true

echo "🎉 실제 집행(Compose 폴백) 완료!"
echo "📊 포스트 관측 추천:"
echo "  - {__name__=~\"duri:integrity:.*\"}[5m]"
echo "  - duri:integrity:failure_rate"
echo "  - increase(duri:integrity:status:tampered[5m]) == 0"
