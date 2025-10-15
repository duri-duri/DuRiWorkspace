#!/bin/bash
# 실행 순서 - 실제 집행

set -e

echo "🚀 실제 집행 시작..."

# 환경변수 설정
export GIT_SHA="${GIT_SHA:-$(git rev-parse HEAD)}"
export NAMESPACE="${NAMESPACE:-duri-prod}"

# 1) 레코딩/알람/게이트 리소스 배포
echo "1️⃣ 레코딩/알람/게이트 리소스 배포..."
kubectl apply -f config/prometheus_recording_rules.yml
kubectl apply -f config/prometheus_rules_final.yml
kubectl apply -f config/prometheus_slo_recording_rules.yml
kubectl apply -f k8s/argo-rollouts-analysis-improved.yaml   # 사용 시
kubectl apply -f k8s/duri-synthetic-cronjob.yaml
kubectl apply -f k8s/backup-recovery-cronjob.yaml
echo "✅ 레코딩/알람/게이트 리소스 배포 완료"

# 2) 배포 시작
echo "2️⃣ 배포 시작..."
./scripts/deploy_start.sh
echo "✅ 배포 시작 완료"

# 3) 새 이미지로 롤아웃
echo "3️⃣ 새 이미지로 롤아웃..."
kubectl set image deployment/duri-app duri-app=your-registry/duri-app:${GIT_SHA} -n $NAMESPACE
kubectl rollout status deployment/duri-app -n $NAMESPACE --timeout=300s
echo "✅ 새 이미지로 롤아웃 완료"

# 4) 무결성 스모크
echo "4️⃣ 무결성 스모크..."
POD=$(kubectl get pod -n $NAMESPACE -l app=duri-app -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n $NAMESPACE "$POD" -c duri-app -- python -c 'from DuRiCore.deployment.deployment_integrity import deployment_integrity as d; r=d.verify_integrity(); assert r["integrity_verified"]; print("OK")'
curl -s http://duri-app-service:9101/metrics | grep duri_integrity_status_verified
echo "✅ 무결성 스모크 완료"

# 5) 성공 처리
echo "5️⃣ 성공 처리..."
./scripts/deploy_success.sh
echo "✅ 성공 처리 완료"

echo ""
echo "🎉 실제 집행 완료!"
echo "📊 포스트 배포 5줄 관측:"
echo "   {__name__=~\"duri:integrity:.*\"}[5m]"
echo "   duri:integrity:failure_rate"
echo "   duri:integrity:hmac:status{enabled=\"false\"}"
echo "   duri:slo:integrity_verified_ratio_30d"
echo "   increase(duri:integrity:status:tampered[5m]) > 0"
echo ""
echo "🚀 배포 성공!"
