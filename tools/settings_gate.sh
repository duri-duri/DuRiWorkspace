#!/usr/bin/env bash
set -Eeuo pipefail
python3 - <<'PY'
import os
os.environ["DURI_ENV"]="prod"
from duri_common.settings import DuRiSettings
s=DuRiSettings()
assert s.env=="prod", s.env
print("SETTINGS OK")
PY

