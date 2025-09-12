#!/usr/bin/env bash
set -euo pipefail

# 워크스페이스 루트 계산
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# PYTHONPATH: 루트 + 신구 패키지 경로 모두 등록
export PYTHONPATH="$ROOT:$ROOT/DuRiCore:$ROOT/duri_core:${PYTHONPATH:-}"

# (선택) pytest가 없다면 설치
command -v pytest >/dev/null 2>&1 || python3 -m pip install -U pytest >/dev/null

echo "[OK] PYTHONPATH set."
python3 -c "import sys;print('[PY]', *sys.path, sep='\n - ')" >/dev/null

# 빠른 계약 테스트 수집만 체크 (실행은 길 수 있으니 -q)
pytest -q tests/contracts || echo '[WARN] 계약 테스트 보완 필요'
