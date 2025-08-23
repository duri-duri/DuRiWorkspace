#!/usr/bin/env bash
set -euo pipefail

# Defaults
DO_TAG=0              # 0=off, 1=on (선택적: 앵커 태그 생성)
DO_STASH=0            # 0=off, 1=on (선택적: 변경사항 stash)
SUBMODULE_MODE="none" # none|reset
DO_COMMIT=0           # 0=stage만, 1=커밋까지
COMMIT_MSG="repo guards: ignore runtime & learning state; add pre-commit; canary+backup coexist"
DRYRUN=0

usage () {
  cat <<'USAGE'
repo_guard_setup.sh [options]
  --tag                 # WIP 앵커 태그 생성
  --stash               # 현재 변경사항 임시 보관(stash -u)
  --submodules reset    # 모든 서브모듈 hard reset/clean
  --commit              # 변경사항 커밋까지 수행
  -m, --message "<msg>" # 커밋 메시지 지정
  --dry-run             # 실행 내용만 출력
  -h, --help
USAGE
}

say(){ echo "[$(date +%T)] $*"; }
run(){ if [[ $DRYRUN -eq 1 ]]; then echo "DRYRUN> $*"; else eval "$@"; fi; }

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag) DO_TAG=1; shift;;
    --stash) DO_STASH=1; shift;;
    --submodules) SUBMODULE_MODE="${2:-none}"; shift 2;;
    --commit) DO_COMMIT=1; shift;;
    -m|--message) COMMIT_MSG="$2"; shift 2;;
    --dry-run) DRYRUN=1; shift;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 2;;
  esac
done

# Sanity
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "Not a git repo."; exit 2; }
ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"

say "Repo: $ROOT"
say "Options: tag=$DO_TAG stash=$DO_STASH submodules=$SUBMODULE_MODE commit=$DO_COMMIT dryrun=$DRYRUN"

# 1) (옵션) 안전 앵커 / 스태시
if [[ $DO_TAG -eq 1 ]]; then
  TAG="WIP_SAFE_ANCHOR_$(date +%F__%H%M)"
  run "git tag -f $TAG"
  say "Tagged $TAG"
fi
if [[ $DO_STASH -eq 1 ]]; then
  run "git stash push -u -m 'repo-guard preflight $(date +%F__%H%M)'"
fi

# 2) 리포 가드: .gitignore + pre-commit 훅
say "Setting .gitignore guards"
IGNORE_BLOCK=$'# --- DuRi repo guards ---\n.local/\nvar/\n__pycache__/\n*.pyc\nlearning_journal/state.json\n'
if ! grep -q "DuRi repo guards" .gitignore 2>/dev/null; then
  run "printf '%s' \"$IGNORE_BLOCK\" >> .gitignore"
fi

say "Installing pre-commit hook"
run "mkdir -p .githooks var/backups"
run ": > var/backups/.gitkeep"
HOOK=".githooks/pre-commit"
cat > /tmp/_precommit.$$ <<'HOOK'
#!/usr/bin/env bash
set -euo pipefail
STAGED="$(git diff --cached --name-only || true)"
if echo "$STAGED" | grep -E '^(var/|\.local/)' >/dev/null; then
  echo "❌ Commit rejected: var/ or .local/ must not be committed."; exit 1
fi
exit 0
HOOK
run "install -m 0755 /tmp/_precommit.$$ $HOOK"
rm -f /tmp/_precommit.$$ 
run "git config core.hooksPath .githooks"

# 3) 이미 추적 중인 산출물 "추적 해제"(파일은 보존)
say "Untracking runtime/learning outputs (files stay on disk)"
run "git rm --cached -r --ignore-unmatch var/ .local/ learning_journal/state.json __pycache__ || true"
# pyc 전체
mapfile -t TRACKED_PYC < <(git ls-files '*.pyc' || true)
if [[ ${#TRACKED_PYC[@]} -gt 0 ]]; then
  run "git rm --cached --ignore-unmatch ${TRACKED_PYC[*]} || true"
fi

# 4) (옵션) 서브모듈 원복(원치 않으면 생략)
if [[ "$SUBMODULE_MODE" == "reset" ]]; then
  say "Hard-reset submodules"
  run "git submodule foreach --recursive 'git reset --hard || true; git clean -fdx || true'"
  run "git submodule update --init --recursive"
fi

# Stage & (옵션) Commit
say "Staging guard changes"
run "git add .gitignore .githooks var/backups/.gitkeep || true"

if [[ $DO_COMMIT -eq 1 ]]; then
  if git diff --cached --quiet; then
    say "Nothing to commit."
  else
    run "git commit -m \"$COMMIT_MSG\""
    say "Committed."
  fi
else
  say "Changes are staged. (use --commit to commit automatically)"
fi

say "Done. ✅"







