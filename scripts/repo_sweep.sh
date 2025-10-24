#!/bin/bash
set -euo pipefail
echo "🧹 Repo sweep 시작..."
git fetch origin
git reset --hard origin/main
git ls-files -o --exclude-standard > /tmp/untracked.txt
tar -czf ~/untracked_backup_$(date +%Y%m%d_%H%M%S).tar.gz -T /tmp/untracked.txt --ignore-failed-read || true
git clean -fdx
sudo rm -rf data/prometheus grafana/data loop_data 2>/dev/null || true
git submodule sync -- 'duri_*_legacy'
git -c submodule.recurse=false submodule update --init --depth 1 -- 'duri_*_legacy'
git status
echo "✅ Sweep 완료!"
