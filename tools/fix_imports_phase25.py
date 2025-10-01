import pathlib
import re
import sys

PKG = "duri_finale"
root = pathlib.Path(__file__).resolve().parents[1]
tgt = root / PKG

# 패턴들
pat_from = re.compile(r"^\s*from\s+\.(\w+)\s+import\s+", re.M)
pat_import = re.compile(r"^\s*import\s+\.(\w+)\s*$", re.M)
pat_from_parent = re.compile(r"^\s*from\s+\.\.(\w+)\s+import\s+", re.M)

changed = 0
for py in tgt.glob("*.py"):
    s = py.read_text(encoding="utf-8")
    s2 = s

    # from .mod import X -> from duri_finale.mod import X
    s2 = pat_from.sub(lambda m: f"from {PKG}.{m.group(1)} import ", s2)
    # import .mod -> from duri_finale import mod
    s2 = pat_import.sub(lambda m: f"from {PKG} import {m.group(1)}", s2)
    # from ..mod import X -> 상대 2단계는 패키지 경계 밖이므로 금지: 일단 duri_finale.mod로 승격
    s2 = pat_from_parent.sub(lambda m: f"from {PKG}.{m.group(1)} import ", s2)

    if s2 != s:
        py.write_text(s2, encoding="utf-8")
        changed += 1
print(f"fixed files: {changed}")
