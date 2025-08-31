"""
DuRi의 Core_Eval 시스템

Dream 전략을 평가하고 채택할지 판단하는 시스템입니다.
유레카 감지 로직을 포함하여 예상 외의 고성능 전략을 즉시 승격합니다.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import math
import uuid

# 평가 로그 및 동시성 제어 시스템 import
from duri_core.utils.evaluation_logger import get_evaluation_logger
from duri_core.utils.evaluation_lock import get_evaluation_lock, get_evaluation_state_manager

logger = logging.getLogger(__name__)

class EvaluationType(Enum):
    """평가 유형"""
    STANDARD = "standard"          # 표준 평가
    EUREKA = "eureka"              # 유레카 감지
    COMPARATIVE = "comparative"     # 비교 평가
    PREDICTIVE = "predictive"       # 예측 평가

class EvaluationResult(Enum):
    """평가 결과"""
    ADOPT = "adopt"                # 채택
    REJECT = "reject"              # 거부
    FURTHER_TEST = "further_test"  # 추가 테스트
    EUREKA_PROMOTE = "eureka_promote"  # 유레카 승격

"""
📌 Evaluation 기준은 core_eval 전용 EvaluationCriteria를 따르며,
SurvivalCriteria와는 목적/적용 범위가 다르므로 통합하지 않음.
단, 향후 기준 통일이 필요할 경우, duri_core/philosophy/unified_criteria.py로 이전 가능.
"""

@dataclass
class DreamEvaluationCriteria:
    """Dream 전략 평가 기준"""
    performance_weight: float = 0.4
    novelty_weight: float = 0.3
    stability_weight: float = 0.2
    efficiency_weight: float = 0.1
    eureka_threshold: float = 0.85
    adoption_threshold: float = 0.7
    rejection_threshold: float = 0.3
    ttl_hours: int = 24  # 24시간 후 자동 폐기
    max_dream_candidates: int = 100  # 최대 Dream 후보 수

@dataclass
class EvaluationDecision:
    """평가 결정"""
    dream_id: str
    evaluation_type: EvaluationType
    result: EvaluationResult
    confidence: float
    reasoning: List[str]
    performance_score: float
    novelty_score: float
    stability_score: float
    efficiency_score: float
    combined_score: float
    evaluation_time: datetime
    eureka_detected: bool

class CoreEval:
    """
    DuRi의 Core_Eval 시스템
    
    Dream 전략을 평가하고 채택할지 판단하는 시스템입니다.
    """
    
    def __init__(self):
        """CoreEval 초기화"""
        self.evaluation_criteria = DreamEvaluationCriteria()
        self.evaluation_history: List[EvaluationDecision] = []
        self.eureka_detections: List[str] = []
        self.adoption_history: List[str] = []
        
        # 평가 통계
        self.evaluation_stats = {
            'total_evaluations': 0,
            'adoptions': 0,
            'rejections': 0,
            'eureka_detections': 0,
            'further_tests': 0,
            'ttl_expired': 0  # TTL 만료된 평가 수
        }
        
        # TTL 관리
        self.last_ttl_cleanup = datetime.now()
        self.ttl_cleanup_interval = timedelta(hours=1)  # 1시간마다 정리
        
        # 평가 로그 및 동시성 제어 시스템
        self.evaluation_logger = get_evaluation_logger()
        self.evaluation_lock = get_evaluation_lock()
        self.state_manager = get_evaluation_state_manager()
        
        logger.info("CoreEval 초기화 완료")
    
    def evaluate_dream_strategy(self, dream_data: Dict[str, Any], 
                              current_performance: float = 0.0,
                              context: Optional[Dict[str, Any]] = None) -> EvaluationDecision:
        """
        Dream 전략을 평가합니다.
        
        Args:
            dream_data: Dream 전략 데이터
            current_performance: 현재 성과
            context: 평가 컨텍스트
            
        Returns:
            EvaluationDecision: 평가 결정
        """
        dream_id = dream_data.get('dream_id', f"dream_{uuid.uuid4().hex[:8]}")
        evaluation_id = f"dream_eval_{uuid.uuid4().hex[:8]}"
        
        try:
            # 동시성 제어 및 상태 관리
            with self.evaluation_lock.evaluation_context(evaluation_id):
                self.state_manager.start_evaluation("dream", evaluation_id)
                
                # TTL 정리
                self.cleanup_expired_evaluations()
                self.enforce_max_candidates()
                
                # 1. 기본 점수 계산
                performance_score = self._calculate_performance_score(dream_data, current_performance)
                novelty_score = self._calculate_novelty_score(dream_data)
                stability_score = self._calculate_stability_score(dream_data)
                efficiency_score = self._calculate_efficiency_score(dream_data)
                
                # 2. 종합 점수 계산
                combined_score = self._calculate_combined_score(
                    performance_score, novelty_score, stability_score, efficiency_score
                )
                
                # 3. 유레카 감지
                eureka_detected = self._detect_eureka(combined_score, novelty_score, performance_score)
                
                # 4. 평가 유형 결정
                evaluation_type = self._determine_evaluation_type(dream_data, eureka_detected)
                
                # 5. 평가 결과 결정
                result, reasoning = self._determine_evaluation_result(
                    combined_score, eureka_detected, context
                )
                
                # 6. 신뢰도 계산
                confidence = self._calculate_evaluation_confidence(
                    performance_score, novelty_score, stability_score, efficiency_score
                )
                
                # 7. 평가 결정 생성
                decision = EvaluationDecision(
                    dream_id=dream_id,
                    evaluation_type=evaluation_type,
                    result=result,
                    confidence=confidence,
                    reasoning=reasoning,
                    performance_score=performance_score,
                    novelty_score=novelty_score,
                    stability_score=stability_score,
                    efficiency_score=efficiency_score,
                    combined_score=combined_score,
                    evaluation_time=datetime.now(),
                    eureka_detected=eureka_detected
                )
                
                # 8. 통계 업데이트
                self._update_evaluation_stats(decision)
                self.evaluation_history.append(decision)
                
                # 9. 평가 로그 저장
                self.evaluation_logger.log_dream_evaluation(
                    dream_id=dream_id,
                    performance_score=performance_score,
                    novelty_score=novelty_score,
                    stability_score=stability_score,
                    efficiency_score=efficiency_score,
                    combined_score=combined_score,
                    result=result.value,
                    confidence=confidence,
                    eureka_detected=eureka_detected
                )
                
                logger.info(f"Dream 전략 평가 완료: {dream_id}, 결과: {result.value}, 점수: {combined_score:.3f}")
                return decision
                
        except Exception as e:
            logger.error(f"Dream 전략 평가 실패: {e}")
            self.state_manager.record_error("dream")
            
            # Fallback 평가 시도
            try:
                return self.evaluate_dream_strategy_fallback(dream_data, current_performance, context)
            except Exception as fallback_error:
                logger.error(f"Fallback 평가도 실패: {fallback_error}")
                return self._create_error_decision(dream_id)
        finally:
            self.state_manager.end_evaluation("dream")
    
    def _calculate_performance_score(self, dream_data: Dict[str, Any], 
                                   current_performance: float) -> float:
        """성과 점수를 계산합니다."""
        # 기본 성과 점수
        base_performance = dream_data.get('confidence_score', 0.5)
        
        # 현재 성과와 비교
        if current_performance > 0:
            performance_improvement = (base_performance - current_performance) / current_performance
            performance_score = base_performance + (performance_improvement * 0.3)
        else:
            performance_score = base_performance
        
        # 전략 유형별 가중치
        strategy_type = dream_data.get('type', 'unknown')
        type_weights = {
            'random_combination': 0.8,
            'pattern_mutation': 0.9,
            'concept_fusion': 0.85,
            'intuition_exploration': 0.7
        }
        
        weight = type_weights.get(strategy_type, 0.8)
        performance_score *= weight
        
        return min(performance_score, 1.0)
    
    def _calculate_novelty_score(self, dream_data: Dict[str, Any]) -> float:
        """새로움 점수를 계산합니다."""
        # 기본 새로움 점수
        novelty_score = dream_data.get('novelty_score', 0.5)
        
        # 전략 유형별 새로움
        strategy_type = dream_data.get('type', 'unknown')
        type_novelty = {
            'random_combination': 0.6,
            'pattern_mutation': 0.7,
            'concept_fusion': 0.8,
            'intuition_exploration': 0.9
        }
        
        type_score = type_novelty.get(strategy_type, 0.6)
        novelty_score = (novelty_score + type_score) / 2
        
        # 복잡성 반영
        complexity = dream_data.get('complexity_score', 0.5)
        novelty_score *= (1 + complexity * 0.2)
        
        return min(novelty_score, 1.0)
    
    def _calculate_stability_score(self, dream_data: Dict[str, Any]) -> float:
        """안정성 점수를 계산합니다."""
        # 기본 안정성
        stability_score = 0.5
        
        # 전략 유형별 안정성
        strategy_type = dream_data.get('type', 'unknown')
        type_stability = {
            'random_combination': 0.6,
            'pattern_mutation': 0.7,
            'concept_fusion': 0.8,
            'intuition_exploration': 0.5
        }
        
        stability_score = type_stability.get(strategy_type, 0.6)
        
        # 신뢰도 반영
        confidence = dream_data.get('confidence_score', 0.5)
        stability_score = (stability_score + confidence) / 2
        
        return min(stability_score, 1.0)
    
    def _calculate_efficiency_score(self, dream_data: Dict[str, Any]) -> float:
        """효율성 점수를 계산합니다."""
        # 기본 효율성
        efficiency_score = 0.5
        
        # 전략 유형별 효율성
        strategy_type = dream_data.get('type', 'unknown')
        type_efficiency = {
            'random_combination': 0.7,
            'pattern_mutation': 0.8,
            'concept_fusion': 0.75,
            'intuition_exploration': 0.6
        }
        
        efficiency_score = type_efficiency.get(strategy_type, 0.7)
        
        # 우선순위 반영
        priority = dream_data.get('priority', 0.5)
        efficiency_score *= priority
        
        return min(efficiency_score, 1.0)
    
    def _calculate_combined_score(self, performance_score: float, novelty_score: float,
                                stability_score: float, efficiency_score: float) -> float:
        """종합 점수를 계산합니다."""
        criteria = self.evaluation_criteria
        
        combined_score = (
            performance_score * criteria.performance_weight +
            novelty_score * criteria.novelty_weight +
            stability_score * criteria.stability_weight +
            efficiency_score * criteria.efficiency_weight
        )
        
        return min(combined_score, 1.0)
    
    def _detect_eureka(self, combined_score: float, novelty_score: float, 
                      performance_score: float) -> bool:
        """유레카를 감지합니다."""
        # 유레카 조건: 높은 종합 점수 + 높은 새로움 + 높은 성과
        eureka_threshold = self.evaluation_criteria.eureka_threshold
        
        if (combined_score >= eureka_threshold and 
            novelty_score >= 0.8 and 
            performance_score >= 0.8):
            return True
        
        # 예상 외의 고성능 조합
        if (combined_score >= 0.9 and 
            novelty_score >= 0.9):
            return True
        
        return False
    
    def _determine_evaluation_type(self, dream_data: Dict[str, Any], 
                                 eureka_detected: bool) -> EvaluationType:
        """평가 유형을 결정합니다."""
        if eureka_detected:
            return EvaluationType.EUREKA
        
        # 특별한 조건들
        strategy_type = dream_data.get('type', 'unknown')
        
        if strategy_type == 'intuition_exploration':
            return EvaluationType.EUREKA
        elif strategy_type == 'concept_fusion':
            return EvaluationType.COMPARATIVE
        else:
            return EvaluationType.STANDARD
    
    def _determine_evaluation_result(self, combined_score: float, eureka_detected: bool,
                                   context: Optional[Dict[str, Any]]) -> Tuple[EvaluationResult, List[str]]:
        """평가 결과를 결정합니다."""
        reasoning = []
        criteria = self.evaluation_criteria
        
        # 유레카 감지된 경우
        if eureka_detected:
            reasoning.append("유레카 감지: 예상 외의 고성능 전략")
            return EvaluationResult.EUREKA_PROMOTE, reasoning
        
        # 채택 임계값 확인
        if combined_score >= criteria.adoption_threshold:
            reasoning.append(f"종합 점수 {combined_score:.2f}로 채택 임계값 {criteria.adoption_threshold} 초과")
            return EvaluationResult.ADOPT, reasoning
        
        # 거부 임계값 확인
        if combined_score <= criteria.rejection_threshold:
            reasoning.append(f"종합 점수 {combined_score:.2f}로 거부 임계값 {criteria.rejection_threshold} 미만")
            return EvaluationResult.REJECT, reasoning
        
        # 추가 테스트
        reasoning.append(f"종합 점수 {combined_score:.2f}로 추가 테스트 필요")
        return EvaluationResult.FURTHER_TEST, reasoning
    
    def _calculate_evaluation_confidence(self, performance_score: float, novelty_score: float,
                                       stability_score: float, efficiency_score: float) -> float:
        """평가 신뢰도를 계산합니다."""
        # 점수들의 일관성
        scores = [performance_score, novelty_score, stability_score, efficiency_score]
        variance = sum((score - sum(scores) / len(scores)) ** 2 for score in scores) / len(scores)
        
        # 일관성 점수 (분산이 낮을수록 높은 신뢰도)
        consistency_score = 1.0 - (variance * 2)
        
        # 평균 점수
        average_score = sum(scores) / len(scores)
        
        # 최종 신뢰도
        confidence = (consistency_score + average_score) / 2
        
        return max(confidence, 0.0)
    
    def _update_evaluation_stats(self, decision: EvaluationDecision):
        """평가 통계를 업데이트합니다."""
        self.evaluation_stats['total_evaluations'] += 1
        
        if decision.result == EvaluationResult.ADOPT:
            self.evaluation_stats['adoptions'] += 1
            self.adoption_history.append(decision.dream_id)
        elif decision.result == EvaluationResult.REJECT:
            self.evaluation_stats['rejections'] += 1
        elif decision.result == EvaluationResult.EUREKA_PROMOTE:
            self.evaluation_stats['eureka_detections'] += 1
            self.eureka_detections.append(decision.dream_id)
        elif decision.result == EvaluationResult.FURTHER_TEST:
            self.evaluation_stats['further_tests'] += 1
    
    def evaluate_dream_strategy_fallback(self, dream_data: Dict[str, Any], 
                                       current_performance: float = 0.0,
                                       context: Optional[Dict[str, Any]] = None) -> EvaluationDecision:
        """
        Fallback 상황에서의 최소 평가 기능
        
        시스템 무력화를 방지하기 위해 제한된 기준으로 기본 평가를 수행합니다.
        """
        dream_id = dream_data.get('dream_id', f"dream_{uuid.uuid4().hex[:8]}")
        
        try:
            logger.warning(f"Core_Eval Fallback 모드 활성화: {dream_id}")
            
            # 제한된 데이터로 기본 점수 계산
            performance_score = self._calculate_fallback_performance_score(dream_data, current_performance)
            novelty_score = self._calculate_fallback_novelty_score(dream_data)
            stability_score = 0.5  # 기본 안정성 점수
            efficiency_score = 0.5  # 기본 효율성 점수
            
            # 단순화된 종합 점수 계산
            combined_score = (performance_score * 0.6 + novelty_score * 0.4)
            
            # 기본 평가 결과 결정
            if combined_score > 0.7:
                result = EvaluationResult.ADOPT
                reasoning = ["Fallback 모드: 높은 기본 점수로 채택"]
            elif combined_score > 0.5:
                result = EvaluationResult.FURTHER_TEST
                reasoning = ["Fallback 모드: 추가 테스트 필요"]
            else:
                result = EvaluationResult.REJECT
                reasoning = ["Fallback 모드: 낮은 점수로 거부"]
            
            # 낮은 신뢰도 (Fallback 모드)
            confidence = 0.3
            
            decision = EvaluationDecision(
                dream_id=dream_id,
                evaluation_type=EvaluationType.STANDARD,
                result=result,
                confidence=confidence,
                reasoning=reasoning,
                performance_score=performance_score,
                novelty_score=novelty_score,
                stability_score=stability_score,
                efficiency_score=efficiency_score,
                combined_score=combined_score,
                evaluation_time=datetime.now(),
                eureka_detected=False
            )
            
            logger.info(f"Fallback 평가 완료: {dream_id}, 결과: {result.value}, 점수: {combined_score:.3f}")
            return decision
            
        except Exception as e:
            logger.error(f"Fallback 평가 실패: {e}")
            return self._create_error_decision(dream_id)
    
    def _calculate_fallback_performance_score(self, dream_data: Dict[str, Any], 
                                            current_performance: float) -> float:
        """Fallback 모드에서의 성과 점수 계산"""
        try:
            # 기본 성과 지표 추출
            performance_indicators = dream_data.get('performance_indicators', {})
            
            if not performance_indicators:
                return 0.5  # 기본값
            
            # 단순화된 성과 계산
            score = 0.0
            count = 0
            
            for indicator, value in performance_indicators.items():
                if isinstance(value, (int, float)):
                    score += min(value, 1.0)
                    count += 1
            
            if count > 0:
                return score / count
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"Fallback 성과 점수 계산 실패: {e}")
            return 0.5
    
    def _calculate_fallback_novelty_score(self, dream_data: Dict[str, Any]) -> float:
        """Fallback 모드에서의 새로움 점수 계산"""
        try:
            # 기본 새로움 지표 추출
            novelty_indicators = dream_data.get('novelty_indicators', {})
            
            if not novelty_indicators:
                return 0.5  # 기본값
            
            # 단순화된 새로움 계산
            score = 0.0
            count = 0
            
            for indicator, value in novelty_indicators.items():
                if isinstance(value, (int, float)):
                    score += min(value, 1.0)
                    count += 1
            
            if count > 0:
                return score / count
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"Fallback 새로움 점수 계산 실패: {e}")
            return 0.5
    
    def _create_error_decision(self, dream_id: str) -> EvaluationDecision:
        """오류 시 기본 결정을 생성합니다."""
        return EvaluationDecision(
            dream_id=dream_id,
            evaluation_type=EvaluationType.STANDARD,
            result=EvaluationResult.REJECT,
            confidence=0.0,
            reasoning=["평가 중 오류 발생"],
            performance_score=0.0,
            novelty_score=0.0,
            stability_score=0.0,
            efficiency_score=0.0,
            combined_score=0.0,
            evaluation_time=datetime.now(),
            eureka_detected=False
        )
    
    def get_evaluation_statistics(self) -> Dict[str, Any]:
        """평가 통계를 반환합니다."""
        total_evaluations = self.evaluation_stats['total_evaluations']
        
        if total_evaluations == 0:
            return {
                "total_evaluations": 0,
                "adoption_rate": 0.0,
                "rejection_rate": 0.0,
                "eureka_rate": 0.0,
                "further_test_rate": 0.0,
                "average_confidence": 0.0,
                "average_combined_score": 0.0
            }
        
        adoption_rate = self.evaluation_stats['adoptions'] / total_evaluations
        rejection_rate = self.evaluation_stats['rejections'] / total_evaluations
        eureka_rate = self.evaluation_stats['eureka_detections'] / total_evaluations
        further_test_rate = self.evaluation_stats['further_tests'] / total_evaluations
        
        # 평균 신뢰도
        avg_confidence = sum(d.confidence for d in self.evaluation_history) / len(self.evaluation_history) if self.evaluation_history else 0
        
        # 평균 종합 점수
        avg_combined_score = sum(d.combined_score for d in self.evaluation_history) / len(self.evaluation_history) if self.evaluation_history else 0
        
        return {
            "total_evaluations": total_evaluations,
            "adoption_rate": adoption_rate,
            "rejection_rate": rejection_rate,
            "eureka_rate": eureka_rate,
            "further_test_rate": further_test_rate,
            "average_confidence": avg_confidence,
            "average_combined_score": avg_combined_score,
            "eureka_detections": self.eureka_detections,
            "adoption_history": self.adoption_history
        }
    
    def update_evaluation_criteria(self, new_criteria: DreamEvaluationCriteria):
        """평가 기준을 업데이트합니다."""
        self.evaluation_criteria = new_criteria
        logger.info("평가 기준 업데이트 완료")
    
    def get_recent_evaluations(self, limit: int = 10) -> List[EvaluationDecision]:
        """최근 평가들을 반환합니다."""
        return self.evaluation_history[-limit:] if self.evaluation_history else []
    
    def cleanup_expired_evaluations(self):
        """TTL이 만료된 평가 결과를 정리합니다."""
        current_time = datetime.now()
        
        # TTL 정리 주기 확인
        if current_time - self.last_ttl_cleanup < self.ttl_cleanup_interval:
            return
        
        ttl_threshold = current_time - timedelta(hours=self.evaluation_criteria.ttl_hours)
        expired_count = 0
        
        # 만료된 평가 결과 제거
        original_count = len(self.evaluation_history)
        self.evaluation_history = [
            eval_result for eval_result in self.evaluation_history
            if eval_result.evaluation_time > ttl_threshold
        ]
        expired_count = original_count - len(self.evaluation_history)
        
        # 만료된 유레카 감지 제거
        self.eureka_detections = [
            dream_id for dream_id in self.eureka_detections
            if any(eval_result.dream_id == dream_id and 
                   eval_result.evaluation_time > ttl_threshold
                   for eval_result in self.evaluation_history)
        ]
        
        # 만료된 채택 히스토리 제거
        self.adoption_history = [
            dream_id for dream_id in self.adoption_history
            if any(eval_result.dream_id == dream_id and 
                   eval_result.evaluation_time > ttl_threshold
                   for eval_result in self.evaluation_history)
        ]
        
        self.evaluation_stats['ttl_expired'] += expired_count
        self.last_ttl_cleanup = current_time
        
        if expired_count > 0:
            logger.info(f"TTL 만료 평가 정리 완료: {expired_count}개 제거")
    
    def enforce_max_candidates(self):
        """최대 Dream 후보 수를 초과하는 경우 오래된 것부터 제거합니다."""
        if len(self.evaluation_history) > self.evaluation_criteria.max_dream_candidates:
            # 오래된 순서대로 정렬하여 초과분 제거
            sorted_evaluations = sorted(self.evaluation_history, 
                                      key=lambda x: x.evaluation_time)
            excess_count = len(self.evaluation_history) - self.evaluation_criteria.max_dream_candidates
            
            self.evaluation_history = sorted_evaluations[excess_count:]
            logger.info(f"최대 후보 수 초과로 {excess_count}개 제거")

# 싱글톤 인스턴스
_core_eval = None

def get_core_eval() -> CoreEval:
    """CoreEval 싱글톤 인스턴스 반환"""
    global _core_eval
    if _core_eval is None:
        _core_eval = CoreEval()
    return _core_eval 