#!/usr/bin/env python3
"""
DuRi 승격 게이트 - 경계 포함 비교 및 CAP 로직
"""
import json
import os
import sys
from typing import Dict, Any

class PromotionGate:
    """승격 게이트 판정기"""
    
    def __init__(self):
        self.policy = os.getenv("HALLUCINATION_POLICY", "relative")
        self.margin = float(os.getenv("HALLUCINATION_MARGIN", "0.005"))
        self.hmax = float(os.getenv("HALLUCINATION_MAX", "0.02"))
        self.success_min = float(os.getenv("SUCCESS_IMPROVEMENT_MIN", "0.5"))
    
    def load_metrics(self, aggregate_file: str) -> Dict[str, Any]:
        """집계 결과 로드"""
        try:
            with open(aggregate_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 메트릭 로드 실패: {e}", file=sys.stderr)
            return {
                "prod_metrics": {"success_rate": 0.0, "hallucination_rate": 0.0, "p95_latency": 0.0, "avg_cost": 0.0, "sample_count": 0},
                "cand_metrics": {"success_rate": 0.0, "hallucination_rate": 0.0, "p95_latency": 0.0, "avg_cost": 0.0, "sample_count": 0}
            }
    
    def check_hallucination_policy(self, prod_metrics: Dict[str, Any], cand_metrics: Dict[str, Any]) -> bool:
        """환각률 정책 검사 (경계 포함)"""
        prod_halluc = prod_metrics.get("hallucination_rate", 0.0)
        cand_halluc = cand_metrics.get("hallucination_rate", 0.0)
        
        if self.policy == "relative":
            # 상대적 정책: cand ≤ min(prod + margin, hmax)
            threshold = min(prod_halluc + self.margin, self.hmax)
        else:
            # 절대적 정책: cand ≤ hmax
            threshold = self.hmax
        
        # 경계 포함 비교 (<=)
        hallucination_ok = cand_halluc <= threshold
        
        return {
            "ok": hallucination_ok,
            "prod_halluc": prod_halluc,
            "cand_halluc": cand_halluc,
            "threshold": threshold,
            "policy": self.policy,
            "margin": self.margin,
            "hmax": self.hmax
        }
    
    def check_success_improvement(self, prod_metrics: Dict[str, Any], cand_metrics: Dict[str, Any]) -> bool:
        """성공률 개선 검사"""
        prod_success = prod_metrics.get("success_rate", 0.0)
        cand_success = cand_metrics.get("success_rate", 0.0)
        
        # 성공률 개선 (백분율 포인트)
        improvement_pp = (cand_success - prod_success) * 100
        
        # 최소 개선 요구사항 확인
        success_ok = improvement_pp >= self.success_min
        
        return {
            "ok": success_ok,
            "prod_success": prod_success,
            "cand_success": cand_success,
            "improvement_pp": improvement_pp,
            "min_required": self.success_min
        }
    
    def check_latency_improvement(self, prod_metrics: Dict[str, Any], cand_metrics: Dict[str, Any]) -> bool:
        """지연시간 개선 검사"""
        prod_latency = prod_metrics.get("p95_latency", 0.0)
        cand_latency = cand_metrics.get("p95_latency", 0.0)
        
        # 지연시간 개선 (낮을수록 좋음)
        latency_improvement = prod_latency - cand_latency
        
        # 지연시간이 개선되었거나 동일하면 OK
        latency_ok = latency_improvement >= 0
        
        return {
            "ok": latency_ok,
            "prod_latency": prod_latency,
            "cand_latency": cand_latency,
            "improvement": latency_improvement
        }
    
    def check_cost_improvement(self, prod_metrics: Dict[str, Any], cand_metrics: Dict[str, Any]) -> bool:
        """비용 개선 검사"""
        prod_cost = prod_metrics.get("avg_cost", 0.0)
        cand_cost = cand_metrics.get("avg_cost", 0.0)
        
        # 비용 개선 (낮을수록 좋음)
        cost_improvement = prod_cost - cand_cost
        
        # 비용이 개선되었거나 동일하면 OK
        cost_ok = cost_improvement >= 0
        
        return {
            "ok": cost_ok,
            "prod_cost": prod_cost,
            "cand_cost": cand_cost,
            "improvement": cost_improvement
        }
    
    def evaluate_promotion(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """승격 평가"""
        prod_metrics = metrics.get("prod_metrics", {})
        cand_metrics = metrics.get("cand_metrics", {})
        
        # 각 기준별 검사
        hallucination_check = self.check_hallucination_policy(prod_metrics, cand_metrics)
        success_check = self.check_success_improvement(prod_metrics, cand_metrics)
        latency_check = self.check_latency_improvement(prod_metrics, cand_metrics)
        cost_check = self.check_cost_improvement(prod_metrics, cand_metrics)
        
        # 전체 승격 여부
        overall_ok = all([
            hallucination_check["ok"],
            success_check["ok"],
            latency_check["ok"],
            cost_check["ok"]
        ])
        
        return {
            "overall_ok": overall_ok,
            "hallucination_check": hallucination_check,
            "success_check": success_check,
            "latency_check": latency_check,
            "cost_check": cost_check,
            "timestamp": metrics.get("timestamp", ""),
            "current_traffic": metrics.get("current_traffic", 0)
        }

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="승격 게이트 판정")
    parser.add_argument("--aggregate", required=True, help="집계 결과 파일")
    args = parser.parse_args()
    
    gate = PromotionGate()
    metrics = gate.load_metrics(args.aggregate)
    result = gate.evaluate_promotion(metrics)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()