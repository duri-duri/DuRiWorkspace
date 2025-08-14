#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 30일 진화 계획 - Day 3: 직관적 사고 시스템

이 모듈은 DuRi가 논리적 분석을 넘어선 직관적 판단 능력을 구현합니다.
패턴 인식 기반 직관 시스템, 빠른 판단 메커니즘, 경험 기반 직관 개발, 직관적 통찰력 시스템을 구현합니다.

주요 기능:
- 패턴 인식 기반 직관 시스템
- 빠른 판단 메커니즘
- 경험 기반 직관 개발
- 직관적 통찰력 시스템
- 직관적 사고 프로세스
"""

import asyncio
import json
import logging
import time
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from collections import defaultdict, deque

# 기존 시스템들 import
try:
    from inner_thinking_system import InnerThinkingSystem, ThoughtDepth
    from emotional_thinking_system import EmotionalThinkingSystem, EmotionalState
    from duri_thought_flow import DuRiThoughtFlow
    from phase_omega_integration import DuRiPhaseOmega
except ImportError as e:
    logging.warning(f"일부 기존 시스템 import 실패: {e}")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntuitiveThinkingMode(Enum):
    """직관적 사고 모드"""
    PATTERN_RECOGNITION = "pattern_recognition"    # 패턴 인식
    RAPID_JUDGMENT = "rapid_judgment"              # 빠른 판단
    EXPERIENCE_BASED = "experience_based"          # 경험 기반
    INSIGHT_GENERATION = "insight_generation"      # 통찰 생성
    SYNTHETIC_THINKING = "synthetic_thinking"      # 종합적 사고


class IntuitiveConfidence(Enum):
    """직관적 신뢰도"""
    VERY_LOW = "very_low"       # 매우 낮음 (0.0-0.2)
    LOW = "low"                 # 낮음 (0.2-0.4)
    MODERATE = "moderate"       # 보통 (0.4-0.6)
    HIGH = "high"               # 높음 (0.6-0.8)
    VERY_HIGH = "very_high"     # 매우 높음 (0.8-1.0)


class PatternType(Enum):
    """패턴 유형"""
    SEQUENTIAL = "sequential"           # 순차적 패턴
    RELATIONAL = "relational"           # 관계적 패턴
    TEMPORAL = "temporal"               # 시간적 패턴
    SPATIAL = "spatial"                 # 공간적 패턴
    CAUSAL = "causal"                   # 인과적 패턴
    EMERGENT = "emergent"               # 창발적 패턴


@dataclass
class IntuitivePattern:
    """직관적 패턴"""
    pattern_id: str
    pattern_type: PatternType
    pattern_data: Dict[str, Any]
    confidence: float  # 0.0-1.0
    frequency: int = 1
    last_seen: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntuitiveJudgment:
    """직관적 판단"""
    judgment_id: str
    situation: Dict[str, Any]
    judgment: str
    confidence: IntuitiveConfidence
    reasoning: str
    patterns_used: List[str] = field(default_factory=list)
    response_time: float = 0.0  # 초 단위
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class IntuitiveInsight:
    """직관적 통찰"""
    insight_id: str
    insight: str
    confidence: float  # 0.0-1.0
    pattern_based: bool = True
    experience_based: bool = False
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ExperienceMemory:
    """경험 기억"""
    memory_id: str
    experience_type: str
    experience_data: Dict[str, Any]
    outcome: str
    success_rate: float  # 0.0-1.0
    frequency: int = 1
    last_accessed: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntuitiveThinkingResult:
    """직관적 사고 결과"""
    process_id: str
    patterns_recognized: List[IntuitivePattern]
    judgments_made: List[IntuitiveJudgment]
    insights_generated: List[IntuitiveInsight]
    experiences_accessed: List[ExperienceMemory]
    average_confidence: float
    response_time: float
    success: bool = True
    error_message: Optional[str] = None


class IntuitiveThinkingSystem:
    """직관적 사고 시스템"""
    
    def __init__(self):
        # 기존 시스템들과의 통합
        self.inner_thinking = None
        self.emotional_thinking = None
        self.thought_flow = None
        self.phase_omega = None
        
        # 직관적 사고 시스템 데이터
        self.intuitive_patterns: List[IntuitivePattern] = []
        self.intuitive_judgments: List[IntuitiveJudgment] = []
        self.intuitive_insights: List[IntuitiveInsight] = []
        self.experience_memories: List[ExperienceMemory] = []
        self.pattern_database: Dict[str, Any] = {}
        
        # 직관적 사고 설정
        self.intuitive_thresholds = {
            "confidence_low": 0.3,
            "confidence_moderate": 0.6,
            "confidence_high": 0.8,
            "response_time_fast": 0.5,  # 초
            "response_time_moderate": 2.0,  # 초
            "pattern_recognition_threshold": 0.7
        }
        
        # 직관적 사고 가중치
        self.intuitive_weights = {
            IntuitiveThinkingMode.PATTERN_RECOGNITION: 0.3,
            IntuitiveThinkingMode.RAPID_JUDGMENT: 0.25,
            IntuitiveThinkingMode.EXPERIENCE_BASED: 0.2,
            IntuitiveThinkingMode.INSIGHT_GENERATION: 0.15,
            IntuitiveThinkingMode.SYNTHETIC_THINKING: 0.1
        }
        
        # 패턴 인식 시스템
        self.pattern_recognition_engine = {}
        self.pattern_matching_algorithms = {}
        
        # 빠른 판단 메커니즘
        self.rapid_judgment_cache = {}
        self.judgment_heuristics = {}
        
        # 경험 기반 직관
        self.experience_database = {}
        self.experience_retrieval_system = {}
        
        # 직관적 통찰력 시스템
        self.insight_generation_engine = {}
        self.insight_validation_system = {}
        
        logger.info("직관적 사고 시스템 초기화 완료")
        
        # 기존 시스템들과의 통합 초기화
        self._initialize_integration()
    
    def _initialize_integration(self):
        """기존 시스템들과의 통합 초기화"""
        try:
            # 내적 사고 시스템 통합
            if 'InnerThinkingSystem' in globals():
                self.inner_thinking = InnerThinkingSystem()
                logger.info("내적 사고 시스템 통합 완료")
            
            # 감정적 사고 시스템 통합
            if 'EmotionalThinkingSystem' in globals():
                self.emotional_thinking = EmotionalThinkingSystem()
                logger.info("감정적 사고 시스템 통합 완료")
            
            # DuRiThoughtFlow 통합
            if 'DuRiThoughtFlow' in globals():
                self.thought_flow = DuRiThoughtFlow({}, {})
                logger.info("DuRiThoughtFlow 통합 완료")
            
            # Phase Omega 통합
            if 'DuRiPhaseOmega' in globals():
                self.phase_omega = DuRiPhaseOmega()
                logger.info("Phase Omega 통합 완료")
                
        except Exception as e:
            logger.warning(f"기존 시스템 통합 중 오류 발생: {e}")
    
    async def think_intuitively(self, situation: Dict[str, Any]) -> IntuitiveThinkingResult:
        """직관적 사고 실행"""
        logger.info(f"=== 직관적 사고 시작 ===")
        
        start_time = datetime.now()
        process_id = f"intuitive_thought_{start_time.strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # 1. 패턴 인식
            patterns = await self._recognize_patterns(situation)
            
            # 2. 빠른 판단
            judgments = await self._make_rapid_judgments(situation, patterns)
            
            # 3. 경험 기반 직관
            experiences = await self._access_experience_memories(situation)
            
            # 4. 직관적 통찰 생성
            insights = await self._generate_intuitive_insights(situation, patterns, experiences)
            
            # 5. 종합적 직관적 사고
            synthetic_insights = await self._apply_synthetic_thinking(situation, patterns, judgments, insights)
            insights.extend(synthetic_insights)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 6. 결과 생성
            result = IntuitiveThinkingResult(
                process_id=process_id,
                patterns_recognized=patterns,
                judgments_made=judgments,
                insights_generated=insights,
                experiences_accessed=experiences,
                average_confidence=await self._calculate_average_confidence(patterns, judgments, insights),
                response_time=duration,
                success=True
            )
            
            # 7. 데이터 저장
            self.intuitive_patterns.extend(patterns)
            self.intuitive_judgments.extend(judgments)
            self.intuitive_insights.extend(insights)
            self.experience_memories.extend(experiences)
            
            logger.info(f"=== 직관적 사고 완료 - 소요시간: {duration:.2f}초, 패턴수: {len(patterns)}개 ===")
            return result
            
        except Exception as e:
            logger.error(f"직관적 사고 중 오류 발생: {e}")
            return IntuitiveThinkingResult(
                process_id=process_id,
                patterns_recognized=[],
                judgments_made=[],
                insights_generated=[],
                experiences_accessed=[],
                average_confidence=0.0,
                response_time=0.0,
                success=False,
                error_message=str(e)
            )
    
    async def _recognize_patterns(self, situation: Dict[str, Any]) -> List[IntuitivePattern]:
        """패턴 인식"""
        patterns = []
        
        # 1. 순차적 패턴 인식
        sequential_patterns = await self._recognize_sequential_patterns(situation)
        patterns.extend(sequential_patterns)
        
        # 2. 관계적 패턴 인식
        relational_patterns = await self._recognize_relational_patterns(situation)
        patterns.extend(relational_patterns)
        
        # 3. 시간적 패턴 인식
        temporal_patterns = await self._recognize_temporal_patterns(situation)
        patterns.extend(temporal_patterns)
        
        # 4. 공간적 패턴 인식
        spatial_patterns = await self._recognize_spatial_patterns(situation)
        patterns.extend(spatial_patterns)
        
        # 5. 인과적 패턴 인식
        causal_patterns = await self._recognize_causal_patterns(situation)
        patterns.extend(causal_patterns)
        
        # 6. 창발적 패턴 인식
        emergent_patterns = await self._recognize_emergent_patterns(situation)
        patterns.extend(emergent_patterns)
        
        return patterns
    
    async def _recognize_sequential_patterns(self, situation: Dict[str, Any]) -> List[IntuitivePattern]:
        """순차적 패턴 인식"""
        patterns = []
        situation_text = str(situation).lower()
        
        # 순차적 패턴 키워드
        sequential_keywords = ["단계", "과정", "순서", "진행", "발전", "진화", "성장"]
        
        for keyword in sequential_keywords:
            if keyword in situation_text:
                pattern = IntuitivePattern(
                    pattern_id=f"sequential_{len(self.intuitive_patterns)}",
                    pattern_type=PatternType.SEQUENTIAL,
                    pattern_data={"keyword": keyword, "context": situation},
                    confidence=0.7,
                    context={"pattern_type": "sequential"}
                )
                patterns.append(pattern)
        
        return patterns
    
    async def _recognize_relational_patterns(self, situation: Dict[str, Any]) -> List[IntuitivePattern]:
        """관계적 패턴 인식"""
        patterns = []
        situation_text = str(situation).lower()
        
        # 관계적 패턴 키워드
        relational_keywords = ["관계", "연결", "상호작용", "의존", "영향", "연관"]
        
        for keyword in relational_keywords:
            if keyword in situation_text:
                pattern = IntuitivePattern(
                    pattern_id=f"relational_{len(self.intuitive_patterns)}",
                    pattern_type=PatternType.RELATIONAL,
                    pattern_data={"keyword": keyword, "context": situation},
                    confidence=0.6,
                    context={"pattern_type": "relational"}
                )
                patterns.append(pattern)
        
        return patterns
    
    async def _recognize_temporal_patterns(self, situation: Dict[str, Any]) -> List[IntuitivePattern]:
        """시간적 패턴 인식"""
        patterns = []
        situation_text = str(situation).lower()
        
        # 시간적 패턴 키워드
        temporal_keywords = ["시간", "시기", "기간", "순간", "지속", "변화", "발전"]
        
        for keyword in temporal_keywords:
            if keyword in situation_text:
                pattern = IntuitivePattern(
                    pattern_id=f"temporal_{len(self.intuitive_patterns)}",
                    pattern_type=PatternType.TEMPORAL,
                    pattern_data={"keyword": keyword, "context": situation},
                    confidence=0.5,
                    context={"pattern_type": "temporal"}
                )
                patterns.append(pattern)
        
        return patterns
    
    async def _recognize_spatial_patterns(self, situation: Dict[str, Any]) -> List[IntuitivePattern]:
        """공간적 패턴 인식"""
        patterns = []
        situation_text = str(situation).lower()
        
        # 공간적 패턴 키워드
        spatial_keywords = ["공간", "위치", "배치", "구조", "형태", "모양", "배열"]
        
        for keyword in spatial_keywords:
            if keyword in situation_text:
                pattern = IntuitivePattern(
                    pattern_id=f"spatial_{len(self.intuitive_patterns)}",
                    pattern_type=PatternType.SPATIAL,
                    pattern_data={"keyword": keyword, "context": situation},
                    confidence=0.4,
                    context={"pattern_type": "spatial"}
                )
                patterns.append(pattern)
        
        return patterns
    
    async def _recognize_causal_patterns(self, situation: Dict[str, Any]) -> List[IntuitivePattern]:
        """인과적 패턴 인식"""
        patterns = []
        situation_text = str(situation).lower()
        
        # 인과적 패턴 키워드
        causal_keywords = ["원인", "결과", "영향", "효과", "결과", "발생", "유발"]
        
        for keyword in causal_keywords:
            if keyword in situation_text:
                pattern = IntuitivePattern(
                    pattern_id=f"causal_{len(self.intuitive_patterns)}",
                    pattern_type=PatternType.CAUSAL,
                    pattern_data={"keyword": keyword, "context": situation},
                    confidence=0.8,
                    context={"pattern_type": "causal"}
                )
                patterns.append(pattern)
        
        return patterns
    
    async def _recognize_emergent_patterns(self, situation: Dict[str, Any]) -> List[IntuitivePattern]:
        """창발적 패턴 인식"""
        patterns = []
        situation_text = str(situation).lower()
        
        # 창발적 패턴 키워드
        emergent_keywords = ["창발", "새로운", "혁신", "창조", "발견", "통찰", "깨달음"]
        
        for keyword in emergent_keywords:
            if keyword in situation_text:
                pattern = IntuitivePattern(
                    pattern_id=f"emergent_{len(self.intuitive_patterns)}",
                    pattern_type=PatternType.EMERGENT,
                    pattern_data={"keyword": keyword, "context": situation},
                    confidence=0.9,
                    context={"pattern_type": "emergent"}
                )
                patterns.append(pattern)
        
        return patterns
    
    async def _make_rapid_judgments(self, situation: Dict[str, Any], 
                                  patterns: List[IntuitivePattern]) -> List[IntuitiveJudgment]:
        """빠른 판단"""
        judgments = []
        
        # 1. 패턴 기반 빠른 판단
        pattern_judgments = await self._make_pattern_based_judgments(situation, patterns)
        judgments.extend(pattern_judgments)
        
        # 2. 경험 기반 빠른 판단
        experience_judgments = await self._make_experience_based_judgments(situation)
        judgments.extend(experience_judgments)
        
        # 3. 직관적 빠른 판단
        intuitive_judgments = await self._make_intuitive_judgments(situation)
        judgments.extend(intuitive_judgments)
        
        return judgments
    
    async def _make_pattern_based_judgments(self, situation: Dict[str, Any], 
                                          patterns: List[IntuitivePattern]) -> List[IntuitiveJudgment]:
        """패턴 기반 빠른 판단"""
        judgments = []
        
        for pattern in patterns:
            if pattern.confidence >= self.intuitive_thresholds["pattern_recognition_threshold"]:
                judgment_text = await self._generate_pattern_based_judgment(pattern, situation)
                
                judgment = IntuitiveJudgment(
                    judgment_id=f"pattern_judgment_{len(self.intuitive_judgments)}",
                    situation=situation,
                    judgment=judgment_text,
                    confidence=IntuitiveConfidence.HIGH if pattern.confidence >= 0.8 else IntuitiveConfidence.MODERATE,
                    reasoning=f"패턴 인식 기반: {pattern.pattern_type.value}",
                    patterns_used=[pattern.pattern_id],
                    response_time=0.1
                )
                judgments.append(judgment)
        
        return judgments
    
    async def _generate_pattern_based_judgment(self, pattern: IntuitivePattern, 
                                             situation: Dict[str, Any]) -> str:
        """패턴 기반 판단 생성"""
        pattern_judgments = {
            PatternType.SEQUENTIAL: "이 상황은 순차적 발전 과정을 보여준다.",
            PatternType.RELATIONAL: "이 상황은 복잡한 관계 구조를 가지고 있다.",
            PatternType.TEMPORAL: "이 상황은 시간적 변화의 패턴을 보여준다.",
            PatternType.SPATIAL: "이 상황은 공간적 구조의 패턴을 보여준다.",
            PatternType.CAUSAL: "이 상황은 명확한 인과 관계를 보여준다.",
            PatternType.EMERGENT: "이 상황은 새로운 창발적 패턴을 보여준다."
        }
        
        return pattern_judgments.get(pattern.pattern_type, "이 상황은 특정 패턴을 보여준다.")
    
    async def _make_experience_based_judgments(self, situation: Dict[str, Any]) -> List[IntuitiveJudgment]:
        """경험 기반 빠른 판단"""
        judgments = []
        
        # 상황과 유사한 경험 검색
        similar_experiences = await self._find_similar_experiences(situation)
        
        for experience in similar_experiences:
            judgment_text = f"이전 경험에 기반하여 {experience.outcome}을 예상한다."
            
            judgment = IntuitiveJudgment(
                judgment_id=f"experience_judgment_{len(self.intuitive_judgments)}",
                situation=situation,
                judgment=judgment_text,
                confidence=IntuitiveConfidence.MODERATE,
                reasoning=f"경험 기반: {experience.experience_type}",
                patterns_used=[],
                response_time=0.2
            )
            judgments.append(judgment)
        
        return judgments
    
    async def _make_intuitive_judgments(self, situation: Dict[str, Any]) -> List[IntuitiveJudgment]:
        """직관적 빠른 판단"""
        judgments = []
        
        # 상황 복잡성 기반 직관적 판단
        complexity = len(str(situation)) / 1000.0
        if complexity > 0.5:
            judgment_text = "이 상황은 복잡하지만 직관적으로 해결 가능하다."
        else:
            judgment_text = "이 상황은 직관적으로 명확하다."
        
        judgment = IntuitiveJudgment(
            judgment_id=f"intuitive_judgment_{len(self.intuitive_judgments)}",
            situation=situation,
            judgment=judgment_text,
            confidence=IntuitiveConfidence.HIGH,
            reasoning="직관적 판단",
            patterns_used=[],
            response_time=0.05
        )
        judgments.append(judgment)
        
        return judgments
    
    async def _access_experience_memories(self, situation: Dict[str, Any]) -> List[ExperienceMemory]:
        """경험 기억 접근"""
        experiences = []
        
        # 1. 유사한 경험 검색
        similar_experiences = await self._find_similar_experiences(situation)
        experiences.extend(similar_experiences)
        
        # 2. 성공한 경험 검색
        successful_experiences = await self._find_successful_experiences(situation)
        experiences.extend(successful_experiences)
        
        # 3. 실패한 경험 검색
        failed_experiences = await self._find_failed_experiences(situation)
        experiences.extend(failed_experiences)
        
        return experiences
    
    async def _find_similar_experiences(self, situation: Dict[str, Any]) -> List[ExperienceMemory]:
        """유사한 경험 검색"""
        experiences = []
        
        # 기본 경험 메모리 생성 (실제로는 더 정교한 검색 알고리즘 사용)
        if "문제" in str(situation):
            experience = ExperienceMemory(
                memory_id=f"experience_{len(self.experience_memories)}",
                experience_type="problem_solving",
                experience_data={"problem_type": "general"},
                outcome="successful_resolution",
                success_rate=0.8
            )
            experiences.append(experience)
        
        if "관계" in str(situation):
            experience = ExperienceMemory(
                memory_id=f"experience_{len(self.experience_memories) + 1}",
                experience_type="relationship_management",
                experience_data={"relationship_type": "general"},
                outcome="positive_interaction",
                success_rate=0.7
            )
            experiences.append(experience)
        
        return experiences
    
    async def _find_successful_experiences(self, situation: Dict[str, Any]) -> List[ExperienceMemory]:
        """성공한 경험 검색"""
        experiences = []
        
        # 성공 경험 메모리 생성
        experience = ExperienceMemory(
            memory_id=f"success_experience_{len(self.experience_memories)}",
            experience_type="success_pattern",
            experience_data={"success_factors": ["patience", "strategy", "adaptation"]},
            outcome="successful_outcome",
            success_rate=0.9
        )
        experiences.append(experience)
        
        return experiences
    
    async def _find_failed_experiences(self, situation: Dict[str, Any]) -> List[ExperienceMemory]:
        """실패한 경험 검색"""
        experiences = []
        
        # 실패 경험 메모리 생성
        experience = ExperienceMemory(
            memory_id=f"failed_experience_{len(self.experience_memories)}",
            experience_type="failure_pattern",
            experience_data={"failure_factors": ["haste", "lack_of_planning", "poor_communication"]},
            outcome="failed_outcome",
            success_rate=0.2
        )
        experiences.append(experience)
        
        return experiences
    
    async def _generate_intuitive_insights(self, situation: Dict[str, Any], 
                                         patterns: List[IntuitivePattern], 
                                         experiences: List[ExperienceMemory]) -> List[IntuitiveInsight]:
        """직관적 통찰 생성"""
        insights = []
        
        # 1. 패턴 기반 통찰
        pattern_insights = await self._generate_pattern_based_insights(patterns)
        insights.extend(pattern_insights)
        
        # 2. 경험 기반 통찰
        experience_insights = await self._generate_experience_based_insights(experiences)
        insights.extend(experience_insights)
        
        # 3. 상황 기반 통찰
        situation_insights = await self._generate_situation_based_insights(situation)
        insights.extend(situation_insights)
        
        return insights
    
    async def _generate_pattern_based_insights(self, patterns: List[IntuitivePattern]) -> List[IntuitiveInsight]:
        """패턴 기반 통찰 생성"""
        insights = []
        
        for pattern in patterns:
            if pattern.confidence >= 0.7:
                insight_text = await self._generate_pattern_insight_text(pattern)
                
                insight = IntuitiveInsight(
                    insight_id=f"pattern_insight_{len(self.intuitive_insights)}",
                    insight=insight_text,
                    confidence=pattern.confidence,
                    pattern_based=True,
                    experience_based=False,
                    context={"pattern_type": pattern.pattern_type.value}
                )
                insights.append(insight)
        
        return insights
    
    async def _generate_pattern_insight_text(self, pattern: IntuitivePattern) -> str:
        """패턴 통찰 텍스트 생성"""
        pattern_insights = {
            PatternType.SEQUENTIAL: "순차적 패턴은 발전과 성장의 자연스러운 과정을 보여준다.",
            PatternType.RELATIONAL: "관계적 패턴은 복잡한 상호작용의 본질을 드러낸다.",
            PatternType.TEMPORAL: "시간적 패턴은 변화와 발전의 리듬을 보여준다.",
            PatternType.SPATIAL: "공간적 패턴은 구조와 형태의 의미를 드러낸다.",
            PatternType.CAUSAL: "인과적 패턴은 원인과 결과의 연결을 보여준다.",
            PatternType.EMERGENT: "창발적 패턴은 새로운 가능성과 기회를 드러낸다."
        }
        
        return pattern_insights.get(pattern.pattern_type, "패턴은 상황의 본질을 드러낸다.")
    
    async def _generate_experience_based_insights(self, experiences: List[ExperienceMemory]) -> List[IntuitiveInsight]:
        """경험 기반 통찰 생성"""
        insights = []
        
        for experience in experiences:
            if experience.success_rate >= 0.7:
                insight_text = f"성공한 경험에서 {experience.outcome}의 핵심 요소를 발견했다."
            else:
                insight_text = f"실패한 경험에서 {experience.outcome}의 개선점을 발견했다."
            
            insight = IntuitiveInsight(
                insight_id=f"experience_insight_{len(self.intuitive_insights)}",
                insight=insight_text,
                confidence=experience.success_rate,
                pattern_based=False,
                experience_based=True,
                context={"experience_type": experience.experience_type}
            )
            insights.append(insight)
        
        return insights
    
    async def _generate_situation_based_insights(self, situation: Dict[str, Any]) -> List[IntuitiveInsight]:
        """상황 기반 통찰 생성"""
        insights = []
        
        situation_text = str(situation)
        
        if "복잡" in situation_text:
            insight_text = "복잡한 상황에서는 단순한 원칙을 적용하는 것이 효과적이다."
        elif "새로운" in situation_text:
            insight_text = "새로운 상황에서는 기존 경험을 창의적으로 적용해야 한다."
        elif "긴급" in situation_text:
            insight_text = "긴급한 상황에서는 빠른 직관적 판단이 중요하다."
        else:
            insight_text = "이 상황에서 직관적 통찰을 활용할 수 있다."
        
        insight = IntuitiveInsight(
            insight_id=f"situation_insight_{len(self.intuitive_insights)}",
            insight=insight_text,
            confidence=0.6,
            pattern_based=False,
            experience_based=False,
            context={"situation_type": "general"}
        )
        insights.append(insight)
        
        return insights
    
    async def _apply_synthetic_thinking(self, situation: Dict[str, Any], 
                                      patterns: List[IntuitivePattern], 
                                      judgments: List[IntuitiveJudgment], 
                                      insights: List[IntuitiveInsight]) -> List[IntuitiveInsight]:
        """종합적 직관적 사고"""
        synthetic_insights = []
        
        # 패턴과 통찰의 종합
        if patterns and insights:
            synthetic_insight = IntuitiveInsight(
                insight_id=f"synthetic_insight_{len(self.intuitive_insights)}",
                insight="패턴과 통찰의 종합을 통해 더 깊은 이해를 얻을 수 있다.",
                confidence=0.8,
                pattern_based=True,
                experience_based=True,
                context={"synthetic_type": "pattern_insight_integration"}
            )
            synthetic_insights.append(synthetic_insight)
        
        # 판단과 경험의 종합
        if judgments and len(judgments) > 1:
            synthetic_insight = IntuitiveInsight(
                insight_id=f"synthetic_insight_{len(self.intuitive_insights) + 1}",
                insight="다양한 판단의 종합을 통해 더 정확한 직관을 얻을 수 있다.",
                confidence=0.7,
                pattern_based=False,
                experience_based=True,
                context={"synthetic_type": "judgment_integration"}
            )
            synthetic_insights.append(synthetic_insight)
        
        return synthetic_insights
    
    async def _calculate_average_confidence(self, patterns: List[IntuitivePattern], 
                                          judgments: List[IntuitiveJudgment], 
                                          insights: List[IntuitiveInsight]) -> float:
        """평균 신뢰도 계산"""
        total_confidence = 0.0
        total_count = 0
        
        # 패턴 신뢰도
        for pattern in patterns:
            total_confidence += pattern.confidence
            total_count += 1
        
        # 판단 신뢰도
        for judgment in judgments:
            confidence_value = self._convert_confidence_enum_to_float(judgment.confidence)
            total_confidence += confidence_value
            total_count += 1
        
        # 통찰 신뢰도
        for insight in insights:
            total_confidence += insight.confidence
            total_count += 1
        
        return total_confidence / total_count if total_count > 0 else 0.0
    
    def _convert_confidence_enum_to_float(self, confidence: IntuitiveConfidence) -> float:
        """신뢰도 열거형을 float로 변환"""
        confidence_values = {
            IntuitiveConfidence.VERY_LOW: 0.1,
            IntuitiveConfidence.LOW: 0.3,
            IntuitiveConfidence.MODERATE: 0.5,
            IntuitiveConfidence.HIGH: 0.7,
            IntuitiveConfidence.VERY_HIGH: 0.9
        }
        return confidence_values.get(confidence, 0.5)
    
    async def get_intuitive_thinking_summary(self) -> Dict[str, Any]:
        """직관적 사고 요약 반환"""
        return {
            "total_patterns": len(self.intuitive_patterns),
            "total_judgments": len(self.intuitive_judgments),
            "total_insights": len(self.intuitive_insights),
            "total_experiences": len(self.experience_memories),
            "average_confidence": await self._calculate_average_confidence(
                self.intuitive_patterns, self.intuitive_judgments, self.intuitive_insights
            ),
            "pattern_distribution": self._get_pattern_distribution(),
            "confidence_distribution": self._get_confidence_distribution(),
            "recent_insights": [i.insight for i in self.intuitive_insights[-3:]] if self.intuitive_insights else []
        }
    
    def _get_pattern_distribution(self) -> Dict[str, int]:
        """패턴 분포 반환"""
        distribution = defaultdict(int)
        for pattern in self.intuitive_patterns:
            distribution[pattern.pattern_type.value] += 1
        return dict(distribution)
    
    def _get_confidence_distribution(self) -> Dict[str, int]:
        """신뢰도 분포 반환"""
        distribution = defaultdict(int)
        for judgment in self.intuitive_judgments:
            distribution[judgment.confidence.value] += 1
        return dict(distribution)


async def test_intuitive_thinking_system():
    """직관적 사고 시스템 테스트"""
    logger.info("=== 직관적 사고 시스템 테스트 시작 ===")
    
    system = IntuitiveThinkingSystem()
    
    # 1. 기본 직관적 사고 테스트
    logger.info("1. 기본 직관적 사고 테스트")
    situation1 = {"context": "문제 해결", "complexity": "높음", "urgency": "보통"}
    result1 = await system.think_intuitively(situation1)
    logger.info(f"기본 직관적 사고 결과: 패턴 {len(result1.patterns_recognized)}개")
    logger.info(f"생성된 통찰: {len(result1.insights_generated)}개")
    logger.info(f"평균 신뢰도: {result1.average_confidence:.2f}")
    
    # 2. 복잡한 직관적 사고 테스트
    logger.info("2. 복잡한 직관적 사고 테스트")
    situation2 = {"context": "창의적 문제 해결", "innovation": "필요", "collaboration": "중요"}
    result2 = await system.think_intuitively(situation2)
    logger.info(f"복잡한 직관적 사고 결과: 패턴 {len(result2.patterns_recognized)}개")
    logger.info(f"생성된 통찰: {len(result2.insights_generated)}개")
    logger.info(f"평균 신뢰도: {result2.average_confidence:.2f}")
    
    # 3. 시스템 요약
    summary = await system.get_intuitive_thinking_summary()
    logger.info(f"시스템 요약: {summary}")
    
    logger.info("=== 직관적 사고 시스템 테스트 완료 ===")
    return system


if __name__ == "__main__":
    asyncio.run(test_intuitive_thinking_system())
