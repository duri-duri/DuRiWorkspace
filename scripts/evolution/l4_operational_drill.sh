#!/usr/bin/env bash
# L4.0 운영 관측·가드 (24h 드릴)
# Usage: bash scripts/evolution/l4_operational_drill.sh

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L4.0 운영 관측·가드 (24h 드릴) ==="
echo ""

# 목표 SLO (28일 롤링)
echo "목표 SLO (28일 롤링):"
echo "  - Drift MTTR p95 ≤ 120s"
echo "  - Drift 발생률 ≤ 0.5/day"
echo "  - Human intervention rate = 0"
echo "  - Gate pass rate ≥ 0.98"
echo ""

# 1. 즉시 상태 확인
echo "1. 즉시 상태 확인"
bash scripts/bin/status_coldsync_oneline.sh
echo ""

# 2. 자동 검증 GO/NO-GO
echo "2. 자동 검증 GO/NO-GO"
bash scripts/bin/verify_coldsync_final.sh && echo "✅ GO" || echo "⚠️  NO-GO"
echo ""

# 3. 보안 스냅샷
echo "3. 보안 스냅샷"
bash scripts/bin/snapshot_coldsync_security.sh
echo ""

# 4. 기준선 태깅
echo "4. 기준선 태깅"
bash scripts/bin/tag_coldsync_baseline.sh
echo ""

# 5. SLO 메트릭 수집 (24h)
echo "5. SLO 메트릭 수집 (24h)"
echo "Drift 발생률:"
DRIFT_COUNT=$(sudo journalctl -u coldsync-install.service --since "24 hours ago" --no-pager 2>/dev/null | grep -cE 'INSTALLED|autofix' || echo "0")
echo "  최근 24h: $DRIFT_COUNT 건"

echo "Human intervention:"
INTERVENTION_COUNT=$(sudo journalctl -u coldsync-install.service --since "24 hours ago" --no-pager 2>/dev/null | grep -ciE 'manual|intervention|human' || echo "0")
echo "  최근 24h: $INTERVENTION_COUNT 건"

echo "Gate pass rate:"
# EvolutionSession에서 계산
if python3 -c "import sys; sys.path.insert(0, 'scripts/evolution'); from evolution_session import EvolutionSessionManager; m = EvolutionSessionManager(); sessions = m.list_sessions(limit=100); passed = sum(1 for s in sessions if s.decision == 'PROMOTE' or (s.metrics and s.metrics.get('passed', False))); rate = passed/len(sessions) if sessions else 1.0; print(f'{rate:.2f}')" 2>/dev/null; then
    RATE=$(python3 -c "import sys; sys.path.insert(0, 'scripts/evolution'); from evolution_session import EvolutionSessionManager; m = EvolutionSessionManager(); sessions = m.list_sessions(limit=100); passed = sum(1 for s in sessions if s.decision == 'PROMOTE' or (s.metrics and s.metrics.get('passed', False))); rate = passed/len(sessions) if sessions else 1.0; print(f'{rate:.2f}')" 2>/dev/null | tail -1)
    echo "  최근 100건: $RATE"
else
    echo "  데이터 없음"
fi
echo ""

echo "=== 운영 관측 완료 ==="
echo ""
echo "📋 다음 24h 드릴:"
echo "  bash scripts/evolution/l4_operational_drill.sh"

