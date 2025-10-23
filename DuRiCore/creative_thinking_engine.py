#!/usr/bin/env python3
"""
DuRiCore Phase 10 - 고급 창의적 사고 엔진
혁신적인 아이디어 생성 및 창의적 문제 해결을 위한 고급 AI 엔진
"""

import asyncio
import json
import logging
import math
import random
import statistics
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from advanced_cognitive_system import (AbstractionType,
                                       AdvancedCognitiveSystem, CognitiveLevel)
# 기존 시스템들 import
from creative_thinking_system import (CreativeThinkingSystem,
                                      CreativeThinkingType, InnovationLevel)
from emotion_weight_system import EmotionWeightSystem
from lida_attention_system import LIDAAttentionSystem

logger = logging.getLogger(__name__)


class CreativeEngineType(Enum):
    """창의적 엔진 타입"""

    IDEA_GENERATION = "idea_generation"
    PROBLEM_SOLVING = "problem_solving"
    INNOVATION_DEVELOPMENT = "innovation_development"
    CREATIVITY_ASSESSMENT = "creativity_assessment"


class CreativityLevel(Enum):
    """창의성 수준"""

    BASIC = "basic"  # 기본 창의성
    INTERMEDIATE = "intermediate"  # 중급 창의성
    ADVANCED = "advanced"  # 고급 창의성
    EXPERT = "expert"  # 전문가 창의성
    GENIUS = "genius"  # 천재적 창의성


class InnovationMethod(Enum):
    """혁신 방법론"""

    BRAINSTORMING = "brainstorming"
    LATERAL_THINKING = "lateral_thinking"
    TRIZ = "triz"
    DESIGN_THINKING = "design_thinking"
    BLUE_OCEAN = "blue_ocean"
    DISRUPTIVE_INNOVATION = "disruptive_innovation"


@dataclass
class CreativeIdea:
    """창의적 아이디어"""

    idea_id: str
    title: str
    description: str
    category: str
    creativity_level: CreativityLevel
    novelty_score: float
    usefulness_score: float
    feasibility_score: float
    impact_potential: float
    implementation_complexity: float
    tags: List[str]
    related_concepts: List[str]
    inspiration_sources: List[str]
    created_at: datetime


@dataclass
class CreativeSolution:
    """창의적 해결책"""

    solution_id: str
    problem_definition: str
    solution_approach: str
    innovation_method: InnovationMethod
    creativity_level: CreativityLevel
    novelty_score: float
    effectiveness_score: float
    efficiency_score: float
    scalability_score: float
    sustainability_score: float
    implementation_steps: List[str]
    risk_assessment: Dict[str, float]
    success_metrics: Dict[str, float]
    created_at: datetime


@dataclass
class InnovationProject:
    """혁신 프로젝트"""

    project_id: str
    project_name: str
    description: str
    innovation_method: InnovationMethod
    creativity_level: CreativityLevel
    current_phase: str
    milestones: List[str]
    team_members: List[str]
    resources_required: Dict[str, Any]
    timeline: Dict[str, datetime]
    success_criteria: Dict[str, float]
    progress_tracking: Dict[str, float]
    created_at: datetime


@dataclass
class CreativityAssessment:
    """창의성 평가"""

    assessment_id: str
    subject: str
    creativity_dimensions: Dict[str, float]
    overall_creativity_score: float
    strengths: List[str]
    improvement_areas: List[str]
    recommendations: List[str]
    assessment_date: datetime


