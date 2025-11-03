#!/usr/bin/env python3
# 베이지안 진행표: Green 비율 Beta(1,1) → Beta(1+G, 1+N-G) 업데이트
import os, json, math
from scipy.stats import beta

STATE_FILE = os.environ.get("STATE_FILE", ".reports/synth/ab_gate_state.json")
BAYES_FILE = os.environ.get("BAYES_FILE", ".reports/synth/ab_bayes_state.json")

def read_bayes_state():
    if os.path.exists(BAYES_FILE):
        with open(BAYES_FILE) as f:
            return json.load(f)
    return {"alpha": 1, "beta": 1, "n_total": 0, "n_green": 0}

def update_bayes(judgment):
    state = read_bayes_state()
    state["n_total"] += 1
    if judgment == "GREEN":
        state["n_green"] += 1
        state["alpha"] += 1
    else:
        state["beta"] += 1
    
    with open(BAYES_FILE, "w") as f:
        json.dump(state, f, indent=2)
    
    return state

def prob_p_ge_threshold(alpha, beta, threshold=0.8):
    """P(p >= threshold | Beta(alpha, beta))"""
    try:
        # Beta CDF를 사용하여 계산
        return 1 - beta.cdf(threshold, alpha, beta)
    except:
        # 간단한 근사 (alpha, beta가 충분히 클 때)
        mean = alpha / (alpha + beta)
        if mean >= threshold:
            return 0.8  # 보수적 추정
        return 0.2

def main():
    import sys
    judgment = sys.argv[1] if len(sys.argv) > 1 else "UNKNOWN"
    
    state = update_bayes(judgment)
    
    prob_ge_08 = prob_p_ge_threshold(state["alpha"], state["beta"], 0.8)
    
    print(f"[BAYES] n={state['n_total']}, G={state['n_green']}, α={state['alpha']}, β={state['beta']}")
    print(f"[BAYES] P(p≥0.8|data)={prob_ge_08:.3f}")
    
    if prob_ge_08 >= 0.8:
        print("[BAYES] → 종결 선언: 기다림 전환 조건 충족")
    
    return prob_ge_08

if __name__ == "__main__":
    main()

