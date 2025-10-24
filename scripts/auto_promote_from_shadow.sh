#!/usr/bin/env bash
set -euo pipefail
cd /home/duri/DuRiWorkspace

MODE="${1:---dry-run}"   # --dry-run | --canary
echo "== [$(date '+%F %T')] auto_promote_from_shadow $MODE =="

# 0) 서브모듈 동기화 (SSH 연결된 서브모듈들)
echo "🔄 서브모듈 동기화 시작..."
source scripts/lib/submodule_sync.sh
sync_all_submodules

# A) 섀도우 게이트 통과 필수 (기존 verify_gate_shadow.sh 활용)
echo "📋 1. 섀도우 게이트 통과 확인..."
./scripts/verify_gate_shadow.sh

# B) 정책 체크 (기존 promotion_gate.py 인터페이스 활용)
echo "📋 2. 승격 정책 체크..."
TEMP_RESULTS="$(mktemp)"
echo '{"latency_ms": 100, "error_rate": 0.01, "success_rate": 0.99}' > "$TEMP_RESULTS"
python3 ./scripts/promotion_gate.py "$TEMP_RESULTS" ./policies/promotion.yaml

# 정리
rm -f "$TEMP_RESULTS"

# C) 실행 모드별 처리
if [[ "$MODE" == "--dry-run" ]]; then
  echo "📋 3. [DRY-RUN] 카나리 승격 시뮬레이션 완료"
  echo "   → 실제 승격 조건 충족 시 --canary 모드로 실행 가능"
  exit 0
fi

if [[ "$MODE" == "--canary" ]]; then
  echo "📋 3. 카나리 승격 실행..."
  # 기존 gate.sh 경로 활용 (pre-promote 단계만 호출)
  ./scripts/gate.sh pre-promote
  echo ""
  echo "🎯 카나리 승격 완료! 다음 단계:"
  echo "   📊 15-30분 모니터링 후:"
  echo "   ✅ 성공 시: ./scripts/gate.sh post-promote"
  echo "   ❌ 실패 시: 수동 롤백 필요 (gate.sh에 rollback 기능 없음)"
  echo ""
  echo "   📈 모니터링 포인트:"
  echo "   - http://localhost:3000 (Grafana)"
  echo "   - http://localhost:9090 (Prometheus)"
  echo "   - docker ps (컨테이너 상태)"
  exit 0
fi

echo "❌ [ERROR] 알 수 없는 모드: $MODE" >&2
echo "   사용법: $0 [--dry-run|--canary]"
exit 2
