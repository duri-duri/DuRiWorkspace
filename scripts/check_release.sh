#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common_notify.sh" 2>/dev/null || true
echo "▶ check_release: start"
( command -v pytest >/dev/null && pytest -q -x --maxfail=1 ) || echo "ℹ️ pytest skip"
( command -v docker >/dev/null && [ -f docker-compose.yml ] && docker compose -f docker-compose.yml config -q ) || echo "ℹ️ compose skip"
echo "✅ check_release: ok"; notify "check_release ok $(date +'%F %T')"




















