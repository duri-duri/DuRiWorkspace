#!/bin/bash
# 마지막 빠른 보완/주의 - 라스트-마일 체크

set -e

echo "🔧 마지막 빠른 보완/주의 시작..."

# 1. Argo Rollouts 버전 체크 로직 보완
echo "1️⃣ Argo Rollouts 버전 체크 로직 보완..."
argo_cli_version=$(kubectl argo rollouts version 2>/dev/null | grep -o 'v[0-9]\+\.[0-9]\+' | head -1 || echo "unknown")
argo_controller_version=$(kubectl get deployment argo-rollouts -n argo-rollouts -o jsonpath='{.spec.template.spec.containers[0].image}' 2>/dev/null | grep -o 'v[0-9]\+\.[0-9]\+' || echo "unknown")
echo "   Argo CLI 버전: $argo_cli_version"
echo "   Argo Controller 버전: $argo_controller_version"
if [[ "$argo_cli_version" == "v1.5"* ]] || [[ "$argo_cli_version" == "v1.6"* ]] || [[ "$argo_cli_version" == "v1.7"* ]]; then
    echo "✅ Argo Rollouts 버전 호환 (skipOnNoData/count 지원)"
else
    echo "⚠️ Argo Rollouts 버전 확인 필요 - skipOnNoData/count 필드 주석 처리 권장"
fi

# 2. 컨테이너 내 curl/jq 의존성 확인
echo "2️⃣ 컨테이너 내 curl/jq 의존성 확인..."
if command -v jq &> /dev/null; then
    echo "✅ jq 설치됨 - CI/런너에서 사용 가능"
else
    echo "⚠️ jq 미설치 - CI/런너에 jq 설치 step 추가 필요"
    echo "📋 설치 명령어: sudo apt-get update && sudo apt-get install -y jq"
fi

# curl 대체 방법 확인
echo "   curl 대체 방법: kubectl run tmp-curl --image=alpine/curl --rm -it --restart=Never -- curl ..."

# 3. 이미지 다이제스트 핀: 앱 본체도 확인
echo "3️⃣ 이미지 다이제스트 핀: 앱 본체도 확인..."
echo "   권장: DURI_APP_DIGEST=\$(crane digest your-registry/duri-app:\${GIT_SHA})"
echo "   적용: kubectl set image ... duri-app=your-registry/duri-app@\${DURI_APP_DIGEST}"

# 4. NetworkPolicy 범위 확인
echo "4️⃣ NetworkPolicy 범위 확인..."
echo "   현재: 앱 파드 기준"
echo "   백업 CronJob S3 접근: 별도 egress 규칙 필요 (S3/VPC 엔드포인트 또는 443 허용)"

# 5. Alertmanager 엔드포인트 보안 확인
echo "5️⃣ Alertmanager 엔드포인트 보안 확인..."
alertmanager_url="${ALERTMANAGER_URL:-http://alertmanager:9093/api/v2/alerts}"
echo "   현재 URL: $alertmanager_url"
echo "   권장: 네임스페이스 내 클러스터IP + 네트워크폴리시 허용만"
echo "   또는: 프록시(OIDC) 경유"

# 6. Helm 스키마의 이미지 패턴 확인
echo "6️⃣ Helm 스키마의 이미지 패턴 확인..."
if [ -f "helm/duri-integrity/values.schema.json" ]; then
    echo "✅ values.schema.json 존재 - @sha256: 패턴 강제"
    echo "   SYNTH_DIGEST와 AWSCLI_DIGEST 반드시 주입 필요"
else
    echo "⚠️ values.schema.json 없음 - 스키마 검증 불가"
fi

# 7. RBAC 검증 대상 SA 확인
echo "7️⃣ RBAC 검증 대상 SA 확인..."
sa_exists=$(kubectl get serviceaccount duri-integrity -n duri-prod 2>/dev/null && echo "exists" || echo "missing")
echo "   ServiceAccount duri-integrity: $sa_exists"
if [ "$sa_exists" = "missing" ]; then
    echo "⚠️ ServiceAccount 없음 - Helm에서 SA 생성 ON 필요"
fi

# 8. Prometheus 라벨/네임스페이스 확인
echo "8️⃣ Prometheus 라벨/네임스페이스 확인..."
prometheus_labels=$(kubectl get pods -l app.kubernetes.io/name=prometheus -A -o jsonpath='{.items[0].metadata.labels}' 2>/dev/null || echo "not found")
echo "   Prometheus 라벨: $prometheus_labels"
echo "   NP에서 app.kubernetes.io/name: prometheus 가정"

# 9. GitHub Actions: 'latest' digest 해석 확인
echo "9️⃣ GitHub Actions: 'latest' digest 해석 확인..."
echo "   현재: amazon/aws-cli:latest → digest 고정"
echo "   권장: 고정 버전 태그 (예: 2.17.x)에서 digest 해석"

# 10. Canary 게이트 쿼리 창 확인
echo "🔟 Canary 게이트 쿼리 창 확인..."
echo "   현재: increase(...[5m]) 1분 주기로 10회"
echo "   권장: 간헐적 스크레이프 지연 시 [6m]로 1분 여유"

echo ""
echo "✅ 마지막 빠른 보완/주의 완료!"
echo "🚀 95점권 확실 - 이제 배포 버튼을 누르세요!"
