#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 tools/league_report.py
echo "DONE Day4: league CSV/MD generated under artifacts_phase1/"
