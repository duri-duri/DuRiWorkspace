#!/usr/bin/env python3
import json, hashlib, os, sys, time, pathlib

SNAP = sys.argv[1] if len(sys.argv) > 1 else "artifacts_phase1/snapshot_1755047836.json"
snap_p = pathlib.Path(SNAP)
assert snap_p.exists(), f"snapshot not found: {snap_p}"

raw = snap_p.read_bytes()
sha256 = hashlib.sha256(raw).hexdigest()

data = json.loads(raw)
meta = data.setdefault("meta", {})
tags = set(meta.get("tags", []))
tags.update({"freeze"})
meta["tags"] = sorted(tags)
meta["promoted_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
meta["sha256"] = sha256

out_dir = pathlib.Path("artifacts_phase1/frozen")
out_dir.mkdir(parents=True, exist_ok=True)
out_f = out_dir / f"{snap_p.stem}_FREEZE.json"
out_f.write_text(json.dumps(data, ensure_ascii=False, indent=2))

# 심볼릭 링크로 최신 freeze 가리키기
latest = out_dir / "current_freeze.json"
if latest.exists() or latest.is_symlink():
    latest.unlink()
latest.symlink_to(out_f.name)

print("✅ Freeze promotion complete")
print(f" - input : {snap_p}")
print(f" - output: {out_f}")
print(f" - sha256: {sha256}")

