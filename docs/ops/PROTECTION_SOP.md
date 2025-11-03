# Standard Operating Procedure (SOP) for Branch Protection Management

## 표준 병합 경로 (v2)

- **자동 병합**: PR에 `merge:temporal-relax` + `safe-change` 라벨 → **Actions: temporal-relax-merge-v2** 자동 가동 (완화→머지→원복→검증)
- **수동 병합**: 룰셋 활성 시 `allow_ruleset_override=true`로 수동 실행 가능
- **워크플로우**: `.github/workflows/temporal-relax-merge-v2.yml`

## 기존 수동 절차 (임시 완화 → 머지 → 원복)

### 1. 보호 규칙 완화

```bash
# JSON 페이로드 생성
cat > /tmp/protection_relax.json <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "obs-lint",
      "sandbox-smoke-60s",
      "promql-unit",
      "dr-rehearsal-24h-pass",
      "canary-quorum-pass",
      "error-budget-burn-ok"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 0,
    "require_code_owner_reviews": false
  },
  "required_conversation_resolution": true,
  "required_linear_history": true,
  "restrictions": null
}
EOF

# 완화 적용
gh api -X PUT repos/duri-duri/DuRiWorkspace/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  --input /tmp/protection_relax.json
```

### 2. PR 머지

```bash
gh pr merge <PR_NUMBER> --squash --delete-branch
```

### 3. 보호 규칙 원복

```bash
# JSON 페이로드 생성
cat > /tmp/protection_restore.json <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "obs-lint",
      "sandbox-smoke-60s",
      "promql-unit",
      "dr-rehearsal-24h-pass",
      "canary-quorum-pass",
      "error-budget-burn-ok"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "require_code_owner_reviews": true
  },
  "required_conversation_resolution": true,
  "required_linear_history": true,
  "restrictions": null
}
EOF

# 원복 적용
gh api -X PUT repos/duri-duri/DuRiWorkspace/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  --input /tmp/protection_restore.json
```

## 주의사항

- **완화 후 즉시 머지하고 원복**해야 함 (보호 규칙 노출 최소화)
- **linear history 유지**를 위해 `--squash` 또는 `--rebase` 사용 권장
- **protection-guard**가 다음 push/스케줄에서 원복 상태 자동 확인

