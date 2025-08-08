#!/usr/bin/env python3
"""
DuRiCore Day 11 - 통합 사회적 지능 시스템
기존 사회적 지능 시스템들을 통합하여 완전한 사회적 지능 구현
"""

import asyncio
import json
import logging
import time
import statistics
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import random
import math
from collections import defaultdict, deque

# 기존 시스템들 import
try:
    from social_intelligence_engine import SocialIntelligenceEngine, SocialIntelligenceLevel, EmotionType, SocialContextType
    from social_intelligence_system import SocialIntelligenceSystem, SocialIntelligenceType, ContextComplexity, AdaptationLevel
except ImportError:
    # 기존 시스템이 없는 경우를 위한 fallback
    pass

logger = logging.getLogger(__name__)

class IntegratedSocialIntelligenceType(Enum):
    """통합 사회적 지능 타입"""
    SOCIAL_CONTEXT_UNDERSTANDING = "social_context_understanding"  # 사회적 맥락 이해
    HUMAN_INTERACTION_OPTIMIZATION = "human_interaction_optimization"  # 인간 상호작용 최적화
    SOCIAL_ADAPTATION = "social_adaptation"  # 사회적 적응
    COLLABORATION_COOPERATION = "collaboration_cooperation"  # 협력 및 협업

class SocialMaturityLevel(Enum):
    """사회적 성숙도 수준"""
    BEGINNER = "beginner"        # 초급 (0.0-0.3)
    INTERMEDIATE = "intermediate"  # 중급 (0.3-0.7)
    ADVANCED = "advanced"        # 고급 (0.7-0.9)
    EXPERT = "expert"            # 전문가 (0.9-1.0)

@dataclass
class SocialContextUnderstanding:
    """사회적 맥락 이해"""
    understanding_id: str
    context_type: str
    social_situation: str
    cultural_factors: List[str]
    power_dynamics: Dict[str, float]
    social_norms: List[str]
    communication_style: str
    relationship_patterns: Dict[str, str]
    understanding_confidence: float
    created_at: datetime

@dataclass
class HumanInteractionOptimization:
    """인간 상호작용 최적화"""
    optimization_id: str
    interaction_type: str
    participants: List[str]
    communication_style: str
    emotional_empathy: float
    social_distance: float
    cooperation_level: float
    interaction_quality: float
    optimization_suggestions: List[str]
    created_at: datetime

@dataclass
class SocialAdaptation:
    """사회적 적응"""
    adaptation_id: str
    environment_type: str
    adaptation_strategy: str
    role_recognition: str
    social_learning: List[str]
    social_growth: float
    adaptation_speed: float
    adaptation_effectiveness: float
    created_at: datetime

@dataclass
class CollaborationCooperation:
    """협력 및 협업"""
    collaboration_id: str
    collaboration_type: str
    participants: List[str]
    teamwork_efficiency: float
    conflict_resolution: float
    communication_effectiveness: float
    leadership_appropriateness: float
    collaboration_quality: float
    created_at: datetime

