#!/bin/bash
# 온콜용 롤백 치트키

set -e

echo "🔄 온콜용 롤백 치트키 시작..."

# 환경변수 설정
export NAMESPACE="${NAMESPACE:-duri-prod}"
export DEPLOYMENT="${DEPLOYMENT:-duri-app}"

# 롤백 함수
rollback_deployment() {
    echo "🔄 배포 롤백 실행..."
    
    # 1. 자동 롤백 스크립트 실행
    if [ -f "scripts/deploy_rollback.sh" ]; then
        ./scripts/deploy_rollback.sh || {
            echo "⚠️ 자동 롤백 스크립트 실패 - 수동 롤백 실행"
            manual_rollback
        }
    else
        echo "⚠️ 자동 롤백 스크립트 없음 - 수동 롤백 실행"
        manual_rollback
    fi
}

# 수동 롤백 함수
manual_rollback() {
    echo "🔧 수동 롤백 실행..."
    
    # 1. 롤백 실행
    kubectl rollout undo deployment/$DEPLOYMENT -n $NAMESPACE --to-revision=1 || {
        echo "❌ 롤백 실행 실패"
        exit 1
    }
    
    # 2. 롤백 상태 확인
    kubectl rollout status deployment/$DEPLOYMENT -n $NAMESPACE --timeout=300s || {
        echo "❌ 롤백 상태 확인 실패"
        exit 1
    }
    
    # 3. 무결성 검증 확인
    kubectl exec -it deployment/$DEPLOYMENT -c duri-app -n $NAMESPACE -- python -c "
from DuRiCore.deployment.deployment_integrity import deployment_integrity
r = deployment_integrity.verify_integrity()
assert r['integrity_verified'], f'Integrity check failed: {r[\"status\"]}'
print('✅ 롤백 후 무결성 검증 통과')
" || {
        echo "❌ 롤백 후 무결성 검증 실패"
        exit 1
    }
    
    echo "✅ 수동 롤백 완료"
}

# 사일런스 / 메인터넌스 퀵 토글
maintenance_toggle() {
    local action=$1
    
    case $action in
        "on")
            echo "🔧 Maintenance 모드 ON..."
            kubectl patch configmap maintenance-config -n $NAMESPACE -p '{"data":{"enabled":"true"}}'
            echo "✅ Maintenance 모드 ON 완료"
            ;;
        "off")
            echo "🔧 Maintenance 모드 OFF..."
            kubectl patch configmap maintenance-config -n $NAMESPACE -p '{"data":{"enabled":"false"}}'
            echo "✅ Maintenance 모드 OFF 완료"
            ;;
        *)
            echo "Usage: $0 maintenance {on|off}"
            exit 1
            ;;
    esac
}

# 메인 로직
case "$1" in
    "rollback")
        rollback_deployment
        ;;
    "maintenance")
        maintenance_toggle "$2"
        ;;
    "status")
        echo "📊 현재 상태 확인..."
        kubectl get pods -l app=duri-app -n $NAMESPACE -o wide
        kubectl logs -l app=duri-app -c duri-integrity-sidecar -n $NAMESPACE --tail=10
        ;;
    *)
        echo "Usage: $0 {rollback|maintenance|status}"
        echo ""
        echo "명령어:"
        echo "  $0 rollback                    # 배포 롤백"
        echo "  $0 maintenance on              # Maintenance 모드 ON"
        echo "  $0 maintenance off             # Maintenance 모드 OFF"
        echo "  $0 status                      # 현재 상태 확인"
        exit 1
        ;;
esac

echo ""
echo "✅ 온콜용 롤백 치트키 완료!"
