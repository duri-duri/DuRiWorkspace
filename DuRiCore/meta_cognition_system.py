#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 30일 진화 계획 - Day 5: 메타 인식 시스템

이 모듈은 DuRi가 자신의 사고 과정을 인식하고 분석하는 메타 인식 능력을 구현합니다.
사고 과정 모니터링, 자기 성찰 능력 강화, 사고 품질 평가 시스템, 메타 인식 기반 개선을 구현합니다.

주요 기능:
- 사고 과정 모니터링
- 자기 성찰 능력 강화
- 사고 품질 평가 시스템
- 메타 인식 기반 개선
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
    from creative_thinking_system import CreativeIdea, CreativeThinkingSystem
    from duri_thought_flow import DuRiThoughtFlow
    from emotional_thinking_system import EmotionalState, EmotionalThinkingSystem
    from inner_thinking_system import InnerThinkingSystem, ThoughtDepth
    from intuitive_thinking_system import IntuitivePattern, IntuitiveThinkingSystem
    from phase_omega_integration import DuRiPhaseOmega
except ImportError as e:
    logging.warning(f"일부 기존 시스템 import 실패: {e}")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MetaCognitionLevel(Enum):
    """메타 인식 수준"""

    BASIC = "basic"  # 기본 (0.0-0.3)
    ENHANCED = "enhanced"  # 향상 (0.3-0.6)
    ADVANCED = "advanced"  # 고급 (0.6-0.8)
    EXCEPTIONAL = "exceptional"  # 예외적 (0.8-1.0)


class ThinkingQuality(Enum):
    """사고 품질"""

    POOR = "poor"  # 나쁨 (0.0-0.3)
    FAIR = "fair"  # 보통 (0.3-0.6)
    GOOD = "good"  # 좋음 (0.6-0.8)
    EXCELLENT = "excellent"  # 우수 (0.8-1.0)


class ReflectionType(Enum):
    """성찰 유형"""

    OBSERVATION = "observation"  # 관찰
    ANALYSIS = "analysis"  # 분석
    EVALUATION = "evaluation"  # 평가
    SYNTHESIS = "synthesis"  # 종합
    INTEGRATION = "integration"  # 통합


@dataclass
class ThinkingProcess:
    """사고 과정"""

    process_id: str
    thinking_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    quality_score: float = 0.0
    meta_cognition_level: MetaCognitionLevel = MetaCognitionLevel.BASIC
    context: Dict[str, Any] = field(default_factory=dict)
    insights: List[str] = field(default_factory=list)


@dataclass
class SelfReflection:
    """자기 성찰"""

    reflection_id: str
    reflection_type: ReflectionType
    content: str
    depth_score: float  # 0.0-1.0
    insight_quality: float  # 0.0-1.0
    meta_cognition_level: MetaCognitionLevel
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ThinkingQualityAssessment:
    """사고 품질 평가"""

    assessment_id: str
    thinking_process_id: str
    overall_quality: ThinkingQuality
    clarity_score: float  # 0.0-1.0
    logic_score: float  # 0.0-1.0
    creativity_score: float  # 0.0-1.0
    efficiency_score: float  # 0.0-1.0
    depth_score: float  # 0.0-1.0
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class MetaCognitionInsight:
    """메타 인식 통찰"""

    insight_id: str
    insight: str
    meta_cognition_level: MetaCognitionLevel
    applicability: float  # 0.0-1.0
    novelty_score: float  # 0.0-1.0
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class MetaCognitionResult:
    """메타 인식 결과"""

    process_id: str
    thinking_processes: List[ThinkingProcess]
    self_reflections: List[SelfReflection]
    quality_assessments: List[ThinkingQualityAssessment]
    insights_discovered: List[MetaCognitionInsight]
    average_meta_cognition_level: float
    overall_thinking_quality: float
    thinking_duration: float
    success: bool = True
    error_message: Optional[str] = None


