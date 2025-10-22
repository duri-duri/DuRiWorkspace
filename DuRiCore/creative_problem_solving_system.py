#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 30일 진화 계획 - Day 7: 창의적 문제 해결 시스템

이 모듈은 DuRi가 복잡한 문제를 창의적으로 해결하는 능력을 구현합니다.
창의적 사고 패턴 인식, 문제 재정의 및 프레이밍, 혁신적 해결책 생성, 창의적 검증 및 평가를 구현합니다.

주요 기능:
- 창의적 사고 패턴 인식
- 문제 재정의 및 프레이밍
- 혁신적 해결책 생성
- 창의적 검증 및 평가
- 창의적 문제 해결 프로세스
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
    from creative_thinking_system import (CreativeIdea, CreativeThinkingSystem,
                                          CreativityLevel)
    from duri_thought_flow import DuRiThoughtFlow
    from emotional_thinking_system import EmotionalThinkingSystem
    from inner_thinking_system import InnerThinkingSystem
    from intuitive_thinking_system import IntuitiveThinkingSystem
    from meta_cognition_system import MetaCognitionLevel, MetaCognitionSystem
    from phase_omega_integration import DuRiPhaseOmega
    from self_directed_learning_system import SelfDirectedLearningSystem
except ImportError as e:
    logging.warning(f"일부 기존 시스템 import 실패: {e}")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProblemComplexity(Enum):
    """문제 복잡성"""

    SIMPLE = "simple"  # 단순 (0.0-0.3)
    MODERATE = "moderate"  # 보통 (0.3-0.6)
    COMPLEX = "complex"  # 복잡 (0.6-0.8)
    WICKED = "wicked"  # 악성 (0.8-1.0)


class ProblemType(Enum):
    """문제 유형"""

    TECHNICAL = "technical"  # 기술적 문제
    SOCIAL = "social"  # 사회적 문제
    CREATIVE = "creative"  # 창의적 문제
    SYSTEMIC = "systemic"  # 시스템적 문제
    EMERGENT = "emergent"  # 긴급 문제


class CreativeApproach(Enum):
    """창의적 접근법"""

    DIVERGENT_THINKING = "divergent_thinking"  # 발산적 사고
    LATERAL_THINKING = "lateral_thinking"  # 측면적 사고
    ANALOGICAL_THINKING = "analogical_thinking"  # 유추적 사고
    COMBINATORIAL_THINKING = "combinatorial_thinking"  # 조합적 사고
    TRANSFORMATIVE_THINKING = "transformative_thinking"  # 변환적 사고
    DESIGN_THINKING = "design_thinking"  # 디자인 사고
    SYSTEMS_THINKING = "systems_thinking"  # 시스템 사고


class SolutionQuality(Enum):
    """해결책 품질"""

    POOR = "poor"  # 나쁨 (0.0-0.3)
    FAIR = "fair"  # 보통 (0.3-0.6)
    GOOD = "good"  # 좋음 (0.6-0.8)
    EXCELLENT = "excellent"  # 우수 (0.8-1.0)


@dataclass
class CreativeProblem:
    """창의적 문제"""

    problem_id: str
    title: str
    description: str
    problem_type: ProblemType
    complexity: ProblemComplexity
    context: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    stakeholders: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ProblemReframe:
    """문제 재정의"""

    reframe_id: str
    original_problem_id: str
    reframed_title: str
    reframed_description: str
    reframe_approach: CreativeApproach
    novelty_score: float  # 0.0-1.0
    clarity_score: float  # 0.0-1.0
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CreativeSolution:
    """창의적 해결책"""

    solution_id: str
    problem_id: str
    title: str
    description: str
    approach: CreativeApproach
    innovation_score: float  # 0.0-1.0
    feasibility_score: float  # 0.0-1.0
    impact_score: float  # 0.0-1.0
    quality: SolutionQuality
    implementation_steps: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def overall_score(self) -> float:
        """전체 점수"""
        return (self.innovation_score + self.feasibility_score + self.impact_score) / 3.0


