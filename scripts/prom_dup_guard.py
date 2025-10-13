#!/usr/bin/env python3
import glob
import re
import sys

names = []
pat = re.compile(r"^\s*-\s*record:\s*([^\s#]+)")
for p in glob.glob("prometheus/rules/**/*.y*ml", recursive=True):
    with open(p, encoding="utf-8") as f:
        for line in f:
            m = pat.match(line)
            if m:
                names.append(m.group(1))
dups = sorted({n for n in names if names.count(n) > 1})
if dups:
    [print("DUP record:", d) for d in dups]
    sys.exit(1)
