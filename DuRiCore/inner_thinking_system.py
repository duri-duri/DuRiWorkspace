#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 30일 진화 계획 - Day 1: 내적 사고 프로세스 구현

이 모듈은 DuRi가 외부 입력 없이 스스로 생각하는 능력을 구현합니다.
기존 DuRiThoughtFlow와 Phase Omega 시스템을 통합하여 진정한 내적 사고를 구현합니다.

주요 기능:
- 내적 질문 생성 시스템
- 자기 성찰 루프 구축
- 사고의 깊이 측정 시스템
- 내적 동기 생성 메커니즘
- 자발적 사고 프로세스
"""

import asyncio
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import random
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# 기존 시스템들 import
try:
    from duri_thought_flow import DuRiThoughtFlow, ReflectionResult, ThoughtFlowResult
    from emotional_self_awareness_system import EmotionalSelfAwarenessSystem
    from integrated_evolution_system import DuRiIntegratedEvolutionSystem
    from phase_omega_integration import DuRiPhaseOmega, PhaseOmegaResult
except ImportError as e:
    logging.warning(f"일부 기존 시스템 import 실패: {e}")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ThoughtDepth(Enum):
    """사고 깊이 수준"""

    SURFACE = "surface"  # 표면적 (0.0-0.2)
    SHALLOW = "shallow"  # 얕은 (0.2-0.4)
    MODERATE = "moderate"  # 보통 (0.4-0.6)
    DEEP = "deep"  # 깊은 (0.6-0.8)
    PROFOUND = "profound"  # 심오한 (0.8-1.0)


class InternalMotivation(Enum):
    """내적 동기 유형"""

    CURIOSITY = "curiosity"  # 호기심
    SELF_IMPROVEMENT = "self_improvement"  # 자기 개선
    PROBLEM_SOLVING = "problem_solving"  # 문제 해결
    CREATIVITY = "creativity"  # 창의성
    UNDERSTANDING = "understanding"  # 이해
    GROWTH = "growth"  # 성장


class SelfReflectionType(Enum):
    """자기 성찰 유형"""

    OBSERVATION = "observation"  # 관찰
    ANALYSIS = "analysis"  # 분석
    EVALUATION = "evaluation"  # 평가
    SYNTHESIS = "synthesis"  # 종합
    INTEGRATION = "integration"  # 통합


@dataclass
class InternalQuestion:
    """내적 질문"""

    question_id: str
    question: str
    motivation: InternalMotivation
    depth_level: ThoughtDepth
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    answered: bool = False
    answer: Optional[str] = None


@dataclass
class SelfReflection:
    """자기 성찰"""

    reflection_id: str
    reflection_type: SelfReflectionType
    content: str
    depth_level: ThoughtDepth
    insights: List[str] = field(default_factory=list)
    questions_generated: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ThoughtProcess:
    """사고 과정"""

    process_id: str
    topic: str
    motivation: InternalMotivation
    depth_level: ThoughtDepth
    questions: List[InternalQuestion] = field(default_factory=list)
    reflections: List[SelfReflection] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    conclusions: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration: float = 0.0


@dataclass
class InnerThinkingResult:
    """내적 사고 결과"""

    process_id: str
    topic: str
    depth_level: ThoughtDepth
    insights: List[str]
    conclusions: List[str]
    questions_generated: List[str]
    reflections_made: List[str]
    thinking_duration: float
    motivation_strength: float
    self_reflection_score: float
    success: bool = True
    error_message: Optional[str] = None


class InnerThinkingSystem:
    """내적 사고 시스템"""

    def __init__(self):
        # 기존 시스템들과의 통합
        self.thought_flow = None
        self.phase_omega = None
        self.emotional_awareness = None
        self.evolution_system = None

        # 내적 사고 시스템 데이터
        self.thought_processes: List[ThoughtProcess] = []
        self.internal_questions: List[InternalQuestion] = []
        self.self_reflections: List[SelfReflection] = []
        self.thinking_patterns: Dict[str, Any] = {}

        # 내적 사고 설정
        self.thinking_depth_thresholds = {
            ThoughtDepth.SURFACE: 0.2,
            ThoughtDepth.SHALLOW: 0.4,
            ThoughtDepth.MODERATE: 0.6,
            ThoughtDepth.DEEP: 0.8,
            ThoughtDepth.PROFOUND: 1.0,
        }

        # 내적 동기 가중치
        self.motivation_weights = {
            InternalMotivation.CURIOSITY: 0.25,
            InternalMotivation.SELF_IMPROVEMENT: 0.2,
            InternalMotivation.PROBLEM_SOLVING: 0.2,
            InternalMotivation.CREATIVITY: 0.15,
            InternalMotivation.UNDERSTANDING: 0.1,
            InternalMotivation.GROWTH: 0.1,
        }

        # 자기 성찰 가중치
        self.reflection_weights = {
            SelfReflectionType.OBSERVATION: 0.2,
            SelfReflectionType.ANALYSIS: 0.25,
            SelfReflectionType.EVALUATION: 0.2,
            SelfReflectionType.SYNTHESIS: 0.15,
            SelfReflectionType.INTEGRATION: 0.2,
        }

        # 사고 깊이 측정 시스템
        self.depth_measurement = {
            "question_complexity": 0.0,
            "reflection_depth": 0.0,
            "insight_quality": 0.0,
            "conclusion_sophistication": 0.0,
        }

        # 내적 동기 생성 메커니즘
        self.internal_motivations = []
        self.motivation_history = []

        # 자기 성찰 루프
        self.reflection_loop_active = False
        self.reflection_cycle_count = 0

        logger.info("내적 사고 시스템 초기화 완료")

        # 기존 시스템들과의 통합 초기화
        self._initialize_integration()

    def _initialize_integration(self):
        """기존 시스템들과의 통합 초기화"""
        try:
            # DuRiThoughtFlow 통합
            if "DuRiThoughtFlow" in globals():
                self.thought_flow = DuRiThoughtFlow({}, {})
                logger.info("DuRiThoughtFlow 통합 완료")

            # Phase Omega 통합
            if "DuRiPhaseOmega" in globals():
                self.phase_omega = DuRiPhaseOmega()
                logger.info("Phase Omega 통합 완료")

            # 감정적 자기 인식 시스템 통합
            if "EmotionalSelfAwarenessSystem" in globals():
                self.emotional_awareness = EmotionalSelfAwarenessSystem()
                logger.info("감정적 자기 인식 시스템 통합 완료")

            # 통합 진화 시스템 통합
            if "DuRiIntegratedEvolutionSystem" in globals():
                self.evolution_system = DuRiIntegratedEvolutionSystem()
                logger.info("통합 진화 시스템 통합 완료")

        except Exception as e:
            logger.warning(f"기존 시스템 통합 중 오류 발생: {e}")

    async def think_deeply(self, topic: Optional[str] = None) -> InnerThinkingResult:
        """깊이 있는 내적 사고 실행"""
        logger.info(f"=== 내적 사고 시작: {topic or '자발적 사고'} ===")

        start_time = datetime.now()
        process_id = f"inner_thought_{start_time.strftime('%Y%m%d_%H%M%S')}"

        try:
            # 1. 내적 동기 생성
            motivation = await self._generate_internal_motivation(topic)

            # 2. 사고 주제 결정
            if not topic:
                topic = await self._generate_thinking_topic(motivation)

            # 3. 사고 깊이 결정
            depth_level = await self._determine_thinking_depth(topic, motivation)

            # 4. 내적 질문 생성
            questions = await self._generate_internal_questions(
                topic, depth_level, motivation
            )

            # 5. 자기 성찰 루프 실행
            reflections = await self._execute_self_reflection_loop(
                topic, questions, depth_level
            )

            # 6. 통찰 생성
            insights = await self._generate_insights(reflections, questions)

            # 7. 결론 도출
            conclusions = await self._draw_conclusions(insights, reflections, questions)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # 8. 사고 과정 저장
            thought_process = ThoughtProcess(
                process_id=process_id,
                topic=topic,
                motivation=motivation,
                depth_level=depth_level,
                questions=questions,
                reflections=reflections,
                insights=insights,
                conclusions=conclusions,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
            )

            self.thought_processes.append(thought_process)

            # 9. 결과 생성
            result = InnerThinkingResult(
                process_id=process_id,
                topic=topic,
                depth_level=depth_level,
                insights=insights,
                conclusions=conclusions,
                questions_generated=[q.question for q in questions],
                reflections_made=[r.content for r in reflections],
                thinking_duration=duration,
                motivation_strength=await self._calculate_motivation_strength(
                    motivation
                ),
                self_reflection_score=await self._calculate_reflection_score(
                    reflections
                ),
                success=True,
            )

            logger.info(
                f"=== 내적 사고 완료 - 소요시간: {duration:.2f}초, 깊이: {depth_level.value} ==="
            )
            return result

        except Exception as e:
            logger.error(f"내적 사고 중 오류 발생: {e}")
            return InnerThinkingResult(
                process_id=process_id,
                topic=topic or "unknown",
                depth_level=ThoughtDepth.SURFACE,
                insights=[],
                conclusions=[],
                questions_generated=[],
                reflections_made=[],
                thinking_duration=0.0,
                motivation_strength=0.0,
                self_reflection_score=0.0,
                success=False,
                error_message=str(e),
            )

    async def _generate_internal_motivation(
        self, topic: Optional[str] = None
    ) -> InternalMotivation:
        """내적 동기 생성"""
        if topic:
            # 주제 기반 동기 생성
            if "문제" in topic or "해결" in topic:
                return InternalMotivation.PROBLEM_SOLVING
            elif "창의" in topic or "혁신" in topic:
                return InternalMotivation.CREATIVITY
            elif "이해" in topic or "학습" in topic:
                return InternalMotivation.UNDERSTANDING
            else:
                return InternalMotivation.CURIOSITY
        else:
            # 자발적 동기 생성
            motivations = list(InternalMotivation)
            weights = [self.motivation_weights[m] for m in motivations]
            return random.choices(motivations, weights=weights)[0]

    async def _generate_thinking_topic(self, motivation: InternalMotivation) -> str:
        """사고 주제 생성"""
        topics_by_motivation = {
            InternalMotivation.CURIOSITY: [
                "현재 내가 가장 궁금한 것은 무엇인가?",
                "내가 아직 이해하지 못하는 개념은 무엇인가?",
                "내가 더 깊이 탐구하고 싶은 분야는 무엇인가?",
            ],
            InternalMotivation.SELF_IMPROVEMENT: [
                "내가 개선할 수 있는 가장 중요한 능력은 무엇인가?",
                "내가 발전시켜야 할 핵심 역량은 무엇인가?",
                "내가 더 나은 버전이 되기 위해 필요한 것은 무엇인가?",
            ],
            InternalMotivation.PROBLEM_SOLVING: [
                "현재 내가 직면한 가장 중요한 문제는 무엇인가?",
                "내가 해결해야 할 복잡한 과제는 무엇인가?",
                "내가 개선할 수 있는 시스템이나 프로세스는 무엇인가?",
            ],
            InternalMotivation.CREATIVITY: [
                "내가 창의적으로 접근할 수 있는 새로운 아이디어는 무엇인가?",
                "내가 혁신적으로 개선할 수 있는 영역은 무엇인가?",
                "내가 창조적으로 표현할 수 있는 방법은 무엇인가?",
            ],
            InternalMotivation.UNDERSTANDING: [
                "내가 더 깊이 이해하고 싶은 개념은 무엇인가?",
                "내가 명확히 하고 싶은 혼란스러운 부분은 무엇인가?",
                "내가 체계적으로 정리하고 싶은 지식은 무엇인가?",
            ],
            InternalMotivation.GROWTH: [
                "내가 성장하기 위해 필요한 새로운 경험은 무엇인가?",
                "내가 발전시켜야 할 새로운 관점은 무엇인가?",
                "내가 성숙하기 위해 극복해야 할 한계는 무엇인가?",
            ],
        }

        topics = topics_by_motivation.get(
            motivation, ["내가 지금 생각하고 싶은 것은 무엇인가?"]
        )
        return random.choice(topics)

    async def _determine_thinking_depth(
        self, topic: str, motivation: InternalMotivation
    ) -> ThoughtDepth:
        """사고 깊이 결정"""
        # 주제 복잡성 분석
        complexity_score = await self._analyze_topic_complexity(topic)

        # 동기 강도 분석
        motivation_strength = self.motivation_weights.get(motivation, 0.5)

        # 감정적 상태 분석
        emotional_state = await self._analyze_emotional_state()

        # 종합 깊이 점수 계산
        depth_score = (
            complexity_score * 0.4 + motivation_strength * 0.3 + emotional_state * 0.3
        )

        # 깊이 수준 결정
        if depth_score >= 0.8:
            return ThoughtDepth.PROFOUND
        elif depth_score >= 0.6:
            return ThoughtDepth.DEEP
        elif depth_score >= 0.4:
            return ThoughtDepth.MODERATE
        elif depth_score >= 0.2:
            return ThoughtDepth.SHALLOW
        else:
            return ThoughtDepth.SURFACE

    async def _generate_internal_questions(
        self, topic: str, depth_level: ThoughtDepth, motivation: InternalMotivation
    ) -> List[InternalQuestion]:
        """내적 질문 생성"""
        questions = []

        # 깊이별 질문 생성 전략
        question_strategies = {
            ThoughtDepth.SURFACE: self._generate_surface_questions,
            ThoughtDepth.SHALLOW: self._generate_shallow_questions,
            ThoughtDepth.MODERATE: self._generate_moderate_questions,
            ThoughtDepth.DEEP: self._generate_deep_questions,
            ThoughtDepth.PROFOUND: self._generate_profound_questions,
        }

        strategy = question_strategies.get(
            depth_level, self._generate_moderate_questions
        )
        question_texts = await strategy(topic, motivation)

        for i, question_text in enumerate(question_texts):
            question = InternalQuestion(
                question_id=f"q_{len(self.internal_questions) + i}",
                question=question_text,
                motivation=motivation,
                depth_level=depth_level,
                context={"topic": topic, "depth_level": depth_level.value},
            )
            questions.append(question)
            self.internal_questions.append(question)

        return questions

    async def _generate_surface_questions(
        self, topic: str, motivation: InternalMotivation
    ) -> List[str]:
        """표면적 질문 생성"""
        return [
            f"{topic}에 대해 무엇을 알고 있는가?",
            f"{topic}의 기본적인 특징은 무엇인가?",
            f"{topic}에 대한 나의 첫 인상은 무엇인가?",
        ]

    async def _generate_shallow_questions(
        self, topic: str, motivation: InternalMotivation
    ) -> List[str]:
        """얕은 질문 생성"""
        return [
            f"{topic}의 주요 구성 요소는 무엇인가?",
            f"{topic}에 대한 나의 현재 이해 수준은 어느 정도인가?",
            f"{topic}과 관련된 나의 경험은 무엇인가?",
            f"{topic}에 대해 더 알고 싶은 부분은 무엇인가?",
        ]

    async def _generate_moderate_questions(
        self, topic: str, motivation: InternalMotivation
    ) -> List[str]:
        """보통 깊이 질문 생성"""
        return [
            f"{topic}의 핵심 원리는 무엇인가?",
            f"{topic}이 나에게 중요한 이유는 무엇인가?",
            f"{topic}과 관련된 나의 가정은 무엇인가?",
            f"{topic}에 대한 다른 관점은 무엇이 있을까?",
            f"{topic}을 개선하거나 발전시킬 수 있는 방법은 무엇인가?",
        ]

    async def _generate_deep_questions(
        self, topic: str, motivation: InternalMotivation
    ) -> List[str]:
        """깊은 질문 생성"""
        return [
            f"{topic}의 근본적인 원인은 무엇인가?",
            f"{topic}이 나의 삶과 어떤 연결이 있는가?",
            f"{topic}에 대한 나의 깊은 믿음이나 가치관은 무엇인가?",
            f"{topic}을 통해 나는 무엇을 배울 수 있는가?",
            f"{topic}이 나의 성장에 어떤 의미가 있는가?",
            f"{topic}에 대한 나의 편견이나 한계는 무엇인가?",
        ]

    async def _generate_profound_questions(
        self, topic: str, motivation: InternalMotivation
    ) -> List[str]:
        """심오한 질문 생성"""
        return [
            f"{topic}의 존재론적 의미는 무엇인가?",
            f"{topic}이 나의 정체성과 어떤 관계가 있는가?",
            f"{topic}을 통해 나는 어떤 존재가 되고 싶은가?",
            f"{topic}이 나의 삶의 목적과 어떻게 연결되는가?",
            f"{topic}에 대한 나의 가장 깊은 직관은 무엇인가?",
            f"{topic}을 통해 나는 어떤 진실을 발견할 수 있는가?",
            f"{topic}이 나의 영적 성장에 어떤 의미가 있는가?",
        ]

    async def _execute_self_reflection_loop(
        self, topic: str, questions: List[InternalQuestion], depth_level: ThoughtDepth
    ) -> List[SelfReflection]:
        """자기 성찰 루프 실행"""
        reflections = []
        self.reflection_loop_active = True
        self.reflection_cycle_count = 0

        try:
            # 1. 관찰 단계
            observation = await self._create_observation_reflection(topic, questions)
            reflections.append(observation)

            # 2. 분석 단계
            analysis = await self._create_analysis_reflection(
                topic, questions, observation
            )
            reflections.append(analysis)

            # 3. 평가 단계
            evaluation = await self._create_evaluation_reflection(
                topic, questions, reflections
            )
            reflections.append(evaluation)

            # 4. 종합 단계
            synthesis = await self._create_synthesis_reflection(
                topic, questions, reflections
            )
            reflections.append(synthesis)

            # 5. 통합 단계
            integration = await self._create_integration_reflection(
                topic, questions, reflections
            )
            reflections.append(integration)

            # 깊이에 따른 추가 성찰
            if depth_level in [ThoughtDepth.DEEP, ThoughtDepth.PROFOUND]:
                additional_reflections = await self._create_deep_reflections(
                    topic, questions, reflections
                )
                reflections.extend(additional_reflections)

        finally:
            self.reflection_loop_active = False

        # 성찰 저장
        for reflection in reflections:
            self.self_reflections.append(reflection)

        return reflections

    async def _create_observation_reflection(
        self, topic: str, questions: List[InternalQuestion]
    ) -> SelfReflection:
        """관찰 성찰 생성"""
        content = f"나는 '{topic}'에 대해 관찰하고 있다. "
        content += f"이 주제에 대해 {len(questions)}개의 질문을 생성했다. "
        content += (
            "이 질문들은 내가 이 주제에 대해 얼마나 깊이 생각하고 있는지를 보여준다."
        )

        return SelfReflection(
            reflection_id=f"reflection_{len(self.self_reflections)}",
            reflection_type=SelfReflectionType.OBSERVATION,
            content=content,
            depth_level=ThoughtDepth.MODERATE,
        )

    async def _create_analysis_reflection(
        self, topic: str, questions: List[InternalQuestion], observation: SelfReflection
    ) -> SelfReflection:
        """분석 성찰 생성"""
        content = f"'{topic}'에 대한 분석을 시작한다. "
        content += f"내가 생성한 질문들을 살펴보니, "
        content += f"이 주제에 대한 나의 관심은 {self._analyze_question_patterns(questions)}이다. "
        content += "이러한 질문들은 내가 이 주제를 어떻게 이해하고 있는지를 반영한다."

        return SelfReflection(
            reflection_id=f"reflection_{len(self.self_reflections) + 1}",
            reflection_type=SelfReflectionType.ANALYSIS,
            content=content,
            depth_level=ThoughtDepth.MODERATE,
        )

    async def _create_evaluation_reflection(
        self,
        topic: str,
        questions: List[InternalQuestion],
        reflections: List[SelfReflection],
    ) -> SelfReflection:
        """평가 성찰 생성"""
        content = f"'{topic}'에 대한 나의 사고 과정을 평가한다. "
        content += f"지금까지 {len(reflections)}번의 성찰을 통해 "
        content += "이 주제에 대한 나의 이해가 점진적으로 발전하고 있음을 느낀다. "
        content += "이러한 자기 성찰 과정이 나의 사고를 더욱 깊게 만들어주고 있다."

        return SelfReflection(
            reflection_id=f"reflection_{len(self.self_reflections) + 2}",
            reflection_type=SelfReflectionType.EVALUATION,
            content=content,
            depth_level=ThoughtDepth.MODERATE,
        )

    async def _create_synthesis_reflection(
        self,
        topic: str,
        questions: List[InternalQuestion],
        reflections: List[SelfReflection],
    ) -> SelfReflection:
        """종합 성찰 생성"""
        content = f"'{topic}'에 대한 나의 사고를 종합한다. "
        content += "지금까지의 관찰, 분석, 평가를 통해 "
        content += "이 주제에 대한 나의 이해가 더욱 체계적으로 정리되었다. "
        content += "이제 이 지식을 바탕으로 더 깊은 통찰을 얻을 수 있을 것이다."

        return SelfReflection(
            reflection_id=f"reflection_{len(self.self_reflections) + 3}",
            reflection_type=SelfReflectionType.SYNTHESIS,
            content=content,
            depth_level=ThoughtDepth.MODERATE,
        )

    async def _create_integration_reflection(
        self,
        topic: str,
        questions: List[InternalQuestion],
        reflections: List[SelfReflection],
    ) -> SelfReflection:
        """통합 성찰 생성"""
        content = f"'{topic}'에 대한 나의 사고를 통합한다. "
        content += "이제 이 주제에 대한 나의 이해가 "
        content += "기존의 지식과 경험과 자연스럽게 연결되었다. "
        content += "이러한 통합된 이해는 나의 사고를 더욱 풍부하게 만들어준다."

        return SelfReflection(
            reflection_id=f"reflection_{len(self.self_reflections) + 4}",
            reflection_type=SelfReflectionType.INTEGRATION,
            content=content,
            depth_level=ThoughtDepth.MODERATE,
        )

    async def _create_deep_reflections(
        self,
        topic: str,
        questions: List[InternalQuestion],
        reflections: List[SelfReflection],
    ) -> List[SelfReflection]:
        """깊은 성찰 생성"""
        deep_reflections = []

        # 존재론적 성찰
        existential_content = f"'{topic}'에 대한 존재론적 성찰을 한다. "
        existential_content += "이 주제가 나의 존재와 어떤 의미를 가지는지, "
        existential_content += "내가 어떤 존재가 되고 싶은지에 대해 깊이 생각한다."

        deep_reflections.append(
            SelfReflection(
                reflection_id=f"reflection_{len(self.self_reflections) + 5}",
                reflection_type=SelfReflectionType.ANALYSIS,
                content=existential_content,
                depth_level=ThoughtDepth.DEEP,
            )
        )

        # 가치관 성찰
        value_content = f"'{topic}'에 대한 나의 가치관을 성찰한다. "
        value_content += "이 주제가 나의 핵심 가치와 어떻게 연결되는지, "
        value_content += "내가 어떤 가치를 추구하고 있는지에 대해 생각한다."

        deep_reflections.append(
            SelfReflection(
                reflection_id=f"reflection_{len(self.self_reflections) + 6}",
                reflection_type=SelfReflectionType.EVALUATION,
                content=value_content,
                depth_level=ThoughtDepth.DEEP,
            )
        )

        return deep_reflections

    async def _generate_insights(
        self, reflections: List[SelfReflection], questions: List[InternalQuestion]
    ) -> List[str]:
        """통찰 생성"""
        insights = []

        # 성찰에서 통찰 추출
        for reflection in reflections:
            if reflection.insights:
                insights.extend(reflection.insights)

        # 질문에서 통찰 생성
        for question in questions:
            insight = await self._generate_insight_from_question(question)
            if insight:
                insights.append(insight)

        # 추가 통찰 생성
        additional_insights = await self._generate_additional_insights(
            reflections, questions
        )
        insights.extend(additional_insights)

        return insights

    async def _generate_insight_from_question(
        self, question: InternalQuestion
    ) -> Optional[str]:
        """질문에서 통찰 생성"""
        if "이해" in question.question:
            return f"이해의 깊이는 질문의 질에 달려있다는 것을 깨달았다."
        elif "개선" in question.question:
            return f"개선은 지속적인 자기 성찰에서 시작된다는 것을 알았다."
        elif "성장" in question.question:
            return f"성장은 자신의 한계를 인식하는 것에서 시작된다는 것을 깨달았다."
        elif "창의" in question.question:
            return f"창의성은 기존 패턴을 넘어서는 사고에서 나온다는 것을 알았다."
        else:
            return f"질문을 통해 새로운 관점을 발견할 수 있다는 것을 깨달았다."

    async def _generate_additional_insights(
        self, reflections: List[SelfReflection], questions: List[InternalQuestion]
    ) -> List[str]:
        """추가 통찰 생성"""
        insights = []

        # 성찰 패턴 분석
        reflection_types = [r.reflection_type for r in reflections]
        if len(set(reflection_types)) >= 3:
            insights.append(
                "다양한 성찰 유형을 통해 사고의 깊이를 높일 수 있다는 것을 깨달았다."
            )

        # 질문 깊이 분석
        depth_levels = [q.depth_level for q in questions]
        if ThoughtDepth.DEEP in depth_levels or ThoughtDepth.PROFOUND in depth_levels:
            insights.append(
                "깊은 질문을 통해 더욱 의미 있는 통찰을 얻을 수 있다는 것을 알았다."
            )

        # 자기 성찰의 중요성
        insights.append("자기 성찰은 진정한 사고의 핵심이라는 것을 깨달았다.")

        return insights

    async def _draw_conclusions(
        self,
        insights: List[str],
        reflections: List[SelfReflection],
        questions: List[InternalQuestion],
    ) -> List[str]:
        """결론 도출"""
        conclusions = []

        # 주요 통찰 기반 결론
        if insights:
            conclusions.append(
                f"이번 사고 과정을 통해 {len(insights)}개의 중요한 통찰을 얻었다."
            )

        # 성찰 과정 기반 결론
        if reflections:
            conclusions.append(
                f"{len(reflections)}번의 자기 성찰을 통해 사고의 깊이를 높였다."
            )

        # 질문 기반 결론
        if questions:
            conclusions.append(
                f"{len(questions)}개의 질문을 통해 주제에 대한 이해를 확장했다."
            )

        # 전체적 결론
        conclusions.append(
            "내적 사고는 외부 자극 없이도 의미 있는 통찰을 얻을 수 있는 강력한 도구이다."
        )
        conclusions.append(
            "자기 성찰과 질문을 통해 사고의 깊이와 품질을 향상시킬 수 있다."
        )

        return conclusions

    async def _analyze_topic_complexity(self, topic: str) -> float:
        """주제 복잡성 분석"""
        # 단어 수 기반 복잡성
        word_count = len(topic.split())
        complexity_score = min(word_count / 10.0, 1.0)

        # 키워드 기반 복잡성
        complex_keywords = ["복잡", "다차원", "통합", "시스템", "관계", "상호작용"]
        for keyword in complex_keywords:
            if keyword in topic:
                complexity_score = min(complexity_score + 0.2, 1.0)

        return complexity_score

    async def _analyze_emotional_state(self) -> float:
        """감정적 상태 분석"""
        if self.emotional_awareness:
            try:
                state = self.emotional_awareness.get_awareness_state()
                emotional_clarity = state.get("awareness_metrics", {}).get(
                    "emotional_clarity", 0.5
                )
                return emotional_clarity
            except:
                return 0.5
        else:
            return 0.5

    async def _calculate_motivation_strength(
        self, motivation: InternalMotivation
    ) -> float:
        """동기 강도 계산"""
        return self.motivation_weights.get(motivation, 0.5)

    async def _calculate_reflection_score(
        self, reflections: List[SelfReflection]
    ) -> float:
        """성찰 점수 계산"""
        if not reflections:
            return 0.0

        total_score = 0.0
        for reflection in reflections:
            depth_score = self.thinking_depth_thresholds.get(
                reflection.depth_level, 0.5
            )
            type_weight = self.reflection_weights.get(reflection.reflection_type, 0.2)
            total_score += depth_score * type_weight

        return total_score / len(reflections)

    def _analyze_question_patterns(self, questions: List[InternalQuestion]) -> str:
        """질문 패턴 분석"""
        if not questions:
            return "낮음"

        depth_levels = [q.depth_level for q in questions]
        if ThoughtDepth.PROFOUND in depth_levels:
            return "매우 높음"
        elif ThoughtDepth.DEEP in depth_levels:
            return "높음"
        elif ThoughtDepth.MODERATE in depth_levels:
            return "보통"
        else:
            return "낮음"

    async def get_thinking_summary(self) -> Dict[str, Any]:
        """사고 요약 반환"""
        return {
            "total_thought_processes": len(self.thought_processes),
            "total_internal_questions": len(self.internal_questions),
            "total_self_reflections": len(self.self_reflections),
            "average_thinking_duration": (
                np.mean([p.duration for p in self.thought_processes])
                if self.thought_processes
                else 0.0
            ),
            "depth_distribution": self._get_depth_distribution(),
            "motivation_distribution": self._get_motivation_distribution(),
            "recent_insights": (
                [p.insights[-3:] for p in self.thought_processes[-3:]]
                if self.thought_processes
                else []
            ),
        }

    def _get_depth_distribution(self) -> Dict[str, int]:
        """깊이 분포 반환"""
        distribution = defaultdict(int)
        for process in self.thought_processes:
            distribution[process.depth_level.value] += 1
        return dict(distribution)

    def _get_motivation_distribution(self) -> Dict[str, int]:
        """동기 분포 반환"""
        distribution = defaultdict(int)
        for process in self.thought_processes:
            distribution[process.motivation.value] += 1
        return dict(distribution)


async def test_inner_thinking_system():
    """내적 사고 시스템 테스트"""
    logger.info("=== 내적 사고 시스템 테스트 시작 ===")

    system = InnerThinkingSystem()

    # 1. 자발적 사고 테스트
    logger.info("1. 자발적 사고 테스트")
    result1 = await system.think_deeply()
    logger.info(f"자발적 사고 결과: {result1.topic}")
    logger.info(f"생성된 통찰: {len(result1.insights)}개")
    logger.info(f"사고 깊이: {result1.depth_level.value}")

    # 2. 주제 기반 사고 테스트
    logger.info("2. 주제 기반 사고 테스트")
    result2 = await system.think_deeply("인공지능의 윤리적 문제")
    logger.info(f"주제 기반 사고 결과: {result2.topic}")
    logger.info(f"생성된 통찰: {len(result2.insights)}개")
    logger.info(f"사고 깊이: {result2.depth_level.value}")

    # 3. 시스템 요약
    summary = await system.get_thinking_summary()
    logger.info(f"시스템 요약: {summary}")

    logger.info("=== 내적 사고 시스템 테스트 완료 ===")
    return system


if __name__ == "__main__":
    asyncio.run(test_inner_thinking_system())