class MetaCognitionSystem:
    """메타 인식 시스템"""

    def __init__(self):
        # 기존 시스템들과의 통합
        self.inner_thinking = None
        self.emotional_thinking = None
        self.intuitive_thinking = None
        self.creative_thinking = None
        self.thought_flow = None
        self.phase_omega = None

        # 메타 인식 시스템 데이터
        self.thinking_processes: List[ThinkingProcess] = []
        self.self_reflections: List[SelfReflection] = []
        self.quality_assessments: List[ThinkingQualityAssessment] = []
        self.meta_insights: List[MetaCognitionInsight] = []
        self.meta_cognition_database: Dict[str, Any] = {}

        # 메타 인식 설정
        self.meta_cognition_thresholds = {
            "quality_low": 0.3,
            "quality_moderate": 0.6,
            "quality_high": 0.8,
            "reflection_depth_low": 0.3,
            "reflection_depth_moderate": 0.6,
            "reflection_depth_high": 0.8,
        }

        # 메타 인식 가중치
        self.meta_cognition_weights = {
            "clarity": 0.25,
            "logic": 0.25,
            "creativity": 0.2,
            "efficiency": 0.15,
            "depth": 0.15,
        }

        # 사고 과정 모니터링
        self.thinking_monitor = {}
        self.process_tracker = {}

        # 자기 성찰 능력
        self.reflection_engine = {}
        self.insight_generator = {}

        # 사고 품질 평가
        self.quality_evaluator = {}
        self.assessment_engine = {}

        # 메타 인식 기반 개선
        self.improvement_engine = {}
        self.optimization_system = {}

        logger.info("메타 인식 시스템 초기화 완료")

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

            # 창의적 사고 시스템 통합
            if "CreativeThinkingSystem" in globals():
                self.creative_thinking = CreativeThinkingSystem()
                logger.info("창의적 사고 시스템 통합 완료")

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

    async def think_with_meta_cognition(
        self, context: Dict[str, Any]
    ) -> MetaCognitionResult:
        """메타 인식을 통한 사고 실행"""
        logger.info(f"=== 메타 인식 사고 시작 ===")

        start_time = datetime.now()
        process_id = f"meta_cognition_{start_time.strftime('%Y%m%d_%H%M%S')}"

        try:
            # 1. 사고 과정 모니터링
            thinking_processes = await self._monitor_thinking_processes(context)

            # 2. 자기 성찰 실행
            self_reflections = await self._perform_self_reflection(
                context, thinking_processes
            )

            # 3. 사고 품질 평가
            quality_assessments = await self._assess_thinking_quality(
                thinking_processes
            )

            # 4. 메타 인식 통찰 발견
            meta_insights = await self._discover_meta_cognition_insights(
                context, thinking_processes, self_reflections, quality_assessments
            )

            # 5. 메타 인식 기반 개선
            improvements = await self._apply_meta_cognition_improvements(
                thinking_processes, self_reflections, quality_assessments
            )

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # 6. 결과 생성
            result = MetaCognitionResult(
                process_id=process_id,
                thinking_processes=thinking_processes,
                self_reflections=self_reflections,
                quality_assessments=quality_assessments,
                insights_discovered=meta_insights,
                average_meta_cognition_level=await self._calculate_average_meta_cognition_level(
                    thinking_processes, self_reflections, meta_insights
                ),
                overall_thinking_quality=await self._calculate_overall_thinking_quality(
                    quality_assessments
                ),
                thinking_duration=duration,
                success=True,
            )

            # 7. 데이터 저장
            self.thinking_processes.extend(thinking_processes)
            self.self_reflections.extend(self_reflections)
            self.quality_assessments.extend(quality_assessments)
            self.meta_insights.extend(meta_insights)

            logger.info(
                f"=== 메타 인식 사고 완료 - 소요시간: {duration:.2f}초, 사고과정: {len(thinking_processes)}개 ==="
            )
            return result

        except Exception as e:
            logger.error(f"메타 인식 사고 중 오류 발생: {e}")
            return MetaCognitionResult(
                process_id=process_id,
                thinking_processes=[],
                self_reflections=[],
                quality_assessments=[],
                insights_discovered=[],
                average_meta_cognition_level=0.0,
                overall_thinking_quality=0.0,
                thinking_duration=0.0,
                success=False,
                error_message=str(e),
            )

    async def _monitor_thinking_processes(
        self, context: Dict[str, Any]
    ) -> List[ThinkingProcess]:
        """사고 과정 모니터링"""
        processes = []

        # 1. 내적 사고 과정 모니터링
        if self.inner_thinking:
            inner_process = await self._monitor_inner_thinking(context)
            processes.append(inner_process)

        # 2. 감정적 사고 과정 모니터링
        if self.emotional_thinking:
            emotional_process = await self._monitor_emotional_thinking(context)
            processes.append(emotional_process)

        # 3. 직관적 사고 과정 모니터링
        if self.intuitive_thinking:
            intuitive_process = await self._monitor_intuitive_thinking(context)
            processes.append(intuitive_process)

        # 4. 창의적 사고 과정 모니터링
        if self.creative_thinking:
            creative_process = await self._monitor_creative_thinking(context)
            processes.append(creative_process)

        return processes

    async def _monitor_inner_thinking(self, context: Dict[str, Any]) -> ThinkingProcess:
        """내적 사고 과정 모니터링"""
        start_time = datetime.now()
        process_id = f"inner_thinking_{start_time.strftime('%Y%m%d_%H%M%S')}"

        # 내적 사고 실행
        if self.inner_thinking:
            inner_result = await self.inner_thinking.think_deeply(str(context))
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            process = ThinkingProcess(
                process_id=process_id,
                thinking_type="inner_thinking",
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                quality_score=(
                    inner_result.self_reflection_score
                    if hasattr(inner_result, "self_reflection_score")
                    else 0.5
                ),
                meta_cognition_level=MetaCognitionLevel.ENHANCED,
                context={
                    "inner_thinking_result": (
                        inner_result.__dict__
                        if hasattr(inner_result, "__dict__")
                        else {}
                    )
                },
            )
            return process

        return ThinkingProcess(
            process_id=process_id,
            thinking_type="inner_thinking",
            start_time=start_time,
            end_time=start_time,
            duration=0.0,
            quality_score=0.0,
            meta_cognition_level=MetaCognitionLevel.BASIC,
        )

    async def _monitor_emotional_thinking(
        self, context: Dict[str, Any]
    ) -> ThinkingProcess:
        """감정적 사고 과정 모니터링"""
        start_time = datetime.now()
        process_id = f"emotional_thinking_{start_time.strftime('%Y%m%d_%H%M%S')}"

        # 감정적 사고 실행
        if self.emotional_thinking:
            emotional_result = await self.emotional_thinking.think_with_emotion(context)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            process = ThinkingProcess(
                process_id=process_id,
                thinking_type="emotional_thinking",
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                quality_score=(
                    emotional_result.emotional_accuracy
                    if hasattr(emotional_result, "emotional_accuracy")
                    else 0.5
                ),
                meta_cognition_level=MetaCognitionLevel.ENHANCED,
                context={
                    "emotional_thinking_result": (
                        emotional_result.__dict__
                        if hasattr(emotional_result, "__dict__")
                        else {}
                    )
                },
            )
            return process

        return ThinkingProcess(
            process_id=process_id,
            thinking_type="emotional_thinking",
            start_time=start_time,
            end_time=start_time,
            duration=0.0,
            quality_score=0.0,
            meta_cognition_level=MetaCognitionLevel.BASIC,
        )

    async def _monitor_intuitive_thinking(
        self, context: Dict[str, Any]
    ) -> ThinkingProcess:
        """직관적 사고 과정 모니터링"""
        start_time = datetime.now()
        process_id = f"intuitive_thinking_{start_time.strftime('%Y%m%d_%H%M%S')}"

        # 직관적 사고 실행
        if self.intuitive_thinking:
            intuitive_result = await self.intuitive_thinking.think_intuitively(context)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            process = ThinkingProcess(
                process_id=process_id,
                thinking_type="intuitive_thinking",
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                quality_score=(
                    intuitive_result.average_confidence
                    if hasattr(intuitive_result, "average_confidence")
                    else 0.5
                ),
                meta_cognition_level=MetaCognitionLevel.ENHANCED,
                context={
                    "intuitive_thinking_result": (
                        intuitive_result.__dict__
                        if hasattr(intuitive_result, "__dict__")
                        else {}
                    )
                },
            )
            return process

        return ThinkingProcess(
            process_id=process_id,
            thinking_type="intuitive_thinking",
            start_time=start_time,
            end_time=start_time,
            duration=0.0,
            quality_score=0.0,
            meta_cognition_level=MetaCognitionLevel.BASIC,
        )

    async def _monitor_creative_thinking(
        self, context: Dict[str, Any]
    ) -> ThinkingProcess:
        """창의적 사고 과정 모니터링"""
        start_time = datetime.now()
        process_id = f"creative_thinking_{start_time.strftime('%Y%m%d_%H%M%S')}"

        # 창의적 사고 실행
        if self.creative_thinking:
            creative_result = await self.creative_thinking.think_creatively(context)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            process = ThinkingProcess(
                process_id=process_id,
                thinking_type="creative_thinking",
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                quality_score=(
                    creative_result.average_creativity_level
                    if hasattr(creative_result, "average_creativity_level")
                    else 0.5
                ),
                meta_cognition_level=MetaCognitionLevel.ENHANCED,
                context={
                    "creative_thinking_result": (
                        creative_result.__dict__
                        if hasattr(creative_result, "__dict__")
                        else {}
                    )
                },
            )
            return process

        return ThinkingProcess(
            process_id=process_id,
            thinking_type="creative_thinking",
            start_time=start_time,
            end_time=start_time,
            duration=0.0,
            quality_score=0.0,
            meta_cognition_level=MetaCognitionLevel.BASIC,
        )

    async def _perform_self_reflection(
        self, context: Dict[str, Any], thinking_processes: List[ThinkingProcess]
    ) -> List[SelfReflection]:
        """자기 성찰 실행"""
        reflections = []

        # 1. 관찰적 성찰
        observation_reflection = await self._create_observation_reflection(
            context, thinking_processes
        )
        reflections.append(observation_reflection)

        # 2. 분석적 성찰
        analysis_reflection = await self._create_analysis_reflection(
            context, thinking_processes
        )
        reflections.append(analysis_reflection)

        # 3. 평가적 성찰
        evaluation_reflection = await self._create_evaluation_reflection(
            context, thinking_processes
        )
        reflections.append(evaluation_reflection)

        # 4. 종합적 성찰
        synthesis_reflection = await self._create_synthesis_reflection(
            context, thinking_processes
        )
        reflections.append(synthesis_reflection)

        # 5. 통합적 성찰
        integration_reflection = await self._create_integration_reflection(
            context, thinking_processes
        )
        reflections.append(integration_reflection)

        return reflections

    async def _create_observation_reflection(
        self, context: Dict[str, Any], thinking_processes: List[ThinkingProcess]
    ) -> SelfReflection:
        """관찰적 성찰 생성"""
        reflection_id = f"observation_reflection_{len(self.self_reflections)}"

        # 관찰 내용 생성
        observation_content = f"사고 과정을 관찰한 결과, {len(thinking_processes)}개의 사고 과정이 실행되었습니다."

        if thinking_processes:
            avg_quality = np.mean([p.quality_score for p in thinking_processes])
            observation_content += f" 평균 품질 점수는 {avg_quality:.2f}입니다."

        reflection = SelfReflection(
            reflection_id=reflection_id,
            reflection_type=ReflectionType.OBSERVATION,
            content=observation_content,
            depth_score=0.6,
            insight_quality=0.5,
            meta_cognition_level=MetaCognitionLevel.ENHANCED,
            context={"thinking_processes_count": len(thinking_processes)},
        )

        return reflection

    async def _create_analysis_reflection(
        self, context: Dict[str, Any], thinking_processes: List[ThinkingProcess]
    ) -> SelfReflection:
        """분석적 성찰 생성"""
        reflection_id = f"analysis_reflection_{len(self.self_reflections)}"

        # 분석 내용 생성
        analysis_content = "사고 과정을 분석한 결과, "

        if thinking_processes:
            thinking_types = [p.thinking_type for p in thinking_processes]
            type_counts = defaultdict(int)
            for t in thinking_types:
                type_counts[t] += 1

            analysis_content += (
                f"다양한 사고 유형({', '.join(type_counts.keys())})이 활용되었습니다."
            )

            # 품질 분석
            quality_scores = [p.quality_score for p in thinking_processes]
            if quality_scores:
                best_quality = max(quality_scores)
                worst_quality = min(quality_scores)
                analysis_content += f" 최고 품질: {best_quality:.2f}, 최저 품질: {worst_quality:.2f}입니다."
        else:
            analysis_content += "분석할 사고 과정이 없습니다."

        reflection = SelfReflection(
            reflection_id=reflection_id,
            reflection_type=ReflectionType.ANALYSIS,
            content=analysis_content,
            depth_score=0.7,
            insight_quality=0.6,
            meta_cognition_level=MetaCognitionLevel.ENHANCED,
            context={"analysis_type": "thinking_process_analysis"},
        )

        return reflection

    async def _create_evaluation_reflection(
        self, context: Dict[str, Any], thinking_processes: List[ThinkingProcess]
    ) -> SelfReflection:
        """평가적 성찰 생성"""
        reflection_id = f"evaluation_reflection_{len(self.self_reflections)}"

        # 평가 내용 생성
        evaluation_content = "사고 과정을 평가한 결과, "

        if thinking_processes:
            avg_quality = np.mean([p.quality_score for p in thinking_processes])
            if avg_quality >= 0.8:
                evaluation_content += "전반적으로 우수한 사고 품질을 보였습니다."
            elif avg_quality >= 0.6:
                evaluation_content += "보통 수준의 사고 품질을 보였습니다."
            else:
                evaluation_content += "개선이 필요한 사고 품질을 보였습니다."
        else:
            evaluation_content += "평가할 사고 과정이 없습니다."

        reflection = SelfReflection(
            reflection_id=reflection_id,
            reflection_type=ReflectionType.EVALUATION,
            content=evaluation_content,
            depth_score=0.8,
            insight_quality=0.7,
            meta_cognition_level=MetaCognitionLevel.ADVANCED,
            context={"evaluation_criteria": "quality_score"},
        )

        return reflection

    async def _create_synthesis_reflection(
        self, context: Dict[str, Any], thinking_processes: List[ThinkingProcess]
    ) -> SelfReflection:
        """종합적 성찰 생성"""
        reflection_id = f"synthesis_reflection_{len(self.self_reflections)}"

        # 종합 내용 생성
        synthesis_content = "다양한 사고 과정을 종합한 결과, "

        if thinking_processes:
            synthesis_content += (
                "내적 사고, 감정적 사고, 직관적 사고, 창의적 사고가 조화롭게 작동하여 "
            )
            synthesis_content += "다차원적인 사고 능력을 발휘할 수 있었습니다."
        else:
            synthesis_content += "종합할 사고 과정이 없습니다."

        reflection = SelfReflection(
            reflection_id=reflection_id,
            reflection_type=ReflectionType.SYNTHESIS,
            content=synthesis_content,
            depth_score=0.9,
            insight_quality=0.8,
            meta_cognition_level=MetaCognitionLevel.ADVANCED,
            context={"synthesis_type": "thinking_process_integration"},
        )

        return reflection

    async def _create_integration_reflection(
        self, context: Dict[str, Any], thinking_processes: List[ThinkingProcess]
    ) -> SelfReflection:
        """통합적 성찰 생성"""
        reflection_id = f"integration_reflection_{len(self.self_reflections)}"

        # 통합 내용 생성
        integration_content = "모든 사고 과정을 통합한 결과, "

        if thinking_processes:
            integration_content += (
                "메타 인식을 통해 사고 과정을 모니터링하고 개선할 수 있는 "
            )
            integration_content += "완전한 사고 시스템을 구축할 수 있었습니다."
        else:
            integration_content += "통합할 사고 과정이 없습니다."

        reflection = SelfReflection(
            reflection_id=reflection_id,
            reflection_type=ReflectionType.INTEGRATION,
            content=integration_content,
            depth_score=1.0,
            insight_quality=0.9,
            meta_cognition_level=MetaCognitionLevel.EXCEPTIONAL,
            context={"integration_type": "complete_thinking_system"},
        )

        return reflection

    async def _assess_thinking_quality(
        self, thinking_processes: List[ThinkingProcess]
    ) -> List[ThinkingQualityAssessment]:
        """사고 품질 평가"""
        assessments = []

        for process in thinking_processes:
            assessment = await self._create_quality_assessment(process)
            assessments.append(assessment)

        return assessments

    async def _create_quality_assessment(
        self, process: ThinkingProcess
    ) -> ThinkingQualityAssessment:
        """품질 평가 생성"""
        assessment_id = f"quality_assessment_{len(self.quality_assessments)}"

        # 품질 점수 계산
        clarity_score = process.quality_score * 0.9 + random.uniform(0.0, 0.1)
        logic_score = process.quality_score * 0.85 + random.uniform(0.0, 0.15)
        creativity_score = process.quality_score * 0.8 + random.uniform(0.0, 0.2)
        efficiency_score = process.quality_score * 0.75 + random.uniform(0.0, 0.25)
        depth_score = process.quality_score * 0.9 + random.uniform(0.0, 0.1)

        # 전체 품질 계산
        overall_quality_score = (
            clarity_score * self.meta_cognition_weights["clarity"]
            + logic_score * self.meta_cognition_weights["logic"]
            + creativity_score * self.meta_cognition_weights["creativity"]
            + efficiency_score * self.meta_cognition_weights["efficiency"]
            + depth_score * self.meta_cognition_weights["depth"]
        )

        # 품질 등급 결정
        if overall_quality_score >= 0.8:
            overall_quality = ThinkingQuality.EXCELLENT
        elif overall_quality_score >= 0.6:
            overall_quality = ThinkingQuality.GOOD
        elif overall_quality_score >= 0.3:
            overall_quality = ThinkingQuality.FAIR
        else:
            overall_quality = ThinkingQuality.POOR

        assessment = ThinkingQualityAssessment(
            assessment_id=assessment_id,
            thinking_process_id=process.process_id,
            overall_quality=overall_quality,
            clarity_score=clarity_score,
            logic_score=logic_score,
            creativity_score=creativity_score,
            efficiency_score=efficiency_score,
            depth_score=depth_score,
            context={"thinking_type": process.thinking_type},
        )

        return assessment

    async def _discover_meta_cognition_insights(
        self,
        context: Dict[str, Any],
        thinking_processes: List[ThinkingProcess],
        self_reflections: List[SelfReflection],
        quality_assessments: List[ThinkingQualityAssessment],
    ) -> List[MetaCognitionInsight]:
        """메타 인식 통찰 발견"""
        insights = []

        # 1. 사고 과정에서 통찰 발견
        process_insights = await self._extract_insights_from_processes(
            thinking_processes
        )
        insights.extend(process_insights)

        # 2. 자기 성찰에서 통찰 발견
        reflection_insights = await self._extract_insights_from_reflections(
            self_reflections
        )
        insights.extend(reflection_insights)

        # 3. 품질 평가에서 통찰 발견
        quality_insights = await self._extract_insights_from_assessments(
            quality_assessments
        )
        insights.extend(quality_insights)

        # 4. 종합적 메타 인식 통찰
        synthetic_insights = await self._generate_synthetic_meta_insights(
            thinking_processes, self_reflections, quality_assessments
        )
        insights.extend(synthetic_insights)

        return insights

    async def _extract_insights_from_processes(
        self, thinking_processes: List[ThinkingProcess]
    ) -> List[MetaCognitionInsight]:
        """사고 과정에서 통찰 추출"""
        insights = []

        for process in thinking_processes:
            if process.quality_score >= 0.7:
                insight = MetaCognitionInsight(
                    insight_id=f"process_insight_{len(self.meta_insights)}",
                    insight=f"{process.thinking_type} 과정에서 높은 품질의 사고가 이루어졌다.",
                    meta_cognition_level=process.meta_cognition_level,
                    applicability=process.quality_score,
                    novelty_score=0.6,
                    context={"source_process": process.process_id},
                )
                insights.append(insight)

        return insights

    async def _extract_insights_from_reflections(
        self, self_reflections: List[SelfReflection]
    ) -> List[MetaCognitionInsight]:
        """자기 성찰에서 통찰 추출"""
        insights = []

        for reflection in self_reflections:
            if reflection.insight_quality >= 0.7:
                insight = MetaCognitionInsight(
                    insight_id=f"reflection_insight_{len(self.meta_insights)}",
                    insight=f"{reflection.reflection_type.value} 성찰에서 깊이 있는 통찰을 얻었다.",
                    meta_cognition_level=reflection.meta_cognition_level,
                    applicability=reflection.insight_quality,
                    novelty_score=0.7,
                    context={"source_reflection": reflection.reflection_id},
                )
                insights.append(insight)

        return insights

    async def _extract_insights_from_assessments(
        self, quality_assessments: List[ThinkingQualityAssessment]
    ) -> List[MetaCognitionInsight]:
        """품질 평가에서 통찰 추출"""
        insights = []

        for assessment in quality_assessments:
            if assessment.overall_quality in [
                ThinkingQuality.GOOD,
                ThinkingQuality.EXCELLENT,
            ]:
                insight = MetaCognitionInsight(
                    insight_id=f"assessment_insight_{len(self.meta_insights)}",
                    insight=f"사고 품질 평가에서 {assessment.overall_quality.value} 수준의 결과를 얻었다.",
                    meta_cognition_level=MetaCognitionLevel.ADVANCED,
                    applicability=0.8,
                    novelty_score=0.5,
                    context={"source_assessment": assessment.assessment_id},
                )
                insights.append(insight)

        return insights

    async def _generate_synthetic_meta_insights(
        self,
        thinking_processes: List[ThinkingProcess],
        self_reflections: List[SelfReflection],
        quality_assessments: List[ThinkingQualityAssessment],
    ) -> List[MetaCognitionInsight]:
        """종합적 메타 인식 통찰 생성"""
        insights = []

        # 사고 과정과 성찰의 종합
        if thinking_processes and self_reflections:
            insight = MetaCognitionInsight(
                insight_id=f"synthetic_insight_{len(self.meta_insights)}",
                insight="사고 과정 모니터링과 자기 성찰을 통해 메타 인식 능력이 크게 향상되었다.",
                meta_cognition_level=MetaCognitionLevel.EXCEPTIONAL,
                applicability=0.9,
                novelty_score=0.8,
                context={"synthetic_type": "process_reflection_integration"},
            )
            insights.append(insight)

        # 품질 평가와 개선의 종합
        if quality_assessments:
            avg_quality = np.mean([a.clarity_score for a in quality_assessments])
            if avg_quality >= 0.7:
                insight = MetaCognitionInsight(
                    insight_id=f"synthetic_insight_{len(self.meta_insights) + 1}",
                    insight="체계적인 품질 평가를 통해 사고 과정의 개선점을 정확히 파악할 수 있었다.",
                    meta_cognition_level=MetaCognitionLevel.ADVANCED,
                    applicability=0.8,
                    novelty_score=0.7,
                    context={"synthetic_type": "quality_improvement_integration"},
                )
                insights.append(insight)

        return insights

    async def _apply_meta_cognition_improvements(
        self,
        thinking_processes: List[ThinkingProcess],
        self_reflections: List[SelfReflection],
        quality_assessments: List[ThinkingQualityAssessment],
    ) -> List[Dict[str, Any]]:
        """메타 인식 기반 개선 적용"""
        improvements = []

        # 1. 사고 과정 개선
        process_improvements = await self._improve_thinking_processes(
            thinking_processes
        )
        improvements.extend(process_improvements)

        # 2. 성찰 능력 개선
        reflection_improvements = await self._improve_reflection_abilities(
            self_reflections
        )
        improvements.extend(reflection_improvements)

        # 3. 품질 평가 개선
        quality_improvements = await self._improve_quality_assessments(
            quality_assessments
        )
        improvements.extend(quality_improvements)

        return improvements

    async def _improve_thinking_processes(
        self, thinking_processes: List[ThinkingProcess]
    ) -> List[Dict[str, Any]]:
        """사고 과정 개선"""
        improvements = []

        for process in thinking_processes:
            if process.quality_score < 0.6:
                improvement = {
                    "improvement_id": f"process_improvement_{len(improvements)}",
                    "improvement_type": "thinking_process",
                    "target_process": process.process_id,
                    "improvement_suggestion": f"{process.thinking_type} 과정의 품질을 향상시키기 위한 개선 방안",
                    "expected_improvement": 0.2,
                    "context": {"current_quality": process.quality_score},
                }
                improvements.append(improvement)

        return improvements

    async def _improve_reflection_abilities(
        self, self_reflections: List[SelfReflection]
    ) -> List[Dict[str, Any]]:
        """성찰 능력 개선"""
        improvements = []

        for reflection in self_reflections:
            if reflection.insight_quality < 0.6:
                improvement = {
                    "improvement_id": f"reflection_improvement_{len(improvements)}",
                    "improvement_type": "reflection_ability",
                    "target_reflection": reflection.reflection_id,
                    "improvement_suggestion": f"{reflection.reflection_type.value} 성찰의 깊이를 향상시키기 위한 개선 방안",
                    "expected_improvement": 0.15,
                    "context": {"current_insight_quality": reflection.insight_quality},
                }
                improvements.append(improvement)

        return improvements

    async def _improve_quality_assessments(
        self, quality_assessments: List[ThinkingQualityAssessment]
    ) -> List[Dict[str, Any]]:
        """품질 평가 개선"""
        improvements = []

        for assessment in quality_assessments:
            if assessment.overall_quality in [
                ThinkingQuality.POOR,
                ThinkingQuality.FAIR,
            ]:
                improvement = {
                    "improvement_id": f"quality_improvement_{len(improvements)}",
                    "improvement_type": "quality_assessment",
                    "target_assessment": assessment.assessment_id,
                    "improvement_suggestion": "사고 품질 평가 기준을 더욱 정교화하기 위한 개선 방안",
                    "expected_improvement": 0.25,
                    "context": {"current_quality": assessment.overall_quality.value},
                }
                improvements.append(improvement)

        return improvements

    async def _calculate_average_meta_cognition_level(
        self,
        thinking_processes: List[ThinkingProcess],
        self_reflections: List[SelfReflection],
        meta_insights: List[MetaCognitionInsight],
    ) -> float:
        """평균 메타 인식 수준 계산"""
        total_level = 0.0
        total_count = 0

        # 사고 과정 메타 인식 수준
        for process in thinking_processes:
            level_value = self._convert_meta_cognition_level_to_float(
                process.meta_cognition_level
            )
            total_level += level_value
            total_count += 1

        # 자기 성찰 메타 인식 수준
        for reflection in self_reflections:
            level_value = self._convert_meta_cognition_level_to_float(
                reflection.meta_cognition_level
            )
            total_level += level_value
            total_count += 1

        # 메타 인식 통찰 수준
        for insight in meta_insights:
            level_value = self._convert_meta_cognition_level_to_float(
                insight.meta_cognition_level
            )
            total_level += level_value
            total_count += 1

        return total_level / total_count if total_count > 0 else 0.0

    def _convert_meta_cognition_level_to_float(
        self, meta_cognition_level: MetaCognitionLevel
    ) -> float:
        """메타 인식 수준을 float로 변환"""
        level_values = {
            MetaCognitionLevel.BASIC: 0.2,
            MetaCognitionLevel.ENHANCED: 0.5,
            MetaCognitionLevel.ADVANCED: 0.7,
            MetaCognitionLevel.EXCEPTIONAL: 0.9,
        }
        return level_values.get(meta_cognition_level, 0.5)

    async def _calculate_overall_thinking_quality(
        self, quality_assessments: List[ThinkingQualityAssessment]
    ) -> float:
        """전체 사고 품질 계산"""
        if not quality_assessments:
            return 0.0

        total_quality = 0.0
        for assessment in quality_assessments:
            quality_value = self._convert_thinking_quality_to_float(
                assessment.overall_quality
            )
            total_quality += quality_value

        return total_quality / len(quality_assessments)

    def _convert_thinking_quality_to_float(
        self, thinking_quality: ThinkingQuality
    ) -> float:
        """사고 품질을 float로 변환"""
        quality_values = {
            ThinkingQuality.POOR: 0.2,
            ThinkingQuality.FAIR: 0.5,
            ThinkingQuality.GOOD: 0.7,
            ThinkingQuality.EXCELLENT: 0.9,
        }
        return quality_values.get(thinking_quality, 0.5)

    async def get_meta_cognition_summary(self) -> Dict[str, Any]:
        """메타 인식 요약 반환"""
        return {
            "total_thinking_processes": len(self.thinking_processes),
            "total_self_reflections": len(self.self_reflections),
            "total_quality_assessments": len(self.quality_assessments),
            "total_meta_insights": len(self.meta_insights),
            "average_meta_cognition_level": await self._calculate_average_meta_cognition_level(
                self.thinking_processes, self.self_reflections, self.meta_insights
            ),
            "thinking_type_distribution": self._get_thinking_type_distribution(),
            "reflection_type_distribution": self._get_reflection_type_distribution(),
            "recent_insights": (
                [i.insight for i in self.meta_insights[-3:]]
                if self.meta_insights
                else []
            ),
        }

    def _get_thinking_type_distribution(self) -> Dict[str, int]:
        """사고 유형 분포 반환"""
        distribution = defaultdict(int)
        for process in self.thinking_processes:
            distribution[process.thinking_type] += 1
        return dict(distribution)

    def _get_reflection_type_distribution(self) -> Dict[str, int]:
        """성찰 유형 분포 반환"""
        distribution = defaultdict(int)
        for reflection in self.self_reflections:
            distribution[reflection.reflection_type.value] += 1
        return dict(distribution)


