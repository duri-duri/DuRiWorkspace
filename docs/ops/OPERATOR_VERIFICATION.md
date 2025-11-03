# Operator Immediate Verification Commands
# Purpose: Copy-paste commands for immediate verification

## Cron Registration

```bash
# Textfile heartbeat (every 5 minutes)
(crontab -l 2>/dev/null | grep -v "textfile_heartbeat"; echo "*/5 * * * *  bash $HOME/DuRiWorkspace/scripts/ops/textfile_heartbeat.sh") | crontab -

# DR rehearsal (daily at 02:00)
(crontab -l 2>/dev/null | grep -v "dr_rehearsal"; echo "0  2 * * *  bash $HOME/DuRiWorkspace/scripts/ops/dr_rehearsal.sh success") | crontab -
```

## Prometheus Reload

```bash
curl -s -X POST http://localhost:9090/-/reload | xargs -r echo
```

## Core Time Series Verification (8 metrics)

```bash
for q in \
 'duri_green_uptime_ratio' \
 'duri_dr_success_ratio_7d' \
 'duri_dr_rto_seconds_p95_7d' \
 'duri_error_budget_burn_short' \
 'duri_error_budget_burn_long' \
 'duri_lyapunov_v' \
 'duri_p_uniform_ks_p{window="2h"}' \
 'duri_p_unique_ratio{window="2h"}'
do
  printf "[%s] " "$q"
  curl -s --data-urlencode "query=$q" http://localhost:9090/api/v1/query | jq -r '.status, (.data.result|length)'
done
```

**Pass Criteria**: `status=success` and most `len≥1` (DR p95 normalizes after 24h)

## DR Test Mode

```bash
# Generate success case metrics
bash scripts/ops/dr_rehearsal.sh success

# Generate fail case metrics
bash scripts/ops/dr_rehearsal.sh fail
```

## Canary Evaluation Test

```bash
# Check canary health
bash scripts/ops/evolution/canary/canary_promote_or_rollback.sh

# Exit codes:
# 0 = PROMOTE
# 3 = NO_QUORUM (wait)
# 4 = ROLLBACK
```

## Protected Branch Test

```bash
# Should be rejected (no PR, no approvals)
git push origin main

# Should work (with PR + approvals)
gh pr create --title "Test" --body "Test" --base main
```

