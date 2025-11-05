# [G] Check promfile freshness (cadence-aware) - GENERATED FROM SPEC
echo '[G] Check promfile freshness (cadence-aware)'
prom_dir="$dir"
now=$(date +%s)

check_age() {
  local f="$1"
  local max="$2"
  local label="$3"
  local warn_only="${4:-0}"
  
  if [[ ! -f "$f" ]]; then
    if [[ $warn_only -eq 1 ]]; then
      echo "⚠️  WARN: $label missing (tolerated)"
      return 0
    else
      echo "❌ MISSING: $label ($f)"
      return 1
    fi
  fi
  
  local mtime
  mtime=$(stat -c %Y "$f" 2>/dev/null || stat -f %m "$f" 2>/dev/null || echo 0)
  local age=$((now - mtime))
  
  echo "  $label age: ${age}s (limit: ${max}s)"
  
  if [[ $age -gt $max ]]; then
    if [[ $warn_only -eq 1 ]]; then
      echo "⚠️  WARN: $label older than limit (${max}s)"
      return 0
    else
      echo "❌ FAIL: $label stale (>${max}s)"
      return 1
    fi
  fi
  
  return 0
}

# weekly_decision: 7d + 2h = 612000s
if ! check_age "$prom_dir/l4_weekly_decision.prom" "612000" "weekly_decision" 0; then
  fail=1
fi

# boot_status: 1d + 2h = 93600s
check_age "$prom_dir/l4_boot_status.prom" "93600" "boot_status" 1 || true

# selftest_pass: 10m + 0m = 600s
check_age "$prom_dir/l4_selftest.pass.prom" "600" "selftest_pass" 1 || true
