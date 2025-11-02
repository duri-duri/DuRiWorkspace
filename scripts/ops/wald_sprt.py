#!/usr/bin/env python3
# Wald SPRT: Green 비율 p≥0.8 vs p≤0.6 판정
import os, json, math

STATE_FILE = os.environ.get("SPRT_FILE", ".reports/synth/ab_sprt_state.json")

# SPRT 파라미터
ALPHA = 0.05  # Type I error
BETA = 0.2    # Type II error
P0 = 0.6      # H0: p <= 0.6
P1 = 0.8      # H1: p >= 0.8

def log_likelihood_ratio(green_count, total_count, p0, p1):
    """로그 우도비 계산"""
    if total_count == 0:
        return 0.0
    p_hat = green_count / total_count
    if p_hat == 0:
        return -math.inf
    if p_hat == 1:
        return math.inf
    # LR = log(P(data|H1) / P(data|H0))
    # LR = n * (p_hat * log(p1/p0) + (1-p_hat) * log((1-p1)/(1-p0)))
    return total_count * (p_hat * math.log(p1/p0) + (1-p_hat) * math.log((1-p1)/(1-p0)))

def calculate_sprt_bounds(alpha, beta):
    """SPRT 상한/하한 계산"""
    A = math.log((1-beta) / alpha)      # 상한
    B = math.log(beta / (1-alpha))     # 하한
    return A, B

def read_sprt_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"green_count": 0, "total_count": 0, "log_lr": 0.0}

def update_sprt(judgment):
    state = read_sprt_state()
    state["total_count"] += 1
    if judgment == "GREEN":
        state["green_count"] += 1
    
    A, B = calculate_sprt_bounds(ALPHA, BETA)
    state["log_lr"] = log_likelihood_ratio(state["green_count"], state["total_count"], P0, P1)
    
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    
    return state, A, B

def main():
    import sys
    judgment = sys.argv[1] if len(sys.argv) > 1 else "UNKNOWN"
    
    state, A, B = update_sprt(judgment)
    
    print(f"[SPRT] n={state['total_count']}, G={state['green_count']}, LR={state['log_lr']:.3f}")
    print(f"[SPRT] Bounds: A={A:.3f}, B={B:.3f}")
    
    if state["log_lr"] >= A:
        print("[SPRT] → 상한선 도달: 개선 확정 (기다림 모드)")
        return "ACCEPT"
    elif state["log_lr"] <= B:
        print("[SPRT] → 하한선 도달: 개선 부정 (가중 원복 + 재시드)")
        return "REJECT"
    else:
        print("[SPRT] → 계속 관찰")
        return "CONTINUE"

if __name__ == "__main__":
    main()

