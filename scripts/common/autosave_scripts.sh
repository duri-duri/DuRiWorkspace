#!/bin/bash
set -Eeuo pipefail
cd ~/duri-all-scripts || exit 1

# 최신 내용 반영
git pull origin main --rebase

# 자동 커밋 실행
bash /home/duri/scripts/auto_commit.sh >> /home/duri/logs/script_autosave.log 2>&1
