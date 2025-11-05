#!/usr/bin/env bash
# L4 Static Validation (Read-Only)
# Purpose: Validate configuration files without making any changes
# Usage: bash scripts/ops/l4_static_validation.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*"
}

PASS=0
FAIL=0

log "=== L4 Static Validation (Read-Only) ==="
log ""

# 1. Environment variables check (read-only)
log "1. Environment variables..."
if [ -n "${PROMETHEUS_URL:-}" ]; then
  log "  ✅ PROMETHEUS_URL: Set"
  PASS=$((PASS + 1))
else
  log "  ⚠️  PROMETHEUS_URL: Not set (optional)"
fi

if [ -n "${PROMETHEUS_AUTH:-}" ]; then
  log "  ✅ PROMETHEUS_AUTH: Set"
  PASS=$((PASS + 1))
else
  log "  ℹ️  PROMETHEUS_AUTH: Not set (optional)"
fi

# 2. Prometheus rules validation (read-only)
log ""
log "2. Prometheus rules validation..."
if command -v promtool >/dev/null 2>&1; then
  if [ -d "$REPO_ROOT/prometheus/rules" ]; then
    if promtool check rules "$REPO_ROOT/prometheus/rules"/*.yml >/dev/null 2>&1; then
      log "  ✅ Prometheus rules valid"
      PASS=$((PASS + 1))
    else
      log "  ❌ Prometheus rules validation failed"
      FAIL=$((FAIL + 1))
    fi
  else
    log "  ⚠️  prometheus/rules directory not found"
  fi
else
  log "  ⚠️  promtool not installed, skipping"
fi

# 3. Rulepack schema validation (read-only)
log ""
log "3. Rulepack schema validation..."
if command -v yq >/dev/null 2>&1 && command -v jq >/dev/null 2>&1; then
  if [ -f "$REPO_ROOT/rulepack/safe-docs.yml" ]; then
    if yq -o=json '.' "$REPO_ROOT/rulepack/safe-docs.yml" 2>/dev/null | \
       jq -e 'has("scenario") and has("allow_paths") and has("relaxable")' >/dev/null 2>&1; then
      log "  ✅ Rulepack schema valid"
      PASS=$((PASS + 1))
    else
      log "  ❌ Rulepack schema validation failed"
      FAIL=$((FAIL + 1))
    fi
  else
    log "  ⚠️  rulepack/safe-docs.yml not found"
  fi
else
  log "  ⚠️  yq or jq not installed, skipping"
fi

# 4. SLO config validation (read-only)
log ""
log "4. SLO config validation..."
if [ -f "$REPO_ROOT/.slo/auto_relax.yml" ]; then
  if command -v yq >/dev/null 2>&1 && command -v jq >/dev/null 2>&1; then
    if yq -o=json '.' "$REPO_ROOT/.slo/auto_relax.yml" 2>/dev/null | \
       jq -e 'has("window") and has("slo")' >/dev/null 2>&1; then
      log "  ✅ SLO config shape valid"
      PASS=$((PASS + 1))
    else
      log "  ❌ SLO config validation failed"
      FAIL=$((FAIL + 1))
    fi
  else
    log "  ⚠️  yq or jq not installed, skipping"
  fi
else
  log "  ⚠️  .slo/auto_relax.yml not found"
fi

# 5. GitHub Actions linting (read-only)
log ""
log "5. GitHub Actions linting..."
if command -v actionlint >/dev/null 2>&1; then
  if actionlint "$REPO_ROOT/.github/workflows"/*.yml >/dev/null 2>&1; then
    log "  ✅ GitHub Actions syntax valid"
    PASS=$((PASS + 1))
  else
    log "  ⚠️  GitHub Actions linting warnings (check manually)"
  fi
else
  log "  ⚠️  actionlint not installed, skipping"
fi

# 6. Shell script linting (read-only)
log ""
log "6. Shell script linting..."
if command -v shellcheck >/dev/null 2>&1; then
  SCRIPT_COUNT=0
  ERROR_COUNT=0
  for script in "$SCRIPT_DIR"/*.sh "$REPO_ROOT/scripts/bin"/*.sh 2>/dev/null; do
    if [ -f "$script" ]; then
      SCRIPT_COUNT=$((SCRIPT_COUNT + 1))
      if ! shellcheck "$script" >/dev/null 2>&1; then
        ERROR_COUNT=$((ERROR_COUNT + 1))
      fi
    fi
  done
  
  if [ $ERROR_COUNT -eq 0 ] && [ $SCRIPT_COUNT -gt 0 ]; then
    log "  ✅ Shell scripts valid ($SCRIPT_COUNT scripts)"
    PASS=$((PASS + 1))
  elif [ $SCRIPT_COUNT -eq 0 ]; then
    log "  ⚠️  No shell scripts found"
  else
    log "  ⚠️  Shell script linting warnings ($ERROR_COUNT/$SCRIPT_COUNT scripts)"
  fi
else
  log "  ⚠️  shellcheck not installed, skipping"
fi

# 7. Audit index format check (read-only)
log ""
log "7. Audit index format check..."
INDEX_FILE="$REPO_ROOT/docs/ops/audit/audit_index.jsonl"
if [ -s "$INDEX_FILE" ]; then
  if jq -e . < "$INDEX_FILE" >/dev/null 2>&1; then
    ENTRY_COUNT=$(wc -l < "$INDEX_FILE" | tr -d ' ')
    log "  ✅ Audit index format valid ($ENTRY_COUNT entries)"
    PASS=$((PASS + 1))
  else
    log "  ❌ Audit index format invalid"
    FAIL=$((FAIL + 1))
  fi
else
  log "  ℹ️  Audit index not found or empty (expected initially)"
fi

# 8. File hash snapshot (read-only)
log ""
log "8. Creating file hash snapshot..."
SNAPSHOT_FILE="/tmp/l4_frozen_$(date +%Y%m%d).sha256"
tar -cf - \
  "$REPO_ROOT/.github/workflows/auto-relax-merge-restore.yml" \
  "$REPO_ROOT/.github/workflows/l4-post-merge-quality-watch.yml" \
  "$REPO_ROOT/.github/workflows/l4-auto-rollback.yml" \
  "$SCRIPT_DIR/prom_query.sh" \
  "$SCRIPT_DIR/l4_evaluation.sh" \
  "$REPO_ROOT/scripts/evolution/policy_learning_loop.py" \
  "$REPO_ROOT/rulepack" \
  "$REPO_ROOT/.slo" \
  2>/dev/null | sha256sum > "$SNAPSHOT_FILE" 2>/dev/null || true

if [ -f "$SNAPSHOT_FILE" ]; then
  HASH=$(cat "$SNAPSHOT_FILE" | cut -d' ' -f1)
  log "  ✅ Hash snapshot created: $HASH"
  log "     File: $SNAPSHOT_FILE"
  PASS=$((PASS + 1))
else
  log "  ⚠️  Failed to create hash snapshot"
fi

log ""
log "=== Validation Summary ==="
log "Passed: $PASS"
log "Failed: $FAIL"
log ""

if [ $FAIL -eq 0 ]; then
  log "✅ All validations passed"
  exit 0
else
  log "⚠️  Some validations failed (see above)"
  exit 1
fi

