"""
DuRi의 전략 생존 판단 기준

전략 생존 판단을 위한 기준과 정책을 관리합니다.
수치적 성과와 감정 상태의 균형적 판단을 위한 기준을 정의합니다.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class JudgmentAction(Enum):
    """판단 행동"""
    CONTINUE = "continue"      # 전략 지속
    MODIFY = "modify"          # 전략 수정
    DISCARD = "discard"        # 전략 폐기

class EmotionPolicy(Enum):
    """감정 처리 정책"""
    POSITIVE = "positive"      # 호감 - 지속 가능성 강화
    NEGATIVE = "negative"      # 불호 - 조정/폐기 유도
    REPEATED_NEGATIVE = "repeated_negative"  # 반복 불호 - 폐기 가속

@dataclass
class SurvivalCriteria:
    """생존 판단 기준"""
    judgment_period: int = 3  # 판단 주기 (일)
    min_improvement: float = 0.01  # 최소 개선률 (1%)
    failure_threshold: float = 0.5  # 실패율 임계값 (50%)
    emotion_weight: float = 0.3  # 감정 가중치 (30%)
    performance_weight: float = 0.7  # 성과 가중치 (70%)

@dataclass
class JudgmentResult:
    """판단 결과"""
    action: JudgmentAction
    confidence: float
    reasoning: List[str]
    performance_score: float
    emotion_score: float
    combined_score: float
    next_evaluation_date: datetime

class SurvivalCriteriaManager:
    """
    DuRi의 전략 생존 판단 기준 관리자
    
    전략 생존 판단을 위한 기준과 정책을 관리합니다.
    """
    
    def __init__(self):
        """SurvivalCriteriaManager 초기화"""
        self.criteria = SurvivalCriteria()
        self.emotion_policy = self._initialize_emotion_policy()
        self.judgment_history: List[JudgmentResult] = []
        
        logger.info("SurvivalCriteriaManager 초기화 완료")
    
    def _initialize_emotion_policy(self) -> Dict[str, EmotionPolicy]:
        """감정 처리 정책을 초기화합니다."""
        return {
            "호감": EmotionPolicy.POSITIVE,
            "좋음": EmotionPolicy.POSITIVE,
            "만족": EmotionPolicy.POSITIVE,
            "불호": EmotionPolicy.NEGATIVE,
            "싫음": EmotionPolicy.NEGATIVE,
            "불만": EmotionPolicy.NEGATIVE,
            "반복_불호": EmotionPolicy.REPEATED_NEGATIVE,
            "지속_불호": EmotionPolicy.REPEATED_NEGATIVE
        }
    
    def evaluate_strategy_survival(self, 
                                 performance_history: List[float],
                                 emotion_history: List[str],
                                 current_performance: float,
                                 current_emotion: str,
                                 strategy_age_days: int) -> JudgmentResult:
        """
        전략 생존을 판단합니다.
        
        Args:
            performance_history: 성과 히스토리
            emotion_history: 감정 히스토리
            current_performance: 현재 성과
            current_emotion: 현재 감정
            strategy_age_days: 전략 사용 일수
            
        Returns:
            JudgmentResult: 판단 결과
        """
        try:
            # 1. 성과 기반 판단
            performance_score = self._calculate_performance_score(performance_history, current_performance)
            
            # 2. 감정 기반 판단
            emotion_score = self._calculate_emotion_score(emotion_history, current_emotion)
            
            # 3. 통합 점수 계산
            combined_score = (performance_score * self.criteria.performance_weight + 
                            emotion_score * self.criteria.emotion_weight)
            
            # 4. 판단 행동 결정
            action, reasoning = self._determine_action(performance_score, emotion_score, 
                                                     combined_score, strategy_age_days)
            
            # 5. 신뢰도 계산
            confidence = self._calculate_confidence(performance_score, emotion_score, 
                                                 len(performance_history), len(emotion_history))
            
            # 6. 다음 평가 날짜 설정
            next_evaluation_date = datetime.now() + timedelta(days=self.criteria.judgment_period)
            
            result = JudgmentResult(
                action=action,
                confidence=confidence,
                reasoning=reasoning,
                performance_score=performance_score,
                emotion_score=emotion_score,
                combined_score=combined_score,
                next_evaluation_date=next_evaluation_date
            )
            
            self.judgment_history.append(result)
            
            logger.info(f"전략 생존 판단 완료: {action.value}, 신뢰도: {confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"전략 생존 판단 실패: {e}")
            return JudgmentResult(
                action=JudgmentAction.CONTINUE,
                confidence=0.0,
                reasoning=[f"판단 실패: {str(e)}"],
                performance_score=0.0,
                emotion_score=0.0,
                combined_score=0.0,
                next_evaluation_date=datetime.now() + timedelta(days=self.criteria.judgment_period)
            )
    
    def _calculate_performance_score(self, performance_history: List[float], 
                                   current_performance: float) -> float:
        """성과 점수를 계산합니다."""
        if not performance_history:
            return 0.5  # 기본값
        
        # 최근 3일간 성과 변화 분석
        recent_performances = performance_history[-3:] if len(performance_history) >= 3 else performance_history
        
        if len(recent_performances) < 2:
            return 0.5
        
        # 개선률 계산
        initial_performance = recent_performances[0]
        final_performance = recent_performances[-1]
        
        if initial_performance == 0:
            improvement_rate = 0.0
        else:
            improvement_rate = (final_performance - initial_performance) / initial_performance
        
        # 성과 점수 계산
        if improvement_rate >= self.criteria.min_improvement:
            # 개선이 있음
            performance_score = 0.8 + (improvement_rate * 2)  # 최대 1.0
        elif improvement_rate >= 0:
            # 미미한 개선
            performance_score = 0.6 + (improvement_rate / self.criteria.min_improvement) * 0.2
        else:
            # 성과 하락
            performance_score = max(0.0, 0.6 + improvement_rate)
        
        return min(performance_score, 1.0)
    
    def _calculate_emotion_score(self, emotion_history: List[str], 
                               current_emotion: str) -> float:
        """감정 점수를 계산합니다."""
        if not emotion_history:
            return 0.5  # 기본값
        
        # 현재 감정의 정책 확인
        emotion_policy = self.emotion_policy.get(current_emotion, EmotionPolicy.POSITIVE)
        
        # 감정 히스토리 분석
        recent_emotions = emotion_history[-3:] if len(emotion_history) >= 3 else emotion_history
        
        positive_count = sum(1 for e in recent_emotions if self.emotion_policy.get(e) == EmotionPolicy.POSITIVE)
        negative_count = sum(1 for e in recent_emotions if self.emotion_policy.get(e) == EmotionPolicy.NEGATIVE)
        repeated_negative_count = sum(1 for e in recent_emotions if self.emotion_policy.get(e) == EmotionPolicy.REPEATED_NEGATIVE)
        
        # 감정 점수 계산
        if emotion_policy == EmotionPolicy.POSITIVE:
            base_score = 0.7
        elif emotion_policy == EmotionPolicy.NEGATIVE:
            base_score = 0.3
        elif emotion_policy == EmotionPolicy.REPEATED_NEGATIVE:
            base_score = 0.1
        else:
            base_score = 0.5
        
        # 반복 패턴에 따른 조정
        if repeated_negative_count >= 2:
            base_score *= 0.5  # 반복 불호 시 점수 감소
        elif positive_count > negative_count:
            base_score *= 1.2  # 긍정적 감정 우세 시 점수 증가
        
        return min(base_score, 1.0)
    
    def _determine_action(self, performance_score: float, emotion_score: float,
                         combined_score: float, strategy_age_days: int) -> tuple[JudgmentAction, List[str]]:
        """판단 행동을 결정합니다."""
        reasoning = []
        
        # 1. 조건 변경 판단 (3일간 1% 미만 개선)
        if strategy_age_days >= self.criteria.judgment_period:
            if performance_score < 0.6:  # 성과가 낮음
                reasoning.append(f"성과 점수 {performance_score:.2f}로 낮은 성과")
                if emotion_score < 0.4:  # 감정도 부정적
                    reasoning.append(f"감정 점수 {emotion_score:.2f}로 부정적 감정")
                    return JudgmentAction.DISCARD, reasoning
                else:
                    reasoning.append("감정은 양호하나 성과 개선 필요")
                    return JudgmentAction.MODIFY, reasoning
        
        # 2. 전략 수정 판단 (조건 변경 후에도 미개선)
        if strategy_age_days >= self.criteria.judgment_period * 2:
            if performance_score < 0.7:  # 지속적으로 낮은 성과
                reasoning.append(f"장기간 낮은 성과 {performance_score:.2f}")
                return JudgmentAction.MODIFY, reasoning
        
        # 3. 전략 폐기 판단 (수정 후에도 실패)
        if strategy_age_days >= self.criteria.judgment_period * 3:
            if combined_score < 0.4:  # 종합 점수가 매우 낮음
                reasoning.append(f"종합 점수 {combined_score:.2f}로 매우 낮은 성과")
                return JudgmentAction.DISCARD, reasoning
        
        # 4. 지속 판단 (기본값)
        reasoning.append(f"성과 점수 {performance_score:.2f}, 감정 점수 {emotion_score:.2f}로 양호")
        return JudgmentAction.CONTINUE, reasoning
    
    def _calculate_confidence(self, performance_score: float, emotion_score: float,
                            performance_data_count: int, emotion_data_count: int) -> float:
        """신뢰도를 계산합니다."""
        # 데이터 양에 따른 신뢰도
        data_confidence = min(performance_data_count / 10, 1.0) * 0.5 + min(emotion_data_count / 10, 1.0) * 0.5
        
        # 점수 일관성에 따른 신뢰도
        score_confidence = 1.0 - abs(performance_score - emotion_score) * 0.3
        
        return min(data_confidence + score_confidence, 1.0)
    
    def update_criteria(self, new_criteria: SurvivalCriteria):
        """판단 기준을 업데이트합니다."""
        self.criteria = new_criteria
        logger.info("판단 기준 업데이트 완료")
    
    def get_judgment_statistics(self) -> Dict[str, Any]:
        """판단 통계를 반환합니다."""
        total_judgments = len(self.judgment_history)
        
        action_counts = {}
        for result in self.judgment_history:
            action_name = result.action.value
            action_counts[action_name] = action_counts.get(action_name, 0) + 1
        
        avg_confidence = sum(r.confidence for r in self.judgment_history) / total_judgments if total_judgments > 0 else 0
        avg_performance_score = sum(r.performance_score for r in self.judgment_history) / total_judgments if total_judgments > 0 else 0
        avg_emotion_score = sum(r.emotion_score for r in self.judgment_history) / total_judgments if total_judgments > 0 else 0
        
        return {
            "total_judgments": total_judgments,
            "action_distribution": action_counts,
            "average_confidence": avg_confidence,
            "average_performance_score": avg_performance_score,
            "average_emotion_score": avg_emotion_score,
            "current_criteria": {
                "judgment_period": self.criteria.judgment_period,
                "min_improvement": self.criteria.min_improvement,
                "failure_threshold": self.criteria.failure_threshold,
                "emotion_weight": self.criteria.emotion_weight,
                "performance_weight": self.criteria.performance_weight
            }
        }

# 싱글톤 인스턴스
_survival_criteria_manager = None

def get_survival_criteria_manager() -> SurvivalCriteriaManager:
    """SurvivalCriteriaManager 싱글톤 인스턴스 반환"""
    global _survival_criteria_manager
    if _survival_criteria_manager is None:
        _survival_criteria_manager = SurvivalCriteriaManager()
    return _survival_criteria_manager 