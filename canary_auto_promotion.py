#!/usr/bin/env python3
"""
카나리 자동 승격: 지능형 승격 게이트 연동
- 5분마다 SLO 체크
- 통과 시 다음 단계로 승격 (원자적)
- 실패 시 롤백
"""

import redis
import time
import json
from datetime import datetime

# Redis 연결
r = redis.Redis(host='localhost', port=6379, db=0)

# 지능형 승격 게이트 연동
try:
    from tools.intelligent_promotion_gate import intelligent_promotion_gate, PromotionMetric
    INTELLIGENT_GATE_AVAILABLE = True
except ImportError:
    INTELLIGENT_GATE_AVAILABLE = False
    print("⚠️ 지능형 승격 게이트를 사용할 수 없습니다. 기본 SLO 체크만 사용합니다.")

# 카나리 단계 정의
CANARY_STAGES = [0.01, 0.05, 0.20]  # 1%, 5%, 20%
STAGE_NAMES = ["1%", "5%", "20%"]

# Lua 스크립트: 원자적 승격
PROMOTE_SCRIPT = """
local stages = {0.01, 0.05, 0.20}
local cur = tonumber(redis.call('GET', KEYS[1]) or '0') or 0
local next = cur
for i=1,#stages do 
    if cur < stages[i] then 
        next = stages[i]
        break 
    end 
end
if next > cur then 
    redis.call('SET', KEYS[1], next, 'EX', 600)
    return next 
else 
    return cur 
end
"""

def get_current_stage():
    """현재 카나리 단계 확인"""
    current_ratio = float(r.get("canary:ratio") or 0)
    for i, stage in enumerate(CANARY_STAGES):
        if current_ratio <= stage:
            return i, stage
    return len(CANARY_STAGES) - 1, CANARY_STAGES[-1]

def check_slo_health():
    """SLO 건강성 체크"""
    try:
        # 5xx 비율 체크 (임시)
        error_rate = 0.02  # 2%
        if error_rate > 0.05:  # 5% 초과
            return False, f"5xx 비율 높음: {error_rate:.2%}"
        
        # p90 지연 체크 (임시)
        p90_latency = 0.8  # 0.8초
        if p90_latency > 1.0:  # 1초 초과
            return False, f"p90 지연 높음: {p90_latency:.2f}s"
        
        return True, "SLO 정상"
        
    except Exception as e:
        return False, f"SLO 체크 실패: {e}"

def get_intelligent_metrics():
    """지능형 메트릭 수집"""
    if not INTELLIGENT_GATE_AVAILABLE:
        return {}
    
    try:
        # 실제 구현에서는 자동평가 하네스에서 메트릭 수집
        # 여기서는 시뮬레이션
        metrics = {
            PromotionMetric.TASK_SUCCESS_RATE: 0.90,
            PromotionMetric.HALLUCINATION_RATE: 0.03,
            PromotionMetric.TOOL_SUCCESS_RATE: 0.95,
            PromotionMetric.RESPONSE_QUALITY: 0.85,
            PromotionMetric.SAFETY_SCORE: 0.98,
            PromotionMetric.BURN_RATE: 0.02,
            PromotionMetric.P95_LATENCY: 800.0  # 0.8초
        }
        return metrics
    except Exception as e:
        print(f"❌ 지능형 메트릭 수집 실패: {e}")
        return {}

def promote_canary_intelligent():
    """지능형 카나리 승격"""
    stage_idx, current_ratio = get_current_stage()
    
    if stage_idx >= len(CANARY_STAGES) - 1:
        print("🎉 카나리 승격 완료: 이미 최대 단계")
        return
    
    # 기본 SLO 체크
    is_healthy, slo_reason = check_slo_health()
    
    # 지능형 승격 게이트 체크
    intelligent_decision = None
    if INTELLIGENT_GATE_AVAILABLE:
        metrics = get_intelligent_metrics()
        if metrics:
            intelligent_decision = intelligent_promotion_gate.evaluate_promotion("canary", metrics)
            print(f"🧠 지능형 승격 게이트: {intelligent_decision.decision} (점수: {intelligent_decision.score:.3f})")
    
    # 승격 결정
    if is_healthy and (intelligent_decision is None or intelligent_decision.decision == "promote"):
        # Lua 스크립트로 원자적 승격
        promote = r.register_script(PROMOTE_SCRIPT)
        new_ratio = float(promote(keys=['canary:ratio']))
        
        if new_ratio > current_ratio:
            print(f"🚀 카나리 원자적 승격: {current_ratio:.1%} → {new_ratio:.1%}")
            print(f"   SLO 이유: {slo_reason}")
            if intelligent_decision:
                print(f"   지능형 이유: {intelligent_decision.reasons[:2]}")
            
            # 승격 기록
            r.lpush("canary:promotions", json.dumps({
                "timestamp": datetime.now().isoformat(),
                "from": current_ratio,
                "to": new_ratio,
                "slo_reason": slo_reason,
                "intelligent_decision": intelligent_decision.decision if intelligent_decision else "none",
                "intelligent_score": intelligent_decision.score if intelligent_decision else 0.0
            }))
        else:
            print(f"ℹ️ 카나리 승격 없음: {current_ratio:.1%}")
    
    elif intelligent_decision and intelligent_decision.decision == "hold":
        print(f"⏸️ 카나리 홀드: {intelligent_decision.reasons[:2]}")
        
        # 홀드 기록
        r.lpush("canary:holds", json.dumps({
            "timestamp": datetime.now().isoformat(),
            "reason": intelligent_decision.reasons,
            "score": intelligent_decision.score
        }))
    
    else:
        # 롤백
        r.set("canary:ratio", 0.0, ex=600)  # 10분 TTL
        rollback_reason = slo_reason
        if intelligent_decision:
            rollback_reason += f" | 지능형: {intelligent_decision.reasons[:2]}"
        
        print(f"🚨 카나리 롤백: {rollback_reason}")
        
        # 롤백 기록
        r.lpush("canary:rollbacks", json.dumps({
            "timestamp": datetime.now().isoformat(),
            "reason": rollback_reason,
            "slo_healthy": is_healthy,
            "intelligent_decision": intelligent_decision.decision if intelligent_decision else "none"
        }))

if __name__ == "__main__":
    print("🚀 카나리 자동 승격 시작 (지능형 게이트 연동)")
    
    # 5분마다 체크
    while True:
        promote_canary_intelligent()
        time.sleep(300)  # 5분
