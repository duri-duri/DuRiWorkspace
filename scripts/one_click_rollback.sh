#!/bin/bash
# 롤백 원클릭

set -e

echo "🧯 롤백 원클릭 시작..."

# 환경변수 설정
export NAMESPACE="${NAMESPACE:-duri-prod}"

# 롤백 옵션
case "$1" in
    "auto")
        echo "🔄 자동 롤백 실행..."
        ./scripts/emergency_rollback.sh auto
        ;;
    "manual")
        echo "🔄 수동 롤백 실행..."
        ./scripts/emergency_rollback.sh manual
        ;;
    "revision")
        REVISION=${2:-1}
        echo "🔄 특정 리비전($REVISION)으로 롤백 실행..."
        ./scripts/emergency_rollback.sh revision $REVISION
        ;;
    *)
        echo "Usage: $0 {auto|manual|revision [N]}"
        echo ""
        echo "명령어:"
        echo "  $0 auto                    # 자동 롤백 (스크립트)"
        echo "  $0 manual                  # 수동 롤백 (kubectl)"
        echo "  $0 revision 1              # 특정 리비전으로 롤백"
        echo ""
        echo "🧯 롤백 원클릭 완료!"
        exit 1
        ;;
esac

echo ""
echo "✅ 롤백 원클릭 완료!"