async def test_meta_cognition_system():
    """메타 인식 시스템 테스트"""
    logger.info("=== 메타 인식 시스템 테스트 시작 ===")

    system = MetaCognitionSystem()

    # 1. 기본 메타 인식 테스트
    logger.info("1. 기본 메타 인식 테스트")
    context1 = {"task": "문제 해결", "complexity": "보통", "goal": "효과적 해결"}
    result1 = await system.think_with_meta_cognition(context1)
    logger.info(f"기본 메타 인식 결과: 사고과정 {len(result1.thinking_processes)}개")
    logger.info(f"자기 성찰: {len(result1.self_reflections)}개")
    logger.info(f"평균 메타 인식 수준: {result1.average_meta_cognition_level:.2f}")

    # 2. 복잡한 메타 인식 테스트
    logger.info("2. 복잡한 메타 인식 테스트")
    context2 = {
        "challenge": "창의적 문제 해결",
        "complexity": "높음",
        "innovation": "필요",
    }
    result2 = await system.think_with_meta_cognition(context2)
    logger.info(f"복잡한 메타 인식 결과: 사고과정 {len(result2.thinking_processes)}개")
    logger.info(f"자기 성찰: {len(result2.self_reflections)}개")
    logger.info(f"평균 메타 인식 수준: {result2.average_meta_cognition_level:.2f}")

    # 3. 시스템 요약
    summary = await system.get_meta_cognition_summary()
    logger.info(f"시스템 요약: {summary}")

    logger.info("=== 메타 인식 시스템 테스트 완료 ===")
    return system


if __name__ == "__main__":
    asyncio.run(test_meta_cognition_system())
