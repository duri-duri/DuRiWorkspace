#!/usr/bin/env bash
set -euo pipefail

# === Config ===
ROOT="${ROOT:-$HOME/DuRiWorkspace}"
POLICY="${POLICY:-$ROOT/policies/auto_code_loop/gate_policy.yaml}"
LOGDIR="${LOGDIR:-$HOME/.local/duri/logs/auto_code_loop_beta/$(date +%F)}"
REGRESSION="${REGRESSION:-$ROOT/run_regression_tests.sh}"
SECURITY_CHECK="${SECURITY_CHECK:-$ROOT/tools/policy_verify.sh}"
RESTORE_SMOKE="${RESTORE_SMOKE:-$ROOT/scripts/smoke_restore_test.sh}"
CANARY_PIPELINE="${CANARY_PIPELINE:-$ROOT/tools/canary_pipeline.sh}"
BRANCH="${BRANCH:-gate-test}"
TAG="day15-beta-$(date +%F_%H%M)"
BUDGET_TOKENS="${BUDGET_TOKENS:-120000}"     # per-PR
BUDGET_MINUTES="${BUDGET_MINUTES:-20}"       # per-PR
PR_LIMIT_PER_DAY="${PR_LIMIT_PER_DAY:-3}"    # per-day
DRY_RUN="${DRY_RUN:-0}"                      # 1: simulate

mkdir -p "$LOGDIR"
# [logging disabled: handled by wrapper]

echo "[INFO] Day15 auto-code-loop beta start @ $(date)"
echo "[INFO] ROOT=$ROOT BRANCH=$BRANCH LOGDIR=$LOGDIR POLICY=$POLICY"

cd "$ROOT"
# DRY_RUN일 때는 브랜치 체크 무시
if [[ "$DRY_RUN" != "1" ]]; then
  git rev-parse --abbrev-ref HEAD | grep -qx "$BRANCH" || { echo "[ERR] not on $BRANCH"; exit 2; }
fi

# === Gate 0: policy file exists ===
[[ -s "$POLICY" ]] || { echo "[ERR] policy not found: $POLICY"; exit 2; }

# === Gate 1: Rate limit (<= 3 PR/day) ===
COUNT_TODAY="$(git log --since "$(date +%F) 00:00" --pretty=format:%s | grep -c '\[auto-code-loop\] PR')"
if (( COUNT_TODAY >= PR_LIMIT_PER_DAY )); then
  echo "[STOP] PR/day limit reached ($COUNT_TODAY >= $PR_LIMIT_PER_DAY)"
  exit 0
fi

# === Phase: PLAN ===
echo "[PLAN] generating patch plan under whitelist"
PLAN_JSON="$LOGDIR/plan.json"
echo "[DEBUG] entering PLAN @ $(date)"
timeout 20s python3 - "$POLICY" >"$PLAN_JSON" <<'PY'
import sys, yaml, glob, os, json
policy = sys.argv[1]
with open(policy, "r", encoding="utf-8") as f:
    p = yaml.safe_load(f)
wl = p.get("whitelist", [])
cands = []
for w in wl:
    cands += glob.glob(w, recursive=True)
targets = [x for x in cands if os.path.isfile(x) and x.endswith((".py",".sh",".md",".yaml",".yml"))]
plan = [{"file": t, "action": "small_refactor", "reason": "lint/perf/doc"} for t in sorted(targets)[:p.get("plan_max_files", 5)]]
json.dump({"plan": plan}, sys.stdout, ensure_ascii=False, indent=2)
PY
rc=$?; echo "[DEBUG] PLAN exit=$rc @ $(date)"; if [ $rc -ne 0 ]; then echo "[FAIL] PLAN generation timeout or error"; exit 2; fi
# === Phase: EDIT (apply tiny patches) ===
echo "[EDIT] applying minimal patches"
timeout 20s python3 - <<'PY' "$PLAN_JSON"
import json, sys, io, re, os
plan_path = sys.argv[1]
plan = json.load(open(plan_path))
def touchup_text(s):
    s = re.sub(r'[ \t]+$', '', s, flags=re.MULTILINE)         # trim EOL spaces
    s = re.sub(r'\n{3,}', '\n\n', s)                           # collapse blank lines
    return s
for item in plan["plan"]:
    fp = item["file"]
    if not os.path.exists(fp):
        continue
    try:
        if fp.endswith(('.py', '.sh', '.md', '.yaml', '.yml')):
            with open(fp, 'r', encoding='utf-8') as f:
                src = f.read()
            new = touchup_text(src)
            if new != src:
                with open(fp, 'w', encoding='utf-8') as f:
                    f.write(new)
                print(f"[PATCH] normalized: {fp}")
    except Exception as e:
        print(f"[SKIP] {fp}: {e}")
PY

# === Gate 3: Unit & Regression ===
echo "[TEST] unit & regression"
set +e
UNIT_OK=0; REG_OK=0; SEC_OK=0; ROLLBACK_OK=0

# Unit tests (if exists)
if [ -f "pytest.ini" ] || ls tests/*.py >/dev/null 2>&1; then
  pytest -q | tee "$LOGDIR/unit.log"
  [[ ${PIPESTATUS[0]} -eq 0 ]] && UNIT_OK=1
else
  echo "[NOTE] no unit tests → mark pass"
  UNIT_OK=1
fi

# Regression 12-tasks
if [ -x "$REGRESSION" ]; then
  "$REGRESSION" | tee "$LOGDIR/regression.log"
  [[ ${PIPESTATUS[0]} -eq 0 ]] && REG_OK=1
else
  echo "[WARN] regression script missing: $REGRESSION"
fi

# Security/policy again (post-edit)
bash "$SECURITY_CHECK" --policy "$POLICY" --scan | tee "$LOGDIR/security.log"
[[ ${PIPESTATUS[0]} -eq 0 ]] && SEC_OK=1

# Rollback smoke test
bash "$RESTORE_SMOKE" | tee "$LOGDIR/restore.log"
[[ ${PIPESTATUS[0]} -eq 0 ]] && ROLLBACK_OK=1
set -e

echo "[TEST-RESULT] unit=$UNIT_OK reg=$REG_OK sec=$SEC_OK rollback=$ROLLBACK_OK"

# === Promote Gate ===
if (( UNIT_OK && REG_OK && SEC_OK && ROLLBACK_OK )); then
  echo "[PROMOTE] all gates passed"
else
  echo "[STOP] gate not satisfied → no promote"
  exit 4
fi

# === Commit & PR (local tagging style) ===
git add -A
git commit -m "[auto-code-loop] PR: day15 beta patch (budget: ${BUDGET_TOKENS}t/${BUDGET_MINUTES}m) [policy:v1]" || true
git tag -f "$TAG" || true

# === Canary 10% ===
if (( DRY_RUN==1 )); then
  echo "[DRY_RUN] skip canary"
  exit 0
fi
if [ -x "$CANARY_PIPELINE" ]; then
  bash "$CANARY_PIPELINE" --percent 10 --annotate "day15 beta $TAG" | tee "$LOGDIR/canary.log"
else
  echo "[WARN] no canary pipeline: $CANARY_PIPELINE"
fi

echo "[DONE] Day15 auto-code-loop beta finished @ $(date)"
