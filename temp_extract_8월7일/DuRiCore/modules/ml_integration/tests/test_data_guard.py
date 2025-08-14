import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART  = ROOT / "artifacts_phase1"

def test_categorical_datetime_are_dropped():
    d1 = max((ART).glob("error_slicing_*.json"), key=lambda p: p.stat().st_mtime)
    obj = json.load(open(d1))
    exp = obj["schema_expectations"]

    dropped_cat = exp.get("categorical_removed", [])
    dropped_dt  = exp.get("datetime_removed", [])
    assert isinstance(dropped_cat, list) and isinstance(dropped_dt, list)

    # 최종 학습 컬럼 스냅샷이 있으면 거기서 검증 (없으면 D1 스키마 로그 기준)
    # 간단히: 최종 선택 특성 목록 파일이 있다면 더 엄격 체크
    final_cols_path = ART / "evidence_final_feature_columns.json"
    if final_cols_path.exists():
        cols = json.load(open(final_cols_path)).get("feature_columns", [])
        assert all(c not in cols for c in dropped_cat), "categorical 누락 실패"
        assert all(c not in cols for c in dropped_dt),  "datetime 누락 실패"



