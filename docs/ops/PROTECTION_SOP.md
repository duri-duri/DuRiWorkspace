# Branch Protection SOP

## 완화 스위치 (꼭 필요할 때만)

```bash
gh api -X PUT repos/duri-duri/DuRiWorkspace/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  -f enforce_admins=false \
  -f required_conversation_resolution=false \
  -F required_status_checks[strict]=true \
  -F required_status_checks[contexts][]=obs-lint \
  -F required_status_checks[contexts][]=sandbox-smoke-60s \
  -F required_status_checks[contexts][]=promql-unit \
  -F required_status_checks[contexts][]=dr-rehearsal-24h-pass \
  -F required_status_checks[contexts][]=canary-quorum-pass \
  -F required_status_checks[contexts][]=error-budget-burn-ok \
  -F required_status_checks[contexts][]=test \
  -F required_pull_request_reviews[required_approving_review_count]=0 \
  -F required_pull_request_reviews[require_code_owner_reviews]=false
```

## 원복 스위치 (기본)

```bash
gh api -X PUT repos/duri-duri/DuRiWorkspace/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  -f enforce_admins=true \
  -f required_conversation_resolution=true \
  -F required_status_checks[strict]=true \
  -F required_status_checks[contexts][]=obs-lint \
  -F required_status_checks[contexts][]=sandbox-smoke-60s \
  -F required_status_checks[contexts][]=promql-unit \
  -F required_status_checks[contexts][]=dr-rehearsal-24h-pass \
  -F required_status_checks[contexts][]=canary-quorum-pass \
  -F required_status_checks[contexts][]=error-budget-burn-ok \
  -F required_pull_request_reviews[required_approving_review_count]=1 \
  -F required_pull_request_reviews[require_code_owner_reviews]=true
```

## 확인 루틴

```bash
# 보호 규칙 상태 확인
gh api repos/duri-duri/DuRiWorkspace/branches/main/protection --jq '{
  linear: .required_linear_history.enabled,
  admin: .enforce_admins.enabled,
  reviews: .required_pull_request_reviews.required_approving_review_count,
  codeowners: .required_pull_request_reviews.require_code_owner_reviews,
  contexts: .required_status_checks.contexts
}'

# Ruleset 확인 (저장소 레벨)
gh api --paginate repos/duri-duri/DuRiWorkspace/rulesets -q '.[] | {id, name, enforcement, rules: [.rules[].type]}'

# Ruleset 확인 (조직 레벨)
gh api --paginate orgs/<ORG>/rulesets -q '.[] | {id, name, enforcement, rules: [.rules[].type]}'
```

## 예상 스냅샷

- `required_status_checks.contexts`: `["obs-lint","sandbox-smoke-60s","promql-unit","dr-rehearsal-24h-pass","canary-quorum-pass","error-budget-burn-ok"]`
- `required_approving_review_count`: `1`
- `require_code_owner_reviews`: `true`
- `required_linear_history`: `true`
- `enforce_admins`: `true`
- `required_conversation_resolution`: `true`
