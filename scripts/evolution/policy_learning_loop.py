#!/usr/bin/env python3
"""
Policy Learning Loop
Purpose: Analyze failure patterns and automatically propose rulepack updates
Usage: python3 scripts/evolution/policy_learning_loop.py
"""

import os
import json
import sys
import subprocess
import tempfile
import datetime
from pathlib import Path
from collections import Counter
from typing import Dict, List, Optional, Tuple

# Configuration
AUDIT_DIR = Path("docs/ops/audit")
RULEPACK_DIR = Path("rulepack")
RULEPACK_FILE = RULEPACK_DIR / "auto_relax.yml"

# Failure cause classification keys
CAUSE_KEYS = [
    "pending_checks",
    "forbidden_path",
    "context_mismatch",
    "not_single_cause",
    "forked_pr",
    "base_not_main",
    "network_error",
    "restore_failed",
    "unknown"
]


def log(msg: str):
    """Log message with timestamp"""
    print(f"[{datetime.datetime.utcnow().isoformat()}] {msg}", file=sys.stderr)


def run_cmd(cmd: List[str], **kwargs) -> str:
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            **kwargs
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        log(f"Command failed: {' '.join(cmd)}")
        log(f"Error: {e.stderr}")
        return ""


def load_audit_logs() -> List[Dict]:
    """Load audit logs from audit directory"""
    items = []
    
    if not AUDIT_DIR.exists():
        log("Audit directory not found")
        return items
    
    # Load from both JSON files and JSONL index
    INDEX_FILE = AUDIT_DIR / "audit_index.jsonl"
    
    if INDEX_FILE.exists():
        try:
            with open(INDEX_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            items.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
        except Exception as e:
            log(f"Failed to load audit index: {e}")
    
    # Also load individual JSON files
    for p in AUDIT_DIR.glob("*.json"):
        if p.name == "audit_index.jsonl":
            continue
        try:
            with open(p, 'r') as f:
                data = json.load(f)
                items.append(data)
        except Exception as e:
            log(f"Failed to load {p}: {e}")
    
    return items


def classify_failure(item: Dict) -> str:
    """Classify failure cause from audit log item"""
    msg = json.dumps(item).lower()
    
    # Classification rules
    if "pending" in msg or "wait for completion" in msg:
        return "pending_checks"
    if "allowlist" in msg or "path not allowed" in msg or "deny" in msg:
        return "forbidden_path"
    if "context" in msg or "required" in msg:
        return "context_mismatch"
    if "not single cause" in msg or "not a pure-review block" in msg:
        return "not_single_cause"
    if "fork" in msg or "cross repository" in msg:
        return "forked_pr"
    if "base" in msg and "main" in msg:
        return "base_not_main"
    if "api" in msg and ("rate limit" in msg or "5" in msg or "timeout" in msg):
        return "network_error"
    if "restore" in msg and "fail" in msg:
        return "restore_failed"
    
    return "unknown"


def analyze_failures(audits: List[Dict]) -> Counter:
    """Analyze failures and return frequency counter"""
    counter = Counter()
    
    for item in audits:
        cause = classify_failure(item)
        counter[cause] += 1
    
    return counter


def propose_rulepack_update(counter: Counter) -> Optional[Tuple[str, str]]:
    """Propose rulepack update based on failure patterns"""
    if not counter:
        return None
    
    # Find most common failure cause
    common_cause, count = counter.most_common(1)[0]
    
    # Require at least 3 occurrences to trigger update
    if count < 3:
        log(f"Most common cause '{common_cause}' has only {count} occurrences (threshold: 3)")
        return None
    
    log(f"Most common failure cause: {common_cause} ({count} occurrences)")
    
    # Rate limiting: same category within 24h
    PROPOSED_FILE = RULEPACK_DIR / f"{common_cause}_proposed.yml"
    if PROPOSED_FILE.exists():
        # Check if proposed within 24h
        file_age = datetime.datetime.now() - datetime.datetime.fromtimestamp(PROPOSED_FILE.stat().st_mtime)
        if file_age.total_seconds() < 86400:  # 24 hours
            log(f"Proposal for '{common_cause}' created within 24h, skipping")
            return None
    
    # Generate patch based on cause
    if common_cause == "forbidden_path":
        patch = """# Auto-updated by policy learning loop
paths:
  - docs/**
  - prometheus/rules/**
  - scripts/ops/**
  - scripts/bin/**
  - .github/workflows/**
  # Suggested addition based on frequent path violations
  # Consider adding frequently denied paths here
"""
        path = str(RULEPACK_DIR / "paths_proposed.yml")
        
    elif common_cause == "pending_checks":
        patch = """# Auto-updated by policy learning loop
checks:
  min_checks_green: 0  # pending==0 enforced
  wait_for_pending: false  # Skip if pending checks exist
"""
        path = str(RULEPACK_DIR / "checks_proposed.yml")
        
    elif common_cause == "context_mismatch":
        patch = """# Auto-updated by policy learning loop
contexts:
  # Consider relaxing context requirements if frequently mismatched
  strict_mode: false  # Allow partial context matches
"""
        path = str(RULEPACK_DIR / "contexts_proposed.yml")
        
    else:
        # Generic update
        patch = f"""# Auto-updated by policy learning loop
# Most common failure cause: {common_cause} ({count} occurrences)
# Consider updating rules to handle this case
"""
        path = str(RULEPACK_DIR / "extra_proposed.yml")
    
    return path, patch


def create_policy_update_pr(path: str, patch: str, counter: Counter) -> bool:
    """Create PR with policy update"""
    try:
        # Create branch
        branch_name = f"policy/update-{datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        run_cmd(["git", "checkout", "-b", branch_name])
        
        # Ensure directory exists
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        # Write patch
        with open(path, 'w') as f:
            f.write(patch)
        
        # Commit
        run_cmd(["git", "add", path])
        run_cmd(["git", "commit", "-m", f"chore(policy): auto-update rulepack for {Counter(counter).most_common(1)[0][0]}"])
        
        # Push
        run_cmd(["git", "push", "origin", branch_name, "-f"])
        
        # Create PR
        title = f"chore(policy): rulepack auto-update ({Counter(counter).most_common(1)[0][0]})"
        body = f"""Auto-generated policy update based on failure analysis.

**Failure Analysis:**
```json
{json.dumps(dict(counter), indent=2)}
```

**Proposed Change:**
- File: `{path}`
- Most common cause: {Counter(counter).most_common(1)[0][0]} ({Counter(counter).most_common(1)[0][1]} occurrences)

Please review and approve if changes look reasonable.
"""
        
        run_cmd([
            "gh", "pr", "create",
            "--base", "main",
            "--head", branch_name,
            "--title", title,
            "--body", body,
            "--label", "change:safe",
            "--label", "auto-relax-merge"
        ])
        
        log(f"✅ Policy update PR created: {branch_name}")
        return True
        
    except Exception as e:
        log(f"Failed to create policy update PR: {e}")
        return False


def generate_report(counter: Counter) -> str:
    """Generate policy learning report"""
    report = f"""# Policy Learning Report

Generated: {datetime.datetime.utcnow().isoformat()}Z

## Failure Analysis

```
{json.dumps(dict(counter), indent=2)}
```

## Summary

- Total failures analyzed: {sum(counter.values())}
- Most common cause: {counter.most_common(1)[0][0] if counter else 'N/A'} ({counter.most_common(1)[0][1] if counter else 0} occurrences)
- Unique causes: {len(counter)}
"""
    return report


def main():
    """Main entry point"""
    log("Starting policy learning loop")
    
    # Load audit logs
    audits = load_audit_logs()
    if not audits:
        log("No audit logs found, exiting")
        return 0
    
    log(f"Loaded {len(audits)} audit log entries")
    
    # Analyze failures
    counter = analyze_failures(audits)
    if not counter:
        log("No failures found in audit logs")
        return 0
    
    log(f"Failure analysis: {dict(counter)}")
    
    # Generate report
    report = generate_report(counter)
    report_path = Path("docs/ops/POLICY_LEARNING_REPORT.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)
    
    # Propose update
    update = propose_rulepack_update(counter)
    if update:
        path, patch = update
        log(f"Proposing update: {path}")
        
        # Check if we're in a git repo
        if not Path(".git").exists():
            log("Not in a git repository, skipping PR creation")
            print(patch)
            return 0
        
        # Create PR
        if create_policy_update_pr(path, patch, counter):
            log("✅ Policy update PR created successfully")
            return 0
        else:
            log("⚠️  Failed to create policy update PR")
            return 1
    else:
        log("No policy update needed")
        return 0


if __name__ == "__main__":
    sys.exit(main())

