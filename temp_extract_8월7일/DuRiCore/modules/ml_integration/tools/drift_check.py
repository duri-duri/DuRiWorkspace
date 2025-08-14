# tools/drift_check.py
import json, sys, argparse, os
from pathlib import Path

def load_json(p: Path, required=True):
    if not p.exists():
        if required:
            print(f"[ERR] missing file: {p}", file=sys.stderr)
            sys.exit(3)
        return {}
    return json.load(open(p))

def pct(x): 
    try: return f"{float(x):.3f}"
    except: return str(x)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artdir", default="artifacts_phase1")
    ap.add_argument("--baseline", default="schema_expectations_baseline.json")
    # 임계값은 인자/환경변수로도 바꿀 수 있게
    ap.add_argument("--na_delta", type=float, default=float(os.getenv("DRIFT_NA_DELTA", "0.02")))
    ap.add_argument("--outlier_delta", type=float, default=float(os.getenv("DRIFT_OUTLIER_DELTA", "0.10")))
    ap.add_argument("--target_iqr_ratio", type=float, default=float(os.getenv("DRIFT_TARGET_IQR_RATIO", "1.15")))
    args = ap.parse_args()

    ART = Path(args.artdir)
    
    # 외부 파일 주입 지원 (테스트용)
    BASE_FILE = os.getenv("DRIFT_BASE_FILE")
    CUR_FILE = os.getenv("DRIFT_CURRENT_FILE")
    
    if BASE_FILE:
        base = load_json(Path(BASE_FILE))
    else:
        base = load_json(ART / args.baseline)
    
    if CUR_FILE:
        cur = load_json(Path(CUR_FILE))
    else:
        # 최신 D1 리포트에서 현재 스키마 기대치 읽기
        latest = max(ART.glob("error_slicing_*.json"), key=lambda p: p.stat().st_mtime)
        cur = load_json(latest)["schema_expectations"]

    notes = []

    # NA율 증가 체크
    for col, b in base.get("na_rate", {}).items():
        c = cur.get("na_rate", {}).get(col, 0.0)
        if (c - b) > args.na_delta:
            notes.append(f"NA↑ {col}: {pct(b)}→{pct(c)} (>{args.na_delta:.2f})")

    # IQR 기반 이상치율 증가 체크
    for col, bsum in base.get("numeric_summary", {}).items():
        csum = cur.get("numeric_summary", {}).get(col, {})
        if "outlier_rate_iqr" in bsum and "outlier_rate_iqr" in csum:
            if (csum["outlier_rate_iqr"] - bsum["outlier_rate_iqr"]) > args.outlier_delta:
                notes.append(f"Outlier↑ {col}: {pct(bsum['outlier_rate_iqr'])}→{pct(csum['outlier_rate_iqr'])} (>{args.outlier_delta:.2f})")

    # 타깃 IQR 비대 증가 체크
    bIQ = base.get("target_summary", {}).get("iqr")
    cIQ = cur.get("target_summary", {}).get("iqr")
    if bIQ and cIQ and (cIQ / bIQ) > args.target_iqr_ratio:
        notes.append(f"Target IQR↑ {bIQ:.3f}→{cIQ:.3f} (>{args.target_iqr_ratio:.2f}x)")

    if notes:
        print("DRIFT CHECK: WARN")
        for n in notes:
            print(" -", n)
        # 경고는 2로 종료 → 상위 자동화에서 "스윕/진화 SKIP" 트리거용
        sys.exit(2)
    else:
        print("DRIFT CHECK: OK")
        sys.exit(0)

if __name__ == "__main__":
    main()
