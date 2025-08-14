#!/usr/bin/env python3
import json, shutil, hashlib, time
from pathlib import Path

ART  = Path("artifacts_phase1")
PROD = Path("artifacts_prod")
PROD.mkdir(exist_ok=True)

# === Promote gate (절대+상대) ===
GATE_ABS_PROMOTE = dict(
    max_r2_gap=0.02,      # 원래 엄격한 기준 복원
    max_mse_ratio=1.10,   # 원래 엄격한 기준 복원
    max_nrmse_ratio=1.20, # 원래 엄격한 기준 복원
    min_test_r2=0.80      # 절대 기준 강화 (원래대로)
)
REL = dict(
    min_delta_test_r2=0.000,
    allow_within=0.010  # 승격은 동급 허용 (기존: 0.005)
)

def _abs_gap_ok(m):
    g = m.get("gap_analysis", {})
    return (
        g.get("r2_gap", 1)   <= GATE_ABS_PROMOTE["max_r2_gap"] and
        g.get("mse_ratio", 1e9)   <= GATE_ABS_PROMOTE["max_mse_ratio"] and
        g.get("nrmse_ratio", 1e9) <= GATE_ABS_PROMOTE["max_nrmse_ratio"]
    )

def load_current_metrics():
    return json.loads((ART / "final_metrics_valid_test.json").read_text(encoding="utf-8"))

def load_prod_baseline_r2():
    """prod/stable이 있으면 그 안의 PROMOTED.json 기준, 없으면 현재 metrics를 베이스라인으로."""
    stable = PROD / "stable"
    if stable.exists() and stable.is_symlink():
        try:
            stable_path = stable.resolve()
            meta = json.loads((stable_path / "PROMOTED.json").read_text(encoding="utf-8"))
            return meta["metrics"]["test"]["r2"]
        except (FileNotFoundError, KeyError):
            pass
    # 초기 배포 전: 현재 파일 기준
    return json.loads((ART / "final_metrics_valid_test.json").read_text(encoding="utf-8"))["test"]["r2"]

def gate_pass_promote(m, base_r2):
    if not _abs_gap_ok(m):
        return False, "abs_gap"
    test_r2 = m["test"]["r2"]
    if test_r2 < GATE_ABS_PROMOTE["min_test_r2"]:
        return False, "abs_floor"
    # 기본: 개선 +0.005 원칙 복원 (동급 승격 제한)
    min_delta = max(REL["min_delta_test_r2"], 0.005)
    rel_ok = test_r2 >= base_r2 + min_delta
    return (rel_ok, "ok" if rel_ok else "rel")

def sha256(p: Path):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()

def log_fail(reason, m, base_r2):
    """승격 실패 이력 기록"""
    fail_log = PROD / "promote_fail_log.jsonl"
    entry = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "base_test_r2": base_r2,
        "current_test_r2": m["test"]["r2"],
        "reason": reason,
        "metrics": m
    }
    with open(fail_log, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def main():
    m = load_current_metrics()
    base_r2 = load_prod_baseline_r2()
    ok, reason = gate_pass_promote(m, base_r2)
    print(f"[PROMOTE] baseR2={base_r2:.4f} testR2={m['test']['r2']:.4f} reason={reason} -> {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("[PROMOTE] aborted (gate not satisfied)")
        log_fail(reason, m, base_r2)
        return

    stamp = time.strftime("%Y%m%d_%H%M%S")
    bundle = (PROD / f"phase1_{stamp}")
    bundle.mkdir()

    files = [
        "final_model.pkl",
        "final_metrics_valid_test.json",
        max(ART.glob("snapshot_*.json"), key=lambda p: p.stat().st_mtime).name,
        max(ART.glob("summary_*.json"),  key=lambda p: p.stat().st_mtime).name,
    ]
    manifest = []
    for name in files:
        src = ART / name
        dst = bundle / name
        shutil.copy2(src, dst)
        manifest.append({"file": name, "sha256": sha256(dst)})

    meta = {
        "tag": f"promoted_{stamp}",
        "metrics": m,
        "files": manifest,
        "source_dir": str(ART.resolve()),
        "baseline_test_r2": base_r2,
        "gate_reason": reason,
    }
    (bundle / "PROMOTED.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    for link in ["latest", "stable"]:
        p = PROD / link
        if p.exists() or p.is_symlink():
            p.unlink()
        p.symlink_to(bundle.name)

    print(f"[PROMOTE] -> {bundle}")
    print(f"[PROMOTE] symlinks updated: {PROD / 'latest'} , {PROD / 'stable'}")

if __name__ == "__main__":
    main()
