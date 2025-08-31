#!/usr/bin/env python3
"""
DuRi Performance Scorer
성과 측정기 - 루프별 성장 기여도 측정 및 내부 피드백
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import math

logger = logging.getLogger(__name__)

class PerformanceMetric(Enum):
    """성과 지표"""
    EMOTIONAL_GROWTH = "emotional_growth"
    COGNITIVE_DEVELOPMENT = "cognitive_development"
    SOCIAL_PROGRESS = "social_progress"
    CREATIVITY_LEVEL = "creativity_level"
    PROBLEM_SOLVING = "problem_solving"
    ADAPTABILITY = "adaptability"
    AUTONOMY = "autonomy"
    OVERALL_GROWTH = "overall_growth"

class PerformanceLevel(Enum):
    """성과 수준"""
    EXCELLENT = "excellent"      # 90-100%
    GOOD = "good"               # 70-89%
    AVERAGE = "average"         # 50-69%
    BELOW_AVERAGE = "below_average"  # 30-49%
    POOR = "poor"              # 0-29%

@dataclass
class PerformanceScore:
    """성과 점수"""
    metric: PerformanceMetric
    score: float
    level: PerformanceLevel
    contribution: float
    feedback: str
    timestamp: str

@dataclass
class LoopPerformance:
    """루프 성과"""
    loop_id: str
    timestamp: str
    duration: float
    scores: Dict[PerformanceMetric, PerformanceScore]
    overall_score: float
    growth_contribution: float
    efficiency_rating: float
    recommendations: List[str]

class PerformanceScorer:
    """성과 측정기"""
    
    def __init__(self):
        self.performance_history = []
        self.metric_weights = {
            PerformanceMetric.EMOTIONAL_GROWTH: 0.2,
            PerformanceMetric.COGNITIVE_DEVELOPMENT: 0.25,
            PerformanceMetric.SOCIAL_PROGRESS: 0.15,
            PerformanceMetric.CREATIVITY_LEVEL: 0.1,
            PerformanceMetric.PROBLEM_SOLVING: 0.15,
            PerformanceMetric.ADAPTABILITY: 0.1,
            PerformanceMetric.AUTONOMY: 0.05
        }
        self.baseline_scores = {}
        self.improvement_trends = {}
        logger.info("성과 측정기 초기화 완료")
    
    def score_loop_performance(self, 
                              loop_data: Dict[str, Any],
                              emotional_state: str,
                              growth_metrics: Dict[str, Any],
                              judgment_result: Dict[str, Any]) -> LoopPerformance:
        """루프 성과 측정"""
        loop_id = f"loop_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        timestamp = datetime.now().isoformat()
        
        # 각 지표별 점수 계산
        scores = {}
        for metric in PerformanceMetric:
            if metric == PerformanceMetric.OVERALL_GROWTH:
                continue
            
            score = self._calculate_metric_score(metric, loop_data, emotional_state, growth_metrics, judgment_result)
            level = self._determine_performance_level(score)
            contribution = self._calculate_contribution(score, metric)
            feedback = self._generate_feedback(metric, score, level)
            
            scores[metric] = PerformanceScore(
                metric=metric,
                score=score,
                level=level,
                contribution=contribution,
                feedback=feedback,
                timestamp=timestamp
            )
        
        # 전체 점수 계산
        overall_score = self._calculate_overall_score(scores)
        
        # 성장 기여도 계산
        growth_contribution = self._calculate_growth_contribution(scores, growth_metrics)
        
        # 효율성 평가
        efficiency_rating = self._calculate_efficiency_rating(loop_data, overall_score)
        
        # 권장사항 생성
        recommendations = self._generate_recommendations(scores, overall_score)
        
        loop_performance = LoopPerformance(
            loop_id=loop_id,
            timestamp=timestamp,
            duration=loop_data.get("duration", 0.0),
            scores=scores,
            overall_score=overall_score,
            growth_contribution=growth_contribution,
            efficiency_rating=efficiency_rating,
            recommendations=recommendations
        )
        
        self.performance_history.append(loop_performance)
        self._update_baselines(scores)
        self._update_trends(loop_performance)
        
        logger.info(f"루프 성과 측정 완료: {loop_id} - 전체 점수: {overall_score:.2f}")
        return loop_performance
    
    def _calculate_metric_score(self, metric: PerformanceMetric, loop_data: Dict[str, Any], 
                               emotional_state: str, growth_metrics: Dict[str, Any], 
                               judgment_result: Dict[str, Any]) -> float:
        """지표별 점수 계산"""
        if metric == PerformanceMetric.EMOTIONAL_GROWTH:
            return self._score_emotional_growth(emotional_state, loop_data)
        elif metric == PerformanceMetric.COGNITIVE_DEVELOPMENT:
            return self._score_cognitive_development(growth_metrics, loop_data)
        elif metric == PerformanceMetric.SOCIAL_PROGRESS:
            return self._score_social_progress(loop_data, emotional_state)
        elif metric == PerformanceMetric.CREATIVITY_LEVEL:
            return self._score_creativity_level(loop_data, growth_metrics)
        elif metric == PerformanceMetric.PROBLEM_SOLVING:
            return self._score_problem_solving(judgment_result, loop_data)
        elif metric == PerformanceMetric.ADAPTABILITY:
            return self._score_adaptability(loop_data, emotional_state)
        elif metric == PerformanceMetric.AUTONOMY:
            return self._score_autonomy(loop_data, growth_metrics)
        else:
            return 0.0
    
    def _score_emotional_growth(self, emotional_state: str, loop_data: Dict[str, Any]) -> float:
        """감정 성장 점수"""
        emotional_intensity = self._get_emotional_intensity(emotional_state)
        emotional_stability = loop_data.get("emotional_stability", 0.5)
        emotional_insight = loop_data.get("emotional_insight", 0.0)
        
        # 감정 강도, 안정성, 통찰력을 종합하여 점수 계산
        score = (emotional_intensity * 0.4 + emotional_stability * 0.4 + emotional_insight * 0.2) * 100
        return min(100.0, max(0.0, score))
    
    def _score_cognitive_development(self, growth_metrics: Dict[str, Any], loop_data: Dict[str, Any]) -> float:
        """인지 발달 점수"""
        current_level = growth_metrics.get("current_level", 1)
        experience_points = growth_metrics.get("experience_points", 0)
        cognitive_complexity = loop_data.get("cognitive_complexity", 0.5)
        
        # 레벨, 경험치, 인지 복잡도를 종합하여 점수 계산
        level_score = min(100.0, current_level * 12.5)  # 8단계 기준
        experience_score = min(100.0, experience_points / 10.0)
        complexity_score = cognitive_complexity * 100
        
        score = (level_score * 0.5 + experience_score * 0.3 + complexity_score * 0.2)
        return min(100.0, max(0.0, score))
    
    def _score_social_progress(self, loop_data: Dict[str, Any], emotional_state: str) -> float:
        """사회성 진전 점수"""
        social_interaction = loop_data.get("social_interaction", 0.0)
        empathy_level = loop_data.get("empathy_level", 0.5)
        communication_quality = loop_data.get("communication_quality", 0.5)
        
        # 사회적 상호작용, 공감, 의사소통 품질을 종합하여 점수 계산
        score = (social_interaction * 0.4 + empathy_level * 0.3 + communication_quality * 0.3) * 100
        return min(100.0, max(0.0, score))
    
    def _score_creativity_level(self, loop_data: Dict[str, Any], growth_metrics: Dict[str, Any]) -> float:
        """창의성 수준 점수"""
        creative_expression = loop_data.get("creative_expression", 0.0)
        innovative_thinking = loop_data.get("innovative_thinking", 0.5)
        artistic_sensitivity = loop_data.get("artistic_sensitivity", 0.5)
        
        # 창의적 표현, 혁신적 사고, 예술적 감수성을 종합하여 점수 계산
        score = (creative_expression * 0.4 + innovative_thinking * 0.4 + artistic_sensitivity * 0.2) * 100
        return min(100.0, max(0.0, score))
    
    def _score_problem_solving(self, judgment_result: Dict[str, Any], loop_data: Dict[str, Any]) -> float:
        """문제 해결 점수"""
        bias_score = judgment_result.get("overall_bias_score", 0.0)
        problem_complexity = loop_data.get("problem_complexity", 0.5)
        solution_effectiveness = loop_data.get("solution_effectiveness", 0.5)
        
        # 편향 감소, 문제 복잡도, 해결 효과성을 종합하여 점수 계산
        bias_penalty = bias_score * 50  # 편향이 높을수록 감점
        complexity_bonus = problem_complexity * 30  # 복잡한 문제 해결 시 가산점
        effectiveness_score = solution_effectiveness * 50
        
        score = max(0.0, 100.0 - bias_penalty + complexity_bonus + effectiveness_score)
        return min(100.0, max(0.0, score))
    
    def _score_adaptability(self, loop_data: Dict[str, Any], emotional_state: str) -> float:
        """적응성 점수"""
        change_response = loop_data.get("change_response", 0.5)
        learning_speed = loop_data.get("learning_speed", 0.5)
        stress_management = loop_data.get("stress_management", 0.5)
        
        # 변화 대응, 학습 속도, 스트레스 관리를 종합하여 점수 계산
        score = (change_response * 0.4 + learning_speed * 0.3 + stress_management * 0.3) * 100
        return min(100.0, max(0.0, score))
    
    def _score_autonomy(self, loop_data: Dict[str, Any], growth_metrics: Dict[str, Any]) -> float:
        """자율성 점수"""
        self_direction = loop_data.get("self_direction", 0.0)
        decision_independence = loop_data.get("decision_independence", 0.5)
        initiative_level = loop_data.get("initiative_level", 0.5)
        
        # 자기 주도성, 의사결정 독립성, 주도성을 종합하여 점수 계산
        score = (self_direction * 0.4 + decision_independence * 0.3 + initiative_level * 0.3) * 100
        return min(100.0, max(0.0, score))
    
    def _get_emotional_intensity(self, emotional_state: str) -> float:
        """감정 강도 계산"""
        intensity_map = {
            "joy": 0.8, "excitement": 0.9, "happiness": 0.7,
            "anger": 0.8, "frustration": 0.6, "irritation": 0.5,
            "fear": 0.7, "anxiety": 0.6, "worry": 0.5,
            "sadness": 0.6, "disappointment": 0.5, "melancholy": 0.4,
            "surprise": 0.6, "amazement": 0.8, "shock": 0.9,
            "neutral": 0.3, "calm": 0.2, "peaceful": 0.1
        }
        return intensity_map.get(emotional_state, 0.5)
    
    def _determine_performance_level(self, score: float) -> PerformanceLevel:
        """성과 수준 결정"""
        if score >= 90.0:
            return PerformanceLevel.EXCELLENT
        elif score >= 70.0:
            return PerformanceLevel.GOOD
        elif score >= 50.0:
            return PerformanceLevel.AVERAGE
        elif score >= 30.0:
            return PerformanceLevel.BELOW_AVERAGE
        else:
            return PerformanceLevel.POOR
    
    def _calculate_contribution(self, score: float, metric: PerformanceMetric) -> float:
        """기여도 계산"""
        weight = self.metric_weights.get(metric, 0.1)
        return score * weight
    
    def _generate_feedback(self, metric: PerformanceMetric, score: float, level: PerformanceLevel) -> str:
        """피드백 생성"""
        if level == PerformanceLevel.EXCELLENT:
            return f"{metric.value}에서 탁월한 성과를 보였습니다."
        elif level == PerformanceLevel.GOOD:
            return f"{metric.value}에서 좋은 성과를 보였습니다."
        elif level == PerformanceLevel.AVERAGE:
            return f"{metric.value}에서 평균적인 성과를 보였습니다."
        elif level == PerformanceLevel.BELOW_AVERAGE:
            return f"{metric.value}에서 개선이 필요합니다."
        else:
            return f"{metric.value}에서 상당한 개선이 필요합니다."
    
    def _calculate_overall_score(self, scores: Dict[PerformanceMetric, PerformanceScore]) -> float:
        """전체 점수 계산"""
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for metric, score in scores.items():
            weight = self.metric_weights.get(metric, 0.1)
            total_weighted_score += score.score * weight
            total_weight += weight
        
        return total_weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_growth_contribution(self, scores: Dict[PerformanceMetric, PerformanceScore], 
                                      growth_metrics: Dict[str, Any]) -> float:
        """성장 기여도 계산"""
        # 성장 지표와 성과 점수의 상관관계를 기반으로 기여도 계산
        growth_indicators = [
            growth_metrics.get("emotional_maturity", 0.0),
            growth_metrics.get("cognitive_development", 0.0),
            growth_metrics.get("social_skills", 0.0),
            growth_metrics.get("self_motivation", 0.0)
        ]
        
        performance_scores = [score.score for score in scores.values()]
        
        # 간단한 상관관계 계산 (실제로는 더 복잡한 통계적 방법 사용 가능)
        avg_growth = sum(growth_indicators) / len(growth_indicators) if growth_indicators else 0.0
        avg_performance = sum(performance_scores) / len(performance_scores) if performance_scores else 0.0
        
        contribution = (avg_growth + avg_performance) / 2.0
        return min(1.0, max(0.0, contribution))
    
    def _calculate_efficiency_rating(self, loop_data: Dict[str, Any], overall_score: float) -> float:
        """효율성 평가"""
        duration = loop_data.get("duration", 1.0)
        complexity = loop_data.get("complexity", 0.5)
        
        # 시간 효율성과 복잡도를 고려한 효율성 계산
        time_efficiency = 1.0 / (duration + 0.1)  # 시간이 짧을수록 효율적
        complexity_efficiency = complexity  # 복잡할수록 더 많은 노력 필요
        
        efficiency = (time_efficiency * 0.6 + complexity_efficiency * 0.4) * overall_score / 100.0
        return min(1.0, max(0.0, efficiency))
    
    def _generate_recommendations(self, scores: Dict[PerformanceMetric, PerformanceScore], 
                                 overall_score: float) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        # 가장 낮은 점수의 지표에 대한 권장사항
        lowest_score = min(scores.values(), key=lambda x: x.score)
        if lowest_score.score < 50.0:
            recommendations.append(f"{lowest_score.metric.value} 개선이 필요합니다.")
        
        # 전체 성과에 대한 권장사항
        if overall_score < 60.0:
            recommendations.append("전반적인 성과 개선이 필요합니다.")
        elif overall_score > 80.0:
            recommendations.append("탁월한 성과를 유지하세요.")
        
        # 지속적 개선 권장사항
        recommendations.append("지속적인 학습과 성장을 유지하세요.")
        
        return recommendations
    
    def _update_baselines(self, scores: Dict[PerformanceMetric, PerformanceScore]):
        """기준선 업데이트"""
        for metric, score in scores.items():
            if metric not in self.baseline_scores:
                self.baseline_scores[metric] = score.score
            else:
                # 이동 평균으로 기준선 업데이트
                self.baseline_scores[metric] = (self.baseline_scores[metric] * 0.9 + score.score * 0.1)
    
    def _update_trends(self, loop_performance: LoopPerformance):
        """트렌드 업데이트"""
        for metric, score in loop_performance.scores.items():
            if metric not in self.improvement_trends:
                self.improvement_trends[metric] = []
            
            baseline = self.baseline_scores.get(metric, score.score)
            improvement = score.score - baseline
            
            self.improvement_trends[metric].append({
                "timestamp": loop_performance.timestamp,
                "improvement": improvement,
                "score": score.score
            })
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """성과 요약"""
        if not self.performance_history:
            return {"message": "성과 기록이 없습니다."}
        
        recent_performances = self.performance_history[-10:]
        avg_overall_score = sum(p.overall_score for p in recent_performances) / len(recent_performances)
        avg_efficiency = sum(p.efficiency_rating for p in recent_performances) / len(recent_performances)
        
        # 지표별 평균 점수
        metric_averages = {}
        for metric in PerformanceMetric:
            if metric != PerformanceMetric.OVERALL_GROWTH:
                scores = [p.scores[metric].score for p in recent_performances if metric in p.scores]
                metric_averages[metric.value] = sum(scores) / len(scores) if scores else 0.0
        
        return {
            "total_loops": len(self.performance_history),
            "recent_average_score": avg_overall_score,
            "recent_average_efficiency": avg_efficiency,
            "metric_averages": metric_averages,
            "improvement_trends": self.improvement_trends,
            "baseline_scores": self.baseline_scores
        }
    
    def get_performance_trends(self, metric: PerformanceMetric, limit: int = 20) -> List[Dict[str, Any]]:
        """성과 트렌드 조회"""
        trends = []
        for performance in self.performance_history[-limit:]:
            if metric in performance.scores:
                trends.append({
                    "timestamp": performance.timestamp,
                    "score": performance.scores[metric].score,
                    "level": performance.scores[metric].level.value,
                    "overall_score": performance.overall_score
                })
        return trends 
 
 