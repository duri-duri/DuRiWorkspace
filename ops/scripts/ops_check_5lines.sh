#!/usr/bin/env bash
set -Eeuo pipefail

# 운영 체크 5줄 (ChatGPT 제안사항)
# 빠른 시스템 상태 확인을 위한 핵심 체크리스트

PROJECT_DIR="${PROJECT_DIR:-$HOME/DuRiWorkspace}"
cd "$PROJECT_DIR"

echo "=== 운영 체크 5줄 ==="
echo "Timestamp: $(date -Is)"

# 1) 핵심 컨테이너 상태
echo -e "\n**1) 핵심 컨테이너 상태:**"
docker compose -p duriworkspace ps | grep -E 'grafana|prometheus'

# 2) Grafana 헬스체크
echo -e "\n**2) Grafana 헬스체크:**"
curl -sf http://localhost:3000/api/health | jq .

# 3) Prometheus 타겟 상태
echo -e "\n**3) Prometheus 타겟 상태:**"
curl -sf http://localhost:9090/api/v1/targets?state=any \
 | jq '[.data.activeTargets[] | {job: .labels.job, health: .health}]'

# 4) Prometheus 준비 상태
echo -e "\n**4) Prometheus 준비 상태:**"
if curl -sf http://localhost:9090/-/ready >/dev/null 2>&1; then
    echo "✅ Prometheus 준비 완료"
else
    echo "❌ Prometheus 준비 미완료"
fi

# 5) 알림 규칙 상태
echo -e "\n**5) 알림 규칙 상태:**"
curl -sf http://localhost:9090/api/v1/alerts | jq '.data.groups | length'

echo -e "\n=== 운영 체크 완료 ==="
