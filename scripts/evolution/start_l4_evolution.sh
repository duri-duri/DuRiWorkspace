#!/usr/bin/env bash
# L4 Evolution 시스템 - Day21 시작 스크립트
# 목적: L3.5 → L4.1 자율 진화 시스템 구축 시작
# Usage: bash scripts/evolution/start_l4_evolution.sh

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

BRANCH="day21-l4-evolution-skeleton"

echo "=== L4 Evolution 시스템 시작 (Day21) ==="
echo ""

# 1. 브랜치 생성
echo "1. 브랜치 생성: $BRANCH"
git switch -c "$BRANCH" 2>/dev/null || git switch "$BRANCH"
echo "✅ 브랜치 전환 완료"
echo ""

# 2. 디렉토리 구조 생성
echo "2. 디렉토리 구조 생성"
mkdir -p var/evolution/{queue,sessions,metrics,artifacts,EV-*}
mkdir -p scripts/evolution/tasks
echo "✅ 디렉토리 구조 생성 완료"
echo ""

# 3. EvolutionSession 테스트
echo "3. EvolutionSession 테스트"
python3 scripts/evolution/evolution_session.py && echo "✅ EvolutionSession 테스트 통과" || echo "⚠️  EvolutionSession 테스트 실패"
echo ""

# 4. Promotion Gate v2 드라이런
echo "4. Promotion Gate v2 드라이런"
python3 scripts/evolution/promotion_gate_v2.py --dryrun --window 24h --gate L4.1 && echo "✅ Gate 드라이런 완료" || echo "⚠️  Gate 드라이런 실패 (메트릭 없음 정상)"
echo ""

# 5. coldsync 검증
echo "5. coldsync 시스템 검증"
bash scripts/bin/verify_coldsync_final.sh && echo "✅ coldsync 검증 통과" || echo "⚠️  coldsync 검증 실패"
echo ""

# 6. 기준선 태깅
echo "6. 기준선 태깅"
bash scripts/bin/tag_coldsync_baseline.sh && echo "✅ 기준선 태깅 완료" || echo "⚠️  기준선 태깅 실패"
echo ""

echo "=== L4 Evolution 시스템 시작 완료 ==="
echo ""
echo "📋 다음 단계:"
echo "  1. systemd 타이머 설정: bash scripts/evolution/setup_l4_timer.sh"
echo "  2. 태스크 큐 설정: bash scripts/evolution/setup_l4_queue.sh"
echo "  3. 첫 태스크 실행: bash scripts/evolution/run_task.sh obs-rule-tune"
echo ""
echo "📋 생성된 파일:"
echo "  - scripts/evolution/promotion_gate_v2.py"
echo "  - scripts/evolution/evolution_session.py"
echo "  - var/evolution/ (디렉토리 구조)"

