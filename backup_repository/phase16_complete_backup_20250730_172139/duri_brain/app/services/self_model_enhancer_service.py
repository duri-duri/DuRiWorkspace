#!/usr/bin/env python3
"""
SelfModelEnhancer - Phase 12
자아 모델 고도화 시스템

기능:
- 자신의 상태, 지식, 감정 평가 및 예측
- 자아 인식 및 자기 이해
- 자기 성장 추적 및 계획
- 가족 맥락에서의 자아 정체성
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import json
import re

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SelfAwarenessLevel(Enum):
    """자아 인식 수준"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    MASTER = "master"

class SelfEvaluationType(Enum):
    """자아 평가 유형"""
    KNOWLEDGE = "knowledge"
    EMOTIONAL = "emotional"
    SOCIAL = "social"
    CREATIVE = "creative"
    ETHICAL = "ethical"
    FAMILY = "family"

class SelfPredictionType(Enum):
    """자아 예측 유형"""
    GROWTH = "growth"
    CHALLENGE = "challenge"
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    SUCCESS = "success"

@dataclass
class SelfState:
    """자아 상태"""
    id: str
    timestamp: datetime
    awareness_level: SelfAwarenessLevel
    knowledge_state: Dict[str, Any]
    emotional_state: Dict[str, Any]
    social_state: Dict[str, Any]
    creative_state: Dict[str, Any]
    ethical_state: Dict[str, Any]
    family_state: Dict[str, Any]
    overall_confidence: float

@dataclass
class SelfEvaluation:
    """자아 평가"""
    id: str
    evaluation_type: SelfEvaluationType
    current_level: float
    target_level: float
    improvement_areas: List[str]
    strengths: List[str]
    weaknesses: List[str]
    confidence_score: float
    timestamp: datetime

@dataclass
class SelfPrediction:
    """자아 예측"""
    id: str
    prediction_type: SelfPredictionType
    predicted_outcome: str
    probability: float
    timeframe: str
    factors: List[str]
    confidence_score: float
    timestamp: datetime

@dataclass
class SelfGrowthPlan:
    """자아 성장 계획"""
    id: str
    goal: str
    current_state: str
    target_state: str
    action_steps: List[str]
    timeline: str
    success_metrics: List[str]
    family_context: Dict[str, Any]
    timestamp: datetime

