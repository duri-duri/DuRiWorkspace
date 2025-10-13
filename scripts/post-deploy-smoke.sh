#!/usr/bin/env bash
set -euo pipefail
retry() { local n=0; local max=${2:-3}; until "$1"; do n=$((n+1)); [ $n -ge $max ] && return 1; sleep 2; done; }
echo "[SMOKE] promtool version"; retry "promtool --version" 3 || { echo "promtool not found"; exit 1; }
echo "[SMOKE] basic reachability checks (placeholder)"; exit 0
