#!/usr/bin/env bash
set -euo pipefail
curl -fsS localhost:9109/metrics 2>/dev/null | awk '/^duri_(ab_p_value|last_ev_unixtime|ev_velocity)[^_]/ && !/^#/{print}'
