# Protected Branch Configuration Guide
# Purpose: Configure GitHub Protected Branch + Required Status Checks
# NOTE: This must be configured manually in GitHub Settings

## Protected Branches
- `main`
- `release/*`

## Required Status Checks
1. `obs-lint` (promtool check + sandbox smoke)
2. `sandbox-smoke-60s` (Prometheus sandbox validation)
3. `dr-rehearsal-24h-pass` (DR rehearsal passed in last 24h)
4. `canary-quorum-pass` (Canary evaluation passed, if applicable)
5. `error-budget-burn-ok` (Error budget burn rate OK)

## Settings
- **"Allow bypassing branch protections"**: DISABLED
- **"Require pull request reviews before merging"**: Enabled (1 approval)
- **"Require CODEOWNERS approval"**: Enabled
- **"Require status checks to pass before merging"**: Enabled
- **"Require branches to be up to date before merging"**: Enabled

## Emergency Bypass
- Use GitHub label: `emergency-approved`
- Requires: CODEOWNERS approval
- Max uses per month: 3

## FREEZE_BYPASS Removal
- All CI workflows and scripts should ignore `FREEZE_BYPASS` environment variable
- Use GitHub labels + CODEOWNERS approval instead
- Server-side hooks (pre-receive) already block FREEZE_BYPASS

