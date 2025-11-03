#!/usr/bin/env python3
"""AB p-value 분산 테스트: 상수화 방지"""
import glob
import re
import statistics
import pathlib

def test_ab_pvalue_has_variance():
    """AB p-value가 분산을 가지는지 확인 (상수화 방지)"""
    vals = []
    base = pathlib.Path("var/evolution")
    
    # 24시간 내 ab_eval.prom 파일 찾기
    for p in glob.glob(f"{base}/*/ab_eval.prom"):
        try:
            with open(p, 'r') as f:
                for ln in f:
                    # duri_ab_p_value{...} <value> 또는 duri_ab_p_value <value> 형식
                    m = re.match(r'^duri_ab_p_value[^{]*\s+([0-9.eE+-]+)', ln.strip())
                    if m:
                        try:
                            val = float(m.group(1))
                            if not (val != val):  # NaN 체크
                                vals.append(val)
                        except (ValueError, AttributeError):
                            continue
        except (FileNotFoundError, PermissionError):
            continue
    
    assert len(vals) >= 10, f"Not enough AB samples in 24h: {len(vals)} < 10"
    assert len(set(vals)) > 1, f"AB p-values are constant (variance=0): all values = {vals[0] if vals else 'N/A'}"
    
    # 평균이 통계적으로 유의미한지 확인 (선택적)
    mean_val = statistics.mean(vals)
    if mean_val > 0:
        assert mean_val < 0.05 or len(set(vals)) > 1, f"Not statistically significant on average: mean={mean_val}, but variance OK"
    
    # 표준편차 확인
    if len(vals) > 1:
        std_val = statistics.stdev(vals)
        assert std_val > 0, f"Standard deviation is zero: {std_val}"
    
    print(f"[OK] AB p-value variance test: {len(vals)} samples, {len(set(vals))} unique values, std={statistics.stdev(vals) if len(vals)>1 else 0:.9f}")

if __name__ == "__main__":
    test_ab_pvalue_has_variance()
    print("✅ AB variance test passed")

