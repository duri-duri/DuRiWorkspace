# Protected Branch Configuration Guide
# Purpose: Configure GitHub Protected Branch + Required Status Checks
# NOTE: This must be configured manually in GitHub Settings

## Protected Branches
- `main`
- `release/*`

## Required Status Checks (CRITICAL: Job names must match exactly)
1. `obs-lint` (promtool check + sandbox smoke)
2. `sandbox-smoke-60s` (Prometheus sandbox validation)
3. `dr-rehearsal-24h-pass` (DR rehearsal validation)
4. `canary-quorum-pass` (Canary evaluation validation)
5. `error-budget-burn-ok` (Error budget validation)

## Settings (GUI Steps)

### Settings → Branches → Add rule

**For branches matching:** `main`, `release/*`

✅ **Require a pull request before merging**
- Minimum number of approvals: `1`
- Dismiss stale pull request approvals when new commits are pushed: ✅

✅ **Require review from Code Owners**
- CODEOWNERS file: `.github/CODEOWNERS`

✅ **Require status checks to pass before merging**
- Required status checks (select all 5):
  - `obs-lint`
  - `sandbox-smoke-60s`
  - `dr-rehearsal-24h-pass`
  - `canary-quorum-pass`
  - `error-budget-burn-ok`
- Require branches to be up to date before merging: ✅

❌ **Allow force pushes**: UNCHECKED
❌ **Allow deletions**: UNCHECKED
❌ **Allow bypassing branch protections**: UNCHECKED (CRITICAL)

✅ **Require conversation resolution before merging**: CHECKED

## Emergency Bypass (Alternative to FREEZE_BYPASS)
- Use GitHub label: `emergency-approved`
- Requires: CODEOWNERS approval
- Max uses per month: 3

## FREEZE_BYPASS Removal
- ✅ All CI workflows ignore `FREEZE_BYPASS` environment variable
- ✅ Server-side hooks (pre-receive) already block FREEZE_BYPASS
- ✅ Use GitHub labels + CODEOWNERS approval instead

## Verification
After setup, test with:
```bash
# Should be rejected (no PR, no approvals)
git push origin main

# Should work (with PR + approvals)
gh pr create --title "Test" --body "Test" --base main
```


