#!/usr/bin/env bash
set -Eeuo pipefail

# 빠른 검증 루틴 (운영 체크리스트)
# ChatGPT 제안사항 기반으로 생성

PROJECT_DIR="${PROJECT_DIR:-$HOME/DuRiWorkspace}"
cd "$PROJECT_DIR"

echo "=== 빠른 시스템 검증 ==="
echo "Timestamp: $(date -Is)"

# 1) Grafana & Prometheus 컨테이너 상태
echo "**1) 핵심 컨테이너 상태:**"
docker compose -p duriworkspace ps | grep -E 'grafana|prometheus' || echo "⚠️ Grafana 또는 Prometheus 컨테이너 없음"

# 2) Grafana 헬스체크
echo -e "\n**2) Grafana 헬스체크:**"
if curl -sf http://localhost:3000/api/health | jq . 2>/dev/null; then
    echo "✅ Grafana 정상"
else
    echo "❌ Grafana 접속 실패"
fi

# 3) Prometheus 타겟 상태
echo -e "\n**3) Prometheus 타겟 상태:**"
if curl -sf http://localhost:9090/api/v1/targets?state=any | jq '[.data.activeTargets[] | {job: .labels.job, health: .health}]' 2>/dev/null; then
    echo "✅ Prometheus 타겟 조회 성공"
else
    echo "❌ Prometheus 타겟 조회 실패"
fi

# 4) Prometheus 준비 상태
echo -e "\n**4) Prometheus 준비 상태:**"
if curl -sf http://localhost:9090/-/ready >/dev/null 2>&1; then
    echo "✅ Prometheus 준비 완료"
else
    echo "❌ Prometheus 준비 미완료"
fi

# 5) 알림 규칙 상태 (개선된 검증)
echo -e "\n**5) 알림 규칙 상태:**"
ALERT_GROUPS=$(curl -sf http://localhost:9090/api/v1/alerts | jq '.data.groups | length' 2>/dev/null || echo "0")
RULES_GROUPS=$(curl -sf http://localhost:9090/api/v1/rules | jq '.data.groups | length' 2>/dev/null || echo "0")

if [ "$RULES_GROUPS" -gt 0 ]; then
    echo "✅ 규칙 로드 완료 ($RULES_GROUPS 그룹)"
    if [ "$ALERT_GROUPS" -gt 0 ]; then
        echo "⚠️ 활성 알림: $ALERT_GROUPS 그룹"
    else
        echo "✅ 활성 알림 없음 (정상)"
    fi
else
    echo "❌ 규칙 로드 실패"
fi

# 6) 전체 컨테이너 헬스 요약
echo -e "\n**6) 전체 컨테이너 헬스 요약:**"
total=$(docker compose -p duriworkspace ps --format "table {{.Name}}\t{{.State}}" | grep -v "NAME" | wc -l)
healthy=$(docker compose -p duriworkspace ps --format "table {{.Name}}\t{{.State}}" | grep -c "running" || echo "0")
echo "전체: $total, 실행중: $healthy"

if [ "$healthy" -eq "$total" ] && [ "$total" -gt 0 ]; then
    echo "🎉 모든 컨테이너 정상 실행 중!"
    exit 0
else
    echo "⚠️ 일부 컨테이너 문제 있음"
    exit 1
fi