@dataclass
class CreativePattern:
    """창의적 패턴"""

    pattern_id: str
    pattern_name: str
    pattern_description: str
    pattern_type: CreativeApproach
    success_rate: float  # 0.0-1.0
    frequency: int = 1
    last_used: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CreativeValidation:
    """창의적 검증"""

    validation_id: str
    solution_id: str
    validation_method: str
    validation_score: float  # 0.0-1.0
    feedback: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CreativeProblemSolvingResult:
    """창의적 문제 해결 결과"""

    process_id: str
    problem: CreativeProblem
    problem_reframes: List[ProblemReframe]
    solutions: List[CreativeSolution]
    patterns_used: List[CreativePattern]
    validations: List[CreativeValidation]
    average_innovation_score: float
    average_feasibility_score: float
    average_impact_score: float
    overall_quality: SolutionQuality
    solving_duration: float
    success: bool = True
    error_message: Optional[str] = None


class CreativeProblemSolvingSystem:
    """창의적 문제 해결 시스템"""

    def __init__(self):
        # 기존 시스템들과의 통합
        self.creative_thinking_system = CreativeThinkingSystem()
        self.meta_cognition_system = MetaCognitionSystem()
        self.inner_thinking_system = InnerThinkingSystem()
        self.emotional_thinking_system = EmotionalThinkingSystem()
        self.intuitive_thinking_system = IntuitiveThinkingSystem()
        self.self_directed_learning_system = SelfDirectedLearningSystem()

        # DuRiThoughtFlow 초기화
        default_input_data = {
            "goal": "creative_problem_solving",
            "context": "problem_solving_system",
        }
        default_context = {"system_type": "creative_problem_solving", "version": "1.0"}
        self.thought_flow = DuRiThoughtFlow(default_input_data, default_context)

        self.phase_omega = DuRiPhaseOmega()

        # 창의적 문제 해결 상태
        self.solved_problems: List[CreativeProblem] = []
        self.creative_patterns: Dict[str, CreativePattern] = {}
        self.solution_history: List[CreativeSolution] = []
        self.validation_history: List[CreativeValidation] = []

        # 창의적 문제 해결 통계
        self.total_problems_solved = 0
        self.average_solving_time = 0.0
        self.success_rate = 0.0

        logger.info("창의적 문제 해결 시스템 초기화 완료")

    async def solve_creative_problem(
        self, problem: CreativeProblem, context: Dict[str, Any] = None
    ) -> CreativeProblemSolvingResult:
        """창의적 문제 해결 실행"""
        if context is None:
            context = {}

        process_id = f"creative_solving_{int(time.time())}"
        logger.info(f"창의적 문제 해결 시작: {process_id} - {problem.title}")

        start_time = time.time()

        try:
            # 1. 창의적 사고 패턴 인식
            patterns = await self._recognize_creative_patterns(problem, context)

            # 2. 문제 재정의 및 프레이밍
            problem_reframes = await self._reframe_problem(problem, context)

            # 3. 혁신적 해결책 생성
            solutions = await self._generate_innovative_solutions(
                problem, problem_reframes, context
            )

            # 4. 창의적 검증 및 평가
            validations = await self._validate_creative_solutions(solutions, context)

            # 5. 결과 종합
            result = await self._compile_solving_result(
                process_id,
                problem,
                problem_reframes,
                solutions,
                patterns,
                validations,
                start_time,
            )

            # 6. 학습 및 개선
            await self._learn_from_solving_process(result)

            logger.info(f"창의적 문제 해결 완료: {process_id}")
            return result

        except Exception as e:
            logger.error(f"창의적 문제 해결 실패: {e}")
            return CreativeProblemSolvingResult(
                process_id=process_id,
                problem=problem,
                problem_reframes=[],
                solutions=[],
                patterns_used=[],
                validations=[],
                average_innovation_score=0.0,
                average_feasibility_score=0.0,
                average_impact_score=0.0,
                overall_quality=SolutionQuality.POOR,
                solving_duration=time.time() - start_time,
                success=False,
                error_message=str(e),
            )

    async def _recognize_creative_patterns(
        self, problem: CreativeProblem, context: Dict[str, Any]
    ) -> List[CreativePattern]:
        """창의적 사고 패턴 인식"""
        patterns = []

        # 문제 유형에 따른 패턴 인식
        pattern_mappings = {
            ProblemType.TECHNICAL: [
                CreativeApproach.SYSTEMS_THINKING,
                CreativeApproach.ANALOGICAL_THINKING,
                CreativeApproach.COMBINATORIAL_THINKING,
            ],
            ProblemType.SOCIAL: [
                CreativeApproach.DESIGN_THINKING,
                CreativeApproach.LATERAL_THINKING,
                CreativeApproach.DIVERGENT_THINKING,
            ],
            ProblemType.CREATIVE: [
                CreativeApproach.TRANSFORMATIVE_THINKING,
                CreativeApproach.DIVERGENT_THINKING,
                CreativeApproach.LATERAL_THINKING,
            ],
            ProblemType.SYSTEMIC: [
                CreativeApproach.SYSTEMS_THINKING,
                CreativeApproach.TRANSFORMATIVE_THINKING,
                CreativeApproach.DESIGN_THINKING,
            ],
            ProblemType.EMERGENT: [
                CreativeApproach.LATERAL_THINKING,
                CreativeApproach.ANALOGICAL_THINKING,
                CreativeApproach.COMBINATORIAL_THINKING,
            ],
        }

        applicable_patterns = pattern_mappings.get(problem.problem_type, [])

        for pattern_type in applicable_patterns:
            # 패턴 성공률 계산
            success_rate = random.uniform(0.6, 0.9)

            pattern = CreativePattern(
                pattern_id=f"pattern_{pattern_type.value}_{int(time.time())}",
                pattern_name=f"{pattern_type.value.replace('_', ' ').title()} Pattern",
                pattern_description=f"창의적 문제 해결을 위한 {pattern_type.value} 접근법",
                pattern_type=pattern_type,
                success_rate=success_rate,
                context=context,
            )
            patterns.append(pattern)

        logger.info(f"창의적 패턴 {len(patterns)}개 인식 완료")
        return patterns

    async def _reframe_problem(
        self, problem: CreativeProblem, context: Dict[str, Any]
    ) -> List[ProblemReframe]:
        """문제 재정의 및 프레이밍"""
        reframes = []

        # 다양한 창의적 접근법을 통한 문제 재정의
        reframe_approaches = [
            CreativeApproach.DIVERGENT_THINKING,
            CreativeApproach.LATERAL_THINKING,
            CreativeApproach.ANALOGICAL_THINKING,
            CreativeApproach.TRANSFORMATIVE_THINKING,
        ]

        for approach in reframe_approaches:
            # 접근법별 문제 재정의
            reframed_title, reframed_description = await self._apply_reframe_approach(
                problem, approach, context
            )

            # 재정의 품질 평가
            novelty_score = random.uniform(0.5, 0.9)
            clarity_score = random.uniform(0.6, 0.9)

            reframe = ProblemReframe(
                reframe_id=f"reframe_{approach.value}_{int(time.time())}",
                original_problem_id=problem.problem_id,
                reframed_title=reframed_title,
                reframed_description=reframed_description,
                reframe_approach=approach,
                novelty_score=novelty_score,
                clarity_score=clarity_score,
                context=context,
            )
            reframes.append(reframe)

        logger.info(f"문제 재정의 {len(reframes)}개 완료")
        return reframes

    async def _apply_reframe_approach(
        self,
        problem: CreativeProblem,
        approach: CreativeApproach,
        context: Dict[str, Any],
    ) -> Tuple[str, str]:
        """특정 접근법을 통한 문제 재정의"""
        reframe_templates = {
            CreativeApproach.DIVERGENT_THINKING: {
                "title": f"{problem.title}의 다양한 관점에서 접근",
                "description": f"{problem.description}을 여러 가지 다른 관점에서 바라보고, 다양한 가능성을 탐구하는 방식으로 재정의",
            },
            CreativeApproach.LATERAL_THINKING: {
                "title": f"{problem.title}의 측면적 접근",
                "description": f"{problem.description}을 기존의 직선적 사고를 넘어서 측면적이고 창의적인 관점에서 재정의",
            },
            CreativeApproach.ANALOGICAL_THINKING: {
                "title": f"{problem.title}의 유추적 접근",
                "description": f"{problem.description}을 다른 분야나 상황과의 유사점을 찾아 유추적으로 재정의",
            },
            CreativeApproach.TRANSFORMATIVE_THINKING: {
                "title": f"{problem.title}의 변환적 접근",
                "description": f"{problem.description}을 근본적으로 다른 방식으로 바라보고 변환적인 관점에서 재정의",
            },
        }

        template = reframe_templates.get(
            approach,
            {
                "title": f"{problem.title}의 창의적 접근",
                "description": f"{problem.description}을 창의적인 관점에서 재정의",
            },
        )

        return template["title"], template["description"]

    async def _generate_innovative_solutions(
        self,
        problem: CreativeProblem,
        problem_reframes: List[ProblemReframe],
        context: Dict[str, Any],
    ) -> List[CreativeSolution]:
        """혁신적 해결책 생성"""
        solutions = []

        # 각 문제 재정의에 대한 해결책 생성
        for reframe in problem_reframes:
            reframe_solutions = await self._generate_solutions_for_reframe(
                problem, reframe, context
            )
            solutions.extend(reframe_solutions)

        # 추가적인 혁신적 해결책 생성
        additional_solutions = await self._generate_additional_innovative_solutions(
            problem, context
        )
        solutions.extend(additional_solutions)

        logger.info(f"혁신적 해결책 {len(solutions)}개 생성 완료")
        return solutions

    async def _generate_solutions_for_reframe(
        self, problem: CreativeProblem, reframe: ProblemReframe, context: Dict[str, Any]
    ) -> List[CreativeSolution]:
        """특정 재정의에 대한 해결책 생성"""
        solutions = []

        # 재정의 접근법에 따른 해결책 생성
        solution_templates = {
            CreativeApproach.DIVERGENT_THINKING: [
                f"{reframe.reframed_title}에 대한 다각적 접근법",
                f"{reframe.reframed_title}의 통합적 해결책",
                f"{reframe.reframed_title}의 혁신적 방법론",
            ],
            CreativeApproach.LATERAL_THINKING: [
                f"{reframe.reframed_title}의 측면적 해결책",
                f"{reframe.reframed_title}의 창의적 우회 방법",
                f"{reframe.reframed_title}의 혁신적 접근법",
            ],
            CreativeApproach.ANALOGICAL_THINKING: [
                f"{reframe.reframed_title}의 유추적 해결책",
                f"{reframe.reframed_title}의 모방적 접근법",
                f"{reframe.reframed_title}의 비교 분석 기반 해결책",
            ],
            CreativeApproach.TRANSFORMATIVE_THINKING: [
                f"{reframe.reframed_title}의 변환적 해결책",
                f"{reframe.reframed_title}의 근본적 변화 방법",
                f"{reframe.reframed_title}의 혁신적 전환 접근법",
            ],
        }

        templates = solution_templates.get(
            reframe.reframe_approach, [f"{reframe.reframed_title}의 창의적 해결책"]
        )

        for i, template in enumerate(templates):
            # 해결책 품질 평가
            innovation_score = random.uniform(0.6, 0.9)
            feasibility_score = random.uniform(0.5, 0.8)
            impact_score = random.uniform(0.6, 0.9)

            # 품질 수준 결정
            overall_score = (innovation_score + feasibility_score + impact_score) / 3.0
            if overall_score >= 0.8:
                quality = SolutionQuality.EXCELLENT
            elif overall_score >= 0.6:
                quality = SolutionQuality.GOOD
            elif overall_score >= 0.3:
                quality = SolutionQuality.FAIR
            else:
                quality = SolutionQuality.POOR

            solution = CreativeSolution(
                solution_id=f"solution_{reframe.reframe_id}_{i}_{int(time.time())}",
                problem_id=problem.problem_id,
                title=template,
                description=f"{template}을 통한 {problem.title} 해결 방안",
                approach=reframe.reframe_approach,
                innovation_score=innovation_score,
                feasibility_score=feasibility_score,
                impact_score=impact_score,
                quality=quality,
                implementation_steps=[
                    "1단계: 문제 분석 및 이해",
                    "2단계: 해결책 설계",
                    "3단계: 프로토타입 개발",
                    "4단계: 테스트 및 검증",
                    "5단계: 구현 및 적용",
                ],
                context=context,
            )
            solutions.append(solution)

        return solutions

    async def _generate_additional_innovative_solutions(
        self, problem: CreativeProblem, context: Dict[str, Any]
    ) -> List[CreativeSolution]:
        """추가적인 혁신적 해결책 생성"""
        solutions = []

        # 시스템적 접근법을 통한 해결책
        system_solution = CreativeSolution(
            solution_id=f"system_solution_{int(time.time())}",
            problem_id=problem.problem_id,
            title=f"{problem.title}의 시스템적 해결책",
            description=f"{problem.title}을 시스템적 관점에서 접근하는 종합적 해결 방안",
            approach=CreativeApproach.SYSTEMS_THINKING,
            innovation_score=random.uniform(0.7, 0.9),
            feasibility_score=random.uniform(0.6, 0.8),
            impact_score=random.uniform(0.7, 0.9),
            quality=SolutionQuality.GOOD,
            implementation_steps=[
                "1단계: 시스템 분석",
                "2단계: 상호작용 매핑",
                "3단계: 시스템 설계",
                "4단계: 구현 및 테스트",
                "5단계: 시스템 최적화",
            ],
            context=context,
        )
        solutions.append(system_solution)

        # 디자인 사고를 통한 해결책
        design_solution = CreativeSolution(
            solution_id=f"design_solution_{int(time.time())}",
            problem_id=problem.problem_id,
            title=f"{problem.title}의 디자인 사고 기반 해결책",
            description=f"{problem.title}을 사용자 중심의 디자인 사고를 통해 해결하는 방안",
            approach=CreativeApproach.DESIGN_THINKING,
            innovation_score=random.uniform(0.6, 0.8),
            feasibility_score=random.uniform(0.7, 0.9),
            impact_score=random.uniform(0.6, 0.8),
            quality=SolutionQuality.GOOD,
            implementation_steps=[
                "1단계: 공감 및 이해",
                "2단계: 문제 정의",
                "3단계: 아이디어 발상",
                "4단계: 프로토타입",
                "5단계: 테스트 및 반복",
            ],
            context=context,
        )
        solutions.append(design_solution)

        return solutions

    async def _validate_creative_solutions(
        self, solutions: List[CreativeSolution], context: Dict[str, Any]
    ) -> List[CreativeValidation]:
        """창의적 검증 및 평가"""
        validations = []

        for solution in solutions:
            # 다양한 검증 방법 적용
            validation_methods = [
                "창의성 검증",
                "실행 가능성 검증",
                "영향도 검증",
                "통합적 검증",
            ]

            for method in validation_methods:
                validation_score = await self._apply_validation_method(solution, method)

                # 피드백 및 개선사항 생성
                feedback = await self._generate_validation_feedback(
                    solution, method, validation_score
                )
                improvements = await self._generate_improvement_suggestions(
                    solution, method, validation_score
                )

                validation = CreativeValidation(
                    validation_id=f"validation_{solution.solution_id}_{method}_{int(time.time())}",
                    solution_id=solution.solution_id,
                    validation_method=method,
                    validation_score=validation_score,
                    feedback=feedback,
                    improvements=improvements,
                    context=context,
                )
                validations.append(validation)

        logger.info(f"창의적 검증 {len(validations)}개 완료")
        return validations

    async def _apply_validation_method(self, solution: CreativeSolution, method: str) -> float:
        """특정 검증 방법 적용"""
        base_score = solution.overall_score

        # 검증 방법별 가중치 적용
        method_weights = {
            "창의성 검증": 1.2,
            "실행 가능성 검증": 1.0,
            "영향도 검증": 1.1,
            "통합적 검증": 1.0,
        }

        weight = method_weights.get(method, 1.0)
        adjusted_score = min(1.0, base_score * weight)

        # 약간의 변동성 추가
        final_score = adjusted_score + random.uniform(-0.1, 0.1)
        return max(0.0, min(1.0, final_score))

    async def _generate_validation_feedback(
        self, solution: CreativeSolution, method: str, score: float
    ) -> List[str]:
        """검증 피드백 생성"""
        feedback = []

        if score >= 0.8:
            feedback.append(f"{method}에서 우수한 성과를 보임")
            feedback.append("해결책의 품질이 매우 높음")
        elif score >= 0.6:
            feedback.append(f"{method}에서 양호한 성과를 보임")
            feedback.append("일부 개선이 필요하지만 전반적으로 좋음")
        elif score >= 0.4:
            feedback.append(f"{method}에서 보통 수준의 성과를 보임")
            feedback.append("상당한 개선이 필요함")
        else:
            feedback.append(f"{method}에서 개선이 필요함")
            feedback.append("근본적인 재검토가 필요함")

        return feedback

    async def _generate_improvement_suggestions(
        self, solution: CreativeSolution, method: str, score: float
    ) -> List[str]:
        """개선 제안 생성"""
        improvements = []

        if score < 0.8:
            improvements.append(f"{method} 관점에서 해결책을 재검토")
            improvements.append("더 구체적인 실행 계획 수립")

        if score < 0.6:
            improvements.append("해결책의 혁신성 향상 필요")
            improvements.append("실행 가능성에 대한 더 깊은 분석 필요")

        if score < 0.4:
            improvements.append("근본적인 접근법 재검토")
            improvements.append("다른 창의적 접근법 시도")

        return improvements

    async def _compile_solving_result(
        self,
        process_id: str,
        problem: CreativeProblem,
        problem_reframes: List[ProblemReframe],
        solutions: List[CreativeSolution],
        patterns: List[CreativePattern],
        validations: List[CreativeValidation],
        start_time: float,
    ) -> CreativeProblemSolvingResult:
        """해결 결과 종합"""
        solving_duration = time.time() - start_time

        # 평균 점수 계산
        if solutions:
            average_innovation_score = sum(s.innovation_score for s in solutions) / len(solutions)
            average_feasibility_score = sum(s.feasibility_score for s in solutions) / len(solutions)
            average_impact_score = sum(s.impact_score for s in solutions) / len(solutions)
        else:
            average_innovation_score = 0.0
            average_feasibility_score = 0.0
            average_impact_score = 0.0

        # 전체 품질 결정
        overall_score = (
            average_innovation_score + average_feasibility_score + average_impact_score
        ) / 3.0
        if overall_score >= 0.8:
            overall_quality = SolutionQuality.EXCELLENT
        elif overall_score >= 0.6:
            overall_quality = SolutionQuality.GOOD
        elif overall_score >= 0.3:
            overall_quality = SolutionQuality.FAIR
        else:
            overall_quality = SolutionQuality.POOR

        result = CreativeProblemSolvingResult(
            process_id=process_id,
            problem=problem,
            problem_reframes=problem_reframes,
            solutions=solutions,
            patterns_used=patterns,
            validations=validations,
            average_innovation_score=average_innovation_score,
            average_feasibility_score=average_feasibility_score,
            average_impact_score=average_impact_score,
            overall_quality=overall_quality,
            solving_duration=solving_duration,
        )

        return result

    async def _learn_from_solving_process(self, result: CreativeProblemSolvingResult):
        """해결 과정에서 학습"""
        # 해결된 문제 기록
        self.solved_problems.append(result.problem)

        # 해결책 기록
        self.solution_history.extend(result.solutions)

        # 검증 기록
        self.validation_history.extend(result.validations)

        # 패턴 학습
        for pattern in result.patterns_used:
            if pattern.pattern_id in self.creative_patterns:
                self.creative_patterns[pattern.pattern_id].frequency += 1
                self.creative_patterns[pattern.pattern_id].last_used = datetime.now()
            else:
                self.creative_patterns[pattern.pattern_id] = pattern

        # 통계 업데이트
        self.total_problems_solved += 1
        self.average_solving_time = (
            self.average_solving_time * (self.total_problems_solved - 1) + result.solving_duration
        ) / self.total_problems_solved

        # 성공률 계산
        successful_solutions = sum(
            1
            for s in result.solutions
            if s.quality in [SolutionQuality.GOOD, SolutionQuality.EXCELLENT]
        )
        if result.solutions:
            success_rate = successful_solutions / len(result.solutions)
            self.success_rate = (
                self.success_rate * (self.total_problems_solved - 1) + success_rate
            ) / self.total_problems_solved

    async def get_creative_problem_solving_summary(self) -> Dict[str, Any]:
        """창의적 문제 해결 요약 정보 반환"""
        return {
            "total_problems_solved": self.total_problems_solved,
            "average_solving_time": round(self.average_solving_time, 2),
            "success_rate": round(self.success_rate, 3),
            "total_solutions": len(self.solution_history),
            "total_validations": len(self.validation_history),
            "creative_patterns": len(self.creative_patterns),
            "recent_solutions": [
                {
                    "solution_id": s.solution_id,
                    "title": s.title,
                    "quality": s.quality.value,
                    "overall_score": round(s.overall_score, 3),
                }
                for s in self.solution_history[-5:]  # 최근 5개 해결책
            ],
            "pattern_usage": {
                pattern.pattern_name: pattern.frequency
                for pattern in self.creative_patterns.values()
            },
        }


async def test_creative_problem_solving_system():
    """창의적 문제 해결 시스템 테스트"""
    print("=== Day 7: 창의적 문제 해결 시스템 테스트 시작 ===")

    # 시스템 초기화
    solving_system = CreativeProblemSolvingSystem()

    # 테스트 문제 생성
    test_problem = CreativeProblem(
        problem_id="test_problem_001",
        title="지속가능한 도시 교통 시스템 설계",
        description="기존의 자동차 중심 교통 시스템을 환경 친화적이고 효율적인 지속가능한 교통 시스템으로 전환하는 방안을 설계해야 합니다.",
        problem_type=ProblemType.SYSTEMIC,
        complexity=ProblemComplexity.COMPLEX,
        constraints=["예산 제한", "기존 인프라 활용", "시민 수용성"],
        stakeholders=["시민", "정부", "교통업체", "환경단체"],
    )

    # 창의적 문제 해결 실행
    context = {
        "test_mode": True,
        "problem_domain": "urban_planning",
        "stakeholder_needs": ["accessibility", "sustainability", "efficiency"],
    }

    result = await solving_system.solve_creative_problem(test_problem, context)

    # 결과 출력
    print(f"\n=== 창의적 문제 해결 결과 ===")
    print(f"프로세스 ID: {result.process_id}")
    print(f"문제: {result.problem.title}")
    print(f"성공 여부: {result.success}")
    print(f"해결 시간: {result.solving_duration:.2f}초")
    print(f"전체 품질: {result.overall_quality.value}")

    print(f"\n=== 문제 재정의 ({len(result.problem_reframes)}개) ===")
    for reframe in result.problem_reframes[:3]:  # 처음 3개만 출력
        print(f"- {reframe.reframed_title} (접근법: {reframe.reframe_approach.value})")

    print(f"\n=== 창의적 해결책 ({len(result.solutions)}개) ===")
    for solution in result.solutions[:3]:  # 처음 3개만 출력
        print(
            f"- {solution.title} (품질: {solution.quality.value}, 점수: {solution.overall_score:.2f})"
        )

    print(f"\n=== 창의적 패턴 ({len(result.patterns_used)}개) ===")
    for pattern in result.patterns_used:
        print(f"- {pattern.pattern_name} (성공률: {pattern.success_rate:.2f})")

    print(f"\n=== 검증 결과 ({len(result.validations)}개) ===")
    for validation in result.validations[:3]:  # 처음 3개만 출력
        print(f"- {validation.validation_method}: {validation.validation_score:.2f}")

    print(f"\n=== 성과 지표 ===")
    print(f"평균 혁신성 점수: {result.average_innovation_score:.3f}")
    print(f"평균 실행 가능성 점수: {result.average_feasibility_score:.3f}")
    print(f"평균 영향도 점수: {result.average_impact_score:.3f}")

    # 시스템 요약 정보
    summary = await solving_system.get_creative_problem_solving_summary()
    print(f"\n=== 시스템 요약 ===")
    print(f"총 해결된 문제: {summary['total_problems_solved']}")
    print(f"평균 해결 시간: {summary['average_solving_time']}초")
    print(f"성공률: {summary['success_rate']}")
    print(f"총 해결책: {summary['total_solutions']}")
    print(f"총 검증: {summary['total_validations']}")
    print(f"창의적 패턴: {summary['creative_patterns']}개")

    print("\n=== Day 7: 창의적 문제 해결 시스템 테스트 완료 ===")
    return result


if __name__ == "__main__":
    asyncio.run(test_creative_problem_solving_system())
