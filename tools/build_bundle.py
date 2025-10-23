import argparse
import hashlib
import json
import pathlib
import tarfile

import jcs


def sha256b(b):
    return hashlib.sha256(b).hexdigest()


def canonicalize(obj):
    return jcs.canonicalize(obj)  # RFC-8785 bytes


def merkle_root(leaves):
    import hashlib

    L = [bytes.fromhex(h) for h in sorted(leaves)]
    if not L:
        return sha256b(b"")
    while len(L) > 1:
        if len(L) % 2 == 1:
            L.append(L[-1])
        L = [hashlib.sha256(L[i] + L[i + 1]).digest() for i in range(0, len(L), 2)]
    return L[0].hex()


ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="indir", required=True)
ap.add_argument("--out", dest="out", required=True)
ap.add_argument("--merkle", required=True)
ap.add_argument("--hash", required=True)
args = ap.parse_args()

# collect YAML/JSON → JCS bytes and write temp json
temp_dir = pathlib.Path(".bundle_tmp")
temp_dir.mkdir(exist_ok=True)
hashes = []
for rel in ["family.yml", "ops.yml", "manifest.yml", "schema/family.schema.json"]:
    p = pathlib.Path(args.indir) / rel
    if not p.exists():
        continue
    if p.suffix in [".yml", ".yaml"]:
        obj = __import__("yaml").safe_load(open(p, "r"))
    else:
        obj = json.load(open(p, "r"))
    blob = canonicalize(obj)
    outp = temp_dir / (rel.replace("/", "__") + ".json")
    outp.write_bytes(blob)
    hashes.append(sha256b(blob))

# Merkle (proper merkle tree)
root = merkle_root(hashes)
open(args.merkle, "w").write(root)
open(args.hash, "w").write(root)

with tarfile.open(args.out, "w:xz") as tf:
    for f in temp_dir.iterdir():
        tf.add(f, arcname=f.name)
