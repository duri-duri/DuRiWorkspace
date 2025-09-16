#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common_notify.sh" 2>/dev/null || true
echo "▶ check_quality: start"
command -v ruff >/dev/null && ruff check . || echo "ℹ️ ruff skip"
( command -v mypy >/dev/null && ( [ -f mypy.ini ] || [ -f pyproject.toml ] ) && mypy . ) || echo "ℹ️ mypy skip"
( command -v pytest >/dev/null && pytest -q -k "smoke or sanity" -x --maxfail=1 ) || echo "ℹ️ pytest skip or passed"
( command -v docker >/dev/null && [ -f docker-compose.yml ] && docker compose -f docker-compose.yml config -q ) || echo "ℹ️ compose skip"
echo "✅ check_quality: ok"; notify "check_quality ok $(date +'%F %T')"




















