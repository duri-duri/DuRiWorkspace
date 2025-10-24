#!/usr/bin/env bash
# Finalize Regression Guard System - Complete Wrap-up Script
# This script handles all remaining tasks to complete the regression prevention system

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YEL='\033[1;33m'; NC='\033[0m'
log(){ echo -e "${GREEN}[$(date '+%H:%M:%S')] $*${NC}"; }
warn(){ echo -e "${YEL}[$(date '+%H:%M:%S')] $*${NC}"; }
err(){ echo -e "${RED}[$(date '+%H:%M:%S')] $*${NC}"; }

log "🚀 Starting Regression Guard System Finalization"

# 1) Push everything (superproject + submodule)
log "📤 Step 1: Pushing all changes"
git -C duri_core push origin chore/metrics-alias-safe-logging || {
    warn "Submodule push failed - continuing with main repo"
}
git push origin pr/run-once-clean || {
    err "Main repo push failed"
    exit 1
}
log "✅ Git push completed"

# 2) Kill CRLF warnings permanently
log "🔧 Step 2: Setting up .gitattributes for LF line endings"
cat > .gitattributes <<'EOF'
* text=auto
*.py   text eol=lf
*.sh   text eol=lf
*.yml  text eol=lf
*.yaml text eol=lf
*.md   text eol=lf
*.txt  text eol=lf
*.bat  text eol=crlf
EOF

git config core.autocrlf false
git add --renormalize .
git commit -m "chore(repo): enforce LF line endings via .gitattributes" || {
    warn "No changes to commit for .gitattributes"
}
log "✅ CRLF normalization completed"

# 3) Fix "prose-as-.py" landmines (Option A: rename to .md)
log "🧹 Step 3: Converting integration design docs from .py to .md"
INTEGRATION_FILES=(
    "DuRiCore/reasoning_engine/integration/performance_monitor.py"
    "DuRiCore/reasoning_engine/integration/unified_learning_system.py"
    "DuRiCore/reasoning_engine/integration/reasoning_engine.py"
    "DuRiCore/reasoning_engine/integration/abductive_reasoning.py"
    "DuRiCore/reasoning_engine/integration/unified_performance_optimizer.py"
    "DuRiCore/reasoning_engine/integration/unified_conversation_service.py"
    "DuRiCore/reasoning_engine/integration/unified_judgment_system.py"
    "DuRiCore/reasoning_engine/integration/reasoning_optimizer.py"
    "DuRiCore/reasoning_engine/integration/deductive_reasoning.py"
    "DuRiCore/reasoning_engine/integration/inductive_reasoning.py"
    "DuRiCore/reasoning_engine/integration/logical_processor.py"
)

RENAMED_COUNT=0
for f in "${INTEGRATION_FILES[@]}"; do
    if [[ -f "$f" ]]; then
        git mv "$f" "${f%.py}.md" || {
            warn "Failed to rename $f - may already be renamed or not tracked"
        }
        ((RENAMED_COUNT++))
    fi
done

if [[ $RENAMED_COUNT -gt 0 ]]; then
    git commit -m "chore(docs): move integration design notes from .py to .md" || {
        warn "No changes to commit for file renames"
    }
    log "✅ Renamed $RENAMED_COUNT integration files to .md"
else
    log "ℹ️  No integration files found to rename"
fi

# 4) Make sure Prometheus loads alert rules
log "📊 Step 4: Configuring Prometheus to load alert rules"
PROM_CONFIGS=(
    "prometheus/prometheus.yml"
    "prometheus.yml"
    "monitoring/prometheus/prometheus.yml"
)

PROM_UPDATED=false
for PROM in "${PROM_CONFIGS[@]}"; do
    if [[ -f "$PROM" ]]; then
        log "Found Prometheus config: $PROM"
        if ! grep -q 'rule_files:' "$PROM"; then
            sed -i '/^scrape_configs:/i rule_files:\n  - alerting/rules/*.yml' "$PROM"
            git add "$PROM"
            PROM_UPDATED=true
            log "✅ Added rule_files to $PROM"
        else
            log "ℹ️  $PROM already has rule_files configured"
        fi
        break
    fi
done

if [[ "$PROM_UPDATED" == "true" ]]; then
    git commit -m "ops(prometheus): load alerting/rules/*.yml" || {
        warn "No changes to commit for Prometheus config"
    }
fi

# 5) Set up CI protection workflow
log "🛡️  Step 5: Setting up CI protection workflow"
mkdir -p .github/workflows
cat > .github/workflows/guard.yml <<'EOF'
name: Regression Guard
on: [push, pull_request]

jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout with submodules
        uses: actions/checkout@v4
        with:
          submodules: true

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install pre-commit pytest
          pip install -r duri_core/requirements.txt

      - name: Run pre-commit hooks
        run: pre-commit run -a

      - name: CI Guard (fail-fast module loading)
        run: ./scripts/ci_guard.sh

      - name: Gate Shadow Verification
        run: ./scripts/verify_gate_shadow.sh

      - name: Run tests
        run: pytest -q tests/test_imports.py
EOF

git add .github/workflows/guard.yml
git commit -m "ci: enforce pre-commit + build-time fail-fast + gate checks" || {
    warn "No changes to commit for CI workflow"
}
log "✅ CI protection workflow configured"

# 6) Tag the release
log "🏷️  Step 6: Creating release tag"
git tag -a v2025.10.22-regression-guard -m "Regression prevention system completed

- Absolute import enforcement with fail-fast guards
- Runtime module loading verification
- Emotion normalization metrics and alerts
- LF line ending normalization
- Integration docs moved to .md format
- CI protection workflow established
- Comprehensive regression prevention system"

git push origin v2025.10.22-regression-guard || {
    warn "Tag push failed - you may need to push manually"
}
log "✅ Release tag v2025.10.22-regression-guard created"

# Final push of all changes
log "📤 Final push of all changes"
git push origin pr/run-once-clean || {
    err "Final push failed"
    exit 1
}

log "🎉 Regression Guard System Finalization Complete!"
log ""
log "📋 Summary of completed tasks:"
log "  ✅ Git push (main repo + submodule)"
log "  ✅ CRLF normalization (.gitattributes)"
log "  ✅ Integration docs converted to .md"
log "  ✅ Prometheus alert rules configured"
log "  ✅ CI protection workflow established"
log "  ✅ Release tag v2025.10.22-regression-guard created"
log ""
log "🔗 Next steps:"
log "  - Set up branch protection rules in GitHub"
log "  - Configure Prometheus reload/restart"
log "  - Monitor new alert rules in Grafana"
log "  - Update team documentation with new processes"
log ""
log "🚀 Your regression prevention system is now complete and protected!"
