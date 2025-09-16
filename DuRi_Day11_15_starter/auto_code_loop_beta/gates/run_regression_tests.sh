#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${SCRIPT_DIR}/../logs/test_result.json"
mkdir -p "$(dirname "$OUT")"
cat > "$OUT" <<'JSON'
{
  "pass_rate": 0.83,
  "failures": [
    {"task": "qa_fact_01", "type": "Validation", "msg": "mismatch on entity"},
    {"task": "tool_latency_02", "type": "System", "msg": "timeout p95"}
  ]
}
JSON
echo "Wrote $OUT"