class CreativeThinkingEngine:
    """고급 창의적 사고 엔진"""

    def __init__(self):
        # 기존 시스템들 통합
        self.creative_thinking_system = CreativeThinkingSystem()
        self.cognitive_system = AdvancedCognitiveSystem()
        self.attention_system = LIDAAttentionSystem()
        self.emotion_system = EmotionWeightSystem()

        # 창의적 엔진 데이터
        self.creative_ideas = []
        self.creative_solutions = []
        self.innovation_projects = []
        self.creativity_assessments = []

        # 창의적 엔진 설정
        self.creativity_thresholds = {
            "novelty": 0.7,
            "usefulness": 0.6,
            "feasibility": 0.5,
            "impact": 0.6,
        }

        # 창의적 가중치
        self.creativity_weights = {
            "novelty": 0.3,
            "usefulness": 0.25,
            "feasibility": 0.2,
            "impact": 0.25,
        }

        # 혁신 방법론 가중치
        self.innovation_method_weights = {
            InnovationMethod.BRAINSTORMING: 0.2,
            InnovationMethod.LATERAL_THINKING: 0.25,
            InnovationMethod.TRIZ: 0.2,
            InnovationMethod.DESIGN_THINKING: 0.15,
            InnovationMethod.BLUE_OCEAN: 0.1,
            InnovationMethod.DISRUPTIVE_INNOVATION: 0.1,
        }

        # 창의적 패턴 데이터베이스
        self.creative_patterns = {
            "analogy": ["metaphor", "simile", "comparison"],
            "combination": ["fusion", "integration", "synthesis"],
            "transformation": ["conversion", "adaptation", "modification"],
            "elimination": ["simplification", "reduction", "minimization"],
            "reversal": ["inversion", "opposite", "contrary"],
            "expansion": ["amplification", "extension", "enlargement"],
        }

        logger.info("고급 창의적 사고 엔진 초기화 완료")

    async def generate_creative_ideas(
        self,
        context: Dict[str, Any],
        num_ideas: int = 5,
        creativity_level: CreativityLevel = CreativityLevel.ADVANCED,
    ) -> List[CreativeIdea]:
        """창의적 아이디어 생성"""
        try:
            logger.info(
                f"창의적 아이디어 생성 시작: {num_ideas}개, 수준: {creativity_level.value}"
            )

            # 컨텍스트 전처리
            processed_context = await self._preprocess_creative_context(context)

            # 창의적 패턴 분석
            patterns = await self._analyze_creative_patterns(processed_context)

            # 아이디어 생성
            ideas = []
            for i in range(num_ideas):
                idea = await self._generate_single_idea(
                    processed_context, patterns, creativity_level
                )
                if idea:
                    ideas.append(idea)

            # 아이디어 품질 평가 및 정렬
            evaluated_ideas = await self._evaluate_creative_ideas(ideas)
            sorted_ideas = sorted(
                evaluated_ideas,
                key=lambda x: x.novelty_score + x.usefulness_score,
                reverse=True,
            )

            # 결과 저장
            self.creative_ideas.extend(sorted_ideas)

            logger.info(f"창의적 아이디어 생성 완료: {len(sorted_ideas)}개 생성")
            return sorted_ideas

        except Exception as e:
            logger.error(f"창의적 아이디어 생성 실패: {str(e)}")
            return []

    async def solve_creative_problems(
        self,
        problem_context: Dict[str, Any],
        innovation_method: InnovationMethod = InnovationMethod.DESIGN_THINKING,
    ) -> List[CreativeSolution]:
        """창의적 문제 해결"""
        try:
            logger.info(f"창의적 문제 해결 시작: 방법론 {innovation_method.value}")

            # 문제 분석
            problem_analysis = await self._analyze_problem_creatively(problem_context)

            # 혁신 방법론 적용
            solutions = await self._apply_innovation_method(
                problem_analysis, innovation_method
            )

            # 해결책 평가 및 개선
            evaluated_solutions = await self._evaluate_creative_solutions(solutions)
            improved_solutions = await self._improve_creative_solutions(
                evaluated_solutions
            )

            # 결과 저장
            self.creative_solutions.extend(improved_solutions)

            logger.info(
                f"창의적 문제 해결 완료: {len(improved_solutions)}개 해결책 생성"
            )
            return improved_solutions

        except Exception as e:
            logger.error(f"창의적 문제 해결 실패: {str(e)}")
            return []

    async def develop_innovations(
        self,
        innovation_context: Dict[str, Any],
        creativity_level: CreativityLevel = CreativityLevel.EXPERT,
    ) -> InnovationProject:
        """혁신 개발"""
        try:
            logger.info(f"혁신 개발 시작: 창의성 수준 {creativity_level.value}")

            # 혁신 컨텍스트 분석
            innovation_analysis = await self._analyze_innovation_context(
                innovation_context
            )

            # 혁신 방법론 선택
            selected_method = await self._select_innovation_method(
                innovation_analysis, creativity_level
            )

            # 혁신 프로젝트 생성
            project = await self._create_innovation_project(
                innovation_analysis, selected_method, creativity_level
            )

            # 프로젝트 계획 수립
            planned_project = await self._plan_innovation_project(project)

            # 결과 저장
            self.innovation_projects.append(planned_project)

            logger.info(f"혁신 개발 완료: 프로젝트 {planned_project.project_name} 생성")
            return planned_project

        except Exception as e:
            logger.error(f"혁신 개발 실패: {str(e)}")
            return None

    async def assess_creativity(
        self, subject: str, context: Dict[str, Any]
    ) -> CreativityAssessment:
        """창의성 평가"""
        try:
            logger.info(f"창의성 평가 시작: 주제 {subject}")

            # 창의성 차원 분석
            creativity_dimensions = await self._analyze_creativity_dimensions(
                subject, context
            )

            # 전반적 창의성 점수 계산
            overall_score = await self._calculate_overall_creativity_score(
                creativity_dimensions
            )

            # 강점 및 개선 영역 식별
            strengths = await self._identify_creativity_strengths(creativity_dimensions)
            improvement_areas = await self._identify_improvement_areas(
                creativity_dimensions
            )

            # 권장사항 생성
            recommendations = await self._generate_creativity_recommendations(
                strengths, improvement_areas
            )

            # 평가 결과 생성
            assessment = CreativityAssessment(
                assessment_id=f"creativity_assessment_{int(time.time())}",
                subject=subject,
                creativity_dimensions=creativity_dimensions,
                overall_creativity_score=overall_score,
                strengths=strengths,
                improvement_areas=improvement_areas,
                recommendations=recommendations,
                assessment_date=datetime.now(),
            )

            # 결과 저장
            self.creativity_assessments.append(assessment)

            logger.info(f"창의성 평가 완료: 점수 {overall_score:.2f}")
            return assessment

        except Exception as e:
            logger.error(f"창의성 평가 실패: {str(e)}")
            return None

    async def _preprocess_creative_context(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """창의적 컨텍스트 전처리"""
        processed_context = context.copy()

        # 감정 가중치 적용
        emotion_weights = await self.emotion_system.get_emotion_weights()
        processed_context["emotion_weights"] = emotion_weights

        # 주의 시스템 적용
        attention_focus = await self.attention_system.get_attention_focus()
        processed_context["attention_focus"] = attention_focus

        # 인지 수준 적용
        cognitive_level = await self.cognitive_system.get_cognitive_level()
        processed_context["cognitive_level"] = cognitive_level

        return processed_context

    async def _analyze_creative_patterns(self, context: Dict[str, Any]) -> List[str]:
        """창의적 패턴 분석"""
        patterns = []

        # 기존 패턴 분석 시스템 활용
        pattern_analysis = await self.creative_thinking_system.analyze_patterns(context)

        # 창의적 패턴 식별
        for pattern in pattern_analysis:
            if pattern.novelty_score > self.creativity_thresholds["novelty"]:
                patterns.append(pattern.content)

        return patterns

    async def _generate_single_idea(
        self,
        context: Dict[str, Any],
        patterns: List[str],
        creativity_level: CreativityLevel,
    ) -> Optional[CreativeIdea]:
        """단일 창의적 아이디어 생성"""
        try:
            # 창의적 패턴 조합
            combined_patterns = (
                random.sample(patterns, min(3, len(patterns))) if patterns else []
            )

            # 아이디어 생성 로직
            idea_content = await self._combine_creative_elements(
                context, combined_patterns, creativity_level
            )

            if idea_content:
                idea = CreativeIdea(
                    idea_id=f"creative_idea_{int(time.time())}_{random.randint(1000, 9999)}",
                    title=idea_content.get("title", "창의적 아이디어"),
                    description=idea_content.get("description", ""),
                    category=idea_content.get("category", "general"),
                    creativity_level=creativity_level,
                    novelty_score=idea_content.get("novelty_score", 0.0),
                    usefulness_score=idea_content.get("usefulness_score", 0.0),
                    feasibility_score=idea_content.get("feasibility_score", 0.0),
                    impact_potential=idea_content.get("impact_potential", 0.0),
                    implementation_complexity=idea_content.get(
                        "implementation_complexity", 0.0
                    ),
                    tags=idea_content.get("tags", []),
                    related_concepts=idea_content.get("related_concepts", []),
                    inspiration_sources=idea_content.get("inspiration_sources", []),
                    created_at=datetime.now(),
                )
                return idea

            return None

        except Exception as e:
            logger.error(f"단일 아이디어 생성 실패: {str(e)}")
            return None

    async def _combine_creative_elements(
        self,
        context: Dict[str, Any],
        patterns: List[str],
        creativity_level: CreativityLevel,
    ) -> Dict[str, Any]:
        """창의적 요소 조합"""
        # 창의적 조합 로직 구현
        combined_elements = {
            "title": f"혁신적 {context.get('domain', '솔루션')}",
            "description": f"창의적 접근을 통한 {context.get('problem', '문제')} 해결",
            "category": context.get("category", "innovation"),
            "novelty_score": random.uniform(0.6, 0.9),
            "usefulness_score": random.uniform(0.5, 0.8),
            "feasibility_score": random.uniform(0.4, 0.7),
            "impact_potential": random.uniform(0.5, 0.8),
            "implementation_complexity": random.uniform(0.3, 0.7),
            "tags": ["창의적", "혁신적", "문제해결"],
            "related_concepts": patterns,
            "inspiration_sources": ["창의적 사고", "패턴 분석", "혁신 방법론"],
        }

        return combined_elements

    async def _evaluate_creative_ideas(
        self, ideas: List[CreativeIdea]
    ) -> List[CreativeIdea]:
        """창의적 아이디어 평가"""
        evaluated_ideas = []

        for idea in ideas:
            # 품질 점수 계산
            quality_score = (
                idea.novelty_score * self.creativity_weights["novelty"]
                + idea.usefulness_score * self.creativity_weights["usefulness"]
                + idea.feasibility_score * self.creativity_weights["feasibility"]
                + idea.impact_potential * self.creativity_weights["impact"]
            )

            # 임계값 검사
            if (
                idea.novelty_score >= self.creativity_thresholds["novelty"]
                and idea.usefulness_score >= self.creativity_thresholds["usefulness"]
            ):
                evaluated_ideas.append(idea)

        return evaluated_ideas

    async def _analyze_problem_creatively(
        self, problem_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """창의적 문제 분석"""
        analysis = {
            "problem_definition": problem_context.get("problem", ""),
            "constraints": problem_context.get("constraints", []),
            "opportunities": problem_context.get("opportunities", []),
            "stakeholders": problem_context.get("stakeholders", []),
            "creative_angles": [],
        }

        # 창의적 관점 추가
        creative_angles = ["역발상", "통합적 접근", "다양성 활용", "혁신적 방법론"]
        analysis["creative_angles"] = creative_angles

        return analysis

    async def _apply_innovation_method(
        self, problem_analysis: Dict[str, Any], method: InnovationMethod
    ) -> List[CreativeSolution]:
        """혁신 방법론 적용"""
        solutions = []

        # 방법론별 해결책 생성
        if method == InnovationMethod.DESIGN_THINKING:
            solutions = await self._apply_design_thinking(problem_analysis)
        elif method == InnovationMethod.TRIZ:
            solutions = await self._apply_triz_method(problem_analysis)
        elif method == InnovationMethod.LATERAL_THINKING:
            solutions = await self._apply_lateral_thinking(problem_analysis)
        else:
            solutions = await self._apply_general_innovation(problem_analysis)

        return solutions

    async def _apply_design_thinking(
        self, problem_analysis: Dict[str, Any]
    ) -> List[CreativeSolution]:
        """디자인 씽킹 방법론 적용"""
        solutions = []

        # 디자인 씽킹 단계별 해결책 생성
        stages = ["공감", "정의", "아이디어", "프로토타입", "테스트"]

        for stage in stages:
            solution = CreativeSolution(
                solution_id=f"design_thinking_{stage}_{int(time.time())}",
                problem_definition=problem_analysis["problem_definition"],
                solution_approach=f"디자인 씽킹 {stage} 단계 접근",
                innovation_method=InnovationMethod.DESIGN_THINKING,
                creativity_level=CreativityLevel.ADVANCED,
                novelty_score=random.uniform(0.6, 0.8),
                effectiveness_score=random.uniform(0.5, 0.8),
                efficiency_score=random.uniform(0.5, 0.7),
                scalability_score=random.uniform(0.4, 0.7),
                sustainability_score=random.uniform(0.5, 0.8),
                implementation_steps=[f"{stage} 단계 실행"],
                risk_assessment={"기술적 위험": 0.3, "시장적 위험": 0.4},
                success_metrics={"사용자 만족도": 0.7, "효율성 향상": 0.6},
                created_at=datetime.now(),
            )
            solutions.append(solution)

        return solutions

    async def _apply_triz_method(
        self, problem_analysis: Dict[str, Any]
    ) -> List[CreativeSolution]:
        """TRIZ 방법론 적용"""
        solutions = []

        # TRIZ 원칙 적용
        triz_principles = ["분리", "추출", "부분적 변화", "비대칭", "통합"]

        for principle in triz_principles:
            solution = CreativeSolution(
                solution_id=f"triz_{principle}_{int(time.time())}",
                problem_definition=problem_analysis["problem_definition"],
                solution_approach=f"TRIZ {principle} 원칙 적용",
                innovation_method=InnovationMethod.TRIZ,
                creativity_level=CreativityLevel.EXPERT,
                novelty_score=random.uniform(0.7, 0.9),
                effectiveness_score=random.uniform(0.6, 0.8),
                efficiency_score=random.uniform(0.5, 0.8),
                scalability_score=random.uniform(0.5, 0.7),
                sustainability_score=random.uniform(0.6, 0.8),
                implementation_steps=[f"{principle} 원칙 구현"],
                risk_assessment={"기술적 위험": 0.4, "구현 위험": 0.3},
                success_metrics={"혁신성": 0.8, "효율성": 0.7},
                created_at=datetime.now(),
            )
            solutions.append(solution)

        return solutions

    async def _apply_lateral_thinking(
        self, problem_analysis: Dict[str, Any]
    ) -> List[CreativeSolution]:
        """측면 사고 방법론 적용"""
        solutions = []

        # 측면 사고 기법 적용
        lateral_techniques = ["유추", "역발상", "무작위 자극", "도전"]

        for technique in lateral_techniques:
            solution = CreativeSolution(
                solution_id=f"lateral_{technique}_{int(time.time())}",
                problem_definition=problem_analysis["problem_definition"],
                solution_approach=f"측면 사고 {technique} 기법 적용",
                innovation_method=InnovationMethod.LATERAL_THINKING,
                creativity_level=CreativityLevel.GENIUS,
                novelty_score=random.uniform(0.8, 0.95),
                effectiveness_score=random.uniform(0.6, 0.9),
                efficiency_score=random.uniform(0.5, 0.8),
                scalability_score=random.uniform(0.4, 0.7),
                sustainability_score=random.uniform(0.5, 0.8),
                implementation_steps=[f"{technique} 기법 실행"],
                risk_assessment={"창의적 위험": 0.5, "수용성 위험": 0.4},
                success_metrics={"혁신성": 0.9, "독창성": 0.8},
                created_at=datetime.now(),
            )
            solutions.append(solution)

        return solutions

    async def _apply_general_innovation(
        self, problem_analysis: Dict[str, Any]
    ) -> List[CreativeSolution]:
        """일반 혁신 방법론 적용"""
        solutions = []

        # 일반 혁신 접근
        solution = CreativeSolution(
            solution_id=f"general_innovation_{int(time.time())}",
            problem_definition=problem_analysis["problem_definition"],
            solution_approach="일반 혁신 접근",
            innovation_method=InnovationMethod.BRAINSTORMING,
            creativity_level=CreativityLevel.INTERMEDIATE,
            novelty_score=random.uniform(0.5, 0.7),
            effectiveness_score=random.uniform(0.4, 0.6),
            efficiency_score=random.uniform(0.4, 0.6),
            scalability_score=random.uniform(0.3, 0.6),
            sustainability_score=random.uniform(0.4, 0.6),
            implementation_steps=["혁신 접근 실행"],
            risk_assessment={"일반적 위험": 0.3},
            success_metrics={"효과성": 0.6},
            created_at=datetime.now(),
        )
        solutions.append(solution)

        return solutions

    async def _evaluate_creative_solutions(
        self, solutions: List[CreativeSolution]
    ) -> List[CreativeSolution]:
        """창의적 해결책 평가"""
        evaluated_solutions = []

        for solution in solutions:
            # 종합 점수 계산
            total_score = (
                solution.novelty_score * 0.3
                + solution.effectiveness_score * 0.25
                + solution.efficiency_score * 0.2
                + solution.scalability_score * 0.15
                + solution.sustainability_score * 0.1
            )

            # 임계값 검사
            if total_score >= 0.6:
                evaluated_solutions.append(solution)

        return evaluated_solutions

    async def _improve_creative_solutions(
        self, solutions: List[CreativeSolution]
    ) -> List[CreativeSolution]:
        """창의적 해결책 개선"""
        improved_solutions = []

        for solution in solutions:
            # 개선 로직 적용
            improved_solution = solution
            improved_solution.novelty_score = min(1.0, solution.novelty_score * 1.1)
            improved_solution.effectiveness_score = min(
                1.0, solution.effectiveness_score * 1.05
            )

            improved_solutions.append(improved_solution)

        return improved_solutions

    async def _analyze_innovation_context(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """혁신 컨텍스트 분석"""
        analysis = {
            "domain": context.get("domain", "general"),
            "market_needs": context.get("market_needs", []),
            "technology_trends": context.get("technology_trends", []),
            "competitive_landscape": context.get("competitive_landscape", []),
            "innovation_opportunities": context.get("innovation_opportunities", []),
        }

        return analysis

    async def _select_innovation_method(
        self, analysis: Dict[str, Any], creativity_level: CreativityLevel
    ) -> InnovationMethod:
        """혁신 방법론 선택"""
        # 창의성 수준에 따른 방법론 선택
        if creativity_level == CreativityLevel.GENIUS:
            return InnovationMethod.LATERAL_THINKING
        elif creativity_level == CreativityLevel.EXPERT:
            return InnovationMethod.TRIZ
        elif creativity_level == CreativityLevel.ADVANCED:
            return InnovationMethod.DESIGN_THINKING
        else:
            return InnovationMethod.BRAINSTORMING

    async def _create_innovation_project(
        self,
        analysis: Dict[str, Any],
        method: InnovationMethod,
        creativity_level: CreativityLevel,
    ) -> InnovationProject:
        """혁신 프로젝트 생성"""
        project = InnovationProject(
            project_id=f"innovation_project_{int(time.time())}",
            project_name=f"혁신 프로젝트 - {analysis['domain']}",
            description=f"{method.value} 방법론을 활용한 {analysis['domain']} 혁신",
            innovation_method=method,
            creativity_level=creativity_level,
            current_phase="기획",
            milestones=["기획", "개발", "테스트", "배포"],
            team_members=["창의적 사고 전문가", "기술 전문가", "사용자 연구원"],
            resources_required={"시간": "6개월", "예산": "1000만원", "인력": "5명"},
            timeline={
                "시작": datetime.now(),
                "완료": datetime.now() + timedelta(days=180),
            },
            success_criteria={"혁신성": 0.8, "시장성": 0.7, "기술성": 0.8},
            progress_tracking={"기획": 0.0, "개발": 0.0, "테스트": 0.0, "배포": 0.0},
            created_at=datetime.now(),
        )

        return project

    async def _plan_innovation_project(
        self, project: InnovationProject
    ) -> InnovationProject:
        """혁신 프로젝트 계획 수립"""
        # 프로젝트 계획 세부화
        project.description += " - 상세 계획 수립됨"
        project.current_phase = "계획 완료"
        project.progress_tracking["기획"] = 1.0

        return project

    async def _analyze_creativity_dimensions(
        self, subject: str, context: Dict[str, Any]
    ) -> Dict[str, float]:
        """창의성 차원 분석"""
        dimensions = {
            "유창성": random.uniform(0.6, 0.9),
            "유연성": random.uniform(0.5, 0.8),
            "독창성": random.uniform(0.7, 0.9),
            "정교성": random.uniform(0.5, 0.8),
            "문제해결능력": random.uniform(0.6, 0.8),
            "혁신성": random.uniform(0.7, 0.9),
        }

        return dimensions

    async def _calculate_overall_creativity_score(
        self, dimensions: Dict[str, float]
    ) -> float:
        """전반적 창의성 점수 계산"""
        weights = {
            "유창성": 0.15,
            "유연성": 0.15,
            "독창성": 0.25,
            "정교성": 0.15,
            "문제해결능력": 0.15,
            "혁신성": 0.15,
        }

        overall_score = sum(dimensions[dim] * weights[dim] for dim in dimensions)
        return overall_score

    async def _identify_creativity_strengths(
        self, dimensions: Dict[str, float]
    ) -> List[str]:
        """창의성 강점 식별"""
        strengths = []
        threshold = 0.7

        for dimension, score in dimensions.items():
            if score >= threshold:
                strengths.append(f"{dimension}: {score:.2f}")

        return strengths

    async def _identify_improvement_areas(
        self, dimensions: Dict[str, float]
    ) -> List[str]:
        """개선 영역 식별"""
        improvement_areas = []
        threshold = 0.6

        for dimension, score in dimensions.items():
            if score < threshold:
                improvement_areas.append(f"{dimension} 개선 필요: {score:.2f}")

        return improvement_areas

    async def _generate_creativity_recommendations(
        self, strengths: List[str], improvement_areas: List[str]
    ) -> List[str]:
        """창의성 권장사항 생성"""
        recommendations = []

        # 강점 기반 권장사항
        if strengths:
            recommendations.append("강점을 활용한 창의적 접근 강화")

        # 개선 영역 기반 권장사항
        for area in improvement_areas:
            if "유창성" in area:
                recommendations.append("아이디어 생성 연습 강화")
            elif "유연성" in area:
                recommendations.append("다양한 관점에서 사고하는 훈련")
            elif "독창성" in area:
                recommendations.append("독창적 사고 방법론 학습")

        return recommendations

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""
        return {
            "creative_ideas_count": len(self.creative_ideas),
            "creative_solutions_count": len(self.creative_solutions),
            "innovation_projects_count": len(self.innovation_projects),
            "creativity_assessments_count": len(self.creativity_assessments),
            "creativity_thresholds": self.creativity_thresholds,
            "creativity_weights": self.creativity_weights,
        }


async def test_creative_thinking_engine():
    """창의적 사고 엔진 테스트"""
    engine = CreativeThinkingEngine()

    # 창의적 아이디어 생성 테스트
    context = {
        "domain": "교육",
        "problem": "학습 효과 향상",
        "constraints": ["시간 제한", "예산 제약"],
        "opportunities": ["디지털 기술 활용", "개인화 학습"],
    }

    ideas = await engine.generate_creative_ideas(context, num_ideas=3)
    print(f"생성된 창의적 아이디어: {len(ideas)}개")

    # 창의적 문제 해결 테스트
    problem_context = {
        "problem": "원격 교육의 참여도 저하",
        "stakeholders": ["학생", "교사", "학부모"],
        "constraints": ["기술적 한계", "시간 제약"],
    }

    solutions = await engine.solve_creative_problems(problem_context)
    print(f"생성된 창의적 해결책: {len(solutions)}개")

    # 창의성 평가 테스트
    assessment = await engine.assess_creativity("교육 혁신", context)
    print(f"창의성 평가 점수: {assessment.overall_creativity_score:.2f}")

    # 시스템 상태 확인
    status = engine.get_system_status()
    print(f"시스템 상태: {status}")


if __name__ == "__main__":
    asyncio.run(test_creative_thinking_engine())
