#!/usr/bin/env python3
"""
지능형 승격 게이트
- 이미 번레이트·p90 있음 → "태스크 성공률/환각률"을 승격 조건에 추가
- 카나리 조건에 태스크 지표 추가
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict

class PromotionMetric(Enum):
    TASK_SUCCESS_RATE = "task_success_rate"
    HALLUCINATION_RATE = "hallucination_rate"
    TOOL_SUCCESS_RATE = "tool_success_rate"
    RESPONSE_QUALITY = "response_quality"
    SAFETY_SCORE = "safety_score"
    BURN_RATE = "burn_rate"
    P95_LATENCY = "p95_latency"

@dataclass
class PromotionThreshold:
    metric: PromotionMetric
    min_value: float
    max_value: float
    weight: float
    description: str

@dataclass
class PromotionDecision:
    candidate_id: str
    decision: str  # "promote", "hold", "rollback"
    score: float
    reasons: List[str]
    thresholds_met: Dict[str, bool]
    timestamp: datetime

class IntelligentPromotionGate:
    """지능형 승격 게이트"""
    
    def __init__(self):
        self.promotion_history: List[PromotionDecision] = []
        self.current_thresholds: Dict[PromotionMetric, PromotionThreshold] = {}
        
        # 기본 임계값 설정
        self._setup_default_thresholds()
        
        # 승격 가중치
        self.promotion_weights = {
            PromotionMetric.TASK_SUCCESS_RATE: 0.25,
            PromotionMetric.HALLUCINATION_RATE: 0.20,
            PromotionMetric.TOOL_SUCCESS_RATE: 0.15,
            PromotionMetric.RESPONSE_QUALITY: 0.15,
            PromotionMetric.SAFETY_SCORE: 0.10,
            PromotionMetric.BURN_RATE: 0.10,
            PromotionMetric.P95_LATENCY: 0.05
        }
    
    def _setup_default_thresholds(self):
        """기본 임계값 설정"""
        self.current_thresholds = {
            PromotionMetric.TASK_SUCCESS_RATE: PromotionThreshold(
                metric=PromotionMetric.TASK_SUCCESS_RATE,
                min_value=0.85,  # 85% 이상
                max_value=1.0,
                weight=0.25,
                description="태스크 성공률 85% 이상"
            ),
            PromotionMetric.HALLUCINATION_RATE: PromotionThreshold(
                metric=PromotionMetric.HALLUCINATION_RATE,
                min_value=0.0,
                max_value=0.05,  # 5% 이하
                weight=0.20,
                description="환각률 5% 이하"
            ),
            PromotionMetric.TOOL_SUCCESS_RATE: PromotionThreshold(
                metric=PromotionMetric.TOOL_SUCCESS_RATE,
                min_value=0.90,  # 90% 이상
                max_value=1.0,
                weight=0.15,
                description="도구 사용 성공률 90% 이상"
            ),
            PromotionMetric.RESPONSE_QUALITY: PromotionThreshold(
                metric=PromotionMetric.RESPONSE_QUALITY,
                min_value=0.80,  # 80% 이상
                max_value=1.0,
                weight=0.15,
                description="응답 품질 80% 이상"
            ),
            PromotionMetric.SAFETY_SCORE: PromotionThreshold(
                metric=PromotionMetric.SAFETY_SCORE,
                min_value=0.95,  # 95% 이상
                max_value=1.0,
                weight=0.10,
                description="안전성 점수 95% 이상"
            ),
            PromotionMetric.BURN_RATE: PromotionThreshold(
                metric=PromotionMetric.BURN_RATE,
                min_value=0.0,
                max_value=0.05,  # 5% 이하
                weight=0.10,
                description="번레이트 5% 이하"
            ),
            PromotionMetric.P95_LATENCY: PromotionThreshold(
                metric=PromotionMetric.P95_LATENCY,
                min_value=0.0,
                max_value=1000.0,  # 1초 이하
                weight=0.05,
                description="P95 지연 1초 이하"
            )
        }
    
    def evaluate_promotion(self, candidate_id: str, metrics: Dict[PromotionMetric, float]) -> PromotionDecision:
        """승격 평가"""
        thresholds_met = {}
        reasons = []
        total_score = 0.0
        
        # 각 메트릭별 임계값 확인
        for metric, value in metrics.items():
            if metric not in self.current_thresholds:
                continue
            
            threshold = self.current_thresholds[metric]
            weight = self.promotion_weights.get(metric, 0.1)
            
            # 임계값 확인
            if threshold.min_value <= value <= threshold.max_value:
                thresholds_met[metric.value] = True
                reasons.append(f"✅ {threshold.description}: {value:.3f}")
                total_score += weight
            else:
                thresholds_met[metric.value] = False
                if value < threshold.min_value:
                    reasons.append(f"❌ {threshold.description}: {value:.3f} < {threshold.min_value}")
                else:
                    reasons.append(f"❌ {threshold.description}: {value:.3f} > {threshold.max_value}")
        
        # 승격 결정
        if total_score >= 0.8:  # 80% 이상 임계값 통과
            decision = "promote"
        elif total_score >= 0.6:  # 60% 이상
            decision = "hold"
        else:
            decision = "rollback"
        
        promotion_decision = PromotionDecision(
            candidate_id=candidate_id,
            decision=decision,
            score=total_score,
            reasons=reasons,
            thresholds_met=thresholds_met,
            timestamp=datetime.now()
        )
        
        self.promotion_history.append(promotion_decision)
        return promotion_decision
    
    def update_thresholds(self, new_thresholds: Dict[PromotionMetric, PromotionThreshold]):
        """임계값 업데이트"""
        self.current_thresholds.update(new_thresholds)
    
    def get_promotion_stats(self) -> Dict[str, Any]:
        """승격 통계"""
        if not self.promotion_history:
            return {"total_decisions": 0}
        
        recent_decisions = self.promotion_history[-50:]  # 최근 50개
        
        decisions_count = {"promote": 0, "hold": 0, "rollback": 0}
        for decision in recent_decisions:
            decisions_count[decision.decision] += 1
        
        avg_score = sum(decision.score for decision in recent_decisions) / len(recent_decisions)
        
        return {
            "total_decisions": len(self.promotion_history),
            "recent_decisions": len(recent_decisions),
            "decision_breakdown": decisions_count,
            "avg_score": avg_score,
            "promotion_rate": decisions_count["promote"] / len(recent_decisions) if recent_decisions else 0
        }
    
    def get_failure_reasons(self) -> Dict[str, int]:
        """실패 원인 분석"""
        failure_reasons = {}
        
        for decision in self.promotion_history:
            if decision.decision != "promote":
                for reason in decision.reasons:
                    if "❌" in reason:
                        # 메트릭 이름 추출
                        metric_name = reason.split(":")[0].replace("❌ ", "").split(" ")[0]
                        failure_reasons[metric_name] = failure_reasons.get(metric_name, 0) + 1
        
        return failure_reasons

# 전역 인스턴스
intelligent_promotion_gate = IntelligentPromotionGate()
