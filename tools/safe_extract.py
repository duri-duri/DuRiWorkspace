#!/usr/bin/env python3
import argparse, subprocess, hashlib, sys, os
from pathlib import Path

def sha256_file(p: Path, chunk: int = 1<<20) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b: break
            h.update(b)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser(description="Extract one file from tar.zst with optional SHA256 verify")
    ap.add_argument("--archive", required=True, help="...tar.zst path")
    ap.add_argument("--inner-path", required=True, help="path inside tar (e.g., var/checkpoints/best.ckpt)")
    ap.add_argument("--out", required=True, help="output file path")
    ap.add_argument("--sha256", default="", help="expected sha256")
    args = ap.parse_args()

    archive = Path(args.archive)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    # tar -xOf: extract to stdout; zstd -dc: decompress to stdout
    cmd = f"zstd -dq -c '{archive}' | tar -xOf - '{args.inner_path}'"
    with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE) as p, out.open("wb") as f:
        while True:
            chunk = p.stdout.read(1<<20)
            if not chunk: break
            f.write(chunk)
        rc = p.wait()
        if rc != 0:
            print(f"[ERR] extract failed (rc={rc})", file=sys.stderr); sys.exit(2)

    if args.sha256:
        got = sha256_file(out)
        if got.lower() != args.sha256.lower():
            print(f"[ERR] sha256 mismatch: {got}", file=sys.stderr); sys.exit(3)
    print("[OK] extracted:", out)

if __name__ == "__main__":
    main()
