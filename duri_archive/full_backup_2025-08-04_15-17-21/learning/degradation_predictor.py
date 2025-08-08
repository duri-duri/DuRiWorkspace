"""
DuRi 성능 저하 예측 시스템

성능 경향을 분석하여 미래의 성능 저하를 예측하고 리팩터링 필요성을 판단합니다.
"""

import logging
import time
import threading
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import json

logger = logging.getLogger(__name__)

class DegradationLevel(Enum):
    """성능 저하 수준"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RefactorPriority(Enum):
    """리팩터링 우선순위"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class DegradationPrediction:
    """성능 저하 예측"""
    metric_name: str
    current_value: float
    predicted_value: float
    time_horizon_hours: int
    confidence: float
    degradation_level: DegradationLevel
    refactor_priority: RefactorPriority
    prediction_reason: str
    timestamp: datetime

@dataclass
class RefactorRecommendation:
    """리팩터링 권장사항"""
    recommendation_id: str
    target_module: str
    refactor_type: str
    priority: RefactorPriority
    expected_impact: float
    implementation_cost: str  # "low", "medium", "high"
    risk_level: str  # "low", "medium", "high"
    description: str
    reasoning: str
    timestamp: datetime

class DegradationPredictor:
    """DuRi 성능 저하 예측 시스템"""
    
    def __init__(self):
        """DegradationPredictor 초기화"""
        self.predictions: List[DegradationPrediction] = []
        self.recommendations: List[RefactorRecommendation] = []
        self.is_predicting = False
        self.prediction_thread: Optional[threading.Thread] = None
        
        # 예측 설정
        self.prediction_horizon_hours = 24  # 24시간 후 예측
        self.prediction_interval_minutes = 60  # 1시간마다 예측
        self.min_confidence_threshold = 0.7  # 최소 신뢰도 임계값
        
        # 성능 저하 임계값
        self.degradation_thresholds = {
            "cpu_usage": {"low": 70, "medium": 80, "high": 90, "critical": 95},
            "memory_usage": {"low": 75, "medium": 85, "high": 90, "critical": 95},
            "learning_cycle_time": {"low": 3.0, "medium": 5.0, "high": 8.0, "critical": 12.0},
            "error_rate": {"low": 0.05, "medium": 0.10, "high": 0.20, "critical": 0.30},
            "memory_growth_rate": {"low": 0.10, "medium": 0.20, "high": 0.30, "critical": 0.50},
            "system_complexity": {"low": 0.60, "medium": 0.75, "high": 0.85, "critical": 0.95}
        }
        
        # 챗지피티 제안 트리거 조건
        self.trigger_conditions = {
            "performance_decline_threshold": 0.08,  # 8% 성능 하락폭
            "stagnation_detection_days": 3,  # 3일간 정체 감지
            "structure_exhaustion_threshold": 0.85  # 85% 구조 고갈 임계값
        }
        
        # 리팩터링 우선순위 매핑
        self.priority_mapping = {
            DegradationLevel.LOW: RefactorPriority.LOW,
            DegradationLevel.MEDIUM: RefactorPriority.MEDIUM,
            DegradationLevel.HIGH: RefactorPriority.HIGH,
            DegradationLevel.CRITICAL: RefactorPriority.URGENT
        }
        
        logger.info("DegradationPredictor 초기화 완료")
    
    def start_prediction(self):
        """성능 저하 예측을 시작합니다."""
        if self.is_predicting:
            logger.warning("이미 예측 중입니다.")
            return
        
        self.is_predicting = True
        self.prediction_thread = threading.Thread(target=self._prediction_loop, daemon=True)
        self.prediction_thread.start()
        logger.info("성능 저하 예측 시작")
    
    def stop_prediction(self):
        """성능 저하 예측을 중지합니다."""
        self.is_predicting = False
        if self.prediction_thread:
            self.prediction_thread.join(timeout=5)
        logger.info("성능 저하 예측 중지")
    
    def _prediction_loop(self):
        """예측 루프"""
        while self.is_predicting:
            try:
                # 성능 저하 예측 실행
                predictions = self._predict_degradations()
                
                # 리팩터링 권장사항 생성
                recommendations = self._generate_refactor_recommendations(predictions)
                
                # 결과 저장
                self.predictions.extend(predictions)
                self.recommendations.extend(recommendations)
                
                # 오래된 예측 정리 (7일 이상)
                self._cleanup_old_predictions()
                
                logger.info(f"예측 완료: {len(predictions)}개 예측, {len(recommendations)}개 권장사항")
                
                # 다음 예측까지 대기
                time.sleep(self.prediction_interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"예측 중 오류: {e}")
                time.sleep(300)  # 오류 시 5분 대기
    
    def _predict_degradations(self) -> List[DegradationPrediction]:
        """성능 저하를 예측합니다."""
        predictions = []
        
        try:
            # PerformanceHistory에서 최근 데이터 가져오기
            import sys
            sys.path.append('.')
            from duri_brain.learning.performance_history import get_performance_history
            history = get_performance_history()
            
            # 챗지피티 제안 트리거 조건 확인
            if self._check_chatgpt_trigger_conditions(history):
                logger.warning("🚨 챗지피티 제안 트리거 조건 충족 - 리팩터링 필요")
                # 긴급 리팩터링 예측 생성
                emergency_prediction = self._create_emergency_prediction()
                if emergency_prediction:
                    predictions.append(emergency_prediction)
            
            # 각 성능 지표별로 예측
            for metric_name in self.degradation_thresholds.keys():
                try:
                    prediction = self._predict_metric_degradation(metric_name, history)
                    if prediction:
                        predictions.append(prediction)
                except Exception as e:
                    logger.error(f"{metric_name} 예측 실패: {e}")
            
        except Exception as e:
            logger.error(f"성능 저하 예측 실패: {e}")
        
        return predictions
    
    def _check_chatgpt_trigger_conditions(self, history) -> bool:
        """챗지피티 제안 트리거 조건을 확인합니다."""
        try:
            # 1. 최근 3일간 평균 성능 하락폭 > 8% 확인
            recent_trends = history.get_recent_trends(72)  # 3일 = 72시간
            
            if len(recent_trends) < 5:  # 최소 데이터 포인트 필요
                return False
            
            # 성능 하락폭 계산
            total_decline = 0.0
            decline_count = 0
            
            for trend in recent_trends:
                if trend.trend_direction == "degrading":
                    total_decline += abs(trend.change_rate)
                    decline_count += 1
            
            if decline_count > 0:
                avg_decline = total_decline / decline_count
                if avg_decline > self.trigger_conditions["performance_decline_threshold"] * 100:  # 8%
                    logger.warning(f"🚨 평균 성능 하락폭 {avg_decline:.1f}% > 8% 임계값")
                    return True
            
            # 2. DuRi 내부 판단 "정체 + 구조 고갈" 확인
            if self._check_stagnation_and_exhaustion(history):
                logger.warning("🚨 정체 + 구조 고갈 감지")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"트리거 조건 확인 실패: {e}")
            return False
    
    def _check_stagnation_and_exhaustion(self, history) -> bool:
        """정체와 구조 고갈을 확인합니다."""
        try:
            # 시스템 복잡도가 85% 이상이고 성능 개선이 없는 경우
            recent_trends = history.get_recent_trends(24)  # 최근 24시간
            
            complexity_trends = [t for t in recent_trends if t.metric_name == "system_complexity"]
            performance_trends = [t for t in recent_trends if t.metric_name in ["cpu_usage", "memory_usage", "learning_cycle_time"]]
            
            # 시스템 복잡도가 임계값을 초과하는지 확인
            if complexity_trends:
                latest_complexity = complexity_trends[-1].final_value
                if latest_complexity > self.trigger_conditions["structure_exhaustion_threshold"]:
                    # 성능 개선이 없는지 확인
                    improving_count = sum(1 for t in performance_trends if t.trend_direction == "improving")
                    if improving_count == 0:
                        logger.warning(f"🚨 시스템 복잡도 {latest_complexity:.1f}% > 85% 임계값, 성능 개선 없음")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"정체 및 구조 고갈 확인 실패: {e}")
            return False
    
    def _create_emergency_prediction(self) -> Optional[DegradationPrediction]:
        """긴급 리팩터링 예측을 생성합니다."""
        try:
            return DegradationPrediction(
                metric_name="emergency_refactor",
                current_value=0.0,
                predicted_value=0.0,
                time_horizon_hours=24,
                confidence=0.95,  # 높은 신뢰도
                degradation_level=DegradationLevel.CRITICAL,
                refactor_priority=RefactorPriority.URGENT,
                prediction_reason="챗지피티 제안 트리거 조건 충족: 성능 하락폭 > 8% 또는 정체 + 구조 고갈",
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"긴급 예측 생성 실패: {e}")
            return None
    
    def _predict_metric_degradation(self, metric_name: str, history) -> Optional[DegradationPrediction]:
        """특정 지표의 성능 저하를 예측합니다."""
        try:
            # 최근 48시간 데이터 조회
            recent_trends = history.get_recent_trends(48)
            
            # 해당 지표의 데이터 필터링
            metric_trends = [t for t in recent_trends if t.metric_name == metric_name]
            
            if len(metric_trends) < 3:
                return None  # 충분한 데이터가 없음
            
            # 선형 회귀를 사용한 예측
            prediction = self._linear_regression_prediction(metric_trends, metric_name)
            
            if prediction and prediction.confidence >= self.min_confidence_threshold:
                return prediction
            
        except Exception as e:
            logger.error(f"{metric_name} 예측 실패: {e}")
        
        return None
    
    def _linear_regression_prediction(self, trends: List, metric_name: str) -> Optional[DegradationPrediction]:
        """선형 회귀를 사용한 예측"""
        try:
            # 시간과 값 데이터 준비
            times = []
            values = []
            
            for trend in trends:
                # 시간을 시간 단위로 변환
                time_hours = (trend.end_time - trend.start_time).total_seconds() / 3600
                times.append(time_hours)
                values.append(trend.final_value)
            
            if len(times) < 2:
                return None
            
            # 선형 회귀 모델 학습
            X = np.array(times).reshape(-1, 1)
            y = np.array(values)
            
            model = LinearRegression()
            model.fit(X, y)
            
            # 현재 값 (가장 최근)
            current_value = values[-1]
            
            # 미래 예측 (24시간 후)
            future_time = times[-1] + self.prediction_horizon_hours
            predicted_value = model.predict([[future_time]])[0]
            
            # 신뢰도 계산 (R² 점수 기반)
            confidence = max(0.0, min(1.0, model.score(X, y)))
            
            # 성능 저하 수준 판단
            degradation_level = self._determine_degradation_level(metric_name, predicted_value)
            
            # 리팩터링 우선순위 결정
            refactor_priority = self.priority_mapping.get(degradation_level, RefactorPriority.NONE)
            
            # 예측 이유 생성
            prediction_reason = self._generate_prediction_reason(metric_name, current_value, predicted_value, confidence)
            
            return DegradationPrediction(
                metric_name=metric_name,
                current_value=current_value,
                predicted_value=predicted_value,
                time_horizon_hours=self.prediction_horizon_hours,
                confidence=confidence,
                degradation_level=degradation_level,
                refactor_priority=refactor_priority,
                prediction_reason=prediction_reason,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"선형 회귀 예측 실패: {e}")
            return None
    
    def _determine_degradation_level(self, metric_name: str, predicted_value: float) -> DegradationLevel:
        """성능 저하 수준을 판단합니다."""
        thresholds = self.degradation_thresholds.get(metric_name, {})
        
        if predicted_value >= thresholds.get("critical", float('inf')):
            return DegradationLevel.CRITICAL
        elif predicted_value >= thresholds.get("high", float('inf')):
            return DegradationLevel.HIGH
        elif predicted_value >= thresholds.get("medium", float('inf')):
            return DegradationLevel.MEDIUM
        elif predicted_value >= thresholds.get("low", float('inf')):
            return DegradationLevel.LOW
        else:
            return DegradationLevel.NONE
    
    def _generate_prediction_reason(self, metric_name: str, current_value: float, 
                                  predicted_value: float, confidence: float) -> str:
        """예측 이유를 생성합니다."""
        change_rate = ((predicted_value - current_value) / current_value) * 100 if current_value != 0 else 0
        
        if change_rate > 20:
            trend = "급격한 성능 저하"
        elif change_rate > 10:
            trend = "점진적 성능 저하"
        elif change_rate > 0:
            trend = "약간의 성능 저하"
        else:
            trend = "성능 안정"
        
        return f"{metric_name}: {trend} 예상 (변화율: {change_rate:.1f}%, 신뢰도: {confidence:.1f})"
    
    def _generate_refactor_recommendations(self, predictions: List[DegradationPrediction]) -> List[RefactorRecommendation]:
        """리팩터링 권장사항을 생성합니다."""
        recommendations = []
        
        # 높은 우선순위 예측만 필터링
        high_priority_predictions = [
            p for p in predictions 
            if p.refactor_priority in [RefactorPriority.HIGH, RefactorPriority.URGENT]
        ]
        
        for prediction in high_priority_predictions:
            try:
                recommendation = self._create_refactor_recommendation(prediction)
                if recommendation:
                    recommendations.append(recommendation)
            except Exception as e:
                logger.error(f"권장사항 생성 실패: {e}")
        
        return recommendations
    
    def _create_refactor_recommendation(self, prediction: DegradationPrediction) -> Optional[RefactorRecommendation]:
        """특정 예측에 대한 리팩터링 권장사항을 생성합니다."""
        try:
            # 지표별 리팩터링 전략 매핑
            refactor_strategies = {
                "cpu_usage": {
                    "type": "algorithm_optimization",
                    "target_module": "learning_loop_manager",
                    "description": "학습 알고리즘 최적화로 CPU 사용량 감소",
                    "expected_impact": 0.25,
                    "implementation_cost": "medium",
                    "risk_level": "low"
                },
                "memory_usage": {
                    "type": "memory_optimization",
                    "target_module": "memory_sync",
                    "description": "메모리 관리 최적화 및 가비지 컬렉션 개선",
                    "expected_impact": 0.30,
                    "implementation_cost": "medium",
                    "risk_level": "medium"
                },
                "learning_cycle_time": {
                    "type": "performance_optimization",
                    "target_module": "smart_learning_checker",
                    "description": "학습 사이클 실행 시간 최적화",
                    "expected_impact": 0.40,
                    "implementation_cost": "high",
                    "risk_level": "medium"
                },
                "error_rate": {
                    "type": "error_handling_improvement",
                    "target_module": "fallback_handler",
                    "description": "오류 처리 시스템 강화 및 예외 처리 개선",
                    "expected_impact": 0.35,
                    "implementation_cost": "low",
                    "risk_level": "low"
                },
                "memory_growth_rate": {
                    "type": "memory_leak_fix",
                    "target_module": "performance_monitor",
                    "description": "메모리 누수 방지 및 메모리 사용량 모니터링 강화",
                    "expected_impact": 0.45,
                    "implementation_cost": "high",
                    "risk_level": "high"
                },
                "system_complexity": {
                    "type": "code_refactoring",
                    "target_module": "self_learning_orchestrator",
                    "description": "시스템 복잡도 감소를 위한 코드 리팩터링",
                    "expected_impact": 0.20,
                    "implementation_cost": "high",
                    "risk_level": "high"
                }
            }
            
            strategy = refactor_strategies.get(prediction.metric_name, {})
            if not strategy:
                return None
            
            recommendation_id = f"REFACTOR_{prediction.metric_name.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            reasoning = f"예측된 {prediction.metric_name} 성능 저하 ({prediction.degradation_level.value})에 따른 {strategy['description']}"
            
            return RefactorRecommendation(
                recommendation_id=recommendation_id,
                target_module=strategy.get("target_module", "unknown"),
                refactor_type=strategy.get("type", "general"),
                priority=prediction.refactor_priority,
                expected_impact=strategy.get("expected_impact", 0.0),
                implementation_cost=strategy.get("implementation_cost", "medium"),
                risk_level=strategy.get("risk_level", "medium"),
                description=strategy.get("description", "일반적인 성능 최적화"),
                reasoning=reasoning,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"리팩터링 권장사항 생성 실패: {e}")
            return None
    
    def _cleanup_old_predictions(self):
        """오래된 예측을 정리합니다."""
        try:
            cutoff_time = datetime.now() - timedelta(days=7)
            
            # 오래된 예측 제거
            self.predictions = [
                p for p in self.predictions 
                if p.timestamp > cutoff_time
            ]
            
            # 오래된 권장사항 제거
            self.recommendations = [
                r for r in self.recommendations 
                if r.timestamp > cutoff_time
            ]
            
        except Exception as e:
            logger.error(f"오래된 예측 정리 실패: {e}")
    
    def get_recent_predictions(self, hours: int = 24) -> List[DegradationPrediction]:
        """최근 예측을 조회합니다."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            p for p in self.predictions 
            if p.timestamp > cutoff_time
        ]
    
    def get_active_recommendations(self) -> List[RefactorRecommendation]:
        """활성 권장사항을 조회합니다."""
        # 최근 24시간 내의 높은 우선순위 권장사항
        cutoff_time = datetime.now() - timedelta(hours=24)
        return [
            r for r in self.recommendations 
            if r.timestamp > cutoff_time and r.priority in [RefactorPriority.HIGH, RefactorPriority.URGENT]
        ]
    
    def get_prediction_summary(self) -> Dict[str, Any]:
        """예측 요약을 반환합니다."""
        try:
            recent_predictions = self.get_recent_predictions(24)
            active_recommendations = self.get_active_recommendations()
            
            # 경고 수준별 분류
            critical_predictions = [p for p in recent_predictions if p.degradation_level == DegradationLevel.CRITICAL]
            high_predictions = [p for p in recent_predictions if p.degradation_level == DegradationLevel.HIGH]
            medium_predictions = [p for p in recent_predictions if p.degradation_level == DegradationLevel.MEDIUM]
            
            return {
                "total_predictions": len(recent_predictions),
                "critical_predictions": len(critical_predictions),
                "high_predictions": len(high_predictions),
                "medium_predictions": len(medium_predictions),
                "active_recommendations": len(active_recommendations),
                "prediction_confidence_avg": np.mean([p.confidence for p in recent_predictions]) if recent_predictions else 0.0,
                "critical_metrics": [p.metric_name for p in critical_predictions],
                "high_priority_recommendations": [
                    {
                        "id": r.recommendation_id,
                        "target_module": r.target_module,
                        "priority": r.priority.value,
                        "expected_impact": f"{r.expected_impact:.1%}"
                    }
                    for r in active_recommendations
                ]
            }
            
        except Exception as e:
            logger.error(f"예측 요약 생성 실패: {e}")
            return {}

# 전역 인스턴스
_degradation_predictor: Optional[DegradationPredictor] = None

def get_degradation_predictor() -> DegradationPredictor:
    """DegradationPredictor 인스턴스를 반환합니다."""
    global _degradation_predictor
    if _degradation_predictor is None:
        _degradation_predictor = DegradationPredictor()
    return _degradation_predictor

if __name__ == "__main__":
    # 테스트
    predictor = get_degradation_predictor()
    predictor.start_prediction()
    
    print("🔮 성능 저하 예측 시스템 테스트 시작")
    print("⏰ 60초간 예측 실행 중...")
    
    time.sleep(60)
    
    summary = predictor.get_prediction_summary()
    print(f"📊 예측 요약: {summary}")
    
    predictor.stop_prediction()
    print("✅ 테스트 완료") 