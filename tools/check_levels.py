#!/usr/bin/env python3
import glob
import json
import os
import sys

base = sys.argv[1] if len(sys.argv) > 1 else "."


def pick(pattern):
    cands = sorted(glob.glob(os.path.join(base, pattern)))
    return cands[-1] if cands else None


def load_manifest(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:  # noqa: E722
        return {}


# 단순 근사: filelist 아티팩트로 대체
def load_set(prefix):
    fl = pick(f"filelist.{prefix}.*.txt")
    if not fl:
        return set()
    with open(fl, "r", encoding="utf-8") as f:
        return set(x.strip() for x in f if x.strip())


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


core = load_set("CORE")
ext = load_set("EXTENDED")
full = load_set("FULL")
j_ce = jaccard(core, ext)
j_ef = jaccard(ext, full)
print(f"Jaccard(core,ext)={j_ce:.3f}  Jaccard(ext,full)={j_ef:.3f}")

# 임계 위반 시 실패
th_ce = float(os.environ.get("THRESH_CE", "0.70"))
th_ef = float(os.environ.get("THRESH_EF", "0.60"))
if j_ce < th_ce or j_ef < th_ef:
    print("THRESHOLD VIOLATION")
    sys.exit(2)
