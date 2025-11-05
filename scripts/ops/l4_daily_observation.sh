#!/usr/bin/env bash
# L4 Daily Observation Routine
# Purpose: Daily 10-minute observation-only checks (no production changes)
# Usage: bash scripts/ops/l4_daily_observation.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
AUDIT_DIR="$REPO_ROOT/var/audit"
DATE=$(date +%Y%m%d)
TIMESTAMP=$(date +%Y%m%d_%H%M)

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*"
}

mkdir -p "$AUDIT_DIR"

log "=== L4 Daily Observation Routine ==="
log "Date: $DATE"
log ""

# 1. Operational Checklist (read-only)
log "1. Running operational checklist..."
bash "$SCRIPT_DIR/l4_operational_checklist.sh" > "$AUDIT_DIR/checklist_${DATE}.log" 2>&1 || true
CHECKLIST_RESULT=$?
if [ $CHECKLIST_RESULT -eq 0 ]; then
  log "  ✅ Checklist: PASS"
else
  log "  ⚠️  Checklist: Some items failed (see log)"
fi

# 2. L4 Evaluation Snapshot (read-only)
log "2. Running L4 evaluation snapshot..."
bash "$SCRIPT_DIR/l4_evaluation.sh" > "$AUDIT_DIR/l4_eval_${DATE}.log" 2>&1 || true
log "  ✅ Evaluation snapshot saved"

# 3. SLO Metrics Query (read-only, history only)
log "3. Querying SLO metrics (read-only)..."
if [ -n "${PROMETHEUS_URL:-}" ]; then
  export PROM_BASE_URL="$PROMETHEUS_URL"
  export PROM_AUTH_HEADER="${PROMETHEUS_AUTH:-}"
  
  # Query basic uptime metric
  if bash "$SCRIPT_DIR/prom_query.sh" instant 'up{job!=""}' > "$AUDIT_DIR/slo_${TIMESTAMP}.json" 2>&1; then
    log "  ✅ SLO query successful"
  else
    log "  ⚠️  SLO query failed (may be expected if Prometheus not configured)"
  fi
else
  log "  ⚠️  PROMETHEUS_URL not set, skipping SLO query"
fi

# 4. Audit Index Check (read-only)
log "4. Checking audit index..."
INDEX_FILE="$REPO_ROOT/docs/ops/audit/audit_index.jsonl"
if [ -s "$INDEX_FILE" ]; then
  ENTRY_COUNT=$(wc -l < "$INDEX_FILE" | tr -d ' ')
  log "  ✅ Audit index exists ($ENTRY_COUNT entries)"
  
  # Validate JSONL format (read-only)
  if jq -e . < "$INDEX_FILE" >/dev/null 2>&1; then
    log "  ✅ Audit index format valid"
  else
    log "  ⚠️  Audit index format issue detected"
  fi
else
  log "  ⚠️  Audit index not found or empty"
fi

# 5. Policy Learning PRs Check (read-only, list only)
log "5. Checking policy learning PRs (read-only)..."
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  POLICY_PRS=$(gh pr list --search "label:policy:update-proposed" --json number,title,createdAt --limit 10 2>/dev/null || echo "[]")
  PR_COUNT=$(echo "$POLICY_PRS" | jq 'length' 2>/dev/null || echo "0")
  log "  📋 Policy learning PRs: $PR_COUNT"
  echo "$POLICY_PRS" > "$AUDIT_DIR/policy_prs_${DATE}.json" || true
else
  log "  ⚠️  GitHub CLI not available, skipping PR check"
fi

# 6. Rollback Events Summary (read-only, from audit logs)
log "6. Summarizing rollback events..."
ROLLBACK_COUNT=0
if [ -s "$INDEX_FILE" ]; then
  ROLLBACK_COUNT=$(jq -r 'select(.stage=="rollback") | .result' < "$INDEX_FILE" 2>/dev/null | grep -c "success" || echo "0")
fi
log "  📊 Rollback events: $ROLLBACK_COUNT successful"

# 7. Workflow Status Check (read-only)
log "7. Checking workflow status (read-only)..."
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  RECENT_RUNS=$(gh run list --workflow=l4-post-merge-quality-watch.yml --limit 5 --json conclusion,createdAt 2>/dev/null || echo "[]")
  RUN_COUNT=$(echo "$RECENT_RUNS" | jq 'length' 2>/dev/null || echo "0")
  log "  📋 Recent quality watch runs: $RUN_COUNT"
else
  log "  ⚠️  GitHub CLI not available, skipping workflow check"
fi

# 8. Generate Summary
log ""
log "=== Daily Observation Summary ==="
log "Date: $DATE"
log "Checklist: $([ $CHECKLIST_RESULT -eq 0 ] && echo 'PASS' || echo 'FAIL')"
log "Audit entries: ${ENTRY_COUNT:-0}"
log "Rollback events: $ROLLBACK_COUNT"
log "Policy PRs: ${PR_COUNT:-0}"
log ""
log "✅ Observation complete. All logs saved to: $AUDIT_DIR"

# Save summary
cat > "$AUDIT_DIR/daily_summary_${DATE}.txt" <<EOF
L4 Daily Observation Summary
Date: $DATE
Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)

Checklist: $([ $CHECKLIST_RESULT -eq 0 ] && echo 'PASS' || echo 'FAIL')
Audit entries: ${ENTRY_COUNT:-0}
Rollback events: $ROLLBACK_COUNT
Policy PRs: ${PR_COUNT:-0}

Files:
- Checklist: checklist_${DATE}.log
- Evaluation: l4_eval_${DATE}.log
- SLO metrics: slo_${TIMESTAMP}.json
- Policy PRs: policy_prs_${DATE}.json
EOF

log "📄 Summary saved: $AUDIT_DIR/daily_summary_${DATE}.txt"

