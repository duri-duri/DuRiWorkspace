from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time

import yaml

# 견고한 리포 루트 추정 (이 파일 기준)
REPO_ROOT = Path(__file__).resolve().parents[2]
os.chdir(REPO_ROOT)  # 상대경로( configs/, outputs/ )가 리포 기준으로 동작하도록


def load_yaml(p: Path):
    if not p.exists():
        raise FileNotFoundError(f"Config not found: {p}")
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def write_json(p: Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes() if path.exists() else b"")
    return h.hexdigest()[:12]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", type=int, required=True)
    ap.add_argument("--variant", choices=["A", "B"], required=True)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--config", type=str, required=True)
    args = ap.parse_args()

    cfg = load_yaml(Path(args.config))
    out_dir = Path(cfg["paths"]["outputs"]) / f"var_{args.variant}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 메타 기록
    meta = {
        "git_sha": os.popen("git rev-parse --short HEAD").read().strip() or "NA",
        "dirty": bool(os.popen("git status --porcelain").read().strip()),
        "config": args.config,
        "config_hash": file_hash(Path(args.config)),
        "seed": args.seed,
        "variant": args.variant,
        "day": args.day,
        "start_ts": int(time.time()),
    }
    write_json(out_dir / "run_meta.start.json", meta)

    # --- 코어 러너 호출 (기존 welch t 등) ---
    # src/ab/core_runner.py에 `run_ab`가 있다고 가정 (day35 러너의 래핑)
    from src.ab.core_runner import run_ab  # type: ignore

    results = run_ab(
        day=args.day,
        variant=args.variant,
        seed=args.seed,
        config=cfg,
    )

    # 결과 저장
    write_json(out_dir / "results.json", results)
    meta["end_ts"] = int(time.time())
    write_json(out_dir / "run_meta.end.json", meta)

    # 콘솔 요약
    primary = cfg["metrics"]["primary"]
    print(
        f"[OK] Day{args.day} VAR={args.variant} {primary}={results.get(primary)} p={results.get('p_value')}"
    )


if __name__ == "__main__":
    main()
