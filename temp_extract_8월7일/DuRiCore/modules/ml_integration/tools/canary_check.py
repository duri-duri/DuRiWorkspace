#!/usr/bin/env python3
import json, sys
from pathlib import Path
import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
from model_io import latest_model_path

ART = ROOT / "artifacts_phase1"
CANARY = ART / "canary_set.csv"
BASE = ART / "canary_metrics_baseline.json"

def load_model_safely():
    # 명시적 파일이 있으면 우선, 없으면 최신 모델 자동 탐색
    explicit = ART / "final_model.pkl"
    path = explicit if explicit.exists() else latest_model_path(ART)
    if not path:
        raise FileNotFoundError("no model file found in artifacts_phase1")
    try:
        return joblib.load(path), path
    except Exception as e:
        raise RuntimeError(f"failed to load model ({path.name}): {e}")

def expected_feature_names(model):
    """
    모델이 학습 시 사용한 컬럼 이름을 최대한 안전하게 추출.
    - RandomForest 등 sklearn estimator: feature_names_in_
    - 파이프라인인 경우 마지막 스텝(estimator)에 물려 있으면 그쪽에서 시도
    """
    # 1) 모델 자체
    names = list(getattr(model, "feature_names_in_", []))
    if names: return list(names)

    # 2) sklearn Pipeline 이라면 마지막 스텝에서 재시도
    try:
        from sklearn.pipeline import Pipeline
        if isinstance(model, Pipeline):
            final_est = model.steps[-1][1]
            names = list(getattr(final_est, "feature_names_in_", []))
            if names: return list(names)
    except Exception:
        pass
    return []  # 못 찾으면 빈 리스트

def eval_canary(model, df):
    y = df["target"].values
    X = df.drop(columns=["target"])

    # ✅ 핵심: 학습 시 사용한 컬럼만 선택 (순서까지 맞추기)
    exp = expected_feature_names(model)
    if exp:
        missing = [c for c in exp if c not in X.columns]
        extras  = [c for c in X.columns if c not in exp]
        if extras:
            print(f"[CANARY] dropping extra columns: {extras}")
        if missing:
            raise ValueError(f"required features missing in canary CSV: {missing}")
        X = X[exp]  # 순서까지 동일하게

    pred = model.predict(X)
    mse = float(((pred - y) ** 2).mean())
    ybar = float(y.mean())
    ss_tot = float(((y - ybar) ** 2).sum())
    ss_res = float(((y - pred) ** 2).sum())
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0.0
    return {"r2": r2, "mse": mse}

def main():
    assert CANARY.exists(), f"canary not found: {CANARY}"
    df = pd.read_csv(CANARY)
    model, mpath = load_model_safely()
    cur = eval_canary(model, df)

    if BASE.exists():
        base = json.load(open(BASE))
        r2_drop = base["r2"] - cur["r2"]
        mse_ratio = cur["mse"] / max(base["mse"], 1e-12)
        print(f"[CANARY] cur={cur}, base={base}, r2_drop={r2_drop:.4f}, mse_ratio={mse_ratio:.3f}")
        # 게이트: r2_drop <= 0.02 AND mse_ratio <= 1.05
        if r2_drop > 0.02 or mse_ratio > 1.05:
            print("❌ CANARY GATE FAIL → stop.")
            sys.exit(2)
        print("✅ CANARY PASS")
    else:
        json.dump(cur, open(BASE, "w"), indent=2, ensure_ascii=False)
        print(f"[CANARY] baseline saved → {BASE}")
        print("✅ CANARY BASELINE SET")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
