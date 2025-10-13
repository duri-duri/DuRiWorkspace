#!/usr/bin/env bash
set -euo pipefail
ALERT_JSON="${1:?usage: $0 alert.json}"
OUT="postmortem_$(date +%Y%m%d_%H%M%S).md"
jq -r '
  .alerts[] | [
    "## Postmortem",
    "**Alert**: " + (.labels.alertname // ""),
    "**Severity**: " + (.labels.severity // ""),
    "**Team**: " + (.labels.team // ""),
    "**StartsAt**: " + (.startsAt // ""),
    "",
    "### Summary", (.annotations.summary // ""),
    "",
    "### Timeline", "- TBD",
    "",
    "### Root Cause Hypothesis", "- TBD",
    "",
    "### Mitigation", "- TBD",
    "",
    "### Action Items", "- [ ] TBD"
  ] | join("\n")
' "$ALERT_JSON" > "docs/$OUT"
echo "Wrote docs/$OUT"
