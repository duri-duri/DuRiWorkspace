#!/usr/bin/env python3
import sys, re, pathlib

ROOT = pathlib.Path(".")
ALLOW = {"core/trace_io.py"}  # 허용 파일 (필요 시 추가)
EXCLUDE_DIRS = {".git", ".venv", "tests", "bench", "artifacts_phase1"}

PAT = re.compile(r'\bprint\s*\(')

bad = []
for p in ROOT.rglob("*.py"):
    sp = str(p).replace("\\","/")
    if any(sp.endswith(x) for x in (".venv",)) or any(seg.startswith(".") for seg in p.parts):
        continue
    if any(part in EXCLUDE_DIRS for part in p.parts):
        continue
    if sp in ALLOW:
        continue
    try:
        s = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    if PAT.search(s):
        bad.append(sp)

if bad:
    sys.stderr.write("[STRAY-STDOUT] 'print(' 발견 파일 수: %d\n" % len(bad))
    for b in bad: sys.stderr.write(" - %s\n" % b)
    sys.exit(2)
# print("OK: no stray print()")
