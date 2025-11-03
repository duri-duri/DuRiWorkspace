# DuRi Long-Term Strengthening Plan
# Purpose: Mathematical invariants, control functions, and execution mechanisms

## 0) System Invariants

### I1. Safe Merge Invariant
"All changes entering main must pass the same guard set"
- Local/PR/MergeQueue/Tag use identical guards
- Enforced via: `.git/hooks/pre-receive`, CI workflows, Merge Queue

### I2. Observability Invariant
"All critical paths have SLIs, and SLIs are monitored via rules/alerts"
- Catalog: `docs/ops/SLI_CATALOG.md`
- Enforcement: Prometheus rules, alerting

### I3. Recovery Invariant
"Daily DR rehearsal failure = not GREEN for that day"
- Script: `scripts/ops/dr_rehearsal.sh`
- Enforcement: Merge Queue gate, alerting

### I4. Evolution Invariant
"Weakness scan → sandbox validation → canary → auto PR/merge" pipeline must not break
- Scripts: `shadow_generate.sh`, `shadow_validate.sh`, `auto_pr.py`
- Enforcement: Pipeline monitoring, alerts

---

## 1) Lyapunov-Style Control Function

### Definition
\[
\mathcal{V}(t) = \alpha(1-\text{GREEN\_uptime\_ratio})^2 + \beta\text{AlertRate} + \gamma\text{MTTR} + \delta(1-\text{DR\_success\_ratio\_7d}) + \varepsilon(\text{EV\_target}-\text{EV/h})_+
\]

### Coefficients (Default)
- \(\alpha = 0.4\) (GREEN uptime weight)
- \(\beta = 0.25\) (Alert rate weight)
- \(\gamma = 0.20\) (MTTR weight)
- \(\delta = 0.10\) (DR success weight)
- \(\varepsilon = 0.05\) (EV/h target weight)

### Goal
Keep \(\frac{d\mathcal{V}}{dt} < 0\) (system stability)

### Implementation
- Script: `scripts/ops/lyapunov_control.sh`
- Metrics: `duri_lyapunov_v`, `duri_alert_rate_per_hour`, `duri_mttr_seconds`
- Actions: Throttle merges, enhance rules, increase retries, block merges, increase L3 cycle

### Expected Effect
- P(GREEN 24h): 0.999 → 0.9993~0.9996 (p≈0.7)
- MTTR: 5–8분 → 3–6분 (p≈0.6)

---

## 2) L3 → L4 Self-Evolution Promotion

### Goal
"Human approval required, but auto-merge when conditions met"

### Mechanisms
- Promotion gate: `.obs/promotion.yml`
- Canary evaluation: `scripts/ops/evolution/canary/canary_promote_or_rollback.sh`
- Auto-merge: Enhanced `auto_pr.py` with labels (`auto`, `canary-ready`, `dr-safe`)

### Metrics
- `duri_promotion_gate_pass_ratio` (green PR ratio)
- `duri_canary_rollback_rate` (target: < 2% weekly)
- `duri_automerge_latency_seconds` (PR creation → merge)

### Expected Effect (12 weeks)
- EV/h: +0.3~+0.7 (p≈0.65)
- Rollback rate: 5% → ≤2%

---

## 3) Provable DR Contract

### Mechanisms
- Enhanced `dr_rehearsal.sh`: RTO measurement, SLI smoke checks
- Metrics: `duri_dr_rto_seconds`, `duri_dr_rto_seconds_p95_7d`
- Alerting: DR success rate < 0.999 → immediate RED

### Expected Effect
- RTO p95: 10~15분 → 6~9분 (p≈0.6)

---

## 4) Observability Expansion

### SLI Catalog
- File: `docs/ops/SLI_CATALOG.md`
- Coverage: Observability, Evolution, DR, Self-Healing, Stability

### Error Budget Rules
- File: `prometheus/rules/error_budget.rules.yml`
- Alerts: Burn rate short/long, budget exhausted
- Actions: Merge queue throttling, experiment intensity down

