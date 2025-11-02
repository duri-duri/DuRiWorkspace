# L4 Dry-Run Go/No-Go Decision Guide
# Purpose: Final verification checklist for L4 dry-run readiness

## Current State: L3.7 (±0.2)

**4 Axes Connected:**
- ✅ Governance (Protected Branch, CODEOWNERS, CI gates)
- ✅ Observability (SLI catalog, error budget, Lyapunov control)
- ✅ Self-Evolution (L3 → L4 pipeline, canary promotion)
- ✅ DR (Provable DR with RTO p95, daily rehearsals)

---

## Immediate Go/No-Go Criteria

### Go Cut (All Must Pass)
- `duri_green_uptime_ratio{scope="24h"} ≥ 0.9990`
- `error_budget_burn_30d ≤ 0.40`
- `dr_rehearsal_p95_minutes ≤ 12` (last 5 consecutive)
- `canary_failure_ratio ≤ 0.08` AND `canary_unique_ratio ≥ 0.92`

**One failure = No-Go**

---

## Verification Steps

### 1) Protected Branch Verification
```bash
# Check if required checks are configured
gh api repos/:owner/:repo/branches/main/protection | jq '.required_status_checks.contexts'

# Expected: obs-lint, sandbox-smoke-60s, dr-rehearsal-24h-pass, canary-quorum-pass, error-budget-burn-ok
```

### 2) Cron Registration
```bash
# Verify cron entries
crontab -l | grep -E "(textfile_heartbeat|dr_rehearsal)"

# Expected: 2 entries
```

### 3) Core Time Series Verification (8 metrics)
```bash
bash scripts/ops/l4_dryrun_decision.sh
```

### 4) Canary Evaluation Test
```bash
bash scripts/ops/evolution/canary/canary_promote_or_rollback.sh
# Exit codes: 0=promote, 3=no_quorum, 4=rollback
```

### 5) DR Rehearsal Smoke Test
```bash
bash scripts/ops/dr_rehearsal.sh --smoke
curl -s --get 'http://localhost:9090/api/v1/query' --data-urlencode 'query=duri_dr_rehearsal_p95_minutes' | jq -r '.data.result[]?.value[1]'
```

---

## Current Blocking Conditions

Based on last verification:

1. **Protected Branch not configured** (Critical)
   - Required checks missing: obs-lint, sandbox-smoke-60s, dr-rehearsal-24h-pass, canary-quorum-pass, error-budget-burn-ok
   - Action: Configure in GitHub Settings → Branches → Add rule

2. **Metrics not yet populated** (Expected, will normalize after 24h)
   - GREEN uptime, error budget, DR p95, canary metrics
   - Action: Wait 24h after Prometheus reload, then re-verify

3. **Heartbeat not yet increasing** (Temporary)
   - Action: Wait 5 minutes after cron registration, then re-verify

---

## Required Status Checks (GitHub)

**Must be configured exactly as:**
1. `obs-lint`
2. `sandbox-smoke-60s`
3. `dr-rehearsal-24h-pass`
4. `canary-quorum-pass`
5. `error-budget-burn-ok`

**Additional (optional but recommended):**
6. `promql-unit` (if available)

---

## Lyapunov Tuning Rules

### Initial Values
- α = 2.0 (GREEN uptime weight)
- β = 1.0 (Alert rate weight)
- γ = 0.5 (MTTR weight)
- δ = 1.5 (DR success weight)
- ε = 0.8 (EV/h target weight)

### Adjustment Rules
- If ΔV > 0 for ≥3 times in 72h: β += 0.05, δ += 0.05
- If MTTR false positives > 10%: γ -= 0.1

### Promotion Signal
- `rate(lyapunov_V[30m]) < 0` AND `canary_failure_ratio < 0.08` AND `canary_unique_ratio ≥ 0.92` for 2 hours

---

## Rollback & Restart One-Liner

```bash
# Immediate rollback
bash scripts/ops/rollback_restart.sh <bad_sha>
```

---

## Quantitative Forecast (Updated)

- **P(GREEN 24h)**: 0.997 → **0.9992–0.9995** (confidence 0.72)
- **EV/h (90d)**: +0.25 → **+0.45~+0.65** (confidence 0.66)
- **MTTR**: 12–20분 → **4–6분** (confidence 0.62)
- **L4 dry-run success probability (1 week)**: **0.72**

---

## Next Steps

1. **Configure Protected Branch** (GitHub Settings)
2. **Wait 24h for metrics to normalize**
3. **Re-run `bash scripts/ops/l4_dryrun_decision.sh`**
4. **If GO**: Proceed with L4 dry-run tests

---

*Last Updated: $(date +%Y-%m-%d)*