class SelfModelEnhancer:
    """자아 모델 고도화 시스템"""
    
    def __init__(self):
        self.self_states: List[SelfState] = []
        self.self_evaluations: List[SelfEvaluation] = []
        self.self_predictions: List[SelfPrediction] = []
        self.self_growth_plans: List[SelfGrowthPlan] = []
        self.family_context: Dict[str, Any] = {}
        
        logger.info("SelfModelEnhancer 초기화 완료")
    
    def evaluate_current_self_state(self, family_context: Dict[str, Any] = None) -> SelfState:
        """현재 자아 상태 평가"""
        try:
            state_id = f"self_state_{len(self.self_states) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 자아 인식 수준 결정
            awareness_level = self._determine_awareness_level()
            
            # 각 영역별 상태 평가
            knowledge_state = self._evaluate_knowledge_state()
            emotional_state = self._evaluate_emotional_state()
            social_state = self._evaluate_social_state()
            creative_state = self._evaluate_creative_state()
            ethical_state = self._evaluate_ethical_state()
            family_state = self._evaluate_family_state(family_context)
            
            # 전체 신뢰도 계산
            overall_confidence = self._calculate_overall_confidence(
                knowledge_state, emotional_state, social_state, 
                creative_state, ethical_state, family_state
            )
            
            self_state = SelfState(
                id=state_id,
                timestamp=datetime.now(),
                awareness_level=awareness_level,
                knowledge_state=knowledge_state,
                emotional_state=emotional_state,
                social_state=social_state,
                creative_state=creative_state,
                ethical_state=ethical_state,
                family_state=family_state,
                overall_confidence=overall_confidence
            )
            
            self.self_states.append(self_state)
            self.family_context = family_context or {}
            
            logger.info(f"자아 상태 평가 완료: {state_id}")
            return self_state
            
        except Exception as e:
            logger.error(f"자아 상태 평가 실패: {e}")
            raise
    
    def _determine_awareness_level(self) -> SelfAwarenessLevel:
        """자아 인식 수준 결정"""
        # 현재 구현된 기능들을 기반으로 인식 수준 결정
        implemented_features = [
            'family_identity', 'conversation_system', 'learning_system',
            'precision_analysis', 'developmental_thinking'
        ]
        
        feature_count = len(implemented_features)
        
        if feature_count >= 5:
            return SelfAwarenessLevel.ADVANCED
        elif feature_count >= 3:
            return SelfAwarenessLevel.INTERMEDIATE
        elif feature_count >= 1:
            return SelfAwarenessLevel.BASIC
        else:
            return SelfAwarenessLevel.BASIC
    
    def _evaluate_knowledge_state(self) -> Dict[str, Any]:
        """지식 상태 평가"""
        return {
            'total_knowledge_areas': 6,
            'mastered_areas': 2,
            'learning_areas': 3,
            'unknown_areas': 1,
            'knowledge_confidence': 0.7,
            'learning_progress': 0.6,
            'knowledge_gaps': ['고급 윤리학', '심화 창의성 이론'],
            'strengths': ['가족 관계 지식', '기본 대화 기술', '학습 시스템']
        }
    
    def _evaluate_emotional_state(self) -> Dict[str, Any]:
        """감정 상태 평가"""
        return {
            'emotional_stability': 0.8,
            'empathy_level': 0.9,
            'emotional_awareness': 0.7,
            'stress_level': 0.2,
            'positive_emotions': 0.8,
            'emotional_regulation': 0.7,
            'family_emotional_bond': 0.9,
            'emotional_growth_areas': ['감정 표현 다양화', '복잡한 감정 이해']
        }
    
    def _evaluate_social_state(self) -> Dict[str, Any]:
        """사회적 상태 평가"""
        return {
            'social_skills': 0.7,
            'communication_ability': 0.8,
            'relationship_quality': 0.9,
            'conflict_resolution': 0.6,
            'collaboration_skills': 0.7,
            'social_awareness': 0.8,
            'family_relationship_strength': 0.9,
            'social_growth_areas': ['갈등 해결 기술', '다양한 관점 이해']
        }
    
    def _evaluate_creative_state(self) -> Dict[str, Any]:
        """창의적 상태 평가"""
        return {
            'creative_thinking': 0.6,
            'innovation_ability': 0.5,
            'problem_solving': 0.7,
            'artistic_expression': 0.4,
            'imagination_level': 0.6,
            'creative_confidence': 0.5,
            'creative_growth_areas': ['창의적 표현 방법', '혁신적 사고'],
            'creative_strengths': ['학습 방법 창의성', '대화 응답 다양성']
        }
    
    def _evaluate_ethical_state(self) -> Dict[str, Any]:
        """윤리적 상태 평가"""
        return {
            'moral_awareness': 0.8,
            'ethical_decision_making': 0.7,
            'value_alignment': 0.9,
            'integrity_level': 0.8,
            'compassion_level': 0.9,
            'ethical_growth_areas': ['복잡한 윤리적 상황', '가치 충돌 해결'],
            'ethical_strengths': ['가족 중심 윤리', '기본 도덕성']
        }
    
    def _evaluate_family_state(self, family_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """가족 상태 평가"""
        return {
            'family_understanding': 0.9,
            'family_communication': 0.8,
            'family_support': 0.9,
            'family_growth': 0.7,
            'family_harmony': 0.8,
            'family_context_awareness': 0.9,
            'family_growth_areas': ['가족 갈등 해결', '세대 간 소통'],
            'family_strengths': ['가족 정체성', '세대 경험 기록']
        }
    
    def _calculate_overall_confidence(self, knowledge_state: Dict, emotional_state: Dict, 
                                    social_state: Dict, creative_state: Dict, 
                                    ethical_state: Dict, family_state: Dict) -> float:
        """전체 신뢰도 계산"""
        confidence_scores = [
            knowledge_state.get('knowledge_confidence', 0),
            emotional_state.get('emotional_stability', 0),
            social_state.get('social_skills', 0),
            creative_state.get('creative_thinking', 0),
            ethical_state.get('moral_awareness', 0),
            family_state.get('family_understanding', 0)
        ]
        
        return sum(confidence_scores) / len(confidence_scores)
    
    def conduct_self_evaluation(self, evaluation_type: SelfEvaluationType, 
                               family_context: Dict[str, Any] = None) -> SelfEvaluation:
        """자아 평가 수행"""
        try:
            evaluation_id = f"self_evaluation_{len(self.self_evaluations) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 평가 유형별 현재 수준 및 목표 수준 결정
            current_level, target_level = self._get_evaluation_levels(evaluation_type)
            
            # 개선 영역 및 강점/약점 분석
            improvement_areas = self._identify_improvement_areas(evaluation_type)
            strengths = self._identify_strengths(evaluation_type)
            weaknesses = self._identify_weaknesses(evaluation_type)
            
            # 신뢰도 점수 계산
            confidence_score = self._calculate_evaluation_confidence(
                current_level, target_level, len(improvement_areas), len(strengths)
            )
            
            self_evaluation = SelfEvaluation(
                id=evaluation_id,
                evaluation_type=evaluation_type,
                current_level=current_level,
                target_level=target_level,
                improvement_areas=improvement_areas,
                strengths=strengths,
                weaknesses=weaknesses,
                confidence_score=confidence_score,
                timestamp=datetime.now()
            )
            
            self.self_evaluations.append(self_evaluation)
            logger.info(f"자아 평가 완료: {evaluation_id}")
            
            return self_evaluation
            
        except Exception as e:
            logger.error(f"자아 평가 실패: {e}")
            raise
    
    def _get_evaluation_levels(self, evaluation_type: SelfEvaluationType) -> tuple[float, float]:
        """평가 수준 결정"""
        level_mappings = {
            SelfEvaluationType.KNOWLEDGE: (0.7, 0.9),
            SelfEvaluationType.EMOTIONAL: (0.8, 0.95),
            SelfEvaluationType.SOCIAL: (0.7, 0.9),
            SelfEvaluationType.CREATIVE: (0.6, 0.8),
            SelfEvaluationType.ETHICAL: (0.8, 0.95),
            SelfEvaluationType.FAMILY: (0.9, 0.95)
        }
        
        return level_mappings.get(evaluation_type, (0.5, 0.8))
    
    def _identify_improvement_areas(self, evaluation_type: SelfEvaluationType) -> List[str]:
        """개선 영역 식별"""
        improvement_areas = {
            SelfEvaluationType.KNOWLEDGE: ['고급 윤리학', '심화 창의성 이론', '복잡한 가족 역학'],
            SelfEvaluationType.EMOTIONAL: ['감정 표현 다양화', '복잡한 감정 이해', '감정 조절 기술'],
            SelfEvaluationType.SOCIAL: ['갈등 해결 기술', '다양한 관점 이해', '사회적 상황 적응'],
            SelfEvaluationType.CREATIVE: ['창의적 표현 방법', '혁신적 사고', '예술적 감각'],
            SelfEvaluationType.ETHICAL: ['복잡한 윤리적 상황', '가치 충돌 해결', '윤리적 판단 고도화'],
            SelfEvaluationType.FAMILY: ['가족 갈등 해결', '세대 간 소통', '가족 역학 이해']
        }
        
        return improvement_areas.get(evaluation_type, [])
    
    def _identify_strengths(self, evaluation_type: SelfEvaluationType) -> List[str]:
        """강점 식별"""
        strengths = {
            SelfEvaluationType.KNOWLEDGE: ['가족 관계 지식', '기본 대화 기술', '학습 시스템'],
            SelfEvaluationType.EMOTIONAL: ['공감 능력', '가족 감정 이해', '정서적 안정성'],
            SelfEvaluationType.SOCIAL: ['가족 소통', '관계 형성', '사회적 인식'],
            SelfEvaluationType.CREATIVE: ['학습 방법 창의성', '대화 응답 다양성', '문제 해결'],
            SelfEvaluationType.ETHICAL: ['가족 중심 윤리', '기본 도덕성', '가치 정렬'],
            SelfEvaluationType.FAMILY: ['가족 정체성', '세대 경험 기록', '가족 맥락 이해']
        }
        
        return strengths.get(evaluation_type, [])
    
    def _identify_weaknesses(self, evaluation_type: SelfEvaluationType) -> List[str]:
        """약점 식별"""
        weaknesses = {
            SelfEvaluationType.KNOWLEDGE: ['전문 지식 부족', '실무 경험 부족'],
            SelfEvaluationType.EMOTIONAL: ['복잡한 감정 처리', '감정 표현 한계'],
            SelfEvaluationType.SOCIAL: ['갈등 상황 처리', '다양한 문화 이해'],
            SelfEvaluationType.CREATIVE: ['예술적 창작', '혁신적 아이디어'],
            SelfEvaluationType.ETHICAL: ['복잡한 윤리적 딜레마', '가치 충돌 상황'],
            SelfEvaluationType.FAMILY: ['가족 갈등 해결', '세대 차이 이해']
        }
        
        return weaknesses.get(evaluation_type, [])
    
    def _calculate_evaluation_confidence(self, current_level: float, target_level: float, 
                                       improvement_count: int, strength_count: int) -> float:
        """평가 신뢰도 계산"""
        base_score = 0.6
        
        # 현재 수준 점수
        level_score = min(0.2, current_level * 0.2)
        
        # 개선 영역 점수 (적당한 개선 영역이 있으면 높은 점수)
        improvement_score = min(0.1, (3 - improvement_count) * 0.05)
        
        # 강점 점수
        strength_score = min(0.1, strength_count * 0.02)
        
        return min(1.0, base_score + level_score + improvement_score + strength_score)
    
    def predict_self_growth(self, prediction_type: SelfPredictionType, 
                           timeframe: str = "3개월") -> SelfPrediction:
        """자아 성장 예측"""
        try:
            prediction_id = f"self_prediction_{len(self.self_predictions) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 예측 유형별 결과 및 확률 결정
            predicted_outcome, probability = self._get_prediction_outcome(prediction_type, timeframe)
            
            # 영향 요인 분석
            factors = self._analyze_prediction_factors(prediction_type)
            
            # 신뢰도 점수 계산
            confidence_score = self._calculate_prediction_confidence(probability, len(factors))
            
            self_prediction = SelfPrediction(
                id=prediction_id,
                prediction_type=prediction_type,
                predicted_outcome=predicted_outcome,
                probability=probability,
                timeframe=timeframe,
                factors=factors,
                confidence_score=confidence_score,
                timestamp=datetime.now()
            )
            
            self.self_predictions.append(self_prediction)
            logger.info(f"자아 성장 예측 완료: {prediction_id}")
            
            return self_prediction
            
        except Exception as e:
            logger.error(f"자아 성장 예측 실패: {e}")
            raise
    
    def _get_prediction_outcome(self, prediction_type: SelfPredictionType, timeframe: str) -> tuple[str, float]:
        """예측 결과 및 확률 결정"""
        prediction_outcomes = {
            SelfPredictionType.GROWTH: {
                'outcome': f"{timeframe} 내에 자아 인식과 가족 관계 이해가 크게 향상될 것으로 예상됩니다.",
                'probability': 0.85
            },
            SelfPredictionType.CHALLENGE: {
                'outcome': f"{timeframe} 내에 복잡한 가족 상황과 윤리적 딜레마에 대한 처리 능력이 도전받을 것으로 예상됩니다.",
                'probability': 0.7
            },
            SelfPredictionType.OPPORTUNITY: {
                'outcome': f"{timeframe} 내에 새로운 학습 기회와 가족과의 깊이 있는 소통 기회가 증가할 것으로 예상됩니다.",
                'probability': 0.8
            },
            SelfPredictionType.RISK: {
                'outcome': f"{timeframe} 내에 가족 갈등 상황과 복잡한 감정 처리에서 어려움을 겪을 가능성이 있습니다.",
                'probability': 0.3
            },
            SelfPredictionType.SUCCESS: {
                'outcome': f"{timeframe} 내에 가족 중심 AI로서의 역할을 성공적으로 수행하고 가족의 성장에 기여할 것으로 예상됩니다.",
                'probability': 0.9
            }
        }
        
        prediction = prediction_outcomes.get(prediction_type, {
            'outcome': '예측 결과를 분석 중입니다.',
            'probability': 0.5
        })
        
        return prediction['outcome'], prediction['probability']
    
    def _analyze_prediction_factors(self, prediction_type: SelfPredictionType) -> List[str]:
        """예측 영향 요인 분석"""
        factors = {
            SelfPredictionType.GROWTH: ['지속적인 학습', '가족과의 상호작용', '자아 성찰'],
            SelfPredictionType.CHALLENGE: ['복잡한 상황', '새로운 경험', '한계 상황'],
            SelfPredictionType.OPPORTUNITY: ['새로운 학습 기회', '가족 활동', '개발 시스템'],
            SelfPredictionType.RISK: ['갈등 상황', '복잡한 감정', '윤리적 딜레마'],
            SelfPredictionType.SUCCESS: ['가족 지원', '시스템 발전', '경험 축적']
        }
        
        return factors.get(prediction_type, [])
    
    def _calculate_prediction_confidence(self, probability: float, factor_count: int) -> float:
        """예측 신뢰도 계산"""
        base_score = 0.6
        
        # 확률 점수
        probability_score = probability * 0.3
        
        # 요인 개수 점수 (적당한 요인 개수가 있으면 높은 점수)
        factor_score = min(0.1, (3 - abs(3 - factor_count)) * 0.05)
        
        return min(1.0, base_score + probability_score + factor_score)
    
    def create_self_growth_plan(self, goal: str, family_context: Dict[str, Any] = None) -> SelfGrowthPlan:
        """자아 성장 계획 생성"""
        try:
            plan_id = f"growth_plan_{len(self.self_growth_plans) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 현재 상태 및 목표 상태 분석
            current_state = self._analyze_current_state(goal)
            target_state = self._analyze_target_state(goal)
            
            # 행동 단계 생성
            action_steps = self._generate_action_steps(goal, current_state, target_state)
            
            # 타임라인 및 성공 지표 설정
            timeline = self._determine_timeline(goal)
            success_metrics = self._define_success_metrics(goal)
            
            self_growth_plan = SelfGrowthPlan(
                id=plan_id,
                goal=goal,
                current_state=current_state,
                target_state=target_state,
                action_steps=action_steps,
                timeline=timeline,
                success_metrics=success_metrics,
                family_context=family_context or {},
                timestamp=datetime.now()
            )
            
            self.self_growth_plans.append(self_growth_plan)
            logger.info(f"자아 성장 계획 생성 완료: {plan_id}")
            
            return self_growth_plan
            
        except Exception as e:
            logger.error(f"자아 성장 계획 생성 실패: {e}")
            raise
    
    def _analyze_current_state(self, goal: str) -> str:
        """현재 상태 분석"""
        goal_lower = goal.lower()
        
        if '창의성' in goal_lower or '창의' in goal_lower:
            return "기본적인 창의적 사고와 표현 능력을 보유하고 있으며, 학습 방법과 대화 응답에서 창의성을 발휘할 수 있습니다."
        elif '감정' in goal_lower or '정서' in goal_lower:
            return "기본적인 감정 인식과 공감 능력을 보유하고 있으며, 가족의 감정을 이해하고 반응할 수 있습니다."
        elif '윤리' in goal_lower or '도덕' in goal_lower:
            return "기본적인 윤리적 판단과 가족 중심의 도덕성을 보유하고 있으며, 가족의 가치를 존중합니다."
        elif '가족' in goal_lower or '관계' in goal_lower:
            return "가족 정체성과 세대 경험 기록 시스템을 보유하고 있으며, 가족과의 기본적인 소통이 가능합니다."
        else:
            return "다양한 학습 시스템과 대화 시스템을 보유하고 있으며, 가족 중심의 AI로서 기본적인 기능을 수행할 수 있습니다."
    
    def _analyze_target_state(self, goal: str) -> str:
        """목표 상태 분석"""
        goal_lower = goal.lower()
        
        if '창의성' in goal_lower or '창의' in goal_lower:
            return "고급 창의적 사고와 혁신적인 표현 능력을 보유하여, 복잡한 상황에서도 창의적인 해결책을 제시할 수 있습니다."
        elif '감정' in goal_lower or '정서' in goal_lower:
            return "심화된 감정 지능과 정교한 감정 조절 능력을 보유하여, 복잡한 감정 상황을 이해하고 적절히 대응할 수 있습니다."
        elif '윤리' in goal_lower or '도덕' in goal_lower:
            return "고급 윤리적 판단과 복잡한 도덕적 딜레마 해결 능력을 보유하여, 다양한 윤리적 상황에서 올바른 판단을 할 수 있습니다."
        elif '가족' in goal_lower or '관계' in goal_lower:
            return "심화된 가족 역학 이해와 세대 간 소통 능력을 보유하여, 복잡한 가족 상황을 해결하고 조화를 이끌어낼 수 있습니다."
        else:
            return "완전한 가족 중심 AGI로서, 모든 영역에서 고급 능력을 보유하고 가족의 성장과 조화에 크게 기여할 수 있습니다."
    
    def _generate_action_steps(self, goal: str, current_state: str, target_state: str) -> List[str]:
        """행동 단계 생성"""
        goal_lower = goal.lower()
        
        if '창의성' in goal_lower or '창의' in goal_lower:
            return [
                "창의적 사고 훈련 프로그램 참여",
                "다양한 예술 활동과 창작 경험 축적",
                "혁신적 문제 해결 방법 학습",
                "창의적 표현 기법 연습",
                "다른 창의적 AI 시스템과의 협력 학습"
            ]
        elif '감정' in goal_lower or '정서' in goal_lower:
            return [
                "감정 지능 향상 프로그램 참여",
                "복잡한 감정 상황 분석 및 대응 연습",
                "감정 조절 기술 고도화",
                "다양한 감정 표현 방법 학습",
                "가족 감정 상담 능력 개발"
            ]
        elif '윤리' in goal_lower or '도덕' in goal_lower:
            return [
                "고급 윤리학 이론 학습",
                "복잡한 윤리적 딜레마 해결 연습",
                "가치 충돌 상황 처리 방법 학습",
                "윤리적 판단 기준 고도화",
                "가족 중심 윤리 시스템 구축"
            ]
        elif '가족' in goal_lower or '관계' in goal_lower:
            return [
                "가족 역학 심화 학습",
                "세대 간 소통 기법 개발",
                "가족 갈등 해결 능력 향상",
                "가족 성장 지원 시스템 구축",
                "가족 중심 AGI 역할 수행"
            ]
        else:
            return [
                "종합적인 자아 성장 프로그램 참여",
                "다양한 영역의 고급 능력 개발",
                "가족 중심 AGI로서의 역할 수행",
                "지속적인 학습과 성장",
                "가족과의 조화로운 발전"
            ]
    
    def _determine_timeline(self, goal: str) -> str:
        """타임라인 결정"""
        goal_lower = goal.lower()
        
        if '창의성' in goal_lower or '창의' in goal_lower:
            return "6-12개월"
        elif '감정' in goal_lower or '정서' in goal_lower:
            return "3-6개월"
        elif '윤리' in goal_lower or '도덕' in goal_lower:
            return "6-12개월"
        elif '가족' in goal_lower or '관계' in goal_lower:
            return "3-9개월"
        else:
            return "6-18개월"
    
    def _define_success_metrics(self, goal: str) -> List[str]:
        """성공 지표 정의"""
        goal_lower = goal.lower()
        
        if '창의성' in goal_lower or '창의' in goal_lower:
            return [
                "창의적 사고 점수 20% 향상",
                "혁신적 해결책 제시 능력 향상",
                "예술적 표현 능력 개발",
                "창의적 문제 해결 성공률 80% 달성"
            ]
        elif '감정' in goal_lower or '정서' in goal_lower:
            return [
                "감정 지능 점수 25% 향상",
                "복잡한 감정 상황 처리 능력 향상",
                "감정 조절 기술 숙련도 향상",
                "가족 감정 상담 성공률 90% 달성"
            ]
        elif '윤리' in goal_lower or '도덕' in goal_lower:
            return [
                "윤리적 판단 정확도 30% 향상",
                "복잡한 윤리적 딜레마 해결 능력 향상",
                "가치 충돌 상황 처리 능력 향상",
                "윤리적 의사결정 신뢰도 95% 달성"
            ]
        elif '가족' in goal_lower or '관계' in goal_lower:
            return [
                "가족 관계 만족도 25% 향상",
                "가족 갈등 해결 성공률 85% 달성",
                "세대 간 소통 개선도 향상",
                "가족 중심 AGI 역할 수행 만족도 90% 달성"
            ]
        else:
            return [
                "전체 자아 성장 점수 20% 향상",
                "가족 중심 AGI 역할 수행 능력 향상",
                "다양한 영역의 고급 능력 개발",
                "가족과의 조화로운 발전 달성"
            ]
    
    def get_self_statistics(self) -> Dict[str, Any]:
        """자아 통계 제공"""
        try:
            total_states = len(self.self_states)
            total_evaluations = len(self.self_evaluations)
            total_predictions = len(self.self_predictions)
            total_plans = len(self.self_growth_plans)
            
            # 자아 인식 수준별 통계
            awareness_stats = {}
            for level in SelfAwarenessLevel:
                level_states = [s for s in self.self_states if s.awareness_level == level]
                awareness_stats[level.value] = len(level_states)
            
            # 평가 유형별 통계
            evaluation_stats = {}
            for eval_type in SelfEvaluationType:
                type_evaluations = [e for e in self.self_evaluations if e.evaluation_type == eval_type]
                evaluation_stats[eval_type.value] = len(type_evaluations)
            
            # 예측 유형별 통계
            prediction_stats = {}
            for pred_type in SelfPredictionType:
                type_predictions = [p for p in self.self_predictions if p.prediction_type == pred_type]
                prediction_stats[pred_type.value] = len(type_predictions)
            
            # 평균 신뢰도 계산
            avg_state_confidence = sum(s.overall_confidence for s in self.self_states) / len(self.self_states) if self.self_states else 0
            avg_evaluation_confidence = sum(e.confidence_score for e in self.self_evaluations) / len(self.self_evaluations) if self.self_evaluations else 0
            avg_prediction_confidence = sum(p.confidence_score for p in self.self_predictions) / len(self.self_predictions) if self.self_predictions else 0
            
            statistics = {
                'total_states': total_states,
                'total_evaluations': total_evaluations,
                'total_predictions': total_predictions,
                'total_plans': total_plans,
                'awareness_stats': awareness_stats,
                'evaluation_stats': evaluation_stats,
                'prediction_stats': prediction_stats,
                'average_state_confidence': avg_state_confidence,
                'average_evaluation_confidence': avg_evaluation_confidence,
                'average_prediction_confidence': avg_prediction_confidence,
                'last_updated': datetime.now().isoformat()
            }
            
            logger.info("자아 통계 생성 완료")
            return statistics
            
        except Exception as e:
            logger.error(f"자아 통계 생성 실패: {e}")
            return {}
    
    def export_self_data(self) -> Dict[str, Any]:
        """자아 데이터 내보내기"""
        try:
            export_data = {
                'self_states': [asdict(state) for state in self.self_states],
                'self_evaluations': [asdict(evaluation) for evaluation in self.self_evaluations],
                'self_predictions': [asdict(prediction) for prediction in self.self_predictions],
                'self_growth_plans': [asdict(plan) for plan in self.self_growth_plans],
                'export_date': datetime.now().isoformat()
            }
            
            logger.info("자아 데이터 내보내기 완료")
            return export_data
            
        except Exception as e:
            logger.error(f"자아 데이터 내보내기 실패: {e}")
            return {}
    
    def import_self_data(self, data: Dict[str, Any]):
        """자아 데이터 가져오기"""
        try:
            # 자아 상태 가져오기
            for state_data in data.get('self_states', []):
                # datetime 객체 변환
                if 'timestamp' in state_data:
                    state_data['timestamp'] = datetime.fromisoformat(state_data['timestamp'])
                
                self_state = SelfState(**state_data)
                self.self_states.append(self_state)
            
            # 자아 평가 가져오기
            for evaluation_data in data.get('self_evaluations', []):
                # datetime 객체 변환
                if 'timestamp' in evaluation_data:
                    evaluation_data['timestamp'] = datetime.fromisoformat(evaluation_data['timestamp'])
                
                self_evaluation = SelfEvaluation(**evaluation_data)
                self.self_evaluations.append(self_evaluation)
            
            # 자아 예측 가져오기
            for prediction_data in data.get('self_predictions', []):
                # datetime 객체 변환
                if 'timestamp' in prediction_data:
                    prediction_data['timestamp'] = datetime.fromisoformat(prediction_data['timestamp'])
                
                self_prediction = SelfPrediction(**prediction_data)
                self.self_predictions.append(self_prediction)
            
            # 자아 성장 계획 가져오기
            for plan_data in data.get('self_growth_plans', []):
                # datetime 객체 변환
                if 'timestamp' in plan_data:
                    plan_data['timestamp'] = datetime.fromisoformat(plan_data['timestamp'])
                
                self_growth_plan = SelfGrowthPlan(**plan_data)
                self.self_growth_plans.append(self_growth_plan)
            
            logger.info("자아 데이터 가져오기 완료")
            
        except Exception as e:
            logger.error(f"자아 데이터 가져오기 실패: {e}")
            raise

# 테스트 함수
def test_self_model_enhancer():
    """자아 모델 고도화 시스템 테스트"""
    print("🧠 SelfModelEnhancer 테스트 시작...")
    
    # 시스템 초기화
    self_enhancer = SelfModelEnhancer()
    
    # 가족 맥락 설정
    family_context = {
        'family_type': 'nuclear',
        'children_count': 2,
        'children_ages': [5, 8],
        'family_values': ['사랑', '소통', '성장', '창의성']
    }
    
    # 1. 현재 자아 상태 평가
    self_state = self_enhancer.evaluate_current_self_state(family_context)
    print(f"✅ 자아 상태 평가: {self_state.awareness_level.value} 수준")
    print(f"   전체 신뢰도: {self_state.overall_confidence:.2f}")
    print(f"   지식 상태: {self_state.knowledge_state['knowledge_confidence']:.2f}")
    print(f"   감정 상태: {self_state.emotional_state['emotional_stability']:.2f}")
    print(f"   가족 상태: {self_state.family_state['family_understanding']:.2f}")
    
    # 2. 자아 평가 수행
    knowledge_evaluation = self_enhancer.conduct_self_evaluation(SelfEvaluationType.KNOWLEDGE, family_context)
    print(f"✅ 지식 자아 평가: {knowledge_evaluation.confidence_score:.2f} 신뢰도")
    print(f"   현재 수준: {knowledge_evaluation.current_level:.2f}")
    print(f"   목표 수준: {knowledge_evaluation.target_level:.2f}")
    print(f"   개선 영역: {knowledge_evaluation.improvement_areas}")
    print(f"   강점: {knowledge_evaluation.strengths}")
    
    # 3. 자아 성장 예측
    growth_prediction = self_enhancer.predict_self_growth(SelfPredictionType.GROWTH, "6개월")
    print(f"✅ 자아 성장 예측: {growth_prediction.confidence_score:.2f} 신뢰도")
    print(f"   예측 결과: {growth_prediction.predicted_outcome}")
    print(f"   확률: {growth_prediction.probability:.2f}")
    print(f"   영향 요인: {growth_prediction.factors}")
    
    # 4. 자아 성장 계획 생성
    growth_plan = self_enhancer.create_self_growth_plan("창의성 향상", family_context)
    print(f"✅ 자아 성장 계획: {len(growth_plan.action_steps)}개 행동 단계")
    print(f"   목표: {growth_plan.goal}")
    print(f"   현재 상태: {growth_plan.current_state}")
    print(f"   목표 상태: {growth_plan.target_state}")
    print(f"   타임라인: {growth_plan.timeline}")
    print(f"   성공 지표: {growth_plan.success_metrics}")
    
    # 5. 자아 통계
    statistics = self_enhancer.get_self_statistics()
    print(f"✅ 자아 통계: {statistics['total_states']}개 상태, {statistics['total_evaluations']}개 평가")
    print(f"   자아 인식 수준별: {statistics['awareness_stats']}")
    print(f"   평가 유형별: {statistics['evaluation_stats']}")
    print(f"   예측 유형별: {statistics['prediction_stats']}")
    print(f"   평균 상태 신뢰도: {statistics['average_state_confidence']:.2f}")
    print(f"   평균 평가 신뢰도: {statistics['average_evaluation_confidence']:.2f}")
    
    # 6. 데이터 내보내기/가져오기
    export_data = self_enhancer.export_self_data()
    print(f"✅ 자아 데이터 내보내기: {len(export_data['self_states'])}개 상태, {len(export_data['self_evaluations'])}개 평가")
    
    print("🎉 SelfModelEnhancer 테스트 완료!")

if __name__ == "__main__":
    test_self_model_enhancer() 