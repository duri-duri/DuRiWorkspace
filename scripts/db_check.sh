#!/usr/bin/env bash
set -euo pipefail
docker exec -e PGPASSWORD='pgbouncer_pw' duri-postgres psql -U pgbouncer_auth -d postgres -tAc "\l" 2>/dev/null | awk 'NF' | sed -n '1,10p'
