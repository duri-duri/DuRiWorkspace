#!/bin/bash
set -Eeuo pipefail
# D02 마무리 "재개(RESUME)" 스크립트
# 이틀 후 D03 시작용

set -e

echo "🔧 D02 마무리 재개 스크립트 시작..."

# 0) 브랜치/상태 확인
echo "📋 현재 브랜치/상태 확인"
git rev-parse --abbrev-ref HEAD
git status

# 1) 회귀 테스트 커밋 (요약에 나온 미스테이징 처리)
echo "🧪 회귀 테스트 커밋"
git add tests/test_phase11_regression.py
git commit -m "test(phase11): 회귀 테스트 추가 + D02 안정화 완료"

# 2) PR 업데이트 + 라벨(automerge 기본)
echo "📤 PR 업데이트 + 라벨 추가"
./scripts/pr-open.sh
PR=$(gh pr view --json number -q .number)
gh pr edit "$PR" --add-label automerge 2>/dev/null || true
gh pr edit "$PR" --add-label "phase:P11" 2>/dev/null || true

# 3) 로컬 테스트 확인
echo "✅ 로컬 테스트 확인"
python3 -m pytest tests/test_phase11_*.py -q

# 4) CI 체크 관찰
echo "👀 CI 체크 관찰 시작..."
gh pr checks --watch "$PR"

echo "🎉 D02 마무리 완료! D03으로 진행 가능합니다."

