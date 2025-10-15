#!/bin/bash
# CD 파이프라인 스니펫 - 배포 전/중/후 통합

set -e

echo "🚀 CD 파이프라인 스니펫 시작..."

# 환경변수 설정
export GRAFANA_URL="${GRAFANA_URL:-http://grafana:3000}"
export GRAFANA_TOKEN="${GRAFANA_TOKEN:-your-grafana-token}"
export DASHBOARD_ID="${DASHBOARD_ID:-123}"
export GIT_TAG="${GIT_TAG:-dev}"
export NAMESPACE="${NAMESPACE:-duri-prod}"

# 배포 시작 스니펫
echo "📋 배포 시작 스니펫..."
cat > scripts/deploy_start.sh << 'DEPLOY_START'
#!/bin/bash
# 배포 시작 스니펫

set -e

echo "🚀 배포 시작: $GIT_TAG"

# 1. Grafana 어노테이션 (배포 시작)
curl -X POST "$GRAFANA_URL/api/annotations" \
  -H "Authorization: Bearer $GRAFANA_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"dashboardId\": $DASHBOARD_ID,
    \"tags\": [\"deploy\", \"duri\", \"start\"],
    \"text\": \"deploy start: $GIT_TAG\",
    \"time\": $(date +%s%3N)
  }" || echo "⚠️ Grafana 어노테이션 실패"

# 2. Maintenance 모드 활성화 (선택적)
kubectl patch configmap maintenance-config -n $NAMESPACE -p '{"data":{"enabled":"true"}}' || echo "⚠️ Maintenance 모드 설정 실패"

# 3. 이전 배포 백업 (선택적)
kubectl get deployment duri-app -n $NAMESPACE -o yaml > /tmp/duri-app-backup-$(date +%Y%m%d-%H%M%S).yaml || echo "⚠️ 배포 백업 실패"

echo "✅ 배포 시작 완료"
DEPLOY_START

chmod +x scripts/deploy_start.sh

# 배포 성공 스니펫
echo "📋 배포 성공 스니펫..."
cat > scripts/deploy_success.sh << 'DEPLOY_SUCCESS'
#!/bin/bash
# 배포 성공 스니펫

set -e

echo "✅ 배포 성공: $GIT_TAG"

# 1. Grafana 어노테이션 (배포 성공)
curl -X POST "$GRAFANA_URL/api/annotations" \
  -H "Authorization: Bearer $GRAFANA_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"dashboardId\": $DASHBOARD_ID,
    \"tags\": [\"deploy\", \"duri\", \"success\"],
    \"text\": \"deploy success: $GIT_TAG\",
    \"time\": $(date +%s%3N)
  }" || echo "⚠️ Grafana 어노테이션 실패"

# 2. Maintenance 모드 비활성화
kubectl patch configmap maintenance-config -n $NAMESPACE -p '{"data":{"enabled":"false"}}' || echo "⚠️ Maintenance 모드 해제 실패"

# 3. 무결성 검증 확인
kubectl exec -it deployment/duri-app -c duri-app -n $NAMESPACE -- python -c "
from DuRiCore.deployment.deployment_integrity import deployment_integrity
r = deployment_integrity.verify_integrity()
assert r['integrity_verified'], f'Integrity check failed: {r[\"status\"]}'
print('✅ 무결성 검증 통과')
" || {
    echo "❌ 무결성 검증 실패"
    exit 1
}

# 4. 메트릭 확인
curl -s http://duri-app-service:9101/metrics | grep duri_integrity_status_verified || echo "⚠️ 메트릭 확인 실패"

echo "✅ 배포 성공 완료"
DEPLOY_SUCCESS

chmod +x scripts/deploy_success.sh

# 배포 롤백 스니펫
echo "📋 배포 롤백 스니펫..."
cat > scripts/deploy_rollback.sh << 'DEPLOY_ROLLBACK'
#!/bin/bash
# 배포 롤백 스니펫

set -e

echo "🔄 배포 롤백: $GIT_TAG"

# 1. Grafana 어노테이션 (배포 롤백)
curl -X POST "$GRAFANA_URL/api/annotations" \
  -H "Authorization: Bearer $GRAFANA_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"dashboardId\": $DASHBOARD_ID,
    \"tags\": [\"deploy\", \"duri\", \"rollback\"],
    \"text\": \"deploy rollback: $GIT_TAG\",
    \"time\": $(date +%s%3N)
  }" || echo "⚠️ Grafana 어노테이션 실패"

# 2. 롤백 실행
kubectl rollout undo deployment/duri-app -n $NAMESPACE --to-revision=1 || {
    echo "❌ 롤백 실패"
    exit 1
}

# 3. 롤백 상태 확인
kubectl rollout status deployment/duri-app -n $NAMESPACE --timeout=300s || {
    echo "❌ 롤백 상태 확인 실패"
    exit 1
}

# 4. Maintenance 모드 비활성화
kubectl patch configmap maintenance-config -n $NAMESPACE -p '{"data":{"enabled":"false"}}' || echo "⚠️ Maintenance 모드 해제 실패"

# 5. 무결성 검증 확인
kubectl exec -it deployment/duri-app -c duri-app -n $NAMESPACE -- python -c "
from DuRiCore.deployment.deployment_integrity import deployment_integrity
r = deployment_integrity.verify_integrity()
assert r['integrity_verified'], f'Integrity check failed: {r[\"status\"]}'
print('✅ 롤백 후 무결성 검증 통과')
" || {
    echo "❌ 롤백 후 무결성 검증 실패"
    exit 1
}

echo "✅ 배포 롤백 완료"
DEPLOY_ROLLBACK

chmod +x scripts/deploy_rollback.sh

# GitHub Actions 워크플로우 예시
echo "📋 GitHub Actions 워크플로우 예시..."
cat > .github/workflows/deploy.yml << 'GITHUB_ACTIONS'
name: Deploy DuRi Integrity

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  GRAFANA_URL: ${{ secrets.GRAFANA_URL }}
  GRAFANA_TOKEN: ${{ secrets.GRAFANA_TOKEN }}
  DASHBOARD_ID: ${{ secrets.DASHBOARD_ID }}
  NAMESPACE: duri-prod

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'v1.28.0'
    
    - name: Configure kubectl
      run: |
        echo "${{ secrets.KUBECONFIG }}" | base64 -d > ~/.kube/config
    
    - name: Deploy start
      run: ./scripts/deploy_start.sh
      env:
        GIT_TAG: ${{ github.sha }}
    
    - name: Deploy application
      run: |
        kubectl set image deployment/duri-app duri-app=your-registry/duri-app:${{ github.sha }} -n $NAMESPACE
        kubectl rollout status deployment/duri-app -n $NAMESPACE --timeout=300s
    
    - name: Deploy success
      run: ./scripts/deploy_success.sh
      env:
        GIT_TAG: ${{ github.sha }}
    
    - name: Deploy rollback (on failure)
      if: failure()
      run: ./scripts/deploy_rollback.sh
      env:
        GIT_TAG: ${{ github.sha }}
GITHUB_ACTIONS

echo "✅ CD 파이프라인 스니펫 완료!"
echo "📋 사용법:"
echo "   1. GitHub Secrets 설정: GRAFANA_URL, GRAFANA_TOKEN, DASHBOARD_ID, KUBECONFIG"
echo "   2. 배포 시작: ./scripts/deploy_start.sh"
echo "   3. 배포 성공: ./scripts/deploy_success.sh"
echo "   4. 배포 롤백: ./scripts/deploy_rollback.sh"
echo ""
echo "🚀 CD 파이프라인 통합 준비 완료!"