### Expected Effect
- Alert quality ↑, false positives ↓ (weekly <3%)

---

## 5) Knowledge & Data Lineage

### Manifest Schema
- Location: `var/evolution/EV-*/manifest.json`
- Fields: Input (weakness vector, KS/σ/unique snapshot), patch hash, test results, promotion/rollback decision, PR#/tags

### Weekly Report
- Location: `.reports/evolution/weekly.md`
- Content: EV/h decomposition (cause-effect tree)

### Expected Effect
- Waste experiment ratio: 10~20%p↓ (p≈0.6)

---

## 6) Governance Hardening

### Server-Side Guards
- Enhanced `.git/hooks/pre-receive`: FREEZE_BYPASS blocking, required file hash whitelist
- Secrets scanning: CI with `trufflehog --fail` equivalent
- Merge Queue policy: `obs-lint`, `dr-rehearsal-pass` OR `dr-exempt`

### Expected Effect
- Protection compromise probability: <0.1%/quarter (p≈0.7)

---

## 7) Economic Benefit Function

### Definition
\[
\text{BizEV} = \eta_1\text{재내원율} + \eta_2(1/\text{치료리드타임}) + \eta_3(1-\text{다운타임})
\]

### Monthly Report
- Location: `.reports/biz/impact.md`
- Content: EV growth rate ↔ revenue/cost impact

### Policy Loop
- BizEV decline → adjust experiment intensity/direction

### Expected Effect
- Revenue variance ↓, downside risk ↓ (qualitative, 1-2 quarters)

---

## 8) Execution Plan (Day 01-25 Sprint)

### Day 01-03: Setup & Contract
- [x] `.obs/promotion.yml` created
- [x] `docs/ops/SLI_CATALOG.md` created
- [x] Error budget rules added
- [ ] CI Merge Queue required checks configured (manual)

### Day 04-09: L4 Auto-Merge
- [x] `auto_pr.py` enhanced with labels
- [x] `canary_promote_or_rollback.sh` created
- [ ] Canary metrics/alerting (TODO)

### Day 10-15: DR Proof Hardening
- [x] `dr_rehearsal.sh` enhanced (RTO, SLI checks)
- [x] DR RTO recording rules added
- [ ] DR failure → merge block (TODO)

### Day 16-20: Lineage & Reports
- [ ] EV manifest schema fixed (TODO)
- [ ] Weekly report generation job (TODO)

### Day 21-25: Economic Function
- [ ] `.reports/biz/impact.md` auto-generation (TODO)
- [ ] Monthly review process (TODO)

---

## 9) Immediate Snippets

### 9.1 Promotion Config
✅ Created: `.obs/promotion.yml`

### 9.2 Canary Hook
✅ Created: `scripts/ops/evolution/canary/canary_promote_or_rollback.sh`

### 9.3 DR RTO Recording Rule
✅ Added: `duri_dr_rto_seconds_p95_7d`

---

## 10) Risks & Buffers

- Merge Queue enforcement may slow initial speed → Buffer: Emergency bypass label (admin, one-time)
- Canary reliability sensitive to sample size → Buffer: Min sample/max wait quorum in `promotion.yml`
- DR cost (time/IO) → Buffer: Off-peak (02:00), incremental path priority, weekly full test

---

## 11) Final Summary (Quantitative Forecast, Conservative)

- **P(GREEN 24h)**: 0.997 → **0.999–0.9993**
- **EV/h**: +0.25(30d) → **+0.4~+0.6(90d)**
- **MTTR**: 12–20분 → **3–6분**
- **DR Success Rate (7d)**: 0.98 → **≥0.999**
- **False Positive Rate (weekly)**: <3% **maintain/slight improvement**

---

*Last Updated: $(date +%Y-%m-%d)*
*Next Review: $(date -d '+1 month' +%Y-%m-%d)*

