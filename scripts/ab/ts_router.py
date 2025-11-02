#!/usr/bin/env python3
"""
2.3) 트래픽 배분: Thompson Sampling(TS) 최소 구현(파일럿)
각 arm에 Beta(α,β) 사전. 성공/실패 업데이트. 샘플링 큰 값 arm에 더 많은 트래픽.

입력: success_total{arm}, fail_total{arm}
출력: route_fraction{arm}(0~1). 5분마다 갱신 → 라우터에 반영
"""
import os
import random
import sys
import json
from math import isfinite

# D. TS 라우터 보수적 가드 추가(덧대기 금지, 핵심만)
MIN_EXPLORE = float(os.getenv("TS_MIN_EXPLORE", "0.1"))  # 0.1 권장

# 라우터 설정 API가 있다고 가정
# import requests

ARMS = os.environ.get("ARMS", "A,B").split(",")
PRIORS = {a: (1.0, 1.0) for a in ARMS}  # Beta(1,1)
# TODO: Prometheus에서 success/fail을 쿼리하거나, 내부 집계 파일/DB에서 집계 읽기

def thompson_sample(alpha, beta):
    """Beta 분포에서 샘플링 (간단 구현)"""
    import random
    # 파이썬 내장 beta 분포 사용
    return random.betavariate(alpha, beta)

def compute_fractions(counts):
    """
    counts[arm] = (success, fail)
    Thompson Sampling으로 트래픽 비율 계산
    """
    scores = {}
    for a, (s, f) in counts.items():
        a0, b0 = PRIORS[a]
        alpha, beta = a0 + max(0, s), b0 + max(0, f)
        scores[a] = thompson_sample(alpha, beta)
    
    # 보수적 가드: 최소 탐색율 보장
    for a in scores:
        scores[a] = max(scores[a], MIN_EXPLORE)
    
    total = sum(scores.values())
    if total == 0:
        # 균등 분배
        return {a: 1.0 / len(scores) for a in scores}
    
    # 정규화
    frac = {a: (scores[a] / total) for a in scores}
    
    # 최소 탐색율 재보장
    frac_A = max(frac.get("A", 0.5), MIN_EXPLORE)
    frac_B = max(frac.get("B", 0.5), MIN_EXPLORE)
    norm = frac_A + frac_B
    frac_A /= norm
    frac_B /= norm
    
    return {"A": frac_A, "B": frac_B}

def read_counts_from_prom_or_db(arms):
    """
    Prometheus 또는 DB에서 success/fail 집계 읽기
    현재는 예시 데이터 반환
    """
    # TODO: 실제 구현
    # 예시: {"A": (120, 80), "B": (105, 95)}
    return {"A": (120, 80), "B": (105, 95)}

def update_router(route_fractions):
    """
    라우터에 트래픽 비율 반영
    """
    # TODO: 실제 라우터 API 호출
    # ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8080/api/routing")
    # for a, p in route_fractions.items():
    #     requests.post(ROUTER_URL, json={"arm": a, "fraction": p})
    pass

if __name__ == "__main__":
    # B. node_exporter textfile 단일 경로화
    TEXTFILE_DIR = os.getenv("TEXTFILE_DIR", ".reports/synth")
    os.makedirs(TEXTFILE_DIR, exist_ok=True)
    
    # 외부에서 success/fail 집계 읽어오기
    counts = read_counts_from_prom_or_db(ARMS)
    
    # Thompson Sampling으로 트래픽 비율 계산
    frac = compute_fractions(counts)
    
    # 라우터에 반영
    update_router(frac)
    
    # 결과 출력 (Prometheus textfile 형식으로도 기록 가능)
    metrics_out = f"{TEXTFILE_DIR}/ts_router.prom"
    routes_out = f"{TEXTFILE_DIR}/routes.json"
    
    with open(metrics_out, "w") as f:
        print("# HELP ab_route_fraction Traffic fraction per arm (Thompson Sampling)", file=f)
        print("# TYPE ab_route_fraction gauge", file=f)
        for arm, fraction in frac.items():
            print(f'ab_route_fraction{{arm="{arm}"}} {fraction}', file=f)
    
    # routes.json 저장 (관찰/롤백 용이)
    with open(routes_out, "w") as f:
        json.dump(frac, f, indent=2)
    
    print(f"[OK] TS 라우팅 메트릭 기록: {metrics_out}")
    print(f"[OK] 라우팅 설정 저장: {routes_out}")
    
    sys.exit(0)

