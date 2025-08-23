#!/usr/bin/env bash
# READ-ONLY policy verifier (grep/awk only; no writes)
set -u

POLICY="configs/storage_policy.yml"
TMP="/tmp/_policy_verify_$$"
mkdir -p "$TMP"

PASS_C=0; WARN_C=0; FAIL_C=0
p(){ echo "PASS $*"; PASS_C=$((PASS_C+1)); }
w(){ echo "WARN $*"; WARN_C=$((WARN_C+1)); }
f(){ echo "FAIL $*"; FAIL_C=$((FAIL_C+1)); }

cleanup(){ rm -rf "$TMP"; }
trap cleanup EXIT

# 1) repo root / policy presence
if git rev-parse --show-toplevel >/dev/null 2>&1; then
  p "Git repository detected"
else
  f "Not a Git repository"; echo "Summary: PASS=$PASS_C WARN=$WARN_C FAIL=$FAIL_C"; exit 1
fi

if [ -f "$POLICY" ]; then
  p "Policy file found: $POLICY"
else
  f "Missing policy file: $POLICY"; echo "Summary: PASS=$PASS_C WARN=$WARN_C FAIL=$FAIL_C"; exit 1
fi

# 2) minimal schema keys presence (existence only)
need_patterns=(
  '^profiles:' 'default:' '^ *git:' 'track:' 'ignore:'
  '^ *backup:' 'include:' 'exclude:' 'retention:'
  '^ *safety:' 'protect:' 'never_delete:'
)
for pat in "${need_patterns[@]}"; do
  if grep -Eq "$pat" "$POLICY"; then
    :
  else
    f "Schema key missing: /$pat/ in $POLICY"
  fi
done
[ $FAIL_C -eq 0 ] && p "Minimal schema keys present"

# helpers to extract a top-level-ish block
extract_block(){ # $1=block_name
  awk -v key="^ *"$1":" '
    BEGIN{flag=0}
    flag && /^[[:alpha:]]/{flag=0}
    flag{print; next}
    $0 ~ key {flag=1}
  ' "$POLICY"
}

# 3) retention.overrides exactly once
ret_block="$(awk '
  BEGIN{flag=0}
  /^[[:space:]]*retention:/{flag=1; next}
  flag && /^[[:alpha:]]/{flag=0}
  flag{print}
' "$POLICY")"
ovc="$(printf "%s\n" "$ret_block" | grep -Ec '^[[:space:]]*overrides:')"
if [ "$ovc" -eq 1 ]; then
  p "retention.overrides present exactly once"
elif [ "$ovc" -eq 0 ]; then
  f "retention.overrides not found in retention block"
else
  f "retention.overrides appears $ovc times (must be single list)"
fi

# 4) Log path standardization
# .gitignore: must have var/logs/ and NOT var/log/
if grep -qxF 'var/logs/' .gitignore; then
  if grep -qxF 'var/log/' .gitignore; then
    f ".gitignore still contains legacy 'var/log/'"
  else
    p ".gitignore uses 'var/logs/' only"
  fi
else
  f ".gitignore missing 'var/logs/'"
fi

# policy git.ignore and backup.exclude should include var/logs/**
git_block="$(extract_block git)"
if printf "%s\n" "$git_block" | grep -q 'var/logs/\*\*'; then
  p "policy.git.ignore contains var/logs/**"
else
  f "policy.git.ignore missing var/logs/**"
fi
bk_block="$(extract_block backup)"
if printf "%s\n" "$bk_block" | grep -q 'var/logs/\*\*'; then
  p "policy.backup.exclude contains var/logs/**"
else
  f "policy.backup.exclude missing var/logs/**"
fi

# filesystem: var/log should be symlink -> logs
if [ -L "var/log" ] && [ "$(readlink -f var/log 2>/dev/null | xargs -r basename)" = "logs" -o "$(readlink var/log 2>/dev/null)" = "logs" ]; then
  p "var/log -> logs symlink OK"
else
  f "var/log symlink to logs not set"
fi
[ -d "var/log_legacy" ] && echo "NOTE var/log_legacy/ present (kept for safety)"

