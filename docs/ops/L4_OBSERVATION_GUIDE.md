# L4 Observation Period Guide
# Purpose: Guide for observation-only period (no production changes)

## Overview

After achieving L4 compliance (single scenario), we enter a **7-day observation period** to validate operational value through metrics, not code changes.

## Daily Routine (10 minutes)

### Automated Script

```bash
bash scripts/ops/l4_daily_observation.sh
```

This script performs:
1. ✅ Operational checklist (read-only)
2. ✅ L4 evaluation snapshot
3. ✅ SLO metrics query (read-only)
4. ✅ Audit index check
5. ✅ Policy learning PRs check (read-only)
6. ✅ Rollback events summary
7. ✅ Workflow status check (read-only)

All results saved to `var/audit/` directory.

### Manual Tasks

1. **Review Rollback Events** (if any)
   - Open `var/audit/rollback_label.tsv`
   - Label each rollback as TP (True Positive) or FP (False Positive)
   - Format: `DATE\tPR_NUMBER\tLABEL\tNOTES`

2. **Check Policy Learning PRs**
   - Review PRs created by `policy-learning-loop.yml`
   - Note: Do NOT merge/close (observation only)

## Weekly Summary (Day 7)

### Automated Calculation

```bash
bash scripts/ops/l4_weekly_summary.sh [end_date]
```

This calculates:
- **R_SLO**: SLO pass rate (target: ≥99.0%)
- **FP_RB**: False positive rate (target: ≤1.0%)
- **MTTD p95**: Mean time to detect (target: ≤3min)
- **MTTR p95**: Mean time to recover (target: ≤10min)
- **U_POLICY**: Policy effectiveness (target: 1.0)

**Promotion Score Formula:**
```
PromotionScore = 0.35*R_SLO + 0.25*(1-FP_RB) + 0.20*MTTD^-1 + 0.15*MTTR^-1 + 0.05*U_POLICY
```

**Verdict:**
- Score ≥ 0.92: ✅ Global L4 operation approved
- Score ≥ 0.85: ⚠️ Continue observation
- Score < 0.85: ❌ Review and adjust

## Static Validation (Optional, Daily)

```bash
bash scripts/ops/l4_static_validation.sh
```

Validates:
- Environment variables
- Prometheus rules
- Rulepack schema
- SLO config
- GitHub Actions syntax
- Shell script linting
- Audit index format
- File hash snapshot

## Key Principles

1. **NO PRODUCTION CHANGES**: All operations are read-only/dry-run
2. **OBSERVE ONLY**: Collect data, don't modify thresholds
3. **DOCUMENT EVERYTHING**: All observations saved to `var/audit/`
4. **WAIT FOR DATA**: Don't adjust thresholds until ≥2-3 events observed

## Expected Outcomes

After 7 days:
- **SLO Pass Rate ≥ 99%**: Probability p≈0.85-0.9
- **False Positive Rate ≤ 1%**: Probability p≈0.7-0.8
- **Promotion Score ≥ 0.92**: Probability p≈0.6-0.75

If all metrics pass → **"Global L4 operation approved"**

## Files Generated

- `var/audit/daily_summary_YYYYMMDD.txt`: Daily summary
- `var/audit/l4_eval_YYYYMMDD.log`: Evaluation snapshot
- `var/audit/slo_YYYYMMDD_HHMM.json`: SLO metrics
- `var/audit/weekly_summary_YYYYMMDD.json`: Weekly calculation
- `var/audit/rollback_label.tsv`: Manual rollback labeling (create if needed)

## Next Steps After 7 Days

1. Review weekly summary
2. Calculate promotion score
3. If score ≥ 0.92: Declare global L4 operation
4. If score < 0.92: Review thresholds and adjust (one small step)

