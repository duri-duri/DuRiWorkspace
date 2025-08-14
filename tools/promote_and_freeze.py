#!/usr/bin/env python3
import json, shutil, hashlib, time
from pathlib import Path

ART  = Path("artifacts_phase1")
PROD = Path("artifacts_prod")
PROD.mkdir(exist_ok=True)

# === Promote gate (절대+상대) ===
GATE_ABS_PROMOTE = dict(max_r2_gap=0.02, max_mse_ratio=1.10, max_nrmse_ratio=1.20, min_test_r2=0.80)
REL = dict(min_delta_test_r2=0.000, allow_within=0.005)  # 승격은 동급 불가(아래 rel_ok에서 +0.005 요구)

def _abs_gap_ok(m):
    g = m.get("gap_analysis", {})
    return (
        g.get("r2_gap", 1)   <= GATE_ABS_PROMOTE["max_r2_gap"] and
        g.get("mse_ratio", 1e9)   <= GATE_ABS_PROMOTE["max_mse_ratio"] and
        g.get("nrmse_ratio", 1e9) <= GATE_ABS_PROMOTE["max_nrmse_ratio"]
    )

def load_current_metrics():
    return json.loads((ART/"final_metrics_valid_test.json").read_text(encoding="utf-8"))

def load_prod_baseline_r2():
    """prod/stable이 있으면 그 안의 PROMOTED.json 기준, 없으면 현재 metrics를 베이스라인으로."""
    stable = PROD/"stable"
    if stable.exists() and stable.is_symlink():
        meta = json.loads((PROD/stable/"PROMOTED.json").read_text(encoding="utf-8"))
        return meta["metrics"]["test"]["r2"]
    # 초기 배포 전: 현재 파일 기준
    return json.loads((ART/"final_metrics_valid_test.json").read_text(encoding="utf-8"))["test"]["r2"]

def gate_pass_promote(m, base_r2):
    if not _abs_gap_ok(m):
        return False, "abs_gap"
    test_r2 = m["test"]["r2"]
    if test_r2 < GATE_ABS_PROMOTE["min_test_r2"]:
        return False, "abs_floor"
    rel_ok = test_r2 >= base_r2 + max(REL["min_delta_test_r2"], 0.005)  # 승격은 최소 +0.005 개선
    return (rel_ok, "ok" if rel_ok else "rel")

def sha256(p: Path):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for ch in iter(lambda:f.read(1<<20), b""): h.update(ch)
    return h.hexdigest()

def main():
    m = load_current_metrics()
    base_r2 = load_prod_baseline_r2()
    ok, reason = gate_pass_promote(m, base_r2)
    print(f"[PROMOTE] baseR2={base_r2:.4f} testR2={m['test']['r2']:.4f} reason={reason} -> {'PASS' if ok else 'FAIL'}")
    if not ok:
        # print("[PROMOTE] aborted (gate not satisfied)"); return

    stamp = time.strftime("%Y%m%d_%H%M%S")
    bundle = (PROD / f"phase1_{stamp}")
    bundle.mkdir()

    files = [
        "final_model.pkl",
        "final_metrics_valid_test.json",
        max(ART.glob("snapshot_*.json"), key=lambda p:p.stat().st_mtime).name,
        max(ART.glob("summary_*.json"),  key=lambda p:p.stat().st_mtime).name,
    ]
    manifest=[]
    for name in files:
        src = ART/name
        dst = bundle/name
        shutil.copy2(src, dst)
        manifest.append({"file": name, "sha256": sha256(dst)})

    meta = {
        "tag": f"promoted_{stamp}",
        "metrics": m,
        "files": manifest,
        "source_dir": str(ART.resolve()),
        "baseline_test_r2": base_r2,
        "gate_reason": "ok",
    }
    (bundle/"PROMOTED.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    for link in ["latest","stable"]:
        p = PROD/link
        if p.exists() or p.is_symlink(): p.unlink()
        p.symlink_to(bundle.name)

    print(f"[PROMOTE] -> {bundle}")
    print(f"[PROMOTE] symlinks updated: {PROD/'latest'} , {PROD/'stable'}")

if __name__ == "__main__":
    main()



