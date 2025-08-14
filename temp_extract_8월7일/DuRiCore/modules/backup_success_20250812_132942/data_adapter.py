# data_adapter.py
from __future__ import annotations
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any

class RealDataAdapter:
    """
    실데이터 로더/검증/매핑 어댑터
    - 입력: 파일 경로 + 스키마 매핑(dict)
      schema_map = {
        "target": "y_col",
        "numeric": ["num1","num2",...],
        "categorical": ["cat1","cat2",...],      # 없으면 생략 가능
        "drop": ["id","timestamp"],               # 학습 제외
        "datetime": ["ts_col"],                   # 있으면 파싱
      }
    """
    def __init__(self, path: str, schema_map: Dict[str, Any], n_rows: Optional[int]=None):
        self.path = path
        self.schema_map = schema_map
        self.n_rows = n_rows
        self.df: Optional[pd.DataFrame] = None

    def load(self) -> pd.DataFrame:
        if self.path.endswith(".csv"):
            self.df = pd.read_csv(self.path, nrows=self.n_rows)
        elif self.path.endswith(".parquet"):
            self.df = pd.read_parquet(self.path)
            if self.n_rows:
                self.df = self.df.head(self.n_rows)
        else:
            raise ValueError("지원하지 않는 포맷: csv/parquet 만")
        self._apply_schema()
        self._basic_checks()
        return self.df

    def _apply_schema(self):
        sm = self.schema_map
        df = self.df

        # datetime 파싱
        for c in sm.get("datetime", []):
            if c in df.columns:
                df[c] = pd.to_datetime(df[c], errors="coerce")

        # 드랍
        drop_cols = [c for c in sm.get("drop", []) if c in df.columns]
        if drop_cols:
            df.drop(columns=drop_cols, inplace=True, errors="ignore")

        # 카테고리형은 pandas category로 캐스팅(고카디널 경고는 D1에서)
        for c in sm.get("categorical", []):
            if c in df.columns:
                df[c] = df[c].astype("category")

        # ★ datetime 컬럼 완전 제거 (ML 학습에서 제외)
        datetime_cols = [c for c in sm.get("datetime", []) if c in df.columns]
        if datetime_cols:
            df.drop(columns=datetime_cols, inplace=True, errors="ignore")
            print(f"   🔧 datetime 컬럼 제거됨: {datetime_cols}")

        self.df = df

    def _basic_checks(self):
        sm = self.schema_map
        df = self.df
        assert sm.get("target") in df.columns, "target 컬럼이 존재하지 않음"
        num = sm.get("numeric", [])
        cat = sm.get("categorical", [])
        missing = [c for c in (num+cat+[sm["target"]]) if c not in df.columns]
        if missing:
            raise ValueError(f"스키마에 지정했지만 실제로 없는 컬럼: {missing}")

    def split_xy(self) -> Tuple[pd.DataFrame, pd.Series]:
        sm = self.schema_map
        y = self.df[sm["target"]].copy()
        X = self.df.drop(columns=[sm["target"]])
        
        # ★ 명시된 numeric만 사용 (categorical, datetime 완전 제외)
        if sm.get("numeric"):
            use_cols = [c for c in sm.get("numeric", []) if c in X.columns]
            X = X[use_cols]
            print(f"   🔧 ML 학습용 수치형 특성 선택됨: {len(use_cols)}개")
            print(f"   🔧 제외된 컬럼: categorical={sm.get('categorical', [])}, datetime={sm.get('datetime', [])}")
            
            # ★ 추가 안전장치: categorical 컬럼이 남아있다면 강제 제거
            remaining_cat = [c for c in X.columns if c in sm.get("categorical", [])]
            if remaining_cat:
                X = X.drop(columns=remaining_cat)
                print(f"   ⚠️ 남아있던 categorical 컬럼 강제 제거: {remaining_cat}")
            
            # ★ 추가 안전장치: datetime 컬럼이 남아있다면 강제 제거
            remaining_datetime = [c for c in X.columns if c in sm.get("datetime", [])]
            if remaining_datetime:
                X = X.drop(columns=remaining_datetime)
                print(f"   ⚠️ 남아있던 datetime 컬럼 강제 제거: {remaining_datetime}")
        else:
            # 스키마가 명시되지 않은 경우, datetime 컬럼 자동 제외
            datetime_cols = sm.get("datetime", [])
            if datetime_cols:
                X = X.drop(columns=datetime_cols, errors="ignore")
        
        return X, y
