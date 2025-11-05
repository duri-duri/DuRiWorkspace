# Rulepack Documentation
# Purpose: Define multi-scenario rules for auto-relax-merge-restore workflow

## Overview

Rulepacks define scenario-specific rules for the auto-relax-merge-restore workflow. Each scenario specifies:
- Which paths are allowed/denied
- Required labels and contexts
- Merge state requirements
- Actor roles and review requirements

## Schema

```yaml
scenario: "<name>"                # e.g., safe-docs
allow_paths: ["docs/**", ...]    # Glob patterns for allowed paths
deny_paths: []                   # Glob patterns for denied paths
required_labels: ["change:safe","auto-relax-merge"]
base_branch: "main"
required_contexts: ["obs-lint", ...]
merge_state: ["BLOCKED","MERGEABLE"]
trigger_comment: "/auto-merge"
actor_roles: ["admin","maintain","write"]
relaxable: true                  # Whether auto-relax is allowed
require_reviews: 0               # Minimum reviews required
```

## Available Scenarios

- `safe-docs.yml`: Documentation and observability changes
- `observability-only.yml`: Prometheus/Grafana rules only
- `workflows-only.yml`: GitHub workflows only
- `infra-critical.yml`: Infrastructure changes (helm, terraform, k8s)

## Usage

The auto-relax-merge-restore workflow automatically matches changed files against rulepack scenarios. A PR matches a scenario if:
1. All changed files match at least one `allow_path` pattern
2. No changed files match any `deny_path` pattern
3. The scenario's `relaxable` flag is `true`

## Adding New Scenarios

1. Create a new YAML file in `rulepack/` directory
2. Follow the schema defined above
3. Update `rulepack/schema.yml` with the new scenario
4. Test with a sample PR

