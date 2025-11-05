#!/usr/bin/env python3
# L4 Spec Generator - 스펙에서 코드/유닛/알람 자동 생성
# Purpose: Single Source of Truth에서 자동화 구성 요소 생성
# Usage: python3 scripts/ops/gen_l4_from_spec.py

import yaml
import pathlib
import sys

def sec(s):
    """Convert time string (e.g., '7d', '2h', '10m') to seconds"""
    if not s:
        return 0
    u = {"m": 60, "h": 3600, "d": 86400}
    n = int(s[:-1])
    unit = s[-1]
    return n * u.get(unit, 1)

def main():
    spec_file = pathlib.Path("config/l4_spec.yml")
    if not spec_file.exists():
        print(f"Error: {spec_file} not found")
        sys.exit(1)
    
    S = yaml.safe_load(spec_file.open())
    artifacts = S.get("artifacts", [])
    
    # 1) Generate freshness block for l4_autotest.sh
    freshness_lines = [
        "# [G] Check promfile freshness (cadence-aware) - GENERATED FROM SPEC",
        "echo '[G] Check promfile freshness (cadence-aware)'",
        "prom_dir=\"$dir\"",
        "now=$(date +%s)",
        "",
        "check_age() {",
        "  local f=\"$1\"",
        "  local max=\"$2\"",
        "  local label=\"$3\"",
        "  local warn_only=\"${4:-0}\"",
        "  ",
        "  if [[ ! -f \"$f\" ]]; then",
        "    if [[ $warn_only -eq 1 ]]; then",
        "      echo \"⚠️  WARN: $label missing (tolerated)\"",
        "      return 0",
        "    else",
        "      echo \"❌ MISSING: $label ($f)\"",
        "      return 1",
        "    fi",
        "  fi",
        "  ",
        "  local mtime",
        "  mtime=$(stat -c %Y \"$f\" 2>/dev/null || stat -f %m \"$f\" 2>/dev/null || echo 0)",
        "  local age=$((now - mtime))",
        "  ",
        "  echo \"  $label age: ${age}s (limit: ${max}s)\"",
        "  ",
        "  if [[ $age -gt $max ]]; then",
        "    if [[ $warn_only -eq 1 ]]; then",
        "      echo \"⚠️  WARN: $label older than limit (${max}s)\"",
        "      return 0",
        "    else",
        "      echo \"❌ FAIL: $label stale (>${max}s)\"",
        "      return 1",
        "    fi",
        "  fi",
        "  ",
        "  return 0",
        "}",
        "",
    ]
    
    for a in artifacts:
        name = a["name"]
        file = a["file"]
        cadence = a["cadence"]
        grace = a.get("grace", "0m")
        limit = sec(cadence) + sec(grace)
        
        # Determine if warn_only (boot_status, selftest_pass are optional)
        warn_only = 1 if name in ["boot_status", "selftest_pass"] else 0
        
        # Check if first-create should be warn-only
        warn_until_first = a.get("warn_only_until_first_create", False)
        
        freshness_lines.append(f"# {name}: {cadence} + {grace} = {limit}s")
        if warn_only == 1:
            freshness_lines.append(f"check_age \"$prom_dir/{file}\" \"{limit}\" \"{name}\" {warn_only} || true")
        elif warn_until_first:
            # First-create exception: warn if missing, fail if stale
            freshness_lines.append(f"if [[ ! -f \"$prom_dir/{file}\" ]]; then")
            freshness_lines.append(f"  echo \"⚠️  WARN: {name} not yet created (first run pending)\"")
            freshness_lines.append(f"elif ! check_age \"$prom_dir/{file}\" \"{limit}\" \"{name}\" 0; then")
            freshness_lines.append("  fail=1")
            freshness_lines.append("fi")
        else:
            freshness_lines.append(f"if ! check_age \"$prom_dir/{file}\" \"{limit}\" \"{name}\" {warn_only}; then")
            freshness_lines.append("  fail=1")
            freshness_lines.append("fi")
        freshness_lines.append("")
    
    freshness_block = pathlib.Path("scripts/ops/inc/_gen_freshness_block.sh")
    freshness_block.write_text("\n".join(freshness_lines))
    print(f"[OK] Generated: {freshness_block}")
    
    # 2) Generate Prometheus alert rules (append to existing)
    rules_lines = [
        "# Auto-generated from config/l4_spec.yml",
        "# DO NOT EDIT MANUALLY - Regenerate using: python3 scripts/ops/gen_l4_from_spec.py",
        "",
    ]
    
    for a in artifacts:
        if "alert" not in a:
            continue
        
        rule = a["alert"]["rule"]
        window = a["alert"]["window"]
        severity = a["alert"].get("severity", "critical")
        cadence = a["cadence"]
        grace = a.get("grace", "0m")
        threshold = sec(cadence) + sec(grace)
        
        rules_lines.append(f"  - alert: {rule}")
        rules_lines.append(f"    expr: |")
        rules_lines.append(f"      (time() - max_over_time(l4_{a['name']}_ts[{window}])) > {threshold}")
        rules_lines.append(f"    for: 5m")
        rules_lines.append(f"    labels:")
        rules_lines.append(f"      severity: \"{severity}\"")
        rules_lines.append(f"      component: l4_automation")
        rules_lines.append(f"    annotations:")
        rules_lines.append(f"      summary: \"{a['name']} stale (>{cadence})\"")
        rules_lines.append(f"      description: \"{a['name']} has not been updated for more than {cadence}. Check if corresponding service is running.\"")
        rules_lines.append("")
    
    # Decision missing alert
    dw = S["decision_stream"]["recent_window"]
    rules_lines.append(f"  - alert: L4DecisionMissing")
    rules_lines.append(f"    expr: |")
    rules_lines.append(f"      (time() - max_over_time(l4_decision_ts[{dw}])) > {sec(dw)}")
    rules_lines.append(f"    for: 10m")
    rules_lines.append(f"    labels:")
    rules_lines.append(f"      severity: \"warning\"")
    rules_lines.append(f"      component: l4_automation")
    rules_lines.append(f"    annotations:")
    rules_lines.append(f"      summary: \"No decisions in {dw}\"")
    rules_lines.append(f"      description: \"L4 decision stream has been quiet for more than {dw}. Check if decision pipeline is running.\"")
    rules_lines.append("")
    
    # Write rules to a separate file for appending
    rules_block = pathlib.Path("prometheus/rules/l4_alerts_generated.yml")
    rules_block.write_text("\n".join(rules_lines))
    print(f"[OK] Generated: {rules_block}")
    
    # 3) Generate timestamp export helper
    ts_helper_lines = [
        "#!/usr/bin/env bash",
        "# Export timestamp metric for artifact",
        "# Usage: export_timestamp <name>",
        "",
        "export_timestamp() {",
        "  local name=\"$1\"",
        "  local ts=$(date +%s)",
        "  local textfile_dir=\"${NODE_EXPORTER_TEXTFILE_DIR:-${HOME}/.cache/node_exporter/textfile}\"",
        "  ",
        "  mkdir -p \"$textfile_dir\"",
        "  echo \"l4_${name}_ts $ts\" > \"$textfile_dir/l4_${name}_ts.prom\"",
        "  chmod 0644 \"$textfile_dir/l4_${name}_ts.prom\" 2>/dev/null || true",
        "}",
        "",
    ]
    
    ts_helper = pathlib.Path("scripts/ops/inc/_export_timestamp.sh")
    ts_helper.write_text("\n".join(ts_helper_lines))
    ts_helper.chmod(0o755)
    print(f"[OK] Generated: {ts_helper}")
    
    print("\n[SUCCESS] All files generated from spec")
    print("\nNext steps:")
    print("  1. Review generated files")
    print("  2. Merge l4_alerts_generated.yml into l4_alerts.yml")
    print("  3. Update l4_autotest.sh to include _gen_freshness_block.sh")
    print("  4. Update l4_post_decision.sh to call export_timestamp")

if __name__ == "__main__":
    main()

