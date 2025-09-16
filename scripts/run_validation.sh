#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# venv
if [ -f .venv/bin/activate ]; then source .venv/bin/activate; fi

echo "[VALIDATION] pytest..."
pytest -q || { echo ":: pytest failed"; exit 1; }

mkdir -p var/reports
summary=var/reports/validation_summary.md
{
  echo "# Validation Summary"
  echo ""
  date
  echo ""
  echo "## Rollout Status"
  bash -lc "scripts/rollout_ops.sh status" || true
  echo ""
  echo "## Latest Logs"
  bash -lc "for f in \$(ls -1 var/reports/final_verify_*/run.log 2>/dev/null | tail -n 2); do echo '---'; echo \$f; tail -n 50 \$f; done" || true
} > "$summary"

echo "[OK] summary -> $summary"
