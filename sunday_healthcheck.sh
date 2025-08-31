#!/usr/bin/env bash
set -euo pipefail
ROOT="${ROOT:-/home/duri/DuRiWorkspace}"
exec "${ROOT}/scripts/sunday_healthcheck_optimized.sh" "$@"
