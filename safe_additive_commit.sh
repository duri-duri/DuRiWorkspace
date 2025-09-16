#!/usr/bin/env bash
set -euo pipefail
branch="feat/additive_$(date +%y%m%d_%H%M)"
git switch -c "$branch"

# 수정/추가 작업은 여기서…
# 권장 위치: DuRiCore/reasoning_engine/{strategies,optimization,integration}

# 변경사항 확인
git status --porcelain

# 스테이징(추가/수정만, 삭제 자동 제외)
git add -A
# 혹시라도 삭제가 들어갔으면 제거
git restore --staged $(git diff --cached --name-status | awk '$1=="D"{print $2}') 2>/dev/null || true

# 빠른 로컬 테스트(프리커밋이 또 확인함)
pytest -q tests/contracts -k "reasoning or reasoning_smoke" || exit 1

git commit -m "additive: new modules/scaffolds only (no deletions)"
echo "[OK] branch $branch committed."
