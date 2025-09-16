#!/bin/bash

GIT_REPOS=(
  "/home/duri/duri-core"
  "/mnt/remote/db_secure"
  "/mnt/remote/de_secure"
)

LOG_FILE="/home/duri/logs/git_backup_system.log"
timestamp=$(date "+%Y-%m-%d_%H-%M")

for REPO in "${GIT_REPOS[@]}"; do
  echo "[$timestamp] 🔍 Checking: $REPO" >> "$LOG_FILE"

  if [ ! -d "$REPO/.git" ]; then
    echo "[$timestamp] ❌ Not a git repo: $REPO" >> "$LOG_FILE"
    continue
  fi

  cd "$REPO" || continue
  git add .
  git commit -m "⏱️ Auto commit: $timestamp" >> "$LOG_FILE" 2>&1
  git stash push -u -m "stash $timestamp" >> "$LOG_FILE" 2>&1
  git pull origin main --rebase >> "$LOG_FILE" 2>&1
  git stash pop >> "$LOG_FILE" 2>&1
  git push origin main >> "$LOG_FILE" 2>&1
  git tag "snapshot_$timestamp" >> "$LOG_FILE" 2>&1
  git push origin --tags >> "$LOG_FILE" 2>&1
done
