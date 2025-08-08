#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-3: 학습 모니터링 시스템 (Learning Monitoring)

학습 과정의 고급 모니터링 및 분석 기능을 제공하는 시스템입니다.
- 학습 패턴 분석
- 학습 성과 예측
- 학습 최적화 추천
- 학습 이슈 감지
"""

import json
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import numpy as np
import statistics

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitoringLevel(Enum):
    """모니터링 레벨"""
    BASIC = "basic"
    DETAILED = "detailed"
    ADVANCED = "advanced"
    EXPERT = "expert"

class LearningIssueType(Enum):
    """학습 이슈 유형"""
    PERFORMANCE_DECLINE = "performance_decline"
    ENGAGEMENT_DROP = "engagement_drop"
    EFFICIENCY_LOSS = "efficiency_loss"
    QUALITY_DEGRADATION = "quality_degradation"
    PATTERN_BREAK = "pattern_break"
    SYSTEM_ERROR = "system_error"

@dataclass
class LearningIssue:
    """학습 이슈"""
    issue_id: str
    issue_type: LearningIssueType
    severity: str  # low, medium, high, critical
    description: str
    detected_at: datetime
    session_id: str
    metrics_context: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class LearningPrediction:
    """학습 예측"""
    prediction_id: str
    session_id: str
    prediction_type: str
    predicted_value: float
    confidence: float  # 0.0-1.0
    prediction_horizon: timedelta
    factors: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class OptimizationRecommendation:
    """최적화 추천"""
    recommendation_id: str
    session_id: str
    recommendation_type: str
    description: str
    expected_impact: float  # 0.0-1.0
    implementation_difficulty: str  # easy, medium, hard
    priority: str  # low, medium, high, critical
    created_at: datetime = field(default_factory=datetime.now)

class LearningMonitoringSystem:
    """학습 모니터링 시스템"""
    
    def __init__(self):
        """초기화"""
        self.monitoring_level = MonitoringLevel.DETAILED
        self.learning_issues: List[LearningIssue] = []
        self.learning_predictions: List[LearningPrediction] = []
        self.optimization_recommendations: List[OptimizationRecommendation] = []
        
        # 모니터링 설정
        self.monitoring_config = {
            "issue_detection_enabled": True,
            "prediction_enabled": True,
            "optimization_enabled": True,
            "alert_thresholds": {
                "performance_decline": 0.1,
                "engagement_drop": 0.15,
                "efficiency_loss": 0.2,
                "quality_degradation": 0.1
            },
            "prediction_horizon": timedelta(hours=1),
            "analysis_window": timedelta(hours=24)
        }
        
        # 성능 메트릭
        self.performance_metrics = {
            "total_issues_detected": 0,
            "total_predictions_made": 0,
            "total_recommendations_generated": 0,
            "average_prediction_accuracy": 0.0,
            "issue_resolution_rate": 0.0
        }
        
        logger.info("학습 모니터링 시스템 초기화 완료")
    
    async def analyze_learning_patterns(self, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """학습 패턴 분석"""
        try:
            patterns = []
            
            # 시간 기반 패턴 분석
            time_patterns = await self._analyze_time_patterns(session_data)
            patterns.extend(time_patterns)
            
            # 성과 기반 패턴 분석
            performance_patterns = await self._analyze_performance_patterns(session_data)
            patterns.extend(performance_patterns)
            
            # 행동 기반 패턴 분석
            behavior_patterns = await self._analyze_behavior_patterns(session_data)
            patterns.extend(behavior_patterns)
            
            logger.info(f"학습 패턴 분석 완료: {len(patterns)}개 패턴 발견")
            return patterns
            
        except Exception as e:
            logger.error(f"학습 패턴 분석 오류: {e}")
            return []
    
    async def detect_learning_issues(self, session_data: Dict[str, Any]) -> List[LearningIssue]:
        """학습 이슈 감지"""
        try:
            issues = []
            
            # 성과 감소 감지
            performance_issues = await self._detect_performance_issues(session_data)
            issues.extend(performance_issues)
            
            # 참여도 감소 감지
            engagement_issues = await self._detect_engagement_issues(session_data)
            issues.extend(engagement_issues)
            
            # 효율성 손실 감지
            efficiency_issues = await self._detect_efficiency_issues(session_data)
            issues.extend(efficiency_issues)
            
            # 품질 저하 감지
            quality_issues = await self._detect_quality_issues(session_data)
            issues.extend(quality_issues)
            
            # 이슈 저장
            for issue in issues:
                self.learning_issues.append(issue)
                self.performance_metrics["total_issues_detected"] += 1
            
            logger.info(f"학습 이슈 감지 완료: {len(issues)}개 이슈 발견")
            return issues
            
        except Exception as e:
            logger.error(f"학습 이슈 감지 오류: {e}")
            return []
    
    async def predict_learning_outcomes(self, session_data: Dict[str, Any]) -> List[LearningPrediction]:
        """학습 결과 예측"""
        try:
            predictions = []
            
            # 성과 예측
            performance_prediction = await self._predict_performance(session_data)
            if performance_prediction:
                predictions.append(performance_prediction)
            
            # 완료 시간 예측
            completion_prediction = await self._predict_completion_time(session_data)
            if completion_prediction:
                predictions.append(completion_prediction)
            
            # 학습 효율성 예측
            efficiency_prediction = await self._predict_efficiency(session_data)
            if efficiency_prediction:
                predictions.append(efficiency_prediction)
            
            # 예측 저장
            for prediction in predictions:
                self.learning_predictions.append(prediction)
                self.performance_metrics["total_predictions_made"] += 1
            
            logger.info(f"학습 결과 예측 완료: {len(predictions)}개 예측 생성")
            return predictions
            
        except Exception as e:
            logger.error(f"학습 결과 예측 오류: {e}")
            return []
    
    async def generate_optimization_recommendations(self, session_data: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """최적화 추천 생성"""
        try:
            recommendations = []
            
            # 성과 최적화 추천
            performance_recommendations = await self._generate_performance_recommendations(session_data)
            recommendations.extend(performance_recommendations)
            
            # 효율성 최적화 추천
            efficiency_recommendations = await self._generate_efficiency_recommendations(session_data)
            recommendations.extend(efficiency_recommendations)
            
            # 참여도 최적화 추천
            engagement_recommendations = await self._generate_engagement_recommendations(session_data)
            recommendations.extend(engagement_recommendations)
            
            # 추천 저장
            for recommendation in recommendations:
                self.optimization_recommendations.append(recommendation)
                self.performance_metrics["total_recommendations_generated"] += 1
            
            logger.info(f"최적화 추천 생성 완료: {len(recommendations)}개 추천 생성")
            return recommendations
            
        except Exception as e:
            logger.error(f"최적화 추천 생성 오류: {e}")
            return []
    
    async def get_monitoring_report(self, session_id: str = None) -> Dict[str, Any]:
        """모니터링 리포트 생성"""
        try:
            report = {
                "monitoring_level": self.monitoring_level.value,
                "performance_metrics": self.performance_metrics.copy(),
                "recent_issues": [],
                "recent_predictions": [],
                "recent_recommendations": [],
                "system_health": await self._assess_system_health(),
                "generated_at": datetime.now().isoformat()
            }
            
            # 최근 이슈
            recent_issues = [issue for issue in self.learning_issues 
                           if not session_id or issue.session_id == session_id]
            report["recent_issues"] = [self._issue_to_dict(issue) for issue in recent_issues[-10:]]
            
            # 최근 예측
            recent_predictions = [pred for pred in self.learning_predictions 
                                if not session_id or pred.session_id == session_id]
            report["recent_predictions"] = [self._prediction_to_dict(pred) for pred in recent_predictions[-10:]]
            
            # 최근 추천
            recent_recommendations = [rec for rec in self.optimization_recommendations 
                                    if not session_id or rec.session_id == session_id]
            report["recent_recommendations"] = [self._recommendation_to_dict(rec) for rec in recent_recommendations[-10:]]
            
            return report
            
        except Exception as e:
            logger.error(f"모니터링 리포트 생성 오류: {e}")
            return {"error": str(e)}
    
    async def _analyze_time_patterns(self, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """시간 기반 패턴 분석"""
        patterns = []
        
        # 학습 시간 패턴 분석
        if "timestamps" in session_data:
            timestamps = session_data["timestamps"]
            if len(timestamps) > 1:
                # 학습 간격 분석
                intervals = []
                for i in range(1, len(timestamps)):
                    interval = timestamps[i] - timestamps[i-1]
                    intervals.append(interval.total_seconds())
                
                if intervals:
                    avg_interval = statistics.mean(intervals)
                    pattern = {
                        "type": "time_interval",
                        "description": f"평균 학습 간격: {avg_interval:.2f}초",
                        "value": avg_interval,
                        "confidence": 0.8
                    }
                    patterns.append(pattern)
        
        return patterns
    
    async def _analyze_performance_patterns(self, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """성과 기반 패턴 분석"""
        patterns = []
        
        # 성과 점수 패턴 분석
        if "performance_scores" in session_data:
            scores = session_data["performance_scores"]
            if len(scores) > 1:
                # 성과 트렌드 분석
                trend = "improving" if scores[-1] > scores[0] else "declining"
                avg_score = statistics.mean(scores)
                
                pattern = {
                    "type": "performance_trend",
                    "description": f"성과 트렌드: {trend}, 평균 점수: {avg_score:.2f}",
                    "value": avg_score,
                    "trend": trend,
                    "confidence": 0.7
                }
                patterns.append(pattern)
        
        return patterns
    
    async def _analyze_behavior_patterns(self, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """행동 기반 패턴 분석"""
        patterns = []
        
        # 학습 행동 패턴 분석
        if "learning_actions" in session_data:
            actions = session_data["learning_actions"]
            if actions:
                # 가장 빈번한 행동 분석
                action_counts = defaultdict(int)
                for action in actions:
                    action_counts[action] += 1
                
                most_common_action = max(action_counts.items(), key=lambda x: x[1])
                
                pattern = {
                    "type": "behavior_pattern",
                    "description": f"가장 빈번한 행동: {most_common_action[0]} ({most_common_action[1]}회)",
                    "value": most_common_action[1],
                    "confidence": 0.6
                }
                patterns.append(pattern)
        
        return patterns
    
    async def _detect_performance_issues(self, session_data: Dict[str, Any]) -> List[LearningIssue]:
        """성과 이슈 감지"""
        issues = []
        
        if "performance_scores" in session_data:
            scores = session_data["performance_scores"]
            if len(scores) >= 3:
                # 최근 3개 점수의 평균과 이전 3개 점수의 평균 비교
                recent_avg = statistics.mean(scores[-3:])
                previous_avg = statistics.mean(scores[-6:-3]) if len(scores) >= 6 else scores[0]
                
                decline = previous_avg - recent_avg
                if decline > self.monitoring_config["alert_thresholds"]["performance_decline"]:
                    issue = LearningIssue(
                        issue_id=f"perf_{int(time.time())}",
                        issue_type=LearningIssueType.PERFORMANCE_DECLINE,
                        severity="medium" if decline < 0.2 else "high",
                        description=f"성과 감소 감지: {decline:.2f}점 감소",
                        detected_at=datetime.now(),
                        session_id=session_data.get("session_id", "unknown"),
                        metrics_context={"recent_avg": recent_avg, "previous_avg": previous_avg, "decline": decline}
                    )
                    issues.append(issue)
        
        return issues
    
    async def _detect_engagement_issues(self, session_data: Dict[str, Any]) -> List[LearningIssue]:
        """참여도 이슈 감지"""
        issues = []
        
        if "engagement_scores" in session_data:
            scores = session_data["engagement_scores"]
            if len(scores) >= 3:
                recent_avg = statistics.mean(scores[-3:])
                if recent_avg < 0.5:  # 참여도 임계값
                    issue = LearningIssue(
                        issue_id=f"eng_{int(time.time())}",
                        issue_type=LearningIssueType.ENGAGEMENT_DROP,
                        severity="medium" if recent_avg > 0.3 else "high",
                        description=f"참여도 감소 감지: 현재 평균 {recent_avg:.2f}",
                        detected_at=datetime.now(),
                        session_id=session_data.get("session_id", "unknown"),
                        metrics_context={"recent_avg": recent_avg}
                    )
                    issues.append(issue)
        
        return issues
    
    async def _detect_efficiency_issues(self, session_data: Dict[str, Any]) -> List[LearningIssue]:
        """효율성 이슈 감지"""
        issues = []
        
        if "efficiency_scores" in session_data:
            scores = session_data["efficiency_scores"]
            if len(scores) >= 3:
                recent_avg = statistics.mean(scores[-3:])
                if recent_avg < 0.6:  # 효율성 임계값
                    issue = LearningIssue(
                        issue_id=f"eff_{int(time.time())}",
                        issue_type=LearningIssueType.EFFICIENCY_LOSS,
                        severity="medium" if recent_avg > 0.4 else "high",
                        description=f"효율성 손실 감지: 현재 평균 {recent_avg:.2f}",
                        detected_at=datetime.now(),
                        session_id=session_data.get("session_id", "unknown"),
                        metrics_context={"recent_avg": recent_avg}
                    )
                    issues.append(issue)
        
        return issues
    
    async def _detect_quality_issues(self, session_data: Dict[str, Any]) -> List[LearningIssue]:
        """품질 이슈 감지"""
        issues = []
        
        if "quality_scores" in session_data:
            scores = session_data["quality_scores"]
            if len(scores) >= 3:
                recent_avg = statistics.mean(scores[-3:])
                if recent_avg < 0.7:  # 품질 임계값
                    issue = LearningIssue(
                        issue_id=f"qual_{int(time.time())}",
                        issue_type=LearningIssueType.QUALITY_DEGRADATION,
                        severity="medium" if recent_avg > 0.5 else "high",
                        description=f"품질 저하 감지: 현재 평균 {recent_avg:.2f}",
                        detected_at=datetime.now(),
                        session_id=session_data.get("session_id", "unknown"),
                        metrics_context={"recent_avg": recent_avg}
                    )
                    issues.append(issue)
        
        return issues
    
    async def _predict_performance(self, session_data: Dict[str, Any]) -> Optional[LearningPrediction]:
        """성과 예측"""
        if "performance_scores" in session_data and len(session_data["performance_scores"]) >= 3:
            scores = session_data["performance_scores"]
            # 간단한 선형 예측
            if len(scores) >= 3:
                recent_trend = (scores[-1] - scores[-3]) / 2
                predicted_score = min(1.0, max(0.0, scores[-1] + recent_trend))
                
                return LearningPrediction(
                    prediction_id=f"perf_pred_{int(time.time())}",
                    session_id=session_data.get("session_id", "unknown"),
                    prediction_type="performance",
                    predicted_value=predicted_score,
                    confidence=0.6,
                    prediction_horizon=self.monitoring_config["prediction_horizon"],
                    factors=["recent_trend", "historical_performance"]
                )
        return None
    
    async def _predict_completion_time(self, session_data: Dict[str, Any]) -> Optional[LearningPrediction]:
        """완료 시간 예측"""
        if "progress" in session_data and "start_time" in session_data:
            progress = session_data["progress"]
            start_time = session_data["start_time"]
            
            if progress > 0:
                elapsed_time = datetime.now() - start_time
                estimated_total_time = elapsed_time / progress
                remaining_time = estimated_total_time - elapsed_time
                
                return LearningPrediction(
                    prediction_id=f"comp_pred_{int(time.time())}",
                    session_id=session_data.get("session_id", "unknown"),
                    prediction_type="completion_time",
                    predicted_value=remaining_time.total_seconds(),
                    confidence=0.5,
                    prediction_horizon=self.monitoring_config["prediction_horizon"],
                    factors=["current_progress", "elapsed_time"]
                )
        return None
    
    async def _predict_efficiency(self, session_data: Dict[str, Any]) -> Optional[LearningPrediction]:
        """효율성 예측"""
        if "efficiency_scores" in session_data and len(session_data["efficiency_scores"]) >= 3:
            scores = session_data["efficiency_scores"]
            recent_avg = statistics.mean(scores[-3:])
            
            # 효율성 트렌드 기반 예측
            if len(scores) >= 3:
                trend = (scores[-1] - scores[-3]) / 2
                predicted_efficiency = min(1.0, max(0.0, recent_avg + trend))
                
                return LearningPrediction(
                    prediction_id=f"eff_pred_{int(time.time())}",
                    session_id=session_data.get("session_id", "unknown"),
                    prediction_type="efficiency",
                    predicted_value=predicted_efficiency,
                    confidence=0.5,
                    prediction_horizon=self.monitoring_config["prediction_horizon"],
                    factors=["recent_efficiency", "efficiency_trend"]
                )
        return None
    
    async def _generate_performance_recommendations(self, session_data: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """성과 최적화 추천 생성"""
        recommendations = []
        
        if "performance_scores" in session_data:
            scores = session_data["performance_scores"]
            if len(scores) >= 3:
                recent_avg = statistics.mean(scores[-3:])
                
                if recent_avg < 0.7:
                    recommendation = OptimizationRecommendation(
                        recommendation_id=f"perf_rec_{int(time.time())}",
                        session_id=session_data.get("session_id", "unknown"),
                        recommendation_type="performance_optimization",
                        description="성과 향상을 위해 학습 전략을 조정하세요",
                        expected_impact=0.2,
                        implementation_difficulty="medium",
                        priority="high"
                    )
                    recommendations.append(recommendation)
        
        return recommendations
    
    async def _generate_efficiency_recommendations(self, session_data: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """효율성 최적화 추천 생성"""
        recommendations = []
        
        if "efficiency_scores" in session_data:
            scores = session_data["efficiency_scores"]
            if len(scores) >= 3:
                recent_avg = statistics.mean(scores[-3:])
                
                if recent_avg < 0.6:
                    recommendation = OptimizationRecommendation(
                        recommendation_id=f"eff_rec_{int(time.time())}",
                        session_id=session_data.get("session_id", "unknown"),
                        recommendation_type="efficiency_optimization",
                        description="학습 효율성을 높이기 위해 시간 관리를 개선하세요",
                        expected_impact=0.15,
                        implementation_difficulty="easy",
                        priority="medium"
                    )
                    recommendations.append(recommendation)
        
        return recommendations
    
    async def _generate_engagement_recommendations(self, session_data: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """참여도 최적화 추천 생성"""
        recommendations = []
        
        if "engagement_scores" in session_data:
            scores = session_data["engagement_scores"]
            if len(scores) >= 3:
                recent_avg = statistics.mean(scores[-3:])
                
                if recent_avg < 0.5:
                    recommendation = OptimizationRecommendation(
                        recommendation_id=f"eng_rec_{int(time.time())}",
                        session_id=session_data.get("session_id", "unknown"),
                        recommendation_type="engagement_optimization",
                        description="학습 참여도를 높이기 위해 흥미로운 주제를 선택하세요",
                        expected_impact=0.25,
                        implementation_difficulty="easy",
                        priority="high"
                    )
                    recommendations.append(recommendation)
        
        return recommendations
    
    async def _assess_system_health(self) -> Dict[str, Any]:
        """시스템 건강도 평가"""
        health = {
            "overall_status": "healthy",
            "issues_count": len(self.learning_issues),
            "unresolved_issues": len([i for i in self.learning_issues if not i.resolved]),
            "predictions_accuracy": self.performance_metrics["average_prediction_accuracy"],
            "recommendations_effectiveness": 0.0  # TODO: 구현 필요
        }
        
        # 건강도 상태 결정
        if health["unresolved_issues"] > 5:
            health["overall_status"] = "warning"
        elif health["unresolved_issues"] > 10:
            health["overall_status"] = "critical"
        
        return health
    
    def _issue_to_dict(self, issue: LearningIssue) -> Dict[str, Any]:
        """이슈를 딕셔너리로 변환"""
        return {
            "issue_id": issue.issue_id,
            "issue_type": issue.issue_type.value,
            "severity": issue.severity,
            "description": issue.description,
            "detected_at": issue.detected_at.isoformat(),
            "session_id": issue.session_id,
            "resolved": issue.resolved
        }
    
    def _prediction_to_dict(self, prediction: LearningPrediction) -> Dict[str, Any]:
        """예측을 딕셔너리로 변환"""
        return {
            "prediction_id": prediction.prediction_id,
            "prediction_type": prediction.prediction_type,
            "predicted_value": prediction.predicted_value,
            "confidence": prediction.confidence,
            "session_id": prediction.session_id,
            "created_at": prediction.created_at.isoformat()
        }
    
    def _recommendation_to_dict(self, recommendation: OptimizationRecommendation) -> Dict[str, Any]:
        """추천을 딕셔너리로 변환"""
        return {
            "recommendation_id": recommendation.recommendation_id,
            "recommendation_type": recommendation.recommendation_type,
            "description": recommendation.description,
            "expected_impact": recommendation.expected_impact,
            "priority": recommendation.priority,
            "session_id": recommendation.session_id,
            "created_at": recommendation.created_at.isoformat()
        }
