#!/usr/bin/env bash
set -euo pipefail
REPOS=(
  "/home/duri/DuRiWorkspace"
  "/home/duri/DuRiWorkspace/duri_brain"
  "/home/duri/DuRiWorkspace/duri_core"
)
LOG="/home/duri/logs/git_autosave.log"
mkdir -p "$(dirname "$LOG")"

for R in "${REPOS[@]}"; do
  [[ -d "$R/.git" ]] || { echo "skip $R (no git)"; continue; }
  pushd "$R" >/dev/null
  
  git add -A
  git diff --cached --quiet || git commit -m "autosave: $(date +'%F %T')"
  
  # 충돌 방지: pull --rebase, 실패 시 스킵(자율학습 코드 실행 방해 금지)
  if ! git pull --rebase --autostash -q; then
    echo "[WARN] pull conflict at $R, skip push" | tee -a "$LOG"
    popd >/dev/null; continue
  fi
  
  git push -q || echo "[WARN] push fail $R" | tee -a "$LOG"
  popd >/dev/null
done

echo "[OK] autosave $(date +'%F %T')" | tee -a "$LOG"
