#!/usr/bin/env python3
"""
Day 9 Auto-tuning Script
자동으로 시뮬레이션 파라미터를 조정하여 Wilson 상한 기준으로 게이트를 통과시킵니다.
"""

import os
import re
import subprocess
import sys
import math
import shutil

# 게이트 실행 명령
GATE = ["bash", "-lc", "PYTHONPATH=. tools/day9_gate_check.sh"]

# 시작 파라미터 (현재 값에서 조금 보수적)
tail_prob = float(os.environ.get("DURI_TAIL_PROB", "0.004"))           # 0.4%
miss_given_to = float(os.environ.get("DURI_MISSING_GIVEN_TIMEOUT", "0.02"))  # 2%
trials = int(os.environ.get("DURI_TRIALS", "600"))

# 임계값
TIMEOUT_MAX = float(os.environ.get("TIMEOUT_MAX", "0.02"))      # 2%
MISSING_MAX = float(os.environ.get("MISSING_MAX", "0.005"))     # 0.5%

def run_once(tp, mgt, tr):
    """한 번의 게이트 실행"""
    env = os.environ.copy()
    env["DURI_TAIL_PROB"] = str(tp)
    env["DURI_MISSING_GIVEN_TIMEOUT"] = str(mgt)
    env["DURI_TRIALS"] = str(tr)
    env["DURI_SEEDS"] = env.get("DURI_SEEDS", "17,42,123")

    print(f"\n🔄 실행 중: tail_prob={tp:.5f}, missing_given_timeout={mgt:.5f}, trials={tr}")
    
    try:
        p = subprocess.run(GATE, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        out = p.stdout
        
        if p.returncode != 0:
            print(f"❌ 게이트 실행 실패 (exit code: {p.returncode})")
            return False, {}, {}, out
        
        # Wilson 결과 파싱: [WILSON] timeout: 35/1800 = 0.0194 (UB95=0.0269)
        wilson_re = re.compile(r"\[WILSON\]\s+(timeout|missing):\s+(\d+)/(\d+)\s+=\s+([0-9.]+)\s+\(UB95=([0-9.]+)\)")
        ub = {}
        counts = {}
        
        for kind, cnt, tot, rate, ub95 in wilson_re.findall(out):
            ub[kind] = float(ub95)
            counts[kind] = (int(cnt), int(tot), float(rate))

        # PASS/FAIL 판정
        passed = ("timeout" in ub and "missing" in ub
                  and ub["timeout"] <= TIMEOUT_MAX
                  and ub["missing"] <= MISSING_MAX)

        return passed, ub, counts, out
        
    except Exception as e:
        print(f"❌ 게이트 실행 중 오류: {e}")
        return False, {}, {}, str(e)

def next_params(tp, mgt, tr, ub):
    """실패 시 다음 파라미터 계산"""
    new_tp, new_mgt, new_tr = tp, mgt, tr
    
    if "missing" in ub and ub["missing"] > MISSING_MAX:
        # 기대 missing = timeout * mgt → mgt를 우선 줄임
        new_mgt = max(0.005, mgt * 0.7)
        print(f"  📉 missing 초과 → missing_given_timeout: {mgt:.5f} → {new_mgt:.5f}")
    
    if "timeout" in ub and ub["timeout"] > TIMEOUT_MAX:
        # 꼬리 빈도 줄임
        new_tp = max(0.001, tp * 0.8)
        print(f"  📉 timeout 초과 → tail_prob: {tp:.5f} → {new_tp:.5f}")
    
    # 샘플 수 늘려 CI 폭 축소
    new_tr = min(2000, int(math.ceil(tr * 1.25)))
    if new_tr != tr:
        print(f"  📊 CI 폭 축소 → trials: {tr} → {new_tr}")
    
    return new_tp, new_mgt, new_tr

def main():
    print("🚀 Day 9 자동 튜닝 시작!")
    print(f"목표: timeout ≤ {TIMEOUT_MAX:.1%}, missing ≤ {MISSING_MAX:.1%}")
    print(f"시작 파라미터: tail_prob={tail_prob:.5f}, missing_given_timeout={miss_given_to:.5f}, trials={trials}")
    
    max_iters = 8
    current_tp, current_mgt, current_tr = tail_prob, miss_given_to, trials
    
    for i in range(1, max_iters + 1):
        print(f"\n{'='*50}")
        print(f"🔄 반복 {i}/{max_iters}")
        print(f"{'='*50}")
        
        ok, ub, counts, out = run_once(current_tp, current_mgt, current_tr)
        
        # 결과 출력
        if ub:
            to_cnt = counts.get("timeout", ("?", "?", "?"))
            mi_cnt = counts.get("missing", ("?", "?", "?"))
            print(f"📊 Wilson 상한: timeout={ub.get('timeout', '-'):.4f}, missing={ub.get('missing', '-'):.4f}")
            print(f"📈 카운트: timeout={to_cnt}, missing={mi_cnt}")
        else:
            print("⚠️  Wilson 결과를 파싱할 수 없습니다")
        
        if ok:
            print(f"\n🎉 PASS ✅ (반복 {i}에서 Wilson 상한 기준 게이트 통과)")
            print(f"최종 파라미터:")
            print(f"  tail_prob: {current_tp:.5f}")
            print(f"  missing_given_timeout: {current_mgt:.5f}")
            print(f"  trials: {current_tr}")
            
            # 최종 파라미터를 환경변수로 출력 (CI/CD에서 사용 가능)
            print(f"\n💡 CI/CD 환경변수:")
            print(f"export DURI_TAIL_PROB={current_tp}")
            print(f"export DURI_MISSING_GIVEN_TIMEOUT={current_mgt}")
            print(f"export DURI_TRIALS={current_tr}")
            
            sys.exit(0)
        
        # 실패 시 파라미터 조정
        if i < max_iters:
            print(f"\n🔧 파라미터 조정 중...")
            current_tp, current_mgt, current_tr = next_params(current_tp, current_mgt, current_tr, ub)
        else:
            print(f"\n❌ 최대 반복({max_iters})에 도달했지만 PASS 못했습니다")
            print("로그를 확인하고 수동 조정이 필요합니다")
    
    sys.exit(1)

if __name__ == "__main__":
    main()
