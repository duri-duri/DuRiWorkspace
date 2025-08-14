#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==[1/3] 사전 게이트 점검=="
python3 tools/canary_check.py
python3 tools/drift_check.py
pytest -q tests/test_data_guard.py tests/test_split_lock.py
pytest -q tests/test_drift_guard.py -k ok_when_default_thresholds
echo "✅ preflight OK"

echo "==[2/3] 자가-진화 스윕 시작=="
python3 auto_evolve_guarded.py

echo "==[3/3] 리그 테이블 헤드(최근 5개)=="
tail -n 5 artifacts_phase1/league.jsonl || true
echo "DONE Day3"



