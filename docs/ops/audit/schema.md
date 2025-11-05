# Audit Log Schema
# Purpose: Define schema for audit log entries
# Usage: All audit entries should follow this schema

{
  "ts": "RFC3339 timestamp",
  "stage": "gate|post-merge-watch|rollback|policy-learning",
  "result": "pass|fail|breach|skip",
  "reason": "human-readable reason",
  "ctx": {
    "pr": "PR number",
    "sha": "commit SHA",
    "rulepack": "matched scenario",
    "workflow": "workflow name",
    "additional": "context-specific fields"
  }
}

# Example entries:

# Gate failure
{
  "ts": "2025-11-05T12:34:56Z",
  "stage": "gate",
  "result": "fail",
  "reason": "forbidden_path",
  "ctx": {
    "pr": 123,
    "sha": "abc123",
    "rulepack": "default",
    "workflow": "auto-relax-merge-restore"
  }
}

# Post-merge watch breach
{
  "ts": "2025-11-05T12:34:56Z",
  "stage": "post-merge-watch",
  "result": "breach",
  "reason": "SLO violation (dual condition)",
  "ctx": {
    "pr": 123,
    "sha": "abc123",
    "availability_violated": 1,
    "latency_violated": 1,
    "error_violated": 1,
    "dual_condition": 1,
    "workflow": "l4-post-merge-quality-watch"
  }
}

# Rollback success
{
  "ts": "2025-11-05T12:34:56Z",
  "stage": "rollback",
  "result": "success",
  "reason": "SLO violation detected",
  "ctx": {
    "pr": 123,
    "sha": "abc123",
    "revert_pr": 124,
    "dry_run": false,
    "workflow": "l4-auto-rollback"
  }
}

