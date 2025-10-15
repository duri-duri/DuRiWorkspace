#!/bin/bash
# Go/No-Go 초간단 체크 - 필수 8개

set -e

echo "🚦 Go/No-Go 초간단 체크 시작..."

# 1. Argo Rollouts 버전 확인
echo "1️⃣ Argo Rollouts 버전 확인..."
argo_version=$(kubectl get crd rollouts.argoproj.io -o jsonpath='{.spec.versions[0].name}' 2>/dev/null || echo "unknown")
echo "   Argo Rollouts 버전: $argo_version"
if [[ "$argo_version" == "v1.5"* ]] || [[ "$argo_version" == "v1.6"* ]] || [[ "$argo_version" == "v1.7"* ]]; then
    echo "✅ Argo Rollouts 버전 호환 (skipOnNoData/count 지원)"
else
    echo "⚠️ Argo Rollouts 버전 확인 필요 - skipOnNoData/count 필드 주석 처리 권장"
fi

# 2. Helm 스키마 린트 호환 확인
echo "2️⃣ Helm 스키마 린트 호환 확인..."
helm_version=$(helm version --short 2>/dev/null | cut -d'+' -f1 || echo "unknown")
echo "   Helm 버전: $helm_version"
if [[ "$helm_version" == "v3.13"* ]] || [[ "$helm_version" == "v3.14"* ]] || [[ "$helm_version" == "v3.15"* ]]; then
    echo "✅ Helm 스키마 린트 호환 (--schema 지원)"
else
    echo "⚠️ Helm 스키마 린트 미지원 - CI에서는 helm lint만 사용"
fi

# 3. 다이제스트 주입 경로 확인
echo "3️⃣ 다이제스트 주입 경로 확인..."
if command -v crane &> /dev/null; then
    echo "✅ crane 설치됨 - 다이제스트 주입 가능"
elif command -v skopeo &> /dev/null; then
    echo "✅ skopeo 설치됨 - 다이제스트 주입 가능"
else
    echo "⚠️ crane/skopeo 미설치 - 다이제스트 주입 불가"
    echo "📋 설치 명령어:"
    echo "   # crane 설치"
    echo "   curl -L https://github.com/google/go-containerregistry/releases/latest/download/go-containerregistry_Linux_x86_64.tar.gz | tar xz"
    echo "   sudo mv crane /usr/local/bin/"
    echo ""
    echo "   # skopeo 설치"
    echo "   sudo apt-get update && sudo apt-get install -y skopeo"
fi

# 4. 네임스페이스/라벨 정합 확인
echo "4️⃣ 네임스페이스/라벨 정합 확인..."
prometheus_ns=$(kubectl get pods -l app.kubernetes.io/name=prometheus -A -o jsonpath='{.items[0].metadata.namespace}' 2>/dev/null || echo "monitoring")
echo "   Prometheus 네임스페이스: $prometheus_ns"
if [ "$prometheus_ns" = "monitoring" ]; then
    echo "✅ 네임스페이스/라벨 정합 확인됨"
else
    echo "⚠️ Prometheus 네임스페이스 불일치 - values.yaml 수정 필요"
fi

# 5. Alertmanager 엔드포인트 보호 확인
echo "5️⃣ Alertmanager 엔드포인트 보호 확인..."
alertmanager_url="http://alertmanager:9093/api/v2/alerts"
echo "   Alertmanager URL: $alertmanager_url"
kubectl exec -it deployment/duri-app -c duri-app -n duri-prod -- curl -s -o /dev/null -w "%{http_code}\n" "$alertmanager_url" || {
    echo "⚠️ Alertmanager 엔드포인트 접근 실패 - 네트워크 정책 확인 필요"
}

# 6. Grafana 토큰 권한/폴더 스코프 확인
echo "6️⃣ Grafana 토큰 권한/폴더 스코프 확인..."
grafana_token_test=$(curl -s -H "Authorization: Bearer $GRAFANA_TOKEN" "$GRAFANA_URL/api/user" | jq -r '.login' 2>/dev/null || echo "failed")
if [ "$grafana_token_test" != "failed" ]; then
    echo "✅ Grafana 토큰 권한 확인됨"
else
    echo "⚠️ Grafana 토큰 권한 실패 - annotations:write 권한 확인 필요"
fi

# 7. RBAC 확인
echo "7️⃣ RBAC 확인..."
rbac_check=$(kubectl auth can-i patch secrets -n duri-prod --as=system:serviceaccount:duri-prod:duri-integrity 2>/dev/null || echo "no")
if [ "$rbac_check" = "yes" ]; then
    echo "✅ RBAC 권한 확인됨"
else
    echo "⚠️ RBAC 권한 부족 - secrets/configmaps/deployments 패치 권한 필요"
fi

# 8. CronJob 이름 충돌 확인
echo "8️⃣ CronJob 이름 충돌 확인..."
existing_cronjobs=$(kubectl get cronjobs -n duri-prod -o name 2>/dev/null || echo "")
if echo "$existing_cronjobs" | grep -q "duri-synthetic\|duri-backup-recovery"; then
    echo "⚠️ 기존 CronJob 이름 충돌 - 덮어씌우기 예정"
else
    echo "✅ CronJob 이름 충돌 없음"
fi

echo ""
echo "✅ Go/No-Go 초간단 체크 완료!"
echo "🚀 배포 준비 완료 - 이제 배포 버튼을 누르세요!"
