#!/bin/bash
cd ~/snapshots
git add .
git commit -m "📝 자동 기록: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main
