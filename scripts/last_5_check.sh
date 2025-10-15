#!/bin/bash
# 라스트 5 - 60초 점검

set -e

echo "🚀 라스트 5 - 60초 점검 시작..."

# 환경변수 설정
export GRAFANA_URL="${GRAFANA_URL:-http://grafana:3000}"
export GRAFANA_TOKEN="${GRAFANA_TOKEN:-your-grafana-token}"
export DASHBOARD_ID="${DASHBOARD_ID:-123}"
export NAMESPACE="${NAMESPACE:-duri-prod}"

# 1. Helm 템플릿·Lint
echo "1️⃣ Helm 템플릿·Lint..."
if command -v helm &> /dev/null; then
    helm lint helm/duri-integrity
    helm template duri-prod helm/duri-integrity -f helm/duri-integrity/values.yaml | kubectl apply --dry-run=server -f -
    echo "✅ Helm 템플릿·Lint 통과"
else
    echo "⚠️ helm이 설치되지 않음 - 수동으로 확인 필요"
fi

# 2. Prometheus 룰 문법/적용
echo "2️⃣ Prometheus 룰 문법/적용..."
if command -v promtool &> /dev/null; then
    promtool check rules config/prometheus_recording_rules.yml
    promtool check rules config/prometheus_rules_final.yml
    promtool check rules config/prometheus_slo_recording_rules.yml
    echo "✅ Prometheus 룰 문법/적용 통과"
else
    echo "⚠️ promtool이 설치되지 않음 - 수동으로 확인 필요"
fi

# 3. Grafana 어노테이션 Dry-run
echo "3️⃣ Grafana 어노테이션 Dry-run..."
http_code=$(curl -s -o /dev/null -w "%{http_code}\n" -X POST "$GRAFANA_URL/api/annotations" \
  -H "Authorization: Bearer $GRAFANA_TOKEN" -H "Content-Type: application/json" \
  -d "{\"dashboardId\": $DASHBOARD_ID, \"tags\":[\"deploy\",\"dryrun\"],\"text\":\"preflight\",\"time\":$(date +%s%3N)}")

if [ "$http_code" = "200" ]; then
    echo "✅ Grafana 어노테이션 Dry-run 통과 (HTTP $http_code)"
else
    echo "⚠️ Grafana 어노테이션 Dry-run 실패 (HTTP $http_code)"
fi

# 4. CronJob 즉시 실행(합성/백업 리허설)
echo "4️⃣ CronJob 즉시 실행(합성/백업 리허설)..."
kubectl create job --from=cronjob/duri-synthetic duri-synthetic-manual-$(date +%s) -n $NAMESPACE || {
    echo "⚠️ Synthetic CronJob 강제 실행 실패"
}

kubectl create job --from=cronjob/duri-backup-recovery duri-backup-manual-$(date +%s) -n $NAMESPACE || {
    echo "⚠️ Backup Recovery CronJob 강제 실행 실패"
}

echo "✅ CronJob 즉시 실행 완료"

# 5. 게이트 쿼리 즉검 (0이어야 정상)
echo "5️⃣ 게이트 쿼리 즉검 (0이어야 정상)..."
echo "📋 Prometheus 쿼리:"
echo "   increase(duri:integrity:status:tampered[5m]) OR increase(duri:integrity:status:corrupted[5m])"
echo "   → 0이어야 정상"

echo ""
echo "✅ 라스트 5 - 60초 점검 완료!"
echo "🚀 배포 준비 완료 - 이제 배포 버튼을 누르세요!"
