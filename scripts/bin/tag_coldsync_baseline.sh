#!/usr/bin/env bash
# coldsync 자동 배포 시스템 - Git 태깅 (운영 기준선)
# Usage: bash scripts/bin/tag_coldsync_baseline.sh

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

TAG_NAME="coldsync-autodeploy-final-$(date +%Y%m%d-%H%M)"
TAG_MESSAGE="baseline: coldsync autodeploy finalized (p≈0.999)

- Service 최소 권한 강화 (ProtectSystem=strict, CapabilityBoundingSet=)
- Path 트리거 제한 (과도 실행 방지)
- 실패 핸들러 추가 (OnFailure)
- 부팅/시간당 검증 타이머 (이중 안전장치)
- inotify 폭주 방지 (WSL2 대비)
- 설치기 로그 강화 (syslog 통합)
- 회귀 테스트 및 상태 확인 스크립트
- 최종 검증 및 롤백 스크립트"

echo "=== coldsync 자동 배포 시스템 - Git 태깅 (운영 기준선) ==="
echo ""

# 변경사항 확인
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  변경사항이 있습니다. 커밋하시겠습니까?"
    echo ""
    echo "변경된 파일:"
    git status --short
    echo ""
    read -p "커밋 후 태깅하시겠습니까? (y/N): " confirm
    
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        echo ""
        echo "커밋 중..."
        git add scripts/bin/*coldsync*.sh docs/ops/COLDSYNC_AUTODEPLOY*.md 2>/dev/null || true
        git commit -m "ops: finalize coldsync autodeploy (service/path/timer hardened + docs)" || {
            echo "⚠️  커밋 실패 또는 변경사항 없음"
        }
    fi
fi

echo ""
echo "태그 생성: $TAG_NAME"
git tag -a "$TAG_NAME" -m "$TAG_MESSAGE" || {
    echo "❌ 태그 생성 실패"
    exit 1
}

echo "✅ 태그 생성 완료"
echo ""

echo "태그 정보:"
git show "$TAG_NAME" --no-patch --format="%D%n%n%s%n%n%b" | head -20
echo ""

echo "=== 태깅 완료 ==="
echo ""
echo "📋 태그명: $TAG_NAME"
echo "📋 푸시: git push origin $TAG_NAME"
echo "📋 태그 목록: git tag -l 'coldsync-*'"

