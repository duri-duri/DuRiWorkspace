# DuRi SLI Catalog
# Purpose: Define Service Level Indicators for all critical paths

## Overview

All critical paths in DuRi must have:
1. **SLI Definition**: What we measure
2. **Aggregation**: How we aggregate
3. **Alerting**: When we alert
4. **Owner**: Who owns this SLI

---

## 1. Observability Stack

### SLI: Prometheus Uptime
- **Definition**: Prometheus `/-/ready` endpoint responds with 200
- **Aggregation**: `sum_over_time(up{job="prometheus"}[24h]) / 86400`
- **Target**: ≥ 0.999 (99.9% uptime)
- **Alert**: `PrometheusDown` (critical, 2m)
- **Owner**: ops-team

### SLI: Textfile Collector Heartbeat
- **Definition**: `duri_textfile_heartbeat_seq` increases every 5 minutes
- **Aggregation**: `increase(duri_textfile_heartbeat_seq[10m]) > 0`
- **Target**: 100% (no stalls)
- **Alert**: `TextfileHeartbeatStall` (warning, 10m)
- **Owner**: ops-team

### SLI: Rule Evaluation Success Rate
- **Definition**: Prometheus rule evaluation failures
- **Aggregation**: `1 - (sum(increase(prometheus_rule_group_eval_failures_total[24h])) / sum(increase(prometheus_rule_group_rules[24h])))`
- **Target**: ≥ 0.999
- **Alert**: `RuleEvalFailures` (warning, 5m)
- **Owner**: ops-team

---

## 2. Evolution Pipeline

### SLI: EV Generation Rate
- **Definition**: Number of EV bundles created per hour
- **Aggregation**: `rate(duri_ev_created_total[1h])`
- **Target**: ≥ 4.0 EV/h
- **Alert**: `EVVelocityLow` (warning, 30m)
- **Owner**: evolution-team

### SLI: AB Test Quality (KS_p)
- **Definition**: Kolmogorov-Smirnov test p-value for p-value uniformity
- **Aggregation**: `duri_p_uniform_ks_p{window="2h"}`
- **Target**: ≥ 0.7
- **Alert**: `ABPValuesKSUniformityLost` (warning, 10m)
- **Owner**: evolution-team

### SLI: AB Test Variance (σ)
- **Definition**: Standard deviation of p-values
- **Aggregation**: `duri_p_sigma{window="2h"}`
- **Target**: > 0.1
- **Alert**: `ABPValueNoVariance` (warning, 2m)
- **Owner**: evolution-team

---

## 3. Disaster Recovery

### SLI: DR Success Rate
- **Definition**: Successful DR rehearsals / Total rehearsals
- **Aggregation**: `duri_dr_success_ratio_7d`
- **Target**: ≥ 0.999
- **Alert**: `DRSuccessRateLow` (critical, 1h)
- **Owner**: ops-team

### SLI: DR Recovery Time Objective (RTO)
- **Definition**: Time to restore from backup (p95)
- **Aggregation**: `histogram_quantile(0.95, sum by (le) (rate(duri_dr_restore_time_seconds_bucket[7d])))`
- **Target**: ≤ 10 minutes (p95)
- **Alert**: `DRRTOHigh` (warning, 3d consecutive)
- **Owner**: ops-team

### SLI: DR Recovery Point Objective (RPO)
- **Definition**: Maximum data loss window
- **Aggregation**: `max(time() - duri_last_backup_timestamp)`
- **Target**: ≤ 15 minutes
- **Alert**: `DRRPOHigh` (warning, 20m)
- **Owner**: ops-team

---

## 4. Self-Healing

### SLI: Mean Time To Recovery (MTTR)
- **Definition**: Average time from alert to GREEN recovery
- **Aggregation**: `avg_over_time(duri_mttr_seconds[24h])`
- **Target**: ≤ 5 minutes
- **Alert**: `MTTRHigh` (warning, 6h)
- **Owner**: ops-team

### SLI: Auto-Recovery Success Rate
- **Definition**: Successful auto-recoveries / Total recovery attempts
- **Aggregation**: `sum(increase(duri_auto_recovery_success_total[24h])) / sum(increase(duri_auto_recovery_total[24h]))`
- **Target**: ≥ 0.95
- **Alert**: `AutoRecoveryFailure` (warning, 10m)
- **Owner**: ops-team

---

## 5. Operational Stability

### SLI: GREEN Uptime Ratio
- **Definition**: Fraction of time system is in GREEN state
- **Aggregation**: `duri_green_uptime_ratio`
- **Target**: ≥ 0.98 (98% uptime)
- **Alert**: `GreenUptimeLow` (warning, 1h)
- **Owner**: ops-team

### SLI: Alert Rate
- **Definition**: Number of alerts per hour
- **Aggregation**: `sum(rate(alert_firing_total[1h]))`
- **Target**: ≤ 5 alerts/hour (excluding info)
- **Alert**: `AlertRateHigh` (info, 1h)
- **Owner**: ops-team

---

## Error Budget Policy

### Monthly Error Budget
- **Formula**: `1 - GREEN_uptime_ratio`
- **Target**: ≤ 0.02 (2% error budget per month)
- **Burn Rate Alerts**:
  - Short-term: `error_budget_burn_short > 14x` (1h window)
  - Long-term: `error_budget_burn_long > 6x` (6h window)

### Budget Exhaustion Actions
1. **Merge Queue Throttling**: Reduce merge rate by 50%
2. **Experiment Intensity Down**: Reduce L3 evolution frequency
3. **Focus on Stability**: Prioritize stability patches over features

---

## SLI Ownership Matrix

| SLI | Owner | Escalation | Review Frequency |
|-----|-------|------------|------------------|
| Prometheus Uptime | ops-team | immediate | weekly |
| EV Generation Rate | evolution-team | 1h | daily |
| DR Success Rate | ops-team | immediate | weekly |
| MTTR | ops-team | 2h | daily |
| GREEN Uptime | ops-team | 1h | daily |

---

## SLI Calculation Examples

### Prometheus Uptime
```promql
# 24-hour uptime ratio
sum_over_time((up{job="prometheus"} == 1)[24h:30s]) / 86400
```

### DR RTO (p95)
```promql
# 7-day p95 recovery time
histogram_quantile(0.95, sum by (le) (rate(duri_dr_restore_time_seconds_bucket[7d])))
```

### Error Budget Burn Rate (Short-term)
```promql
# 1-hour window burn rate
(1 - duri_green_uptime_ratio) / (error_budget / (30 * 24))
```

---

## SLI Review Process

1. **Weekly**: Review all SLIs, identify trends
2. **Monthly**: Error budget review, adjust targets if needed
3. **Quarterly**: SLI catalog review, add/remove SLIs as needed

---

*Last Updated: $(date +%Y-%m-%d)*
*Next Review: $(date -d '+1 month' +%Y-%m-%d)*

