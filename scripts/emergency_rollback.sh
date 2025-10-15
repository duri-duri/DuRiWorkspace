#!/bin/bash
# 즉시 롤백 스위치

set -e

echo "🔄 즉시 롤백 스위치 시작..."

# 환경변수 설정
export NAMESPACE="${NAMESPACE:-duri-prod}"

# 롤백 옵션
case "$1" in
    "auto")
        echo "🔄 자동 롤백 실행..."
        ./scripts/deploy_rollback.sh
        ;;
    "manual")
        echo "🔄 수동 롤백 실행..."
        kubectl rollout undo deployment/duri-app -n $NAMESPACE
        kubectl rollout status deployment/duri-app -n $NAMESPACE --timeout=300s
        ;;
    "revision")
        echo "🔄 특정 리비전으로 롤백..."
        REVISION=${2:-1}
        kubectl rollout undo deployment/duri-app -n $NAMESPACE --to-revision=$REVISION
        kubectl rollout status deployment/duri-app -n $NAMESPACE --timeout=300s
        ;;
    *)
        echo "Usage: $0 {auto|manual|revision [N]}"
        echo ""
        echo "명령어:"
        echo "  $0 auto                    # 자동 롤백 (스크립트)"
        echo "  $0 manual                  # 수동 롤백 (kubectl)"
        echo "  $0 revision 1              # 특정 리비전으로 롤백"
        exit 1
        ;;
esac

echo ""
echo "✅ 즉시 롤백 스위치 완료!"
