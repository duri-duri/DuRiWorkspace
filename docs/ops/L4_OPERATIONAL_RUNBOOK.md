# L4 Operational Runbook
# Purpose: Step-by-step guide for L4 operational readiness and verification

## Prerequisites

1. **Secrets Setup**
   - GitHub → Settings → Secrets and variables → Actions
   - Add `PROMETHEUS_URL` (e.g., `https://prom.example.com/api/v1`)
   - Add `PROMETHEUS_AUTH` (optional, e.g., `Bearer <token>`)

2. **SLO Configuration**
   - Edit `.slo/auto_relax.yml`
   - Update metric names (job, service, labels) to match your Prometheus setup
   - Adjust thresholds based on your SLO targets

## Immediate Verification (10 minutes)

### Step 1: Run Operational Checklist

```bash
bash scripts/ops/l4_operational_checklist.sh
```

Expected: All checks pass (10/10)

### Step 2: Test Prometheus Connection

```bash
export PROM_BASE_URL="https://your-prometheus/api/v1"
export PROM_AUTH_HEADER="Bearer your-token"  # if needed

# Test instant query
bash scripts/ops/prom_query.sh instant 'up{job="your-job"}'

# Test range query
bash scripts/ops/prom_query.sh range 'up{job="your-job"}' "$(date -d '1 hour ago' +%s)" "$(date +%s)" "30s"
```

Expected: Valid JSON response

### Step 3: Dry-Run Rollback Test

```bash
# Create a test merge commit
git checkout -b test-merge
git commit --allow-empty -m "test merge"
git checkout main
git merge test-merge --no-ff -m "test merge commit"

# Get merge commit SHA
MERGE_SHA=$(git rev-parse HEAD)

# Dry-run rollback
gh workflow run l4-auto-rollback.yml \
  -f pr=1 \
  -f merge_sha="$MERGE_SHA" \
  -f reason="dry-run test" \
  -f dry_run=true
```

Expected: Revert PR created but not auto-merged

### Step 4: Test Fork PR Blocking

```bash
# Create a fork PR (or simulate)
# The workflow should immediately reject it
```

Expected: `isCrossRepository == true` → workflow fails

### Step 5: Test Policy Learning Loop

```bash
# Create sample audit entries
mkdir -p docs/ops/audit
cat > docs/ops/audit/test.json <<EOF
{
  "ts": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "stage": "gate",
  "result": "fail",
  "reason": "forbidden_path",
  "ctx": {"pr": 999, "sha": "test", "workflow": "test"}
}
EOF

# Run policy learning loop
python3 scripts/evolution/policy_learning_loop.py
```

Expected: Policy update PR created (if threshold met)

## Production Test Scenarios

### Scenario A: Successful Merge → SLO Pass

1. Create PR with only `docs/` changes
2. Add labels: `change:safe`, `auto-relax-merge`
3. Ensure all checks pass
4. Auto-merge should succeed
5. Post-merge watch should pass (no violations)

### Scenario B: SLO Violation → Auto-Rollback

1. Create PR with changes
2. Merge with labels
3. Inject test metrics to trigger SLO violation:
   - Increase latency above threshold
   - Increase error rate above threshold
4. Post-merge watch should detect violation
5. Auto-rollback workflow should trigger
6. Revert PR should be created and auto-merged

### Scenario C: Race Condition Test

1. Create 2 PRs simultaneously
2. Both trigger auto-relax-merge-restore
3. Concurrency group should ensure only one runs
4. Other should be queued/cancelled

## Monitoring

### Key Metrics to Watch

1. **SLO Compliance Rate**
   - Query: `rate(slo_violations_total[24h])`
   - Target: < 1% violation rate

2. **Rollback Success Rate**
   - Query: `rate(rollback_success_total[24h]) / rate(rollback_attempts_total[24h])`
   - Target: > 95%

3. **Policy Learning Effectiveness**
   - Monitor policy update PR acceptance rate
   - Target: > 80% acceptance

### Audit Log Monitoring

```bash
# View recent audit entries
tail -20 docs/ops/audit/audit_index.jsonl | jq .

# Count failures by stage
cat docs/ops/audit/audit_index.jsonl | jq -r '.stage' | sort | uniq -c

# Analyze failure reasons
cat docs/ops/audit/audit_index.jsonl | jq -r '.reason' | sort | uniq -c
```

## Troubleshooting

### Prometheus Connection Failures

- Check `PROMETHEUS_URL` secret
- Verify network connectivity
- Check authentication token

### SLO Violations Not Detected

- Verify metric names match Prometheus
- Check thresholds in `.slo/auto_relax.yml`
- Verify query syntax

### Rollback Failures

- Check merge commit SHA validity
- Verify branch protection settings
- Check rollback PR creation logs

### Policy Learning Not Triggering

- Check audit log directory
- Verify failure count threshold (>= 3)
- Check rate limiting (24h cooldown)

## Success Criteria

- ✅ All operational checklist items pass
- ✅ Prometheus queries return valid data
- ✅ Dry-run rollback creates PR successfully
- ✅ Fork PRs are blocked
- ✅ Policy learning generates PRs when appropriate
- ✅ SLO violations trigger rollbacks correctly

## Next Steps

1. Complete immediate verification (10 min)
2. Run production test scenarios (30 min)
3. Monitor for 7 days
4. Review audit logs weekly
5. Adjust SLO thresholds based on actual metrics

