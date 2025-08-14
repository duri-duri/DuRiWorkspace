#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== Preflight (canary → drift → pytest) =="
python3 tools/canary_check.py
python3 tools/drift_check.py
pytest -q tests/test_data_guard.py tests/test_split_lock.py

echo "== Promote current best to prod_artifacts =="
python3 tools/promote_and_freeze.py

echo "== Optional: schedule daily guarded evolve (commented) =="
# (crontab -l 2>/dev/null; echo "45 3 * * * cd $ROOT && python3 auto_evolve_guarded.py >> artifacts_phase1/auto_evolve.log 2>&1") | crontab -
# echo "cron installed: 03:45 daily auto-evolve"

echo "DONE Day5."
