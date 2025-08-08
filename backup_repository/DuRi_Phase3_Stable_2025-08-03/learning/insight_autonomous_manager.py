"""
🧠 DuRi 자율적 통찰 관리 시스템
목표: DuRi가 통찰 결과를 자신의 기준으로 저장/보류/폐기하는 알고리즘
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json
import random

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InsightAction(Enum):
    """통찰 액션"""
    STORE = "store"           # 저장
    HOLD = "hold"             # 보류
    DISCARD = "discard"       # 폐기
    MODIFY = "modify"         # 수정
    PRIORITIZE = "prioritize" # 우선순위

class InsightCategory(Enum):
    """통찰 카테고리"""
    STRATEGY = "strategy"           # 전략
    OPTIMIZATION = "optimization"   # 최적화
    INNOVATION = "innovation"       # 혁신
    REFLECTION = "reflection"       # 반영
    EMERGENCY = "emergency"         # 긴급

class InsightPriority(Enum):
    """통찰 우선순위"""
    CRITICAL = "critical"     # 긴급
    HIGH = "high"            # 높음
    MEDIUM = "medium"        # 중간
    LOW = "low"              # 낮음
    MINOR = "minor"          # 미미

@dataclass
class InsightEvaluation:
    """통찰 평가"""
    relevance_score: float      # 관련성 점수
    feasibility_score: float    # 실현 가능성 점수
    impact_score: float         # 영향도 점수
    risk_score: float          # 위험도 점수
    novelty_score: float       # 신선함 점수
    total_score: float         # 종합 점수
    confidence: float          # 평가 신뢰도

@dataclass
class InsightDecision:
    """통찰 결정"""
    insight_id: str
    action: InsightAction
    category: InsightCategory
    priority: InsightPriority
    reasoning: str
    expected_benefit: float
    risk_assessment: str
    implementation_plan: str
    timestamp: datetime

class InsightAutonomousManager:
    """DuRi 자율적 통찰 관리자"""
    
    def __init__(self):
        self.stored_insights = {}      # 저장된 통찰
        self.held_insights = {}        # 보류된 통찰
        self.discarded_insights = {}   # 폐기된 통찰
        self.priority_queue = []       # 우선순위 큐
        
        # DuRi의 개인적 기준
        self.personal_criteria = {
            "learning_focus": 0.8,     # 학습 중심성
            "safety_threshold": 0.3,   # 안전성 임계값
            "innovation_bias": 0.6,    # 혁신 편향
            "practicality_weight": 0.7, # 실용성 가중치
            "risk_tolerance": 0.4      # 위험 허용도
        }
        
        # 카테고리별 가중치
        self.category_weights = {
            InsightCategory.STRATEGY: 0.9,
            InsightCategory.OPTIMIZATION: 0.7,
            InsightCategory.INNOVATION: 0.8,
            InsightCategory.REFLECTION: 0.6,
            InsightCategory.EMERGENCY: 1.0
        }
        
    def evaluate_insight(self, insight: Dict[str, Any]) -> InsightEvaluation:
        """통찰 평가"""
        logger.info(f"🔍 통찰 평가 시작: {insight.get('strategy', 'Unknown')[:50]}...")
        
        # 1. 관련성 평가 (DuRi의 현재 학습 목표와의 연관성)
        relevance_score = self._evaluate_relevance(insight)
        
        # 2. 실현 가능성 평가
        feasibility_score = self._evaluate_feasibility(insight)
        
        # 3. 영향도 평가
        impact_score = self._evaluate_impact(insight)
        
        # 4. 위험도 평가
        risk_score = self._evaluate_risk(insight)
        
        # 5. 신선함 평가
        novelty_score = self._evaluate_novelty(insight)
        
        # 종합 점수 계산 (DuRi의 개인적 기준 반영)
        total_score = self._calculate_total_score(
            relevance_score, feasibility_score, impact_score, 
            risk_score, novelty_score, insight
        )
        
        # 평가 신뢰도 계산
        confidence = self._calculate_confidence(insight)
        
        evaluation = InsightEvaluation(
            relevance_score=relevance_score,
            feasibility_score=feasibility_score,
            impact_score=impact_score,
            risk_score=risk_score,
            novelty_score=novelty_score,
            total_score=total_score,
            confidence=confidence
        )
        
        logger.info(f"🔍 평가 완료 - 종합 점수: {total_score:.3f}, 신뢰도: {confidence:.3f}")
        return evaluation
        
    def _evaluate_relevance(self, insight: Dict[str, Any]) -> float:
        """관련성 평가"""
        strategy = insight.get('strategy', '').lower()
        
        # DuRi의 현재 학습 목표와 연관성 확인
        learning_keywords = ['학습', '성능', '효율', '개선', '진화', '발전']
        relevance_count = sum(1 for keyword in learning_keywords if keyword in strategy)
        
        # 현재 문제와의 연관성
        problem_relevance = 0.5  # 기본값
        if 'problem' in insight:
            problem = insight['problem'].lower()
            if any(word in problem for word in ['학습', '성능', '메모리', '비용']):
                problem_relevance = 0.8
                
        return min((relevance_count / len(learning_keywords)) * 0.6 + problem_relevance * 0.4, 1.0)
        
    def _evaluate_feasibility(self, insight: Dict[str, Any]) -> float:
        """실현 가능성 평가"""
        strategy = insight.get('strategy', '')
        
        # 구현 복잡도 평가
        complexity_indicators = ['복잡', '어려운', '고급', '혁신적']
        complexity_score = sum(1 for indicator in complexity_indicators if indicator in strategy) / len(complexity_indicators)
        
        # 리소스 요구사항 평가
        resource_indicators = ['메모리', '비용', '시간', '계산']
        resource_score = sum(1 for indicator in resource_indicators if indicator in strategy) / len(resource_indicators)
        
        # 실현 가능성 = (1 - 복잡도) * (1 - 리소스 요구사항)
        feasibility = (1 - complexity_score * 0.5) * (1 - resource_score * 0.3)
        
        return max(feasibility, 0.1)  # 최소 0.1 보장
        
    def _evaluate_impact(self, insight: Dict[str, Any]) -> float:
        """영향도 평가"""
        expected_impact = insight.get('expected_impact', 0.5)
        confidence = insight.get('confidence', 0.5)
        
        # 영향도 = 예상 영향 * 신뢰도
        impact = expected_impact * confidence
        
        # DuRi의 학습 중심성 반영
        impact *= self.personal_criteria['learning_focus']
        
        return min(impact, 1.0)
        
    def _evaluate_risk(self, insight: Dict[str, Any]) -> float:
        """위험도 평가"""
        risk_level = insight.get('risk_level', 'MEDIUM')
        risk_mapping = {'LOW': 0.2, 'MEDIUM': 0.5, 'HIGH': 0.8}
        base_risk = risk_mapping.get(risk_level, 0.5)
        
        # DuRi의 위험 허용도 반영
        adjusted_risk = base_risk * (1 - self.personal_criteria['risk_tolerance'])
        
        return adjusted_risk
        
    def _evaluate_novelty(self, insight: Dict[str, Any]) -> float:
        """신선함 평가"""
        strategy = insight.get('strategy', '')
        
        # 혁신적 키워드 확인
        novelty_keywords = ['혁신', '새로운', '혁명적', '파괴적', '비전통적']
        novelty_count = sum(1 for keyword in novelty_keywords if keyword in strategy)
        
        # 기존 통찰과의 차별성
        existing_insights = list(self.stored_insights.values()) + list(self.held_insights.values())
        similarity_score = 0.0
        
        for existing in existing_insights:
            if 'strategy' in existing and 'strategy' in insight:
                # 간단한 유사도 계산
                common_words = set(existing['strategy'].split()) & set(insight['strategy'].split())
                total_words = set(existing['strategy'].split()) | set(insight['strategy'].split())
                if total_words:
                    similarity_score = max(similarity_score, len(common_words) / len(total_words))
                    
        novelty_score = (novelty_count / len(novelty_keywords)) * 0.7 + (1 - similarity_score) * 0.3
        novelty_score *= self.personal_criteria['innovation_bias']
        
        return min(novelty_score, 1.0)
        
    def _calculate_total_score(self, relevance: float, feasibility: float, 
                             impact: float, risk: float, novelty: float, 
                             insight: Dict[str, Any]) -> float:
        """종합 점수 계산"""
        # 기본 가중치
        weights = {
            'relevance': 0.25,
            'feasibility': 0.20,
            'impact': 0.25,
            'risk': 0.15,
            'novelty': 0.15
        }
        
        # 카테고리별 가중치 조정
        category = self._categorize_insight(insight)
        category_weight = self.category_weights.get(category, 0.7)
        
        # 위험도는 역수로 계산 (위험도가 낮을수록 높은 점수)
        risk_score = 1 - risk
        
        # 종합 점수 계산
        total_score = (
            relevance * weights['relevance'] +
            feasibility * weights['feasibility'] +
            impact * weights['impact'] +
            risk_score * weights['risk'] +
            novelty * weights['novelty']
        ) * category_weight
        
        return min(total_score, 1.0)
        
    def _calculate_confidence(self, insight: Dict[str, Any]) -> float:
        """평가 신뢰도 계산"""
        # 통찰의 원본 신뢰도
        original_confidence = insight.get('confidence', 0.5)
        
        # 평가자의 경험 수준 (시뮬레이션)
        evaluator_experience = 0.8
        
        # 평가 신뢰도 = 원본 신뢰도 * 평가자 경험
        confidence = original_confidence * evaluator_experience
        
        return min(confidence, 1.0)
        
    def _categorize_insight(self, insight: Dict[str, Any]) -> InsightCategory:
        """통찰 카테고리 분류"""
        strategy = insight.get('strategy', '').lower()
        
        if any(word in strategy for word in ['전략', '방법', '접근']):
            return InsightCategory.STRATEGY
        elif any(word in strategy for word in ['최적화', '개선', '효율']):
            return InsightCategory.OPTIMIZATION
        elif any(word in strategy for word in ['혁신', '새로운', '파괴적']):
            return InsightCategory.INNOVATION
        elif any(word in strategy for word in ['반영', '학습', '분석']):
            return InsightCategory.REFLECTION
        elif any(word in strategy for word in ['긴급', '위험', '즉시']):
            return InsightCategory.EMERGENCY
        else:
            return InsightCategory.STRATEGY  # 기본값
            
    def make_decision(self, insight: Dict[str, Any], evaluation: InsightEvaluation) -> InsightDecision:
        """통찰에 대한 결정"""
        logger.info(f"🎯 통찰 결정 시작: {insight.get('strategy', 'Unknown')[:50]}...")
        
        # 1. 액션 결정
        action = self._determine_action(evaluation)
        
        # 2. 카테고리 분류
        category = self._categorize_insight(insight)
        
        # 3. 우선순위 결정
        priority = self._determine_priority(evaluation, category)
        
        # 4. 이유 생성
        reasoning = self._generate_reasoning(evaluation, action, category, priority)
        
        # 5. 예상 이익 계산
        expected_benefit = self._calculate_expected_benefit(evaluation, action)
        
        # 6. 위험 평가
        risk_assessment = self._assess_risk(evaluation, insight)
        
        # 7. 구현 계획
        implementation_plan = self._generate_implementation_plan(action, category, priority)
        
        decision = InsightDecision(
            insight_id=insight.get('session_id', f"insight_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            action=action,
            category=category,
            priority=priority,
            reasoning=reasoning,
            expected_benefit=expected_benefit,
            risk_assessment=risk_assessment,
            implementation_plan=implementation_plan,
            timestamp=datetime.now()
        )
        
        logger.info(f"🎯 결정 완료: {action.value} - {category.value} - {priority.value}")
        return decision
        
    def _determine_action(self, evaluation: InsightEvaluation) -> InsightAction:
        """액션 결정"""
        total_score = evaluation.total_score
        risk_score = evaluation.risk_score
        
        # 위험도가 안전성 임계값을 초과하면 폐기
        if risk_score > self.personal_criteria['safety_threshold']:
            return InsightAction.DISCARD
            
        # 종합 점수에 따른 결정
        if total_score >= 0.8:
            return InsightAction.STORE
        elif total_score >= 0.6:
            return InsightAction.PRIORITIZE
        elif total_score >= 0.4:
            return InsightAction.HOLD
        elif total_score >= 0.2:
            return InsightAction.MODIFY
        else:
            return InsightAction.DISCARD
            
    def _determine_priority(self, evaluation: InsightEvaluation, category: InsightCategory) -> InsightPriority:
        """우선순위 결정"""
        total_score = evaluation.total_score
        impact_score = evaluation.impact_score
        
        # 긴급 카테고리는 높은 우선순위
        if category == InsightCategory.EMERGENCY:
            return InsightPriority.CRITICAL
            
        # 영향도와 종합 점수 기반 우선순위
        priority_score = (total_score + impact_score) / 2
        
        if priority_score >= 0.8:
            return InsightPriority.CRITICAL
        elif priority_score >= 0.6:
            return InsightPriority.HIGH
        elif priority_score >= 0.4:
            return InsightPriority.MEDIUM
        elif priority_score >= 0.2:
            return InsightPriority.LOW
        else:
            return InsightPriority.MINOR
            
    def _generate_reasoning(self, evaluation: InsightEvaluation, action: InsightAction, 
                           category: InsightCategory, priority: InsightPriority) -> str:
        """결정 이유 생성"""
        reasoning = f"DuRi의 자율적 판단: "
        
        if action == InsightAction.STORE:
            reasoning += f"종합 점수 {evaluation.total_score:.2f}로 높은 가치를 인정하여 저장"
        elif action == InsightAction.PRIORITIZE:
            reasoning += f"중요도 {priority.value}로 우선순위 부여하여 저장"
        elif action == InsightAction.HOLD:
            reasoning += f"추가 검토 필요로 보류 (점수: {evaluation.total_score:.2f})"
        elif action == InsightAction.MODIFY:
            reasoning += f"수정 후 재검토 필요 (위험도: {evaluation.risk_score:.2f})"
        else:  # DISCARD
            reasoning += f"낮은 가치 또는 높은 위험으로 폐기"
            
        reasoning += f" (카테고리: {category.value})"
        return reasoning
        
    def _calculate_expected_benefit(self, evaluation: InsightEvaluation, action: InsightAction) -> float:
        """예상 이익 계산"""
        base_benefit = evaluation.total_score * evaluation.impact_score
        
        # 액션별 이익 조정
        action_multipliers = {
            InsightAction.STORE: 1.0,
            InsightAction.PRIORITIZE: 1.2,
            InsightAction.HOLD: 0.5,
            InsightAction.MODIFY: 0.7,
            InsightAction.DISCARD: 0.0
        }
        
        return base_benefit * action_multipliers.get(action, 0.5)
        
    def _assess_risk(self, evaluation: InsightEvaluation, insight: Dict[str, Any]) -> str:
        """위험 평가"""
        risk_score = evaluation.risk_score
        
        if risk_score < 0.2:
            return "낮은 위험 - 안전하게 적용 가능"
        elif risk_score < 0.5:
            return "중간 위험 - 주의 깊게 모니터링 필요"
        elif risk_score < 0.8:
            return "높은 위험 - 단계적 적용 권장"
        else:
            return "매우 높은 위험 - 적용 금지"
            
    def _generate_implementation_plan(self, action: InsightAction, category: InsightCategory, 
                                    priority: InsightPriority) -> str:
        """구현 계획 생성"""
        if action == InsightAction.STORE:
            if priority == InsightPriority.CRITICAL:
                return "즉시 적용 및 모니터링"
            elif priority == InsightPriority.HIGH:
                return "우선순위 적용"
            else:
                return "일반 적용"
        elif action == InsightAction.PRIORITIZE:
            return "우선순위 큐에 추가하여 순차 적용"
        elif action == InsightAction.HOLD:
            return "추가 평가 후 재검토"
        elif action == InsightAction.MODIFY:
            return "수정 후 재평가"
        else:
            return "적용하지 않음"
            
    def execute_decision(self, decision: InsightDecision, insight: Dict[str, Any]):
        """결정 실행"""
        logger.info(f"🔄 결정 실행: {decision.action.value}")
        
        if decision.action == InsightAction.STORE:
            self.stored_insights[decision.insight_id] = {
                **insight,
                'decision': decision,
                'stored_at': datetime.now()
            }
            logger.info(f"💾 통찰 저장: {decision.insight_id}")
            
        elif decision.action == InsightAction.HOLD:
            self.held_insights[decision.insight_id] = {
                **insight,
                'decision': decision,
                'held_at': datetime.now()
            }
            logger.info(f"⏸️ 통찰 보류: {decision.insight_id}")
            
        elif decision.action == InsightAction.DISCARD:
            self.discarded_insights[decision.insight_id] = {
                **insight,
                'decision': decision,
                'discarded_at': datetime.now()
            }
            logger.info(f"🗑️ 통찰 폐기: {decision.insight_id}")
            
        elif decision.action == InsightAction.PRIORITIZE:
            self.stored_insights[decision.insight_id] = {
                **insight,
                'decision': decision,
                'stored_at': datetime.now()
            }
            self.priority_queue.append(decision.insight_id)
            logger.info(f"⭐ 통찰 우선순위 저장: {decision.insight_id}")
            
    def get_management_summary(self) -> Dict[str, Any]:
        """관리 요약"""
        return {
            "stored_count": len(self.stored_insights),
            "held_count": len(self.held_insights),
            "discarded_count": len(self.discarded_insights),
            "priority_count": len(self.priority_queue),
            "total_processed": len(self.stored_insights) + len(self.held_insights) + len(self.discarded_insights),
            "recent_decisions": [
                {
                    "insight_id": insight_id,
                    "action": data['decision'].action.value,
                    "category": data['decision'].category.value,
                    "priority": data['decision'].priority.value
                }
                for insight_id, data in list(self.stored_insights.items())[-5:]
            ]
        }

# 전역 인스턴스
_insight_manager = None

def get_insight_manager() -> InsightAutonomousManager:
    """전역 통찰 관리자 인스턴스 반환"""
    global _insight_manager
    if _insight_manager is None:
        _insight_manager = InsightAutonomousManager()
    return _insight_manager

if __name__ == "__main__":
    # 데모 실행
    manager = get_insight_manager()
    
    # 샘플 통찰
    sample_insight = {
        "session_id": "test_001",
        "strategy": "학습 성능 최적화를 위한 방법론 혼합 전략",
        "confidence": 0.7,
        "expected_impact": 0.8,
        "risk_level": "LOW",
        "problem": "학습 루프 성능 저하"
    }
    
    # 통찰 평가
    evaluation = manager.evaluate_insight(sample_insight)
    print(f"🔍 평가 결과:")
    print(f"   관련성: {evaluation.relevance_score:.3f}")
    print(f"   실현 가능성: {evaluation.feasibility_score:.3f}")
    print(f"   영향도: {evaluation.impact_score:.3f}")
    print(f"   위험도: {evaluation.risk_score:.3f}")
    print(f"   신선함: {evaluation.novelty_score:.3f}")
    print(f"   종합 점수: {evaluation.total_score:.3f}")
    
    # 결정 생성
    decision = manager.make_decision(sample_insight, evaluation)
    print(f"\n🎯 결정:")
    print(f"   액션: {decision.action.value}")
    print(f"   카테고리: {decision.category.value}")
    print(f"   우선순위: {decision.priority.value}")
    print(f"   이유: {decision.reasoning}")
    print(f"   예상 이익: {decision.expected_benefit:.3f}")
    print(f"   위험 평가: {decision.risk_assessment}")
    print(f"   구현 계획: {decision.implementation_plan}")
    
    # 결정 실행
    manager.execute_decision(decision, sample_insight)
    
    # 요약
    summary = manager.get_management_summary()
    print(f"\n�� 관리 요약: {summary}") 