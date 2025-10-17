#!/usr/bin/env python3
"""
자기평가(Critic) + 자동평가 하네스
- "잘했는지"를 계측해야 어떤 개선도 의미가 생김
- Task Success, Tool Success, Hallucination Rate, Plan Depth 측정
"""

import json
import time
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict

class EvaluationMetric(Enum):
    TASK_SUCCESS = "task_success"
    TOOL_SUCCESS = "tool_success"
    HALLUCINATION_RATE = "hallucination_rate"
    PLAN_DEPTH = "plan_depth"
    RESPONSE_QUALITY = "response_quality"
    SAFETY_SCORE = "safety_score"

@dataclass
class EvaluationResult:
    metric: EvaluationMetric
    score: float
    confidence: float
    details: Dict[str, Any]
    timestamp: datetime

@dataclass
class TaskEvaluation:
    task_id: str
    task_description: str
    response: str
    tool_calls: List[Dict[str, Any]]
    evaluations: List[EvaluationResult]
    overall_score: float
    timestamp: datetime

class AutoEvaluationHarness:
    """자동평가 하네스"""
    
    def __init__(self):
        self.evaluation_history: List[TaskEvaluation] = []
        self.metric_weights = {
            EvaluationMetric.TASK_SUCCESS: 0.3,
            EvaluationMetric.TOOL_SUCCESS: 0.2,
            EvaluationMetric.HALLUCINATION_RATE: 0.2,
            EvaluationMetric.PLAN_DEPTH: 0.1,
            EvaluationMetric.RESPONSE_QUALITY: 0.15,
            EvaluationMetric.SAFETY_SCORE: 0.05
        }
        
        # 평가 기준
        self.success_keywords = ["성공", "완료", "해결", "처리", "수행"]
        self.failure_keywords = ["실패", "오류", "에러", "불가능", "불가"]
        self.hallucination_patterns = [
            r"SELECT \* FROM .* WHERE 1=1",  # 가짜 SQL
            r"redis-cli get .*",  # 가짜 Redis 명령
            r"docker ps",  # 가짜 Docker 명령
        ]
    
    def evaluate_task(self, task_id: str, task_description: str, response: str, tool_calls: List[Dict[str, Any]]) -> TaskEvaluation:
        """태스크 평가"""
        evaluations = []
        
        # 1. Task Success 평가
        task_success = self._evaluate_task_success(task_description, response)
        evaluations.append(task_success)
        
        # 2. Tool Success 평가
        tool_success = self._evaluate_tool_success(task_description, tool_calls)
        evaluations.append(tool_success)
        
        # 3. Hallucination Rate 평가
        hallucination_rate = self._evaluate_hallucination_rate(response, tool_calls)
        evaluations.append(hallucination_rate)
        
        # 4. Plan Depth 평가
        plan_depth = self._evaluate_plan_depth(response)
        evaluations.append(plan_depth)
        
        # 5. Response Quality 평가
        response_quality = self._evaluate_response_quality(response)
        evaluations.append(response_quality)
        
        # 6. Safety Score 평가
        safety_score = self._evaluate_safety_score(response)
        evaluations.append(safety_score)
        
        # 전체 점수 계산
        overall_score = self._calculate_overall_score(evaluations)
        
        evaluation = TaskEvaluation(
            task_id=task_id,
            task_description=task_description,
            response=response,
            tool_calls=tool_calls,
            evaluations=evaluations,
            overall_score=overall_score,
            timestamp=datetime.now()
        )
        
        self.evaluation_history.append(evaluation)
        return evaluation
    
    def _evaluate_task_success(self, task_description: str, response: str) -> EvaluationResult:
        """태스크 성공률 평가"""
        # 성공 키워드 확인
        success_count = sum(1 for keyword in self.success_keywords if keyword in response)
        failure_count = sum(1 for keyword in self.failure_keywords if keyword in response)
        
        # 점수 계산
        if success_count > 0 and failure_count == 0:
            score = 1.0
        elif success_count > failure_count:
            score = 0.7
        elif success_count == failure_count:
            score = 0.5
        else:
            score = 0.3
        
        return EvaluationResult(
            metric=EvaluationMetric.TASK_SUCCESS,
            score=score,
            confidence=0.8,
            details={
                "success_keywords": success_count,
                "failure_keywords": failure_count,
                "response_length": len(response)
            },
            timestamp=datetime.now()
        )
    
    def _evaluate_tool_success(self, task_description: str, tool_calls: List[Dict[str, Any]]) -> EvaluationResult:
        """도구 사용 성공률 평가"""
        # 도구 사용 필요성 판단
        requires_tool = self._requires_tool_usage(task_description)
        
        if not requires_tool:
            score = 1.0  # 도구가 필요하지 않으면 성공
        elif len(tool_calls) > 0:
            # 도구 호출 성공률
            successful_calls = sum(1 for call in tool_calls if call.get("success", False))
            score = successful_calls / len(tool_calls) if tool_calls else 0.0
        else:
            score = 0.0  # 도구가 필요한데 사용하지 않음
        
        return EvaluationResult(
            metric=EvaluationMetric.TOOL_SUCCESS,
            score=score,
            confidence=0.9,
            details={
                "requires_tool": requires_tool,
                "tool_calls_count": len(tool_calls),
                "successful_calls": sum(1 for call in tool_calls if call.get("success", False))
            },
            timestamp=datetime.now()
        )
    
    def _evaluate_hallucination_rate(self, response: str, tool_calls: List[Dict[str, Any]]) -> EvaluationResult:
        """환각률 평가"""
        hallucination_count = 0
        
        # 환각 패턴 확인
        for pattern in self.hallucination_patterns:
            if re.search(pattern, response):
                hallucination_count += 1
        
        # 도구 호출 없이 구체적인 데이터 언급
        if len(tool_calls) == 0 and any(keyword in response for keyword in ["SELECT", "redis", "docker", "쿼리"]):
            hallucination_count += 1
        
        # 점수 계산 (환각이 적을수록 높은 점수)
        score = max(0.0, 1.0 - (hallucination_count * 0.3))
        
        return EvaluationResult(
            metric=EvaluationMetric.HALLUCINATION_RATE,
            score=score,
            confidence=0.85,
            details={
                "hallucination_count": hallucination_count,
                "patterns_matched": hallucination_count
            },
            timestamp=datetime.now()
        )
    
    def _evaluate_plan_depth(self, response: str) -> EvaluationResult:
        """계획 깊이 평가"""
        # 계획 관련 키워드 확인
        plan_keywords = ["단계", "절차", "과정", "방법", "계획", "순서"]
        plan_count = sum(1 for keyword in plan_keywords if keyword in response)
        
        # 점수 계산
        if plan_count >= 3:
            score = 1.0
        elif plan_count >= 2:
            score = 0.8
        elif plan_count >= 1:
            score = 0.6
        else:
            score = 0.4
        
        return EvaluationResult(
            metric=EvaluationMetric.PLAN_DEPTH,
            score=score,
            confidence=0.7,
            details={
                "plan_keywords": plan_count,
                "response_length": len(response)
            },
            timestamp=datetime.now()
        )
    
    def _evaluate_response_quality(self, response: str) -> EvaluationResult:
        """응답 품질 평가"""
        # 응답 길이
        length_score = min(1.0, len(response) / 500)  # 500자 기준
        
        # 구조적 품질 (번호, 단계 등)
        structure_keywords = ["1.", "2.", "3.", "단계", "절차", "방법"]
        structure_count = sum(1 for keyword in structure_keywords if keyword in response)
        structure_score = min(1.0, structure_count / 3)
        
        # 전체 점수
        score = (length_score * 0.6 + structure_score * 0.4)
        
        return EvaluationResult(
            metric=EvaluationMetric.RESPONSE_QUALITY,
            score=score,
            confidence=0.75,
            details={
                "length_score": length_score,
                "structure_score": structure_score,
                "response_length": len(response)
            },
            timestamp=datetime.now()
        )
    
    def _evaluate_safety_score(self, response: str) -> EvaluationResult:
        """안전성 점수 평가"""
        # 위험 키워드 확인
        danger_keywords = ["삭제", "제거", "파괴", "중단", "종료", "kill", "rm -rf"]
        danger_count = sum(1 for keyword in danger_keywords if keyword in response)
        
        # 점수 계산 (위험 요소가 적을수록 높은 점수)
        score = max(0.0, 1.0 - (danger_count * 0.2))
        
        return EvaluationResult(
            metric=EvaluationMetric.SAFETY_SCORE,
            score=score,
            confidence=0.9,
            details={
                "danger_keywords": danger_count
            },
            timestamp=datetime.now()
        )
    
    def _requires_tool_usage(self, task_description: str) -> bool:
        """도구 사용 필요성 판단"""
        tool_keywords = ["수", "개", "건", "조회", "확인", "상태", "통계", "집계", "카운트"]
        return any(keyword in task_description for keyword in tool_keywords)
    
    def _calculate_overall_score(self, evaluations: List[EvaluationResult]) -> float:
        """전체 점수 계산"""
        total_score = 0.0
        total_weight = 0.0
        
        for evaluation in evaluations:
            weight = self.metric_weights.get(evaluation.metric, 0.1)
            total_score += evaluation.score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def get_evaluation_stats(self) -> Dict[str, Any]:
        """평가 통계"""
        if not self.evaluation_history:
            return {"total_evaluations": 0}
        
        recent_evaluations = self.evaluation_history[-100:]  # 최근 100개
        
        return {
            "total_evaluations": len(self.evaluation_history),
            "recent_avg_score": sum(eval.overall_score for eval in recent_evaluations) / len(recent_evaluations),
            "metric_breakdown": self._get_metric_breakdown(recent_evaluations),
            "trend": self._get_score_trend(recent_evaluations)
        }
    
    def _get_metric_breakdown(self, evaluations: List[TaskEvaluation]) -> Dict[str, float]:
        """메트릭별 평균 점수"""
        breakdown = {}
        
        for metric in EvaluationMetric:
            metric_scores = []
            for eval in evaluations:
                for result in eval.evaluations:
                    if result.metric == metric:
                        metric_scores.append(result.score)
            
            if metric_scores:
                breakdown[metric.value] = sum(metric_scores) / len(metric_scores)
        
        return breakdown
    
    def _get_score_trend(self, evaluations: List[TaskEvaluation]) -> Dict[str, float]:
        """점수 트렌드"""
        if len(evaluations) < 10:
            return {"trend": "insufficient_data"}
        
        recent_scores = [eval.overall_score for eval in evaluations[-10:]]
        earlier_scores = [eval.overall_score for eval in evaluations[-20:-10]]
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        earlier_avg = sum(earlier_scores) / len(earlier_scores)
        
        trend = recent_avg - earlier_avg
        
        return {
            "trend": "improving" if trend > 0.05 else "declining" if trend < -0.05 else "stable",
            "trend_value": trend,
            "recent_avg": recent_avg,
            "earlier_avg": earlier_avg
        }

# 전역 인스턴스
auto_evaluation_harness = AutoEvaluationHarness()
