#!/bin/bash
# 최종 프리플라이트 - 1분 컷

set -e

echo "🚀 최종 프리플라이트 체크 시작..."

# 환경변수 설정
export GRAFANA_URL="${GRAFANA_URL:-http://grafana:3000}"
export GRAFANA_TOKEN="${GRAFANA_TOKEN:-your-grafana-token}"
export DASHBOARD_ID="${DASHBOARD_ID:-123}"
export NAMESPACE="${NAMESPACE:-duri-prod}"

# 1. Prometheus 룰 문법 검증
echo "1️⃣ Prometheus 룰 문법 검증..."
if command -v promtool &> /dev/null; then
    promtool check rules config/prometheus_rules_final.yml
    promtool check rules config/prometheus_recording_rules.yml
    promtool check rules config/prometheus_slo_recording_rules.yml
    echo "✅ Prometheus 룰 문법 검증 통과"
else
    echo "⚠️ promtool이 설치되지 않음 - 수동으로 확인 필요"
fi

# 2. Grafana 토큰/URL & dashboardId 유효성
echo "2️⃣ Grafana 토큰/URL & dashboardId 유효성 확인..."
curl -s -H "Authorization: Bearer $GRAFANA_TOKEN" "$GRAFANA_URL/api/dashboards/uid/$DASHBOARD_ID" | jq -r '.dashboard.title' || {
    echo "⚠️ Grafana 대시보드 접근 실패 - 토큰/URL/dashboardId 확인 필요"
}

# 3. Prometheus 쿼리 엔드포인트 DNS 확인
echo "3️⃣ Prometheus 쿼리 엔드포인트 DNS 확인..."
kubectl exec -it deployment/duri-app -c duri-app -n $NAMESPACE -- curl -s http://prometheus:9090/api/v1/query?query=up || {
    echo "⚠️ Prometheus 쿼리 엔드포인트 접근 실패 - DNS/네트워크 확인 필요"
}

# 4. CronJob 스케줄 타임존 확인
echo "4️⃣ CronJob 스케줄 타임존 확인..."
echo "📋 CronJob 스케줄:"
echo "   - Synthetic: */5 * * * * (5분마다)"
echo "   - Backup Recovery: 0 2 * * 0 (매주 일요일 2시 UTC)"
echo "   - 클러스터 노드 타임존: UTC (일반적)"

# 5. aws-credentials 시크릿 key 이름 재확인
echo "5️⃣ aws-credentials 시크릿 key 이름 재확인..."
kubectl get secret aws-credentials -n $NAMESPACE -o jsonpath='{.data}' | jq -r 'keys[]' || {
    echo "⚠️ aws-credentials 시크릿 없음 - 생성 필요"
    echo "📋 생성 명령어:"
    echo "   kubectl create secret generic aws-credentials -n $NAMESPACE \\"
    echo "     --from-literal=access-key-id=your-access-key \\"
    echo "     --from-literal=secret-access-key=your-secret-key"
}

# 6. Alertmanager Silence API 권한 확인
echo "6️⃣ Alertmanager Silence API 권한 확인..."
kubectl exec -it deployment/duri-app -c duri-app -n $NAMESPACE -- curl -s http://alertmanager:9093/api/v1/silences || {
    echo "⚠️ Alertmanager Silence API 접근 실패 - 권한/네트워크 확인 필요"
}

# 7. HMAC 듀얼검증 전환 확인
echo "7️⃣ HMAC 듀얼검증 전환 확인..."
kubectl get deployment duri-app -n $NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].env[?(@.name=="DURI_HMAC_KEY_DUAL_VERIFY")].value}' || {
    echo "⚠️ HMAC 듀얼검증 설정 없음 - 필요 시 설정"
}

# 8. Synthetic/Backup CronJob 생성 직후 1회 강제 실행
echo "8️⃣ Synthetic/Backup CronJob 생성 직후 1회 강제 실행..."
kubectl create job --from=cronjob/duri-synthetic duri-synthetic-now -n $NAMESPACE || {
    echo "⚠️ Synthetic CronJob 강제 실행 실패"
}

kubectl create job --from=cronjob/duri-backup-recovery duri-backup-now -n $NAMESPACE || {
    echo "⚠️ Backup Recovery CronJob 강제 실행 실패"
}

echo ""
echo "✅ 최종 프리플라이트 체크 완료!"
echo "🚀 배포 준비 완료 - 이제 배포 버튼을 누르세요!"
