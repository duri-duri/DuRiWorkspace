from __future__ import annotations
import argparse, json, os, sys, time, hashlib
from pathlib import Path
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
    ap.add_argument("--variant", choices=["A","B"], required=True)
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

    # --- 코어 러너 호출 (게이트 훅 포함) ---
    from src.ab.core_runner import run_ab_with_gate  # type: ignore
    
    # 게이트 정책 설정 읽기
    promotion_cfg = cfg.get("promotion", {}) or {}
    policy_rel = promotion_cfg.get("policy")
    policy_path = str(Path(policy_rel).resolve()) if policy_rel else None
    gate_enabled = bool(promotion_cfg.get("enabled", False))

    results = run_ab_with_gate(
        day=args.day,
        variant=args.variant,
        seed=args.seed,
        cfg=cfg,
        gate_policy_path=(policy_path if gate_enabled else None),
    )

    # 결과 저장
    write_json(out_dir / "results.json", results)
    meta["end_ts"] = int(time.time())
    write_json(out_dir / "run_meta.end.json", meta)

    # 콘솔 요약 (게이트 상태 포함)
    primary = cfg["metrics"]["primary"]
    gate_status = results.get("gate_pass")
    gate_str = f" gate={gate_status}" if gate_status is not None else ""
    print(f"[OK] Day{args.day} VAR={args.variant} {primary}={results.get(primary)} p={results.get('p_value')}{gate_str}")

if __name__ == "__main__":
    main()
