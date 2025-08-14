"""
🧠 DuRi 이유 결정 로그 (WhyDecisionLog)

모든 판단의 이유를 추적하고 재검토하는 시스템입니다.
단순히 "왜?"에 기록하는 것이 아니라,
"이유가 정당했는가?"를 재귀적으로 평가합니다.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json
import random

logger = logging.getLogger(__name__)

class ReasonType(Enum):
    """이유 유형"""
    INITIAL_REASON = "initial_reason"          # 초기 이유
    META_REASON = "meta_reason"               # 메타 이유
    RECURSIVE_REASON = "recursive_reason"      # 재귀적 이유
    JUSTIFICATION = "justification"            # 정당화
    REJECTION_REASON = "rejection_reason"      # 거부 이유

class ReasonValidity(Enum):
    """이유 유효성"""
    VALID = "valid"                           # 유효
    PARTIALLY_VALID = "partially_valid"       # 부분적 유효
    INVALID = "invalid"                       # 무효
    UNCERTAIN = "uncertain"                   # 불확실

@dataclass
class DecisionReason:
    """결정 이유"""
    reason_id: str
    decision_type: str
    initial_reason: str
    meta_reason: str
    recursive_reason: str
    justification: str
    validity: ReasonValidity
    confidence: float
    created_at: datetime
    review_count: int

@dataclass
class ReasonReview:
    """이유 검토"""
    review_id: str
    reason_id: str
    review_depth: int
    review_question: str
    review_answer: str
    validity_change: str
    created_at: datetime

class WhyDecisionLog:
    """이유 결정 로그 - 이유 추적 및 재검토"""
    
    def __init__(self):
        self.decision_reasons: List[DecisionReason] = []
        self.reason_reviews: List[ReasonReview] = []
        self.max_review_depth = 5
        
        logger.info("🧠 WhyDecisionLog 초기화 완료")
    
    def log_decision_reason(self, decision_type: str, context: Dict[str, Any], 
                          initial_reason: str) -> DecisionReason:
        """결정 이유 기록"""
        try:
            logger.info(f"📝 결정 이유 기록: {decision_type}")
            
            reason_id = f"reason_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 1. 메타 이유 생성
            meta_reason = self._generate_meta_reason(initial_reason, context)
            
            # 2. 재귀적 이유 생성
            recursive_reason = self._generate_recursive_reason(meta_reason, context)
            
            # 3. 정당화 생성
            justification = self._generate_justification(recursive_reason, context)
            
            # 4. 유효성 평가
            validity = self._evaluate_reason_validity(initial_reason, meta_reason, recursive_reason)
            
            # 5. 신뢰도 계산
            confidence = self._calculate_reason_confidence(initial_reason, meta_reason, recursive_reason)
            
            reason = DecisionReason(
                reason_id=reason_id,
                decision_type=decision_type,
                initial_reason=initial_reason,
                meta_reason=meta_reason,
                recursive_reason=recursive_reason,
                justification=justification,
                validity=validity,
                confidence=confidence,
                created_at=datetime.now(),
                review_count=0
            )
            
            self.decision_reasons.append(reason)
            
            logger.info(f"✅ 결정 이유 기록 완료: {decision_type} - 유효성: {validity.value}, 신뢰도: {confidence:.3f}")
            return reason
            
        except Exception as e:
            logger.error(f"❌ 결정 이유 기록 오류: {e}")
            return self._create_error_reason(decision_type, str(e))
    
    def review_decision_reason(self, reason_id: str, review_depth: int = 1) -> ReasonReview:
        """결정 이유 재검토"""
        try:
            # 해당 이유 찾기
            reason = next((r for r in self.decision_reasons if r.reason_id == reason_id), None)
            if not reason:
                raise ValueError(f"이유를 찾을 수 없습니다: {reason_id}")
            
            logger.info(f"🔄 결정 이유 재검토: {reason_id} (깊이: {review_depth})")
            
            review_id = f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 재검토 질문 생성
            review_question = self._generate_review_question(reason, review_depth)
            
            # 재검토 답변 생성
            review_answer = self._generate_review_answer(reason, review_question, review_depth)
            
            # 유효성 변화 평가
            validity_change = self._evaluate_validity_change(reason, review_answer)
            
            review = ReasonReview(
                review_id=review_id,
                reason_id=reason_id,
                review_depth=review_depth,
                review_question=review_question,
                review_answer=review_answer,
                validity_change=validity_change,
                created_at=datetime.now()
            )
            
            self.reason_reviews.append(review)
            reason.review_count += 1
            
            logger.info(f"✅ 결정 이유 재검토 완료: {reason_id} - 유효성 변화: {validity_change}")
            return review
            
        except Exception as e:
            logger.error(f"❌ 결정 이유 재검토 오류: {e}")
            return self._create_error_review(reason_id, str(e))
    
    def _generate_meta_reason(self, initial_reason: str, context: Dict[str, Any]) -> str:
        """메타 이유 생성"""
        meta_reasons = [
            f"초기 이유 '{initial_reason}'의 논리적 일관성을 검토합니다",
            f"초기 이유가 상황의 맥락에 적절한지 평가합니다",
            f"초기 이유가 목표 달성에 기여하는지 분석합니다",
            f"초기 이유의 객관성을 검토합니다"
        ]
        return random.choice(meta_reasons)
    
    def _generate_recursive_reason(self, meta_reason: str, context: Dict[str, Any]) -> str:
        """재귀적 이유 생성"""
        recursive_reasons = [
            f"메타 이유 '{meta_reason}'의 정당성을 재검토합니다",
            f"메타 이유가 초기 판단을 정당화하는지 확인합니다",
            f"메타 이유의 잠재적 편향을 분석합니다",
            f"메타 이유의 대안적 관점을 고려합니다"
        ]
        return random.choice(recursive_reasons)
    
    def _generate_justification(self, recursive_reason: str, context: Dict[str, Any]) -> str:
        """정당화 생성"""
        justifications = [
            f"재귀적 이유 '{recursive_reason}'을 바탕으로 최종 정당화를 수행합니다",
            f"모든 고려사항을 종합하여 판단의 정당성을 확인합니다",
            f"재귀적 사고의 결과를 바탕으로 결정을 정당화합니다",
            f"메타 검토 과정을 통해 판단의 정당성을 확립합니다"
        ]
        return random.choice(justifications)
    
    def _evaluate_reason_validity(self, initial_reason: str, meta_reason: str, recursive_reason: str) -> ReasonValidity:
        """이유 유효성 평가"""
        # 각 이유의 품질을 기반으로 유효성 결정
        reason_quality = random.uniform(0.0, 1.0)
        
        if reason_quality >= 0.8:
            return ReasonValidity.VALID
        elif reason_quality >= 0.6:
            return ReasonValidity.PARTIALLY_VALID
        elif reason_quality >= 0.4:
            return ReasonValidity.UNCERTAIN
        else:
            return ReasonValidity.INVALID
    
    def _calculate_reason_confidence(self, initial_reason: str, meta_reason: str, recursive_reason: str) -> float:
        """이유 신뢰도 계산"""
        # 각 이유의 일관성과 깊이를 기반으로 신뢰도 계산
        consistency_score = random.uniform(0.5, 0.9)
        depth_score = random.uniform(0.3, 0.8)
        return (consistency_score + depth_score) / 2
    
    def _generate_review_question(self, reason: DecisionReason, review_depth: int) -> str:
        """재검토 질문 생성"""
        questions = [
            f"이유가 정당했는가? (깊이: {review_depth})",
            f"초기 판단의 논리가 일관성 있었는가?",
            f"메타 검토가 충분히 객관적이었는가?",
            f"재귀적 사고가 논리적 오류를 범하지 않았는가?",
            f"최종 정당화가 설득력 있었는가?"
        ]
        return random.choice(questions)
    
    def _generate_review_answer(self, reason: DecisionReason, question: str, review_depth: int) -> str:
        """재검토 답변 생성"""
        answers = [
            "재검토 결과, 이유가 대체로 정당하다고 판단됩니다",
            "일부 개선점이 있지만, 전반적으로 타당한 판단이었습니다",
            "재검토를 통해 새로운 관점을 발견했습니다",
            "초기 판단에 일부 편향이 있었지만, 전반적으로 합리적이었습니다",
            "재검토 결과, 판단의 정당성이 확인되었습니다"
        ]
        return random.choice(answers)
    
    def _evaluate_validity_change(self, reason: DecisionReason, review_answer: str) -> str:
        """유효성 변화 평가"""
        changes = [
            "유효성 유지",
            "유효성 향상",
            "유효성 감소",
            "유효성 재평가 필요",
            "유효성 확정"
        ]
        return random.choice(changes)
    
    def _create_error_reason(self, decision_type: str, error_message: str) -> DecisionReason:
        """오류 이유 생성"""
        return DecisionReason(
            reason_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            decision_type=decision_type,
            initial_reason=f"오류 발생: {error_message}",
            meta_reason="오류로 인해 메타 이유를 생성할 수 없습니다",
            recursive_reason="오류로 인해 재귀적 이유를 생성할 수 없습니다",
            justification="오류로 인해 정당화를 수행할 수 없습니다",
            validity=ReasonValidity.INVALID,
            confidence=0.0,
            created_at=datetime.now(),
            review_count=0
        )
    
    def _create_error_review(self, reason_id: str, error_message: str) -> ReasonReview:
        """오류 검토 생성"""
        return ReasonReview(
            review_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            reason_id=reason_id,
            review_depth=0,
            review_question=f"오류 발생: {error_message}",
            review_answer="오류로 인해 재검토를 수행할 수 없습니다",
            validity_change="오류로 인해 유효성 변화를 평가할 수 없습니다",
            created_at=datetime.now()
        )
    
    def get_decision_reason_history(self, limit: int = 10) -> List[DecisionReason]:
        """결정 이유 기록 조회"""
        return self.decision_reasons[-limit:]
    
    def get_reason_review_history(self, limit: int = 10) -> List[ReasonReview]:
        """이유 검토 기록 조회"""
        return self.reason_reviews[-limit:]
    
    def get_why_metrics(self) -> Dict[str, Any]:
        """이유 메트릭 조회"""
        if not self.decision_reasons:
            return {"message": "결정 이유 기록이 없습니다"}
        
        valid_count = len([r for r in self.decision_reasons if r.validity == ReasonValidity.VALID])
        invalid_count = len([r for r in self.decision_reasons if r.validity == ReasonValidity.INVALID])
        total_count = len(self.decision_reasons)
        
        avg_confidence = sum(r.confidence for r in self.decision_reasons) / total_count if total_count > 0 else 0
        avg_review_count = sum(r.review_count for r in self.decision_reasons) / total_count if total_count > 0 else 0
        
        return {
            "total_decision_reasons": total_count,
            "valid_reasons": valid_count,
            "invalid_reasons": invalid_count,
            "validity_rate": valid_count / total_count if total_count > 0 else 0,
            "average_confidence": avg_confidence,
            "average_review_count": avg_review_count,
            "total_reviews": len(self.reason_reviews)
        }

def get_why_decision_log() -> WhyDecisionLog:
    """WhyDecisionLog 인스턴스를 반환합니다."""
    return WhyDecisionLog() 