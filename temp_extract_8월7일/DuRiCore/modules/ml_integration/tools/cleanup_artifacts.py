#!/usr/bin/env python3
import argparse, os, time, re

KEEP_PATTERNS=[
    r"registry/current\.json$",
    r"registry/model_.*\.json$",
    r"artifacts_phase1/monitor/.*\.json$",
    r"artifacts_phase1/canary/.*\.json$",
    r"artifacts_phase1/summary_.*\.json$",
    r"artifacts_phase1/snapshot_.*\.json$",
]

def keep(path):
    for p in KEEP_PATTERNS:
        if re.search(p, path): return True
    return False

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--days", type=int, default=14)
    args=ap.parse_args()

    cutoff=time.time()-args.days*86400
    removed=0
    for root,_,files in os.walk(args.root):
        for fn in files:
            p=os.path.join(root,fn)
            try:
                st=os.stat(p)
            except FileNotFoundError:
                continue
            if keep(p): continue
            if st.st_mtime<cutoff:
                try:
                    os.remove(p); removed+=1
                except Exception:
                    pass
    print(f"[CLEANUP] removed {removed} files older than {args.days} days (keep list honored)")

if __name__=="__main__":
    main()