# 5) var/reports protection & inclusion
TRACK_COUNT=$(git ls-files -- 'var/reports/*' 2>/dev/null | wc -l | tr -d ' ')
if [ "${TRACK_COUNT:-0}" -gt 0 ]; then
  p "Git tracking var/reports (files: $TRACK_COUNT)"
else
  w "No tracked files under var/reports (may be initial state)"
fi

if git check-ignore -v var/reports >/dev/null 2>&1; then
  f "var/reports is ignored by .gitignore rules"
else
  p "var/reports not ignored by .gitignore"
fi

RSYNC_LIST=$(rsync -nav --prune-empty-dirs --include='var/' --include='var/reports/' --include='var/reports/**' --exclude='*' ./ "$TMP/" 2>/dev/null | grep -E '^var/reports/' || true)
[ -n "$RSYNC_LIST" ] && p "rsync dry-run includes var/reports/**" || f "rsync dry-run did NOT include var/reports/**"

TAR_LIST=$(tar -cvf /dev/null var/reports 2>&1 | grep -E '^var/reports/' || true)
[ -n "$TAR_LIST" ] && p "tar lists var/reports/**" || f "tar did NOT list var/reports/**"

# 6) var/state whitelist
need_ws=("var/state/backup_refs.json" "var/state/restore_slo.jsonl")
miss_any=0
for fpath in "${need_ws[@]}"; do
  if [ -f "$fpath" ]; then
    :
  else
    miss_any=1
  fi
done
[ $miss_any -eq 0 ] && p "var/state whitelist files exist" || w "var/state whitelist files missing (environment may vary)"

if printf "%s\n" "$bk_block" | grep -q 'var/state/backup_refs\.json' && printf "%s\n" "$bk_block" | grep -q 'var/state/restore_slo\.jsonl'; then
  p "policy.backup.include lists var/state whitelist files"
else
  f "policy.backup.include missing var/state whitelist files"
fi

if printf "%s\n" "$ret_block" | grep -q 'var/state/backup_refs\.json' && printf "%s\n" "$ret_block" | grep -q 'var/state/restore_slo\.jsonl'; then
  p "retention.overrides includes var/state files"
else
  f "retention.overrides missing var/state files"
fi

RSYNC_STATE=$(rsync -nav --include='var/' --include='var/state/' --include='var/state/backup_refs.json' --include='var/state/restore_slo.jsonl' --exclude='*' ./ "$TMP/" 2>/dev/null | grep -E '^var/state/' || true)
[ -n "$RSYNC_STATE" ] && p "rsync includes var/state whitelist files" || f "rsync did NOT include var/state whitelist files"

# 7) destructive routines check
DEL_HITS=$(grep -RInE 'rm[[:space:]]+-rf|rm[[:space:]]+-r|find[[:space:]].*-delete|trash' scripts tools 2>/dev/null | grep -vE '\.md|\.rst' || true)
if printf "%s\n" "$DEL_HITS" | grep -qE 'var/reports|var/state'; then
  f "Destructive routine targets var/reports or var/state"; printf "%s\n" "$DEL_HITS" | grep -E 'var/reports|var/state' || true
else
  p "No destructive routines targeting var/reports/var/state"
fi

# 8) repo_guard / hooks disabled
if grep -q '^# --- DuRi repo guards ---' .gitignore 2>/dev/null; then
  f "repo_guard injection signature found in .gitignore"
else
  p "No repo_guard injection signature in .gitignore"
fi
if git config --local --get core.hooksPath >/dev/null 2>&1; then
  hookp=$(git config --local --get core.hooksPath || true)
  if [ -n "${hookp:-}" ]; then
    f "core.hooksPath is set to '$hookp'"
  else
    p "core.hooksPath not set"
  fi
else
  p "core.hooksPath not set"
fi
[ -d ".githooks" ] && w ".githooks/ directory exists" || p "No .githooks/ directory"

# 9) workflows/refs (informational)
if grep -RInq 'var/reports/' .github/workflows 2>/dev/null; then
  echo "NOTE workflows reference var/reports/** (OK & consistent)"
fi

echo "Summary: PASS=$PASS_C WARN=$WARN_C FAIL=$FAIL_C"
[ $FAIL_C -eq 0 ] || exit 1
exit 0





