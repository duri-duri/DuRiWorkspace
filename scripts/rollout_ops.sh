#!/usr/bin/env bash
set -Eeuo pipefail
# 운영 전환 모니터링 스크립트 (기존 backup_ops.sh 패턴 활용)

CMD="${1:-help}"; shift || true

case "$CMD" in
  start-25)
    echo "[ROLLOUT] 25% 전환 시작"
    export DURI_UNIFIED_REASONING_ROLLOUT=25
    export DURI_UNIFIED_REASONING_MODE=auto
    source env/dev_env.sh
    scripts/bench_compare.sh && scripts/final_verify.sh
    echo "[OK] 25% 전환 완료"
    ;;
  start-50)
    echo "[ROLLOUT] 50% 전환 시작"
    export DURI_UNIFIED_REASONING_ROLLOUT=50
    export DURI_UNIFIED_REASONING_MODE=auto
    source env/dev_env.sh
    scripts/bench_compare.sh && scripts/final_verify.sh
    echo "[OK] 50% 전환 완료"
    ;;
  start-100)
    echo "[ROLLOUT] 100% 전환 시작"
    export DURI_UNIFIED_REASONING_ROLLOUT=100
    export DURI_UNIFIED_REASONING_MODE=auto
    source env/dev_env.sh
    scripts/bench_compare.sh && scripts/final_verify.sh
    echo "[OK] 100% 전환 완료"
    ;;
  rollback)
    echo "[ROLLBACK] 즉시 롤백 실행"
    scripts/rollback_unified_reasoning.sh
    source env/dev_env.sh
    scripts/bench_compare.sh && scripts/final_verify.sh
    echo "[OK] 롤백 완료"
    ;;
  status)
    echo "[STATUS] 현재 전환 상태"
    echo "ROLLOUT: ${DURI_UNIFIED_REASONING_ROLLOUT:-0}%"
    echo "MODE: ${DURI_UNIFIED_REASONING_MODE:-auto}"
    echo ""
    echo "최근 벤치 결과:"
    tail -n 20 "$(cat var/reports/LAST_BENCH_DIR 2>/dev/null)/bench_compare.log" 2>/dev/null || echo "벤치 결과 없음"
    ;;
  monitor)
    echo "[MONITOR] 실시간 모니터링 시작 (Ctrl+C로 중단)"
    while true; do
      echo "[$(date '+%H:%M:%S')] 상태 체크"
      pytest -q tests/contracts -k "reasoning" >/dev/null 2>&1 && echo "  ✅ 계약 테스트 통과" || echo "  ❌ 계약 테스트 실패"
      pytest -q tests/contracts_unified -k "unified or rollout" >/dev/null 2>&1 && echo "  ✅ 통합 테스트 통과" || echo "  ❌ 통합 테스트 실패"
      sleep 30
    done
    ;;
  help|*)
    echo "Usage: scripts/rollout_ops.sh {start-25|start-50|start-100|rollback|status|monitor}"
    echo ""
    echo "Commands:"
    echo "  start-25   - 25% 전환 실행"
    echo "  start-50   - 50% 전환 실행"
    echo "  start-100  - 100% 전환 실행"
    echo "  rollback   - 즉시 롤백"
    echo "  status     - 현재 상태 확인"
    echo "  monitor    - 실시간 모니터링"
    ;;
esac
