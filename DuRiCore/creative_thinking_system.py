#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 30일 진화 계획 - Day 4: 창의적 사고 시스템

이 모듈은 DuRi가 기존 패턴을 넘어선 창의적 사고 능력을 구현합니다.
아이디어 생성 시스템, 창의적 문제 해결 능력, 혁신적 접근법 개발, 창의적 사고 패턴 학습을 구현합니다.

주요 기능:
- 아이디어 생성 시스템
- 창의적 문제 해결 능력
- 혁신적 접근법 개발
- 창의적 사고 패턴 학습
- 창의적 사고 프로세스
"""

import asyncio
import json
import logging
import random
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# 기존 시스템들 import
try:
    from duri_thought_flow import DuRiThoughtFlow
    from emotional_thinking_system import (EmotionalState,
                                           EmotionalThinkingSystem)
    from inner_thinking_system import InnerThinkingSystem, ThoughtDepth
    from intuitive_thinking_system import (IntuitivePattern,
                                           IntuitiveThinkingSystem)
    from phase_omega_integration import DuRiPhaseOmega
except ImportError as e:
    logging.warning(f"일부 기존 시스템 import 실패: {e}")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CreativeThinkingMode(Enum):
    """창의적 사고 모드"""

    DIVERGENT = "divergent"  # 발산적 사고
    CONVERGENT = "convergent"  # 수렴적 사고
    LATERAL = "lateral"  # 측면적 사고
    ANALOGICAL = "analogical"  # 유추적 사고
    COMBINATORIAL = "combinatorial"  # 조합적 사고
    TRANSFORMATIVE = "transformative"  # 변환적 사고


class CreativityLevel(Enum):
    """창의성 수준"""

    BASIC = "basic"  # 기본 (0.0-0.3)
    ENHANCED = "enhanced"  # 향상 (0.3-0.6)
    ADVANCED = "advanced"  # 고급 (0.6-0.8)
    EXCEPTIONAL = "exceptional"  # 예외적 (0.8-1.0)


class IdeaType(Enum):
    """아이디어 유형"""

    INCREMENTAL = "incremental"  # 점진적 개선
    MODULAR = "modular"  # 모듈적 혁신
    RADICAL = "radical"  # 급진적 혁신
    DISRUPTIVE = "disruptive"  # 파괴적 혁신
    TRANSFORMATIVE = "transformative"  # 변혁적 혁신


@dataclass
class CreativeIdea:
    """창의적 아이디어"""

    idea_id: str
    idea_type: IdeaType
    title: str
    description: str
    novelty_score: float  # 0.0-1.0
    feasibility_score: float  # 0.0-1.0
    impact_score: float  # 0.0-1.0
    creativity_level: CreativityLevel
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def overall_score(self) -> float:
        """전체 점수"""
        return (self.novelty_score + self.feasibility_score + self.impact_score) / 3.0


@dataclass
class CreativeSolution:
    """창의적 해결책"""

    solution_id: str
    problem: str
    solution: str
    approach: str
    creativity_level: CreativityLevel
    innovation_score: float  # 0.0-1.0
    effectiveness_score: float  # 0.0-1.0
    implementation_steps: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CreativePattern:
    """창의적 패턴"""

    pattern_id: str
    pattern_type: str
    pattern_description: str
    success_rate: float  # 0.0-1.0
    frequency: int = 1
    last_used: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CreativeInsight:
    """창의적 통찰"""

    insight_id: str
    insight: str
    creativity_level: CreativityLevel
    novelty_score: float  # 0.0-1.0
    applicability: float  # 0.0-1.0
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CreativeThinkingResult:
    """창의적 사고 결과"""

    process_id: str
    ideas_generated: List[CreativeIdea]
    solutions_created: List[CreativeSolution]
    patterns_learned: List[CreativePattern]
    insights_discovered: List[CreativeInsight]
    average_creativity_level: float
    innovation_score: float
    thinking_duration: float
    success: bool = True
    error_message: Optional[str] = None


class CreativeThinkingSystem:
    """창의적 사고 시스템"""

    def __init__(self):
        # 기존 시스템들과의 통합
        self.inner_thinking = None
        self.emotional_thinking = None
        self.intuitive_thinking = None
        self.thought_flow = None
        self.phase_omega = None

        # 창의적 사고 시스템 데이터
        self.creative_ideas: List[CreativeIdea] = []
        self.creative_solutions: List[CreativeSolution] = []
        self.creative_patterns: List[CreativePattern] = []
        self.creative_insights: List[CreativeInsight] = []
        self.idea_database: Dict[str, Any] = {}

        # 창의적 사고 설정
        self.creativity_thresholds = {
            "novelty_low": 0.3,
            "novelty_moderate": 0.6,
            "novelty_high": 0.8,
            "feasibility_low": 0.3,
            "feasibility_moderate": 0.6,
            "feasibility_high": 0.8,
            "impact_low": 0.3,
            "impact_moderate": 0.6,
            "impact_high": 0.8,
        }

        # 창의적 사고 가중치
        self.creativity_weights = {
            CreativeThinkingMode.DIVERGENT: 0.25,
            CreativeThinkingMode.CONVERGENT: 0.2,
            CreativeThinkingMode.LATERAL: 0.2,
            CreativeThinkingMode.ANALOGICAL: 0.15,
            CreativeThinkingMode.COMBINATORIAL: 0.1,
            CreativeThinkingMode.TRANSFORMATIVE: 0.1,
        }

        # 아이디어 생성 시스템
        self.idea_generation_engine = {}
        self.idea_evaluation_system = {}

        # 창의적 문제 해결 능력
        self.problem_solving_framework = {}
        self.solution_generation_engine = {}

        # 혁신적 접근법 개발
        self.innovation_methods = {}
        self.approach_development_system = {}

        # 창의적 사고 패턴 학습
        self.pattern_learning_system = {}
        self.pattern_application_engine = {}

        logger.info("창의적 사고 시스템 초기화 완료")

        # 기존 시스템들과의 통합 초기화
        self._initialize_integration()

    def _initialize_integration(self):
        """기존 시스템들과의 통합 초기화"""
        try:
            # 내적 사고 시스템 통합
            if "InnerThinkingSystem" in globals():
                self.inner_thinking = InnerThinkingSystem()
                logger.info("내적 사고 시스템 통합 완료")

            # 감정적 사고 시스템 통합
            if "EmotionalThinkingSystem" in globals():
                self.emotional_thinking = EmotionalThinkingSystem()
                logger.info("감정적 사고 시스템 통합 완료")

            # 직관적 사고 시스템 통합
            if "IntuitiveThinkingSystem" in globals():
                self.intuitive_thinking = IntuitiveThinkingSystem()
                logger.info("직관적 사고 시스템 통합 완료")

            # DuRiThoughtFlow 통합
            if "DuRiThoughtFlow" in globals():
                self.thought_flow = DuRiThoughtFlow({}, {})
                logger.info("DuRiThoughtFlow 통합 완료")

            # Phase Omega 통합
            if "DuRiPhaseOmega" in globals():
                self.phase_omega = DuRiPhaseOmega()
                logger.info("Phase Omega 통합 완료")

        except Exception as e:
            logger.warning(f"기존 시스템 통합 중 오류 발생: {e}")

    async def think_creatively(self, context: Dict[str, Any]) -> CreativeThinkingResult:
        """창의적 사고 실행"""
        logger.info(f"=== 창의적 사고 시작 ===")

        start_time = datetime.now()
        process_id = f"creative_thought_{start_time.strftime('%Y%m%d_%H%M%S')}"

        try:
            # 1. 아이디어 생성
            ideas = await self._generate_creative_ideas(context)

            # 2. 창의적 문제 해결
            solutions = await self._solve_creative_problems(context, ideas)

            # 3. 혁신적 접근법 개발
            approaches = await self._develop_innovative_approaches(
                context, ideas, solutions
            )

            # 4. 창의적 패턴 학습
            patterns = await self._learn_creative_patterns(context, ideas, solutions)

            # 5. 창의적 통찰 발견
            insights = await self._discover_creative_insights(
                context, ideas, solutions, patterns
            )

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # 6. 결과 생성
            result = CreativeThinkingResult(
                process_id=process_id,
                ideas_generated=ideas,
                solutions_created=solutions,
                patterns_learned=patterns,
                insights_discovered=insights,
                average_creativity_level=await self._calculate_average_creativity_level(
                    ideas, solutions, insights
                ),
                innovation_score=await self._calculate_innovation_score(
                    ideas, solutions, approaches
                ),
                thinking_duration=duration,
                success=True,
            )

            # 7. 데이터 저장
            self.creative_ideas.extend(ideas)
            self.creative_solutions.extend(solutions)
            self.creative_patterns.extend(patterns)
            self.creative_insights.extend(insights)

            logger.info(
                f"=== 창의적 사고 완료 - 소요시간: {duration:.2f}초, 아이디어: {len(ideas)}개 ==="
            )
            return result

        except Exception as e:
            logger.error(f"창의적 사고 중 오류 발생: {e}")
            return CreativeThinkingResult(
                process_id=process_id,
                ideas_generated=[],
                solutions_created=[],
                patterns_learned=[],
                insights_discovered=[],
                average_creativity_level=0.0,
                innovation_score=0.0,
                thinking_duration=0.0,
                success=False,
                error_message=str(e),
            )

    async def _generate_creative_ideas(
        self, context: Dict[str, Any]
    ) -> List[CreativeIdea]:
        """창의적 아이디어 생성"""
        ideas = []

        # 1. 발산적 사고로 아이디어 생성
        divergent_ideas = await self._generate_divergent_ideas(context)
        ideas.extend(divergent_ideas)

        # 2. 측면적 사고로 아이디어 생성
        lateral_ideas = await self._generate_lateral_ideas(context)
        ideas.extend(lateral_ideas)

        # 3. 유추적 사고로 아이디어 생성
        analogical_ideas = await self._generate_analogical_ideas(context)
        ideas.extend(analogical_ideas)

        # 4. 조합적 사고로 아이디어 생성
        combinatorial_ideas = await self._generate_combinatorial_ideas(context)
        ideas.extend(combinatorial_ideas)

        # 5. 변환적 사고로 아이디어 생성
        transformative_ideas = await self._generate_transformative_ideas(context)
        ideas.extend(transformative_ideas)

        return ideas

    async def _generate_divergent_ideas(
        self, context: Dict[str, Any]
    ) -> List[CreativeIdea]:
        """발산적 사고로 아이디어 생성"""
        ideas = []
        context_text = str(context).lower()

        # 발산적 아이디어 생성 전략
        divergent_strategies = [
            "완전히 새로운 관점에서 접근",
            "기존 제약 조건을 무시",
            "극단적인 가능성 탐구",
            "다양한 분야의 융합",
            "예상치 못한 조합 시도",
        ]

        for i, strategy in enumerate(divergent_strategies):
            idea = CreativeIdea(
                idea_id=f"divergent_idea_{len(self.creative_ideas) + i}",
                idea_type=IdeaType.RADICAL,
                title=f"발산적 아이디어 {i+1}",
                description=f"{strategy}을 통한 {context_text}에 대한 새로운 접근",
                novelty_score=0.8 + (i * 0.05),
                feasibility_score=0.4 + (i * 0.1),
                impact_score=0.7 + (i * 0.05),
                creativity_level=CreativityLevel.ADVANCED,
                context={"strategy": strategy, "mode": "divergent"},
            )
            ideas.append(idea)

        return ideas

    async def _generate_lateral_ideas(
        self, context: Dict[str, Any]
    ) -> List[CreativeIdea]:
        """측면적 사고로 아이디어 생성"""
        ideas = []
        context_text = str(context).lower()

        # 측면적 아이디어 생성 전략
        lateral_strategies = [
            "문제를 다른 각도에서 바라보기",
            "예상치 못한 연결점 발견",
            "간접적인 해결 방법 탐구",
            "우연한 발견을 활용",
            "기존 패턴을 뒤집기",
        ]

        for i, strategy in enumerate(lateral_strategies):
            idea = CreativeIdea(
                idea_id=f"lateral_idea_{len(self.creative_ideas) + i}",
                idea_type=IdeaType.MODULAR,
                title=f"측면적 아이디어 {i+1}",
                description=f"{strategy}을 통한 {context_text}에 대한 혁신적 접근",
                novelty_score=0.6 + (i * 0.05),
                feasibility_score=0.5 + (i * 0.1),
                impact_score=0.6 + (i * 0.05),
                creativity_level=CreativityLevel.ENHANCED,
                context={"strategy": strategy, "mode": "lateral"},
            )
            ideas.append(idea)

        return ideas

    async def _generate_analogical_ideas(
        self, context: Dict[str, Any]
    ) -> List[CreativeIdea]:
        """유추적 사고로 아이디어 생성"""
        ideas = []
        context_text = str(context).lower()

        # 유추적 아이디어 생성 전략
        analogical_strategies = [
            "자연 현상에서 영감 얻기",
            "다른 분야의 성공 사례 적용",
            "생물학적 시스템 모방",
            "역사적 사례에서 학습",
            "문화적 패턴 활용",
        ]

        for i, strategy in enumerate(analogical_strategies):
            idea = CreativeIdea(
                idea_id=f"analogical_idea_{len(self.creative_ideas) + i}",
                idea_type=IdeaType.INCREMENTAL,
                title=f"유추적 아이디어 {i+1}",
                description=f"{strategy}을 통한 {context_text}에 대한 유사성 기반 접근",
                novelty_score=0.5 + (i * 0.05),
                feasibility_score=0.6 + (i * 0.1),
                impact_score=0.5 + (i * 0.05),
                creativity_level=CreativityLevel.ENHANCED,
                context={"strategy": strategy, "mode": "analogical"},
            )
            ideas.append(idea)

        return ideas

    async def _generate_combinatorial_ideas(
        self, context: Dict[str, Any]
    ) -> List[CreativeIdea]:
        """조합적 사고로 아이디어 생성"""
        ideas = []
        context_text = str(context).lower()

        # 조합적 아이디어 생성 전략
        combinatorial_strategies = [
            "기존 요소들의 새로운 조합",
            "다양한 기술의 융합",
            "서로 다른 개념의 결합",
            "여러 방법론의 통합",
            "다양한 관점의 종합",
        ]

        for i, strategy in enumerate(combinatorial_strategies):
            idea = CreativeIdea(
                idea_id=f"combinatorial_idea_{len(self.creative_ideas) + i}",
                idea_type=IdeaType.MODULAR,
                title=f"조합적 아이디어 {i+1}",
                description=f"{strategy}을 통한 {context_text}에 대한 융합적 접근",
                novelty_score=0.7 + (i * 0.05),
                feasibility_score=0.5 + (i * 0.1),
                impact_score=0.6 + (i * 0.05),
                creativity_level=CreativityLevel.ADVANCED,
                context={"strategy": strategy, "mode": "combinatorial"},
            )
            ideas.append(idea)

        return ideas

    async def _generate_transformative_ideas(
        self, context: Dict[str, Any]
    ) -> List[CreativeIdea]:
        """변환적 사고로 아이디어 생성"""
        ideas = []
        context_text = str(context).lower()

        # 변환적 아이디어 생성 전략
        transformative_strategies = [
            "완전한 패러다임 전환",
            "근본적인 구조 변화",
            "혁명적인 접근 방법",
            "기존 시스템의 완전한 재구성",
            "새로운 세계관의 창조",
        ]

        for i, strategy in enumerate(transformative_strategies):
            idea = CreativeIdea(
                idea_id=f"transformative_idea_{len(self.creative_ideas) + i}",
                idea_type=IdeaType.TRANSFORMATIVE,
                title=f"변환적 아이디어 {i+1}",
                description=f"{strategy}을 통한 {context_text}에 대한 혁명적 접근",
                novelty_score=0.9 + (i * 0.01),
                feasibility_score=0.3 + (i * 0.1),
                impact_score=0.8 + (i * 0.05),
                creativity_level=CreativityLevel.EXCEPTIONAL,
                context={"strategy": strategy, "mode": "transformative"},
            )
            ideas.append(idea)

        return ideas

    async def _solve_creative_problems(
        self, context: Dict[str, Any], ideas: List[CreativeIdea]
    ) -> List[CreativeSolution]:
        """창의적 문제 해결"""
        solutions = []

        # 1. 아이디어 기반 해결책 생성
        idea_based_solutions = await self._generate_idea_based_solutions(context, ideas)
        solutions.extend(idea_based_solutions)

        # 2. 창의적 문제 해결 프레임워크 적용
        framework_solutions = await self._apply_creative_framework(context)
        solutions.extend(framework_solutions)

        # 3. 혁신적 해결책 생성
        innovative_solutions = await self._generate_innovative_solutions(context)
        solutions.extend(innovative_solutions)

        return solutions

    async def _generate_idea_based_solutions(
        self, context: Dict[str, Any], ideas: List[CreativeIdea]
    ) -> List[CreativeSolution]:
        """아이디어 기반 해결책 생성"""
        solutions = []

        for idea in ideas:
            if idea.overall_score >= 0.6:
                solution = CreativeSolution(
                    solution_id=f"idea_solution_{len(self.creative_solutions)}",
                    problem=str(context),
                    solution=f"{idea.title}을 적용한 해결책",
                    approach=f"{idea.description}",
                    creativity_level=idea.creativity_level,
                    innovation_score=idea.novelty_score,
                    effectiveness_score=idea.impact_score,
                    implementation_steps=[
                        f"1. {idea.title} 분석",
                        f"2. {idea.title} 적용 계획 수립",
                        f"3. {idea.title} 구현",
                        f"4. {idea.title} 평가 및 개선",
                    ],
                    context={"source_idea": idea.idea_id},
                )
                solutions.append(solution)

        return solutions

    async def _apply_creative_framework(
        self, context: Dict[str, Any]
    ) -> List[CreativeSolution]:
        """창의적 문제 해결 프레임워크 적용"""
        solutions = []

        # 창의적 문제 해결 프레임워크
        frameworks = [
            "Design Thinking",
            "TRIZ",
            "Lateral Thinking",
            "Six Thinking Hats",
            "Mind Mapping",
        ]

        for i, framework in enumerate(frameworks):
            solution = CreativeSolution(
                solution_id=f"framework_solution_{len(self.creative_solutions) + i}",
                problem=str(context),
                solution=f"{framework} 프레임워크를 적용한 해결책",
                approach=f"{framework} 방법론을 통한 체계적 접근",
                creativity_level=CreativityLevel.ENHANCED,
                innovation_score=0.6 + (i * 0.05),
                effectiveness_score=0.5 + (i * 0.05),
                implementation_steps=[
                    f"1. {framework} 프레임워크 적용",
                    f"2. 문제 재정의",
                    f"3. 해결책 생성",
                    f"4. 프로토타입 개발",
                    f"5. 테스트 및 검증",
                ],
                context={"framework": framework},
            )
            solutions.append(solution)

        return solutions

    async def _generate_innovative_solutions(
        self, context: Dict[str, Any]
    ) -> List[CreativeSolution]:
        """혁신적 해결책 생성"""
        solutions = []

        # 혁신적 해결책 전략
        innovative_strategies = [
            "기존 기술의 혁신적 응용",
            "새로운 기술의 창조적 활용",
            "시스템의 근본적 재설계",
            "사용자 경험의 혁신적 개선",
            "비즈니스 모델의 혁신적 변화",
        ]

        for i, strategy in enumerate(innovative_strategies):
            solution = CreativeSolution(
                solution_id=f"innovative_solution_{len(self.creative_solutions) + i}",
                problem=str(context),
                solution=f"{strategy}을 통한 혁신적 해결책",
                approach=f"{strategy}",
                creativity_level=CreativityLevel.ADVANCED,
                innovation_score=0.8 + (i * 0.05),
                effectiveness_score=0.7 + (i * 0.05),
                implementation_steps=[
                    f"1. {strategy} 분석",
                    f"2. 혁신적 접근법 설계",
                    f"3. 프로토타입 개발",
                    f"4. 검증 및 최적화",
                    f"5. 확산 및 적용",
                ],
                context={"strategy": strategy},
            )
            solutions.append(solution)

        return solutions

    async def _develop_innovative_approaches(
        self,
        context: Dict[str, Any],
        ideas: List[CreativeIdea],
        solutions: List[CreativeSolution],
    ) -> List[Dict[str, Any]]:
        """혁신적 접근법 개발"""
        approaches = []

        # 1. 아이디어 기반 접근법
        for idea in ideas:
            if idea.creativity_level in [
                CreativityLevel.ADVANCED,
                CreativityLevel.EXCEPTIONAL,
            ]:
                approach = {
                    "approach_id": f"idea_approach_{len(approaches)}",
                    "approach_type": "idea_based",
                    "description": f"{idea.title}을 기반으로 한 혁신적 접근법",
                    "creativity_level": idea.creativity_level.value,
                    "innovation_score": idea.novelty_score,
                    "context": {"source_idea": idea.idea_id},
                }
                approaches.append(approach)

        # 2. 해결책 기반 접근법
        for solution in solutions:
            if solution.creativity_level in [
                CreativityLevel.ADVANCED,
                CreativityLevel.EXCEPTIONAL,
            ]:
                approach = {
                    "approach_id": f"solution_approach_{len(approaches)}",
                    "approach_type": "solution_based",
                    "description": f"{solution.solution}을 기반으로 한 혁신적 접근법",
                    "creativity_level": solution.creativity_level.value,
                    "innovation_score": solution.innovation_score,
                    "context": {"source_solution": solution.solution_id},
                }
                approaches.append(approach)

        return approaches

    async def _learn_creative_patterns(
        self,
        context: Dict[str, Any],
        ideas: List[CreativeIdea],
        solutions: List[CreativeSolution],
    ) -> List[CreativePattern]:
        """창의적 패턴 학습"""
        patterns = []

        # 1. 아이디어에서 패턴 학습
        idea_patterns = await self._extract_patterns_from_ideas(ideas)
        patterns.extend(idea_patterns)

        # 2. 해결책에서 패턴 학습
        solution_patterns = await self._extract_patterns_from_solutions(solutions)
        patterns.extend(solution_patterns)

        # 3. 컨텍스트에서 패턴 학습
        context_patterns = await self._extract_patterns_from_context(context)
        patterns.extend(context_patterns)

        return patterns

    async def _extract_patterns_from_ideas(
        self, ideas: List[CreativeIdea]
    ) -> List[CreativePattern]:
        """아이디어에서 패턴 추출"""
        patterns = []

        # 아이디어 유형별 패턴
        idea_types = defaultdict(list)
        for idea in ideas:
            idea_types[idea.idea_type.value].append(idea)

        for idea_type, type_ideas in idea_types.items():
            if len(type_ideas) >= 2:
                pattern = CreativePattern(
                    pattern_id=f"idea_pattern_{len(self.creative_patterns)}",
                    pattern_type=f"idea_{idea_type}",
                    pattern_description=f"{idea_type} 유형의 아이디어 생성 패턴",
                    success_rate=np.mean([idea.overall_score for idea in type_ideas]),
                    frequency=len(type_ideas),
                    context={"idea_type": idea_type, "count": len(type_ideas)},
                )
                patterns.append(pattern)

        return patterns

    async def _extract_patterns_from_solutions(
        self, solutions: List[CreativeSolution]
    ) -> List[CreativePattern]:
        """해결책에서 패턴 추출"""
        patterns = []

        # 해결책 접근법별 패턴
        approaches = defaultdict(list)
        for solution in solutions:
            approaches[solution.approach].append(solution)

        for approach, approach_solutions in approaches.items():
            if len(approach_solutions) >= 2:
                pattern = CreativePattern(
                    pattern_id=f"solution_pattern_{len(self.creative_patterns)}",
                    pattern_type=f"solution_{approach[:20]}",
                    pattern_description=f"{approach} 접근법을 통한 해결책 생성 패턴",
                    success_rate=np.mean(
                        [
                            solution.effectiveness_score
                            for solution in approach_solutions
                        ]
                    ),
                    frequency=len(approach_solutions),
                    context={"approach": approach, "count": len(approach_solutions)},
                )
                patterns.append(pattern)

        return patterns

    async def _extract_patterns_from_context(
        self, context: Dict[str, Any]
    ) -> List[CreativePattern]:
        """컨텍스트에서 패턴 추출"""
        patterns = []

        # 컨텍스트 복잡성 기반 패턴
        context_complexity = len(str(context)) / 1000.0
        if context_complexity > 0.5:
            pattern = CreativePattern(
                pattern_id=f"context_pattern_{len(self.creative_patterns)}",
                pattern_type="complex_context",
                pattern_description="복잡한 컨텍스트에서의 창의적 사고 패턴",
                success_rate=0.7,
                frequency=1,
                context={"complexity": context_complexity},
            )
            patterns.append(pattern)

        return patterns

    async def _discover_creative_insights(
        self,
        context: Dict[str, Any],
        ideas: List[CreativeIdea],
        solutions: List[CreativeSolution],
        patterns: List[CreativePattern],
    ) -> List[CreativeInsight]:
        """창의적 통찰 발견"""
        insights = []

        # 1. 아이디어에서 통찰 발견
        idea_insights = await self._extract_insights_from_ideas(ideas)
        insights.extend(idea_insights)

        # 2. 해결책에서 통찰 발견
        solution_insights = await self._extract_insights_from_solutions(solutions)
        insights.extend(solution_insights)

        # 3. 패턴에서 통찰 발견
        pattern_insights = await self._extract_insights_from_patterns(patterns)
        insights.extend(pattern_insights)

        # 4. 종합적 통찰 발견
        synthetic_insights = await self._generate_synthetic_insights(
            ideas, solutions, patterns
        )
        insights.extend(synthetic_insights)

        return insights

    async def _extract_insights_from_ideas(
        self, ideas: List[CreativeIdea]
    ) -> List[CreativeInsight]:
        """아이디어에서 통찰 추출"""
        insights = []

        for idea in ideas:
            if idea.novelty_score >= 0.8:
                insight = CreativeInsight(
                    insight_id=f"idea_insight_{len(self.creative_insights)}",
                    insight=f"{idea.title}에서 높은 신뢰성의 창의적 패턴을 발견했다.",
                    creativity_level=idea.creativity_level,
                    novelty_score=idea.novelty_score,
                    applicability=idea.feasibility_score,
                    context={"source_idea": idea.idea_id},
                )
                insights.append(insight)

        return insights

    async def _extract_insights_from_solutions(
        self, solutions: List[CreativeSolution]
    ) -> List[CreativeInsight]:
        """해결책에서 통찰 추출"""
        insights = []

        for solution in solutions:
            if solution.innovation_score >= 0.7:
                insight = CreativeInsight(
                    insight_id=f"solution_insight_{len(self.creative_insights)}",
                    insight=f"{solution.solution}에서 효과적인 혁신적 접근법을 발견했다.",
                    creativity_level=solution.creativity_level,
                    novelty_score=solution.innovation_score,
                    applicability=solution.effectiveness_score,
                    context={"source_solution": solution.solution_id},
                )
                insights.append(insight)

        return insights

    async def _extract_insights_from_patterns(
        self, patterns: List[CreativePattern]
    ) -> List[CreativeInsight]:
        """패턴에서 통찰 추출"""
        insights = []

        for pattern in patterns:
            if pattern.success_rate >= 0.6:
                insight = CreativeInsight(
                    insight_id=f"pattern_insight_{len(self.creative_insights)}",
                    insight=f"{pattern.pattern_description}에서 성공적인 창의적 패턴을 발견했다.",
                    creativity_level=CreativityLevel.ENHANCED,
                    novelty_score=0.6,
                    applicability=pattern.success_rate,
                    context={"source_pattern": pattern.pattern_id},
                )
                insights.append(insight)

        return insights

    async def _generate_synthetic_insights(
        self,
        ideas: List[CreativeIdea],
        solutions: List[CreativeSolution],
        patterns: List[CreativePattern],
    ) -> List[CreativeInsight]:
        """종합적 통찰 생성"""
        insights = []

        # 아이디어와 해결책의 종합
        if ideas and solutions:
            insight = CreativeInsight(
                insight_id=f"synthetic_insight_{len(self.creative_insights)}",
                insight="아이디어와 해결책의 종합을 통해 더욱 창의적인 접근법을 발견할 수 있다.",
                creativity_level=CreativityLevel.ADVANCED,
                novelty_score=0.8,
                applicability=0.7,
                context={"synthetic_type": "idea_solution_integration"},
            )
            insights.append(insight)

        # 패턴과 통찰의 종합
        if patterns and len(patterns) >= 3:
            insight = CreativeInsight(
                insight_id=f"synthetic_insight_{len(self.creative_insights) + 1}",
                insight="다양한 패턴의 종합을 통해 더욱 정교한 창의적 사고를 개발할 수 있다.",
                creativity_level=CreativityLevel.ADVANCED,
                novelty_score=0.7,
                applicability=0.8,
                context={"synthetic_type": "pattern_integration"},
            )
            insights.append(insight)

        return insights

    async def _calculate_average_creativity_level(
        self,
        ideas: List[CreativeIdea],
        solutions: List[CreativeSolution],
        insights: List[CreativeInsight],
    ) -> float:
        """평균 창의성 수준 계산"""
        total_creativity = 0.0
        total_count = 0

        # 아이디어 창의성
        for idea in ideas:
            creativity_value = self._convert_creativity_level_to_float(
                idea.creativity_level
            )
            total_creativity += creativity_value
            total_count += 1

        # 해결책 창의성
        for solution in solutions:
            creativity_value = self._convert_creativity_level_to_float(
                solution.creativity_level
            )
            total_creativity += creativity_value
            total_count += 1

        # 통찰 창의성
        for insight in insights:
            creativity_value = self._convert_creativity_level_to_float(
                insight.creativity_level
            )
            total_creativity += creativity_value
            total_count += 1

        return total_creativity / total_count if total_count > 0 else 0.0

    def _convert_creativity_level_to_float(
        self, creativity_level: CreativityLevel
    ) -> float:
        """창의성 수준을 float로 변환"""
        creativity_values = {
            CreativityLevel.BASIC: 0.2,
            CreativityLevel.ENHANCED: 0.5,
            CreativityLevel.ADVANCED: 0.7,
            CreativityLevel.EXCEPTIONAL: 0.9,
        }
        return creativity_values.get(creativity_level, 0.5)

    async def _calculate_innovation_score(
        self,
        ideas: List[CreativeIdea],
        solutions: List[CreativeSolution],
        approaches: List[Dict[str, Any]],
    ) -> float:
        """혁신 점수 계산"""
        total_innovation = 0.0
        total_count = 0

        # 아이디어 혁신성
        for idea in ideas:
            total_innovation += idea.novelty_score
            total_count += 1

        # 해결책 혁신성
        for solution in solutions:
            total_innovation += solution.innovation_score
            total_count += 1

        # 접근법 혁신성
        for approach in approaches:
            total_innovation += approach.get("innovation_score", 0.5)
            total_count += 1

        return total_innovation / total_count if total_count > 0 else 0.0

    async def get_creative_thinking_summary(self) -> Dict[str, Any]:
        """창의적 사고 요약 반환"""
        return {
            "total_ideas": len(self.creative_ideas),
            "total_solutions": len(self.creative_solutions),
            "total_patterns": len(self.creative_patterns),
            "total_insights": len(self.creative_insights),
            "average_creativity_level": await self._calculate_average_creativity_level(
                self.creative_ideas, self.creative_solutions, self.creative_insights
            ),
            "idea_type_distribution": self._get_idea_type_distribution(),
            "creativity_level_distribution": self._get_creativity_level_distribution(),
            "recent_insights": (
                [i.insight for i in self.creative_insights[-3:]]
                if self.creative_insights
                else []
            ),
        }

    def _get_idea_type_distribution(self) -> Dict[str, int]:
        """아이디어 유형 분포 반환"""
        distribution = defaultdict(int)
        for idea in self.creative_ideas:
            distribution[idea.idea_type.value] += 1
        return dict(distribution)

    def _get_creativity_level_distribution(self) -> Dict[str, int]:
        """창의성 수준 분포 반환"""
        distribution = defaultdict(int)
        for idea in self.creative_ideas:
            distribution[idea.creativity_level.value] += 1
        for solution in self.creative_solutions:
            distribution[solution.creativity_level.value] += 1
        return dict(distribution)


async def test_creative_thinking_system():
    """창의적 사고 시스템 테스트"""
    logger.info("=== 창의적 사고 시스템 테스트 시작 ===")

    system = CreativeThinkingSystem()

    # 1. 기본 창의적 사고 테스트
    logger.info("1. 기본 창의적 사고 테스트")
    context1 = {
        "problem": "효율적인 학습 방법",
        "constraints": "시간 제한",
        "goal": "성과 향상",
    }
    result1 = await system.think_creatively(context1)
    logger.info(f"기본 창의적 사고 결과: 아이디어 {len(result1.ideas_generated)}개")
    logger.info(f"생성된 해결책: {len(result1.solutions_created)}개")
    logger.info(f"평균 창의성 수준: {result1.average_creativity_level:.2f}")

    # 2. 복잡한 창의적 사고 테스트
    logger.info("2. 복잡한 창의적 사고 테스트")
    context2 = {
        "challenge": "미래 기술 예측",
        "complexity": "높음",
        "innovation": "필요",
    }
    result2 = await system.think_creatively(context2)
    logger.info(f"복잡한 창의적 사고 결과: 아이디어 {len(result2.ideas_generated)}개")
    logger.info(f"생성된 해결책: {len(result2.solutions_created)}개")
    logger.info(f"평균 창의성 수준: {result2.average_creativity_level:.2f}")

    # 3. 시스템 요약
    summary = await system.get_creative_thinking_summary()
    logger.info(f"시스템 요약: {summary}")

    logger.info("=== 창의적 사고 시스템 테스트 완료 ===")
    return system


if __name__ == "__main__":
    asyncio.run(test_creative_thinking_system())