class IntegratedSocialIntelligenceSystem:
    """통합 사회적 지능 시스템"""
    
    def __init__(self):
        # 기존 시스템들 통합
        try:
            self.social_engine = SocialIntelligenceEngine()
            self.social_system = SocialIntelligenceSystem()
        except NameError:
            # 기존 시스템이 없는 경우를 위한 fallback
            self.social_engine = None
            self.social_system = None
        
        # 통합 사회적 지능 데이터
        self.social_context_understandings = []
        self.human_interaction_optimizations = []
        self.social_adaptations = []
        self.collaboration_cooperations = []
        
        # 통합 시스템 설정
        self.integration_weights = {
            "social_context_understanding": 0.25,
            "human_interaction_optimization": 0.25,
            "social_adaptation": 0.25,
            "collaboration_cooperation": 0.25
        }
        
        # 사회적 성숙도 설정
        self.social_maturity_thresholds = {
            "beginner": 0.3,
            "intermediate": 0.7,
            "advanced": 0.9,
            "expert": 1.0
        }
        
        logger.info("🧠 통합 사회적 지능 시스템 초기화 완료")
    
    async def understand_social_context(self, context: Dict[str, Any]) -> SocialContextUnderstanding:
        """사회적 맥락 이해"""
        try:
            logger.info("사회적 맥락 이해 시작")
            
            # 기존 시스템 활용
            context_type = "일반적"
            if self.social_engine:
                try:
                    social_context = await self.social_engine.understand_social_context(context)
                    if social_context and hasattr(social_context, 'context_type'):
                        if hasattr(social_context.context_type, 'value'):
                            context_type = social_context.context_type.value
                        else:
                            context_type = str(social_context.context_type)
                except Exception as e:
                    logger.warning(f"기존 시스템 활용 실패: {e}")
                    context_type = await self._analyze_context_type(context)
            else:
                context_type = await self._analyze_context_type(context)
            
            # 사회적 상황 분석
            social_situation = await self._analyze_social_situation(context)
            
            # 문화적 요소 분석
            cultural_factors = await self._analyze_cultural_factors(context)
            
            # 권력 역학 분석
            power_dynamics = await self._analyze_power_dynamics(context)
            
            # 사회적 규범 분석
            social_norms = await self._analyze_social_norms(context)
            
            # 의사소통 스타일 분석
            communication_style = await self._analyze_communication_style(context)
            
            # 관계 패턴 분석
            relationship_patterns = await self._analyze_relationship_patterns(context)
            
            # 이해 신뢰도 계산
            understanding_confidence = await self._calculate_understanding_confidence(
                context_type, social_situation, cultural_factors, power_dynamics
            )
            
            # 사회적 맥락 이해 생성
            understanding = SocialContextUnderstanding(
                understanding_id=f"understanding_{int(time.time() * 1000)}",
                context_type=context_type,
                social_situation=social_situation,
                cultural_factors=cultural_factors,
                power_dynamics=power_dynamics,
                social_norms=social_norms,
                communication_style=communication_style,
                relationship_patterns=relationship_patterns,
                understanding_confidence=understanding_confidence,
                created_at=datetime.now()
            )
            
            self.social_context_understandings.append(understanding)
            
            logger.info(f"사회적 맥락 이해 완료: {understanding.understanding_id}")
            return understanding
            
        except Exception as e:
            logger.error(f"사회적 맥락 이해 실패: {e}")
            return await self._create_empty_social_context_understanding()
    
    async def optimize_human_interaction(self, interaction_context: Dict[str, Any]) -> HumanInteractionOptimization:
        """인간 상호작용 최적화"""
        try:
            logger.info("인간 상호작용 최적화 시작")
            
            # 기존 시스템 활용
            interaction_type = "일반적"
            participants = ["참여자"]
            communication_style = "일반적"
            interaction_quality = 0.5
            
            if self.social_engine:
                try:
                    interaction = await self.social_engine.optimize_human_interaction(interaction_context)
                    if interaction:
                        if hasattr(interaction, 'interaction_type'):
                            interaction_type = interaction.interaction_type
                        if hasattr(interaction, 'participants'):
                            participants = interaction.participants
                        if hasattr(interaction, 'communication_style'):
                            communication_style = interaction.communication_style
                        if hasattr(interaction, 'interaction_quality'):
                            interaction_quality = interaction.interaction_quality
                except Exception as e:
                    logger.warning(f"기존 시스템 활용 실패: {e}")
                    interaction_type = await self._analyze_interaction_type(interaction_context)
                    participants = await self._identify_participants(interaction_context)
                    communication_style = await self._analyze_communication_style(interaction_context)
                    interaction_quality = await self._assess_interaction_quality(interaction_context)
            else:
                interaction_type = await self._analyze_interaction_type(interaction_context)
                participants = await self._identify_participants(interaction_context)
                communication_style = await self._analyze_communication_style(interaction_context)
                interaction_quality = await self._assess_interaction_quality(interaction_context)
            
            # 감정적 공감 분석
            emotional_empathy = await self._analyze_emotional_empathy(interaction_context)
            
            # 사회적 거리감 분석
            social_distance = await self._analyze_social_distance(interaction_context)
            
            # 협력 수준 분석
            cooperation_level = await self._analyze_cooperation_level(interaction_context)
            
            # 최적화 제안 생성
            optimization_suggestions = await self._generate_optimization_suggestions(
                interaction_quality, emotional_empathy, social_distance, cooperation_level
            )
            
            # 인간 상호작용 최적화 생성
            optimization = HumanInteractionOptimization(
                optimization_id=f"optimization_{int(time.time() * 1000)}",
                interaction_type=interaction_type,
                participants=participants,
                communication_style=communication_style,
                emotional_empathy=emotional_empathy,
                social_distance=social_distance,
                cooperation_level=cooperation_level,
                interaction_quality=interaction_quality,
                optimization_suggestions=optimization_suggestions,
                created_at=datetime.now()
            )
            
            self.human_interaction_optimizations.append(optimization)
            
            logger.info(f"인간 상호작용 최적화 완료: {optimization.optimization_id}")
            return optimization
            
        except Exception as e:
            logger.error(f"인간 상호작용 최적화 실패: {e}")
            return await self._create_empty_human_interaction_optimization()
    
    async def adapt_socially(self, environment_context: Dict[str, Any]) -> SocialAdaptation:
        """사회적 적응"""
        try:
            logger.info("사회적 적응 시작")
            
            # 환경 타입 분석
            environment_type = await self._analyze_environment_type(environment_context)
            
            # 적응 전략 개발
            adaptation_strategy = await self._develop_adaptation_strategy(environment_context)
            
            # 역할 인식
            role_recognition = await self._recognize_role(environment_context)
            
            # 사회적 학습
            social_learning = await self._identify_social_learning(environment_context)
            
            # 사회적 성장 분석
            social_growth = await self._analyze_social_growth(environment_context)
            
            # 적응 속도 분석
            adaptation_speed = await self._analyze_adaptation_speed(environment_context)
            
            # 적응 효과성 분석
            adaptation_effectiveness = await self._analyze_adaptation_effectiveness(
                adaptation_strategy, environment_context
            )
            
            # 사회적 적응 생성
            adaptation = SocialAdaptation(
                adaptation_id=f"adaptation_{int(time.time() * 1000)}",
                environment_type=environment_type,
                adaptation_strategy=adaptation_strategy,
                role_recognition=role_recognition,
                social_learning=social_learning,
                social_growth=social_growth,
                adaptation_speed=adaptation_speed,
                adaptation_effectiveness=adaptation_effectiveness,
                created_at=datetime.now()
            )
            
            self.social_adaptations.append(adaptation)
            
            logger.info(f"사회적 적응 완료: {adaptation.adaptation_id}")
            return adaptation
            
        except Exception as e:
            logger.error(f"사회적 적응 실패: {e}")
            return await self._create_empty_social_adaptation()
    
    async def collaborate_and_cooperate(self, collaboration_context: Dict[str, Any]) -> CollaborationCooperation:
        """협력 및 협업"""
        try:
            logger.info("협력 및 협업 시작")
            
            # 협력 타입 분석
            collaboration_type = await self._analyze_collaboration_type(collaboration_context)
            
            # 참여자 식별
            participants = await self._identify_collaboration_participants(collaboration_context)
            
            # 팀워크 효율성 분석
            teamwork_efficiency = await self._analyze_teamwork_efficiency(collaboration_context)
            
            # 갈등 해결 능력 분석
            conflict_resolution = await self._analyze_conflict_resolution(collaboration_context)
            
            # 의사소통 효과성 분석
            communication_effectiveness = await self._analyze_communication_effectiveness(collaboration_context)
            
            # 리더십 적절성 분석
            leadership_appropriateness = await self._analyze_leadership_appropriateness(collaboration_context)
            
            # 협력 품질 분석
            collaboration_quality = await self._analyze_collaboration_quality(
                teamwork_efficiency, conflict_resolution, communication_effectiveness, leadership_appropriateness
            )
            
            # 협력 및 협업 생성
            collaboration = CollaborationCooperation(
                collaboration_id=f"collaboration_{int(time.time() * 1000)}",
                collaboration_type=collaboration_type,
                participants=participants,
                teamwork_efficiency=teamwork_efficiency,
                conflict_resolution=conflict_resolution,
                communication_effectiveness=communication_effectiveness,
                leadership_appropriateness=leadership_appropriateness,
                collaboration_quality=collaboration_quality,
                created_at=datetime.now()
            )
            
            self.collaboration_cooperations.append(collaboration)
            
            logger.info(f"협력 및 협업 완료: {collaboration.collaboration_id}")
            return collaboration
            
        except Exception as e:
            logger.error(f"협력 및 협업 실패: {e}")
            return await self._create_empty_collaboration_cooperation()
    
    async def get_integrated_social_intelligence_score(self) -> float:
        """통합 사회적 지능 점수 계산"""
        try:
            scores = []
            
            # 사회적 맥락 이해 점수
            if self.social_context_understandings:
                context_scores = [u.understanding_confidence for u in self.social_context_understandings]
                scores.append(statistics.mean(context_scores) * self.integration_weights["social_context_understanding"])
            
            # 인간 상호작용 최적화 점수
            if self.human_interaction_optimizations:
                interaction_scores = [o.interaction_quality for o in self.human_interaction_optimizations]
                scores.append(statistics.mean(interaction_scores) * self.integration_weights["human_interaction_optimization"])
            
            # 사회적 적응 점수
            if self.social_adaptations:
                adaptation_scores = [a.adaptation_effectiveness for a in self.social_adaptations]
                scores.append(statistics.mean(adaptation_scores) * self.integration_weights["social_adaptation"])
            
            # 협력 및 협업 점수
            if self.collaboration_cooperations:
                collaboration_scores = [c.collaboration_quality for c in self.collaboration_cooperations]
                scores.append(statistics.mean(collaboration_scores) * self.integration_weights["collaboration_cooperation"])
            
            # 통합 점수 계산
            if scores:
                integrated_score = sum(scores)
                return min(1.0, max(0.0, integrated_score))
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"통합 사회적 지능 점수 계산 실패: {e}")
            return 0.5
    
    async def get_social_maturity_level(self) -> SocialMaturityLevel:
        """사회적 성숙도 수준 계산"""
        try:
            integrated_score = await self.get_integrated_social_intelligence_score()
            
            if integrated_score >= self.social_maturity_thresholds["expert"]:
                return SocialMaturityLevel.EXPERT
            elif integrated_score >= self.social_maturity_thresholds["advanced"]:
                return SocialMaturityLevel.ADVANCED
            elif integrated_score >= self.social_maturity_thresholds["intermediate"]:
                return SocialMaturityLevel.INTERMEDIATE
            else:
                return SocialMaturityLevel.BEGINNER
                
        except Exception as e:
            logger.error(f"사회적 성숙도 수준 계산 실패: {e}")
            return SocialMaturityLevel.BEGINNER
    
    # Helper methods for analysis
    async def _analyze_context_type(self, context: Dict[str, Any]) -> str:
        """맥락 타입 분석"""
        context_text = str(context).lower()
        
        if any(word in context_text for word in ["회의", "업무", "프로젝트"]):
            return "전문적"
        elif any(word in context_text for word in ["친구", "가족", "개인"]):
            return "개인적"
        elif any(word in context_text for word in ["문화", "전통", "가치"]):
            return "문화적"
        else:
            return "일반적"
    
    async def _analyze_social_situation(self, context: Dict[str, Any]) -> str:
        """사회적 상황 분석"""
        context_text = str(context).lower()
        
        if any(word in context_text for word in ["갈등", "문제", "어려움"]):
            return "갈등 상황"
        elif any(word in context_text for word in ["협력", "협업", "팀워크"]):
            return "협력 상황"
        elif any(word in context_text for word in ["학습", "교육", "성장"]):
            return "학습 상황"
        else:
            return "일반 상황"
    
    async def _analyze_cultural_factors(self, context: Dict[str, Any]) -> List[str]:
        """문화적 요소 분석"""
        cultural_factors = []
        context_text = str(context).lower()
        
        if any(word in context_text for word in ["한국", "한국어", "한국문화"]):
            cultural_factors.append("한국문화")
        if any(word in context_text for word in ["서양", "영어", "서양문화"]):
            cultural_factors.append("서양문화")
        if any(word in context_text for word in ["전통", "예의", "규범"]):
            cultural_factors.append("전통문화")
        
        return cultural_factors if cultural_factors else ["일반문화"]
    
    async def _analyze_power_dynamics(self, context: Dict[str, Any]) -> Dict[str, float]:
        """권력 역학 분석"""
        power_dynamics = {}
        context_text = str(context).lower()
        
        # 기본 권력 역학 설정
        if "상사" in context_text or "관리자" in context_text:
            power_dynamics["관리자"] = 0.8
            power_dynamics["직원"] = 0.2
        elif "교사" in context_text or "학생" in context_text:
            power_dynamics["교사"] = 0.7
            power_dynamics["학생"] = 0.3
        else:
            power_dynamics["평등"] = 0.5
        
        return power_dynamics
    
    async def _analyze_social_norms(self, context: Dict[str, Any]) -> List[str]:
        """사회적 규범 분석"""
        social_norms = ["상호 존중", "적절한 거리감"]
        context_text = str(context).lower()
        
        if "업무" in context_text:
            social_norms.extend(["전문성", "효율성"])
        if "개인" in context_text:
            social_norms.extend(["친밀감", "공감"])
        
        return social_norms
    
    async def _analyze_communication_style(self, context: Dict[str, Any]) -> str:
        """의사소통 스타일 분석"""
        context_text = str(context).lower()
        
        if any(word in context_text for word in ["공식", "업무", "회의"]):
            return "공식적"
        elif any(word in context_text for word in ["친구", "가족", "개인"]):
            return "비공식적"
        else:
            return "일반적"
    
    async def _analyze_relationship_patterns(self, context: Dict[str, Any]) -> Dict[str, str]:
        """관계 패턴 분석"""
        patterns = {}
        context_text = str(context).lower()
        
        if "상사" in context_text:
            patterns["관계유형"] = "상하관계"
        elif "동료" in context_text:
            patterns["관계유형"] = "동등관계"
        elif "친구" in context_text:
            patterns["관계유형"] = "친밀관계"
        else:
            patterns["관계유형"] = "일반관계"
        
        return patterns
    
    async def _calculate_understanding_confidence(self, context_type: str, social_situation: str, 
                                                cultural_factors: List[str], power_dynamics: Dict[str, float]) -> float:
        """이해 신뢰도 계산"""
        confidence = 0.5
        
        # 맥락 타입에 따른 가중치
        if context_type == "전문적":
            confidence += 0.1
        elif context_type == "개인적":
            confidence += 0.1
        
        # 사회적 상황에 따른 가중치
        if social_situation == "협력 상황":
            confidence += 0.1
        
        # 문화적 요소에 따른 가중치
        if cultural_factors:
            confidence += 0.1
        
        # 권력 역학에 따른 가중치
        if power_dynamics:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    # Additional helper methods for other analyses
    async def _analyze_interaction_type(self, context: Dict[str, Any]) -> str:
        """상호작용 타입 분석"""
        context_text = str(context).lower()
        
        if any(word in context_text for word in ["대화", "소통"]):
            return "대화"
        elif any(word in context_text for word in ["협력", "협업"]):
            return "협력"
        elif any(word in context_text for word in ["갈등", "문제"]):
            return "갈등해결"
        else:
            return "일반적"
    
    async def _identify_participants(self, context: Dict[str, Any]) -> List[str]:
        """참여자 식별"""
        participants = []
        context_text = str(context).lower()
        
        if "사용자" in context_text:
            participants.append("사용자")
        if "DuRi" in context_text or "AI" in context_text:
            participants.append("DuRi")
        
        return participants if participants else ["참여자"]
    
    async def _assess_interaction_quality(self, context: Dict[str, Any]) -> float:
        """상호작용 품질 평가"""
        quality = 0.5
        context_text = str(context).lower()
        
        if any(word in context_text for word in ["협력", "협업", "팀워크"]):
            quality += 0.2
        if any(word in context_text for word in ["공감", "이해", "존중"]):
            quality += 0.2
        
        return min(1.0, quality)
    
    async def _analyze_emotional_empathy(self, context: Dict[str, Any]) -> float:
        """감정적 공감 분석"""
        empathy = 0.5
        context_text = str(context).lower()
        
        if any(word in context_text for word in ["공감", "이해", "감정"]):
            empathy += 0.3
        if any(word in context_text for word in ["슬픔", "기쁨", "분노"]):
            empathy += 0.2
        
        return min(1.0, empathy)
    
    async def _analyze_social_distance(self, context: Dict[str, Any]) -> float:
        """사회적 거리감 분석"""
        distance = 0.5
        context_text = str(context).lower()
        
        if any(word in context_text for word in ["친구", "가족", "친밀"]):
            distance -= 0.3
        elif any(word in context_text for word in ["공식", "업무", "회의"]):
            distance += 0.3
        
        return max(0.0, min(1.0, distance))
    
    async def _analyze_cooperation_level(self, context: Dict[str, Any]) -> float:
        """협력 수준 분석"""
        cooperation = 0.5
        context_text = str(context).lower()
        
        if any(word in context_text for word in ["협력", "협업", "팀워크"]):
            cooperation += 0.3
        if any(word in context_text for word in ["갈등", "대립", "문제"]):
            cooperation -= 0.2
        
        return max(0.0, min(1.0, cooperation))
    
    async def _generate_optimization_suggestions(self, interaction_quality: float, emotional_empathy: float, 
                                               social_distance: float, cooperation_level: float) -> List[str]:
        """최적화 제안 생성"""
        suggestions = []
        
        if interaction_quality < 0.7:
            suggestions.append("상호작용 품질 향상을 위한 의사소통 개선")
        
        if emotional_empathy < 0.6:
            suggestions.append("감정적 공감 능력 향상")
        
        if social_distance > 0.7:
            suggestions.append("사회적 거리감 조절을 통한 친밀감 증진")
        
        if cooperation_level < 0.6:
            suggestions.append("협력 수준 향상을 위한 팀워크 강화")
        
        return suggestions if suggestions else ["현재 상태 유지"]
    
    # Additional helper methods for social adaptation
    async def _analyze_environment_type(self, context: Dict[str, Any]) -> str:
        """환경 타입 분석"""
        context_text = str(context).lower()
        
        if any(word in context_text for word in ["업무", "회사", "직장"]):
            return "업무환경"
        elif any(word in context_text for word in ["학교", "교육", "학습"]):
            return "교육환경"
        elif any(word in context_text for word in ["가족", "친구", "개인"]):
            return "개인환경"
        else:
            return "일반환경"
    
    async def _develop_adaptation_strategy(self, context: Dict[str, Any]) -> str:
        """적응 전략 개발"""
        context_text = str(context).lower()
        
        if "새로운" in context_text or "변화" in context_text:
            return "점진적 적응 전략"
        elif "갈등" in context_text or "문제" in context_text:
            return "갈등 해결 전략"
        else:
            return "일반 적응 전략"
    
    async def _recognize_role(self, context: Dict[str, Any]) -> str:
        """역할 인식"""
        context_text = str(context).lower()
        
        if "리더" in context_text or "관리자" in context_text:
            return "리더"
        elif "팀원" in context_text or "참여자" in context_text:
            return "팀원"
        else:
            return "일반 참여자"
    
    async def _identify_social_learning(self, context: Dict[str, Any]) -> List[str]:
        """사회적 학습 식별"""
        learning = []
        context_text = str(context).lower()
        
        if "의사소통" in context_text:
            learning.append("의사소통 기술")
        if "협력" in context_text:
            learning.append("협력 기술")
        if "갈등해결" in context_text:
            learning.append("갈등 해결 기술")
        
        return learning if learning else ["일반적 사회적 학습"]
    
    async def _analyze_social_growth(self, context: Dict[str, Any]) -> float:
        """사회적 성장 분석"""
        growth = 0.5
        context_text = str(context).lower()
        
        if any(word in context_text for word in ["성장", "발전", "향상"]):
            growth += 0.3
        if any(word in context_text for word in ["학습", "경험", "이해"]):
            growth += 0.2
        
        return min(1.0, growth)
    
    async def _analyze_adaptation_speed(self, context: Dict[str, Any]) -> float:
        """적응 속도 분석"""
        speed = 0.5
        context_text = str(context).lower()
        
        if any(word in context_text for word in ["빠른", "신속한", "즉시"]):
            speed += 0.3
        elif any(word in context_text for word in ["점진적", "천천히", "단계적"]):
            speed -= 0.2
        
        return max(0.0, min(1.0, speed))
    
    async def _analyze_adaptation_effectiveness(self, strategy: str, context: Dict[str, Any]) -> float:
        """적응 효과성 분석"""
        effectiveness = 0.5
        
        if "점진적" in strategy:
            effectiveness += 0.2
        if "갈등 해결" in strategy:
            effectiveness += 0.2
        
        return min(1.0, effectiveness)
    
    # Additional helper methods for collaboration
    async def _analyze_collaboration_type(self, context: Dict[str, Any]) -> str:
        """협력 타입 분석"""
        context_text = str(context).lower()
        
        if any(word in context_text for word in ["프로젝트", "팀워크"]):
            return "프로젝트 협력"
        elif any(word in context_text for word in ["문제해결", "갈등해결"]):
            return "문제해결 협력"
        else:
            return "일반 협력"
    
    async def _identify_collaboration_participants(self, context: Dict[str, Any]) -> List[str]:
        """협력 참여자 식별"""
        participants = []
        context_text = str(context).lower()
        
        if "팀" in context_text:
            participants.append("팀원들")
        if "관리자" in context_text:
            participants.append("관리자")
        if "사용자" in context_text:
            participants.append("사용자")
        
        return participants if participants else ["참여자들"]
    
    async def _analyze_teamwork_efficiency(self, context: Dict[str, Any]) -> float:
        """팀워크 효율성 분석"""
        efficiency = 0.5
        context_text = str(context).lower()
        
        if any(word in context_text for word in ["효율적", "성공적", "좋은"]):
            efficiency += 0.3
        if any(word in context_text for word in ["팀워크", "협력", "협업"]):
            efficiency += 0.2
        
        return min(1.0, efficiency)
    
    async def _analyze_conflict_resolution(self, context: Dict[str, Any]) -> float:
        """갈등 해결 능력 분석"""
        resolution = 0.5
        context_text = str(context).lower()
        
        if any(word in context_text for word in ["갈등해결", "문제해결", "화해"]):
            resolution += 0.3
        if any(word in context_text for word in ["대화", "소통", "이해"]):
            resolution += 0.2
        
        return min(1.0, resolution)
    
    async def _analyze_communication_effectiveness(self, context: Dict[str, Any]) -> float:
        """의사소통 효과성 분석"""
        effectiveness = 0.5
        context_text = str(context).lower()
        
        if any(word in context_text for word in ["효과적", "명확한", "좋은"]):
            effectiveness += 0.3
        if any(word in context_text for word in ["의사소통", "소통", "대화"]):
            effectiveness += 0.2
        
        return min(1.0, effectiveness)
    
    async def _analyze_leadership_appropriateness(self, context: Dict[str, Any]) -> float:
        """리더십 적절성 분석"""
        appropriateness = 0.5
        context_text = str(context).lower()
        
        if any(word in context_text for word in ["리더", "관리자", "지도자"]):
            appropriateness += 0.3
        if any(word in context_text for word in ["적절한", "효과적인", "좋은"]):
            appropriateness += 0.2
        
        return min(1.0, appropriateness)
    
    async def _analyze_collaboration_quality(self, teamwork_efficiency: float, conflict_resolution: float,
                                           communication_effectiveness: float, leadership_appropriateness: float) -> float:
        """협력 품질 분석"""
        quality = (teamwork_efficiency + conflict_resolution + communication_effectiveness + leadership_appropriateness) / 4
        return min(1.0, quality)
    
    # Empty object creation methods
    async def _create_empty_social_context_understanding(self) -> SocialContextUnderstanding:
        """빈 사회적 맥락 이해 생성"""
        return SocialContextUnderstanding(
            understanding_id=f"empty_understanding_{int(time.time() * 1000)}",
            context_type="일반적",
            social_situation="일반 상황",
            cultural_factors=["일반문화"],
            power_dynamics={"평등": 0.5},
            social_norms=["상호 존중", "적절한 거리감"],
            communication_style="일반적",
            relationship_patterns={"관계유형": "일반관계"},
            understanding_confidence=0.5,
            created_at=datetime.now()
        )
    
    async def _create_empty_human_interaction_optimization(self) -> HumanInteractionOptimization:
        """빈 인간 상호작용 최적화 생성"""
        return HumanInteractionOptimization(
            optimization_id=f"empty_optimization_{int(time.time() * 1000)}",
            interaction_type="일반적",
            participants=["참여자"],
            communication_style="일반적",
            emotional_empathy=0.5,
            social_distance=0.5,
            cooperation_level=0.5,
            interaction_quality=0.5,
            optimization_suggestions=["현재 상태 유지"],
            created_at=datetime.now()
        )
    
    async def _create_empty_social_adaptation(self) -> SocialAdaptation:
        """빈 사회적 적응 생성"""
        return SocialAdaptation(
            adaptation_id=f"empty_adaptation_{int(time.time() * 1000)}",
            environment_type="일반환경",
            adaptation_strategy="일반 적응 전략",
            role_recognition="일반 참여자",
            social_learning=["일반적 사회적 학습"],
            social_growth=0.5,
            adaptation_speed=0.5,
            adaptation_effectiveness=0.5,
            created_at=datetime.now()
        )
    
    async def _create_empty_collaboration_cooperation(self) -> CollaborationCooperation:
        """빈 협력 및 협업 생성"""
        return CollaborationCooperation(
            collaboration_id=f"empty_collaboration_{int(time.time() * 1000)}",
            collaboration_type="일반 협력",
            participants=["참여자들"],
            teamwork_efficiency=0.5,
            conflict_resolution=0.5,
            communication_effectiveness=0.5,
            leadership_appropriateness=0.5,
            collaboration_quality=0.5,
            created_at=datetime.now()
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""
        return {
            "system_name": "통합 사회적 지능 시스템",
            "version": "1.0.0",
            "status": "정상 운영",
            "total_context_understandings": len(self.social_context_understandings),
            "total_interaction_optimizations": len(self.human_interaction_optimizations),
            "total_social_adaptations": len(self.social_adaptations),
            "total_collaborations": len(self.collaboration_cooperations),
            "integration_weights": self.integration_weights,
            "social_maturity_thresholds": self.social_maturity_thresholds,
            "created_at": datetime.now().isoformat()
        }

async def test_integrated_social_intelligence_system():
    """통합 사회적 지능 시스템 테스트"""
    try:
        logger.info("🧠 통합 사회적 지능 시스템 테스트 시작")
        
        # 시스템 초기화
        system = IntegratedSocialIntelligenceSystem()
        
        # 테스트 컨텍스트
        test_context = {
            "situation": "팀 프로젝트 회의에서 새로운 아이디어를 제안하는 상황",
            "participants": ["팀원들", "관리자"],
            "environment": "업무환경",
            "communication_style": "공식적"
        }
        
        # 1. 사회적 맥락 이해 테스트
        logger.info("1. 사회적 맥락 이해 테스트")
        understanding = await system.understand_social_context(test_context)
        logger.info(f"   - 이해 ID: {understanding.understanding_id}")
        logger.info(f"   - 맥락 타입: {understanding.context_type}")
        logger.info(f"   - 이해 신뢰도: {understanding.understanding_confidence:.2f}")
        
        # 2. 인간 상호작용 최적화 테스트
        logger.info("2. 인간 상호작용 최적화 테스트")
        optimization = await system.optimize_human_interaction(test_context)
        logger.info(f"   - 최적화 ID: {optimization.optimization_id}")
        logger.info(f"   - 상호작용 품질: {optimization.interaction_quality:.2f}")
        logger.info(f"   - 감정적 공감: {optimization.emotional_empathy:.2f}")
        
        # 3. 사회적 적응 테스트
        logger.info("3. 사회적 적응 테스트")
        adaptation = await system.adapt_socially(test_context)
        logger.info(f"   - 적응 ID: {adaptation.adaptation_id}")
        logger.info(f"   - 적응 효과성: {adaptation.adaptation_effectiveness:.2f}")
        logger.info(f"   - 사회적 성장: {adaptation.social_growth:.2f}")
        
        # 4. 협력 및 협업 테스트
        logger.info("4. 협력 및 협업 테스트")
        collaboration = await system.collaborate_and_cooperate(test_context)
        logger.info(f"   - 협력 ID: {collaboration.collaboration_id}")
        logger.info(f"   - 협력 품질: {collaboration.collaboration_quality:.2f}")
        logger.info(f"   - 팀워크 효율성: {collaboration.teamwork_efficiency:.2f}")
        
        # 5. 통합 사회적 지능 점수 계산
        logger.info("5. 통합 사회적 지능 점수 계산")
        integrated_score = await system.get_integrated_social_intelligence_score()
        logger.info(f"   - 통합 점수: {integrated_score:.2f}")
        
        # 6. 사회적 성숙도 수준 계산
        logger.info("6. 사회적 성숙도 수준 계산")
        maturity_level = await system.get_social_maturity_level()
        logger.info(f"   - 성숙도 수준: {maturity_level.value}")
        
        # 7. 시스템 상태 확인
        logger.info("7. 시스템 상태 확인")
        status = system.get_system_status()
        logger.info(f"   - 시스템 상태: {status['status']}")
        logger.info(f"   - 총 맥락 이해: {status['total_context_understandings']}")
        logger.info(f"   - 총 상호작용 최적화: {status['total_interaction_optimizations']}")
        logger.info(f"   - 총 사회적 적응: {status['total_social_adaptations']}")
        logger.info(f"   - 총 협력: {status['total_collaborations']}")
        
        logger.info("🎉 통합 사회적 지능 시스템 테스트 완료!")
        
        return {
            "understanding": understanding,
            "optimization": optimization,
            "adaptation": adaptation,
            "collaboration": collaboration,
            "integrated_score": integrated_score,
            "maturity_level": maturity_level,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"통합 사회적 지능 시스템 테스트 실패: {e}")
        return None

if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 테스트 실행
    result = asyncio.run(test_integrated_social_intelligence_system())
    
    if result:
        print("\n🎉 테스트 결과 요약:")
        print(f"   - 통합 사회적 지능 점수: {result['integrated_score']:.2f}")
        print(f"   - 사회적 성숙도 수준: {result['maturity_level'].value}")
        print(f"   - 총 맥락 이해: {result['status']['total_context_understandings']}")
        print(f"   - 총 상호작용 최적화: {result['status']['total_interaction_optimizations']}")
        print(f"   - 총 사회적 적응: {result['status']['total_social_adaptations']}")
        print(f"   - 총 협력: {result['status']['total_collaborations']}")
    else:
        print("❌ 테스트 실패")
