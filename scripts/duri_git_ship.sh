#!/usr/bin/env bash
# duri_git_ship.sh : Desktop 최신본 기준 GitHub PR(ship)
set -Eeuo pipefail

REPO_DIR="${REPO_DIR:-/home/duri/DuRiWorkspace}"
BASE_BRANCH="${BASE_BRANCH:-main}"
BR_PREFIX="${BR_PREFIX:-ops}"
LOG_DIR="${LOG_DIR:-/var/log/duri2-backup}"
LOCK_FILE="${LOCK_FILE:-/var/lock/duri_git_ship.lock}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"
GH_LABELS="${GH_LABELS:-backup,automation}"
GH_DRAFT="${GH_DRAFT:-false}"
AUTO_MERGE="${AUTO_MERGE:-true}"
DRYRUN=0
DEBUG=0

usage(){ echo "Usage: $0 [--dry-run] [--debug] [--base BRANCH]"; }
while (( $# )); do
  case "$1" in
    --dry-run) DRYRUN=1 ;;
    --debug) DEBUG=1; LOG_LEVEL=DEBUG; set -x ;;
    --base) BASE_BRANCH="$2"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown arg: $1"; usage; exit 2;;
  esac; shift
done

mkdir -p "$LOG_DIR"; LOG_FILE="$LOG_DIR/git_ship.$(date +%Y%m%d_%H%M%S).log"
TS(){ date -Iseconds; }
jlog(){ local lvl="$1"; shift; local msg="$1"; shift||true; case "$LOG_LEVEL:$lvl" in
  DEBUG:DEBUG|INFO:DEBUG|INFO:INFO|WARN:DEBUG|WARN:INFO|WARN:WARN|ERROR:*) ;; *) return 0;; esac
  local kv=""; for x in "$@"; do kv="$kv,\"${x%%=*}\":\"${x#*=}\""; done
  printf '{"ts":"%s","level":"%s","msg":"%s"%s}\n' "$(TS)" "$lvl" "$msg" "${kv#*,}" | tee -a "$LOG_FILE"
}
exec 9>"$LOCK_FILE"; flock -n 9 || { echo "[skip] git-ship running"; exit 0; }

cd "$REPO_DIR"
git add -A
if git diff --cached --quiet; then
  jlog INFO "no_changes"; exit 0
fi

ts="$(date +%Y%m%d-%H%M%S)"
BR="$BR_PREFIX/$ts"
MSG="backup(ship): $ts"

if [[ $DRYRUN -eq 1 ]]; then
  jlog INFO "dry_run_commit" branch="$BR" base="$BASE_BRANCH"
  exit 0
fi

git checkout -B "$BR" "$BASE_BRANCH"
git commit -m "$MSG" --signoff
git push -u origin "$BR"
jlog INFO "branch_pushed" branch="$BR"

if command -v gh >/dev/null 2>&1; then
  PR_URL=$(gh pr create \
    --base "$BASE_BRANCH" --head "$BR" \
    --title "$MSG" \
    --body "Automated backup PR at $(date -Iseconds). Changes are code/scripts only." \
    $( [[ "$GH_DRAFT" == "true" ]] && echo --draft ) \
    --label "$GH_LABELS" )
  jlog INFO "pr_created" url="$PR_URL"
  if [[ "$AUTO_MERGE" == "true" ]]; then
    gh pr merge --squash --auto "$PR_URL"
    jlog INFO "auto_merge_requested"
  fi
else
  jlog WARN "gh_cli_missing"
fi

jlog INFO "git_ship_done"

