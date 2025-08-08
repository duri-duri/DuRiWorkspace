#!/bin/bash
cd /home/duri/duri-snapshots
git add .
git commit -m "🔄 snapshot auto backup on $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main
