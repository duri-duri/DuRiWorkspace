#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-3: 메타 인식 학습 전략 (Meta-Cognition Learning Strategy)

메타 인식 학습 전략을 구현하는 모듈입니다.
- 사고 과정 모니터링
- 자기 성찰 능력 강화
- 사고 품질 평가 시스템
- 메타 인식 기반 개선
"""

import json
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetaCognitionLevel(Enum):
    """메타 인식 수준"""
    BASIC = "basic"                      # 기본 (0.0-0.3)
    ENHANCED = "enhanced"                # 향상 (0.3-0.6)
    ADVANCED = "advanced"                # 고급 (0.6-0.8)
    EXCEPTIONAL = "exceptional"          # 예외적 (0.8-1.0)

class ThinkingQuality(Enum):
    """사고 품질"""
    POOR = "poor"                        # 나쁨 (0.0-0.3)
    FAIR = "fair"                        # 보통 (0.3-0.6)
    GOOD = "good"                        # 좋음 (0.6-0.8)
    EXCELLENT = "excellent"              # 우수 (0.8-1.0)

class ReflectionType(Enum):
    """성찰 유형"""
    OBSERVATION = "observation"          # 관찰
    ANALYSIS = "analysis"                # 분석
    EVALUATION = "evaluation"            # 평가
    SYNTHESIS = "synthesis"              # 종합
    INTEGRATION = "integration"          # 통합

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

class MetaCognitionStrategy:
    """메타 인식 학습 전략"""
    
    def __init__(self):
        """초기화"""
        self.thinking_processes: List[ThinkingProcess] = []
        self.self_reflections: List[SelfReflection] = []
        self.quality_assessments: List[ThinkingQualityAssessment] = []
        self.meta_insights: List[MetaCognitionInsight] = []
        
        # 성능 메트릭
        self.performance_metrics = {
            'total_thinking_processes': 0,
            'total_reflections': 0,
            'total_assessments': 0,
            'average_meta_cognition_level': 0.0,
            'average_thinking_quality': 0.0,
            'insight_discovery_rate': 0.0
        }
        
        logger.info("메타 인식 학습 전략 초기화 완료")
    
    async def think_with_meta_cognition(self, context: Dict[str, Any]) -> MetaCognitionResult:
        """메타 인식을 통한 사고"""
        process_id = f"meta_cognition_process_{int(time.time())}"
        start_time = datetime.now()
        
        try:
            # 1. 사고 과정 모니터링
            thinking_processes = await self._monitor_thinking_processes(context)
            
            # 2. 자기 성찰 수행
            self_reflections = await self._perform_self_reflection(context, thinking_processes)
            
            # 3. 사고 품질 평가
            quality_assessments = await self._assess_thinking_quality(thinking_processes)
            
            # 4. 메타 인식 통찰 발견
            insights_discovered = await self._discover_meta_cognition_insights(
                context, thinking_processes, self_reflections, quality_assessments
            )
            
            # 5. 결과 컴파일
            end_time = datetime.now()
            thinking_duration = (end_time - start_time).total_seconds()
            
            result = await self._compile_meta_cognition_result(
                process_id, thinking_processes, self_reflections,
                quality_assessments, insights_discovered, thinking_duration
            )
            
            logger.info(f"메타 인식 사고 완료: {process_id} (지속시간: {thinking_duration:.2f}초)")
            return result
            
        except Exception as e:
            logger.error(f"메타 인식 사고 실패: {e}")
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
                error_message=str(e)
            )
    
    async def _monitor_thinking_processes(self, context: Dict[str, Any]) -> List[ThinkingProcess]:
        """사고 과정 모니터링"""
        processes = []
        
        # 다양한 사고 유형 모니터링
        thinking_types = ['cognitive', 'emotional', 'intuitive', 'creative']
        
        for thinking_type in thinking_types:
            process = ThinkingProcess(
                process_id=f"process_{int(time.time())}_{thinking_type}",
                thinking_type=thinking_type,
                start_time=datetime.now(),
                quality_score=0.7,  # 기본 품질 점수
                meta_cognition_level=MetaCognitionLevel.ENHANCED,
                context=context
            )
            
            # 사고 과정 시뮬레이션
            await asyncio.sleep(0.1)  # 실제 사고 시간 시뮬레이션
            
            process.end_time = datetime.now()
            process.duration = (process.end_time - process.start_time).total_seconds()
            processes.append(process)
        
        self.thinking_processes.extend(processes)
        logger.info(f"사고 과정 {len(processes)}개 모니터링 완료")
        return processes
    
    async def _perform_self_reflection(self, context: Dict[str, Any], 
                                     thinking_processes: List[ThinkingProcess]) -> List[SelfReflection]:
        """자기 성찰 수행"""
        reflections = []
        
        # 다양한 성찰 유형 수행
        for reflection_type in ReflectionType:
            reflection = await self._create_reflection(reflection_type, context, thinking_processes)
            reflections.append(reflection)
        
        self.self_reflections.extend(reflections)
        logger.info(f"자기 성찰 {len(reflections)}개 수행 완료")
        return reflections
    
    async def _create_reflection(self, reflection_type: ReflectionType, context: Dict[str, Any],
                               thinking_processes: List[ThinkingProcess]) -> SelfReflection:
        """성찰 생성"""
        reflection_id = f"reflection_{int(time.time())}_{reflection_type.value}"
        
        # 성찰 유형별 내용 생성
        if reflection_type == ReflectionType.OBSERVATION:
            content = "사고 과정을 관찰하여 패턴과 특징을 발견했습니다."
            depth_score = 0.6
        elif reflection_type == ReflectionType.ANALYSIS:
            content = "사고 과정을 분석하여 원인과 결과를 파악했습니다."
            depth_score = 0.7
        elif reflection_type == ReflectionType.EVALUATION:
            content = "사고 과정을 평가하여 장단점을 식별했습니다."
            depth_score = 0.8
        elif reflection_type == ReflectionType.SYNTHESIS:
            content = "다양한 사고 과정을 종합하여 통합적 관점을 형성했습니다."
            depth_score = 0.9
        elif reflection_type == ReflectionType.INTEGRATION:
            content = "사고 과정을 통합하여 새로운 인사이트를 창출했습니다."
            depth_score = 0.85
        
        reflection = SelfReflection(
            reflection_id=reflection_id,
            reflection_type=reflection_type,
            content=content,
            depth_score=depth_score,
            insight_quality=0.75,
            meta_cognition_level=MetaCognitionLevel.ADVANCED,
            context=context
        )
        
        return reflection
    
    async def _assess_thinking_quality(self, thinking_processes: List[ThinkingProcess]) -> List[ThinkingQualityAssessment]:
        """사고 품질 평가"""
        assessments = []
        
        for process in thinking_processes:
            assessment = await self._create_quality_assessment(process)
            assessments.append(assessment)
        
        self.quality_assessments.extend(assessments)
        logger.info(f"사고 품질 평가 {len(assessments)}개 완료")
        return assessments
    
    async def _create_quality_assessment(self, process: ThinkingProcess) -> ThinkingQualityAssessment:
        """품질 평가 생성"""
        assessment_id = f"assessment_{int(time.time())}_{process.process_id}"
        
        # 품질 점수 계산
        clarity_score = 0.8
        logic_score = 0.75
        creativity_score = 0.7
        efficiency_score = 0.85
        depth_score = 0.8
        
        overall_quality_score = (clarity_score + logic_score + creativity_score + efficiency_score + depth_score) / 5.0
        
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
            context=process.context
        )
        
        return assessment
    
    async def _discover_meta_cognition_insights(self, context: Dict[str, Any],
                                              thinking_processes: List[ThinkingProcess],
                                              self_reflections: List[SelfReflection],
                                              quality_assessments: List[ThinkingQualityAssessment]) -> List[MetaCognitionInsight]:
        """메타 인식 통찰 발견"""
        insights = []
        
        # 사고 과정에서 통찰 추출
        process_insights = await self._extract_insights_from_processes(thinking_processes)
        insights.extend(process_insights)
        
        # 성찰에서 통찰 추출
        reflection_insights = await self._extract_insights_from_reflections(self_reflections)
        insights.extend(reflection_insights)
        
        # 평가에서 통찰 추출
        assessment_insights = await self._extract_insights_from_assessments(quality_assessments)
        insights.extend(assessment_insights)
        
        # 종합적 메타 통찰 생성
        synthetic_insights = await self._generate_synthetic_meta_insights(
            thinking_processes, self_reflections, quality_assessments
        )
        insights.extend(synthetic_insights)
        
        self.meta_insights.extend(insights)
        logger.info(f"메타 인식 통찰 {len(insights)}개 발견")
        return insights
    
    async def _extract_insights_from_processes(self, thinking_processes: List[ThinkingProcess]) -> List[MetaCognitionInsight]:
        """사고 과정에서 통찰 추출"""
        insights = []
        
        for process in thinking_processes:
            insight = MetaCognitionInsight(
                insight_id=f"insight_{int(time.time())}_process_{process.process_id}",
                insight=f"{process.thinking_type} 사고 과정에서 효율성 패턴을 발견했습니다.",
                meta_cognition_level=process.meta_cognition_level,
                applicability=0.8,
                novelty_score=0.6,
                context=process.context
            )
            insights.append(insight)
        
        return insights
    
    async def _extract_insights_from_reflections(self, self_reflections: List[SelfReflection]) -> List[MetaCognitionInsight]:
        """성찰에서 통찰 추출"""
        insights = []
        
        for reflection in self_reflections:
            insight = MetaCognitionInsight(
                insight_id=f"insight_{int(time.time())}_reflection_{reflection.reflection_id}",
                insight=f"{reflection.reflection_type.value} 성찰을 통해 자기 인식이 향상되었습니다.",
                meta_cognition_level=reflection.meta_cognition_level,
                applicability=0.9,
                novelty_score=0.7,
                context=reflection.context
            )
            insights.append(insight)
        
        return insights
    
    async def _extract_insights_from_assessments(self, quality_assessments: List[ThinkingQualityAssessment]) -> List[MetaCognitionInsight]:
        """평가에서 통찰 추출"""
        insights = []
        
        for assessment in quality_assessments:
            insight = MetaCognitionInsight(
                insight_id=f"insight_{int(time.time())}_assessment_{assessment.assessment_id}",
                insight=f"사고 품질 평가를 통해 개선 영역을 식별했습니다.",
                meta_cognition_level=MetaCognitionLevel.ADVANCED,
                applicability=0.85,
                novelty_score=0.5,
                context=assessment.context
            )
            insights.append(insight)
        
        return insights
    
    async def _generate_synthetic_meta_insights(self, thinking_processes: List[ThinkingProcess],
                                              self_reflections: List[SelfReflection],
                                              quality_assessments: List[ThinkingQualityAssessment]) -> List[MetaCognitionInsight]:
        """종합적 메타 통찰 생성"""
        insights = []
        
        # 종합적 통찰 생성
        synthetic_insight = MetaCognitionInsight(
            insight_id=f"insight_{int(time.time())}_synthetic",
            insight="다양한 사고 과정과 성찰을 통합하여 메타 인식 능력이 향상되었습니다.",
            meta_cognition_level=MetaCognitionLevel.EXCEPTIONAL,
            applicability=0.95,
            novelty_score=0.8,
            context={"synthetic": True}
        )
        insights.append(synthetic_insight)
        
        return insights
    
    async def _compile_meta_cognition_result(self, process_id: str,
                                           thinking_processes: List[ThinkingProcess],
                                           self_reflections: List[SelfReflection],
                                           quality_assessments: List[ThinkingQualityAssessment],
                                           insights_discovered: List[MetaCognitionInsight],
                                           thinking_duration: float) -> MetaCognitionResult:
        """메타 인식 결과 컴파일"""
        # 평균 메타 인식 수준 계산
        average_meta_cognition_level = await self._calculate_average_meta_cognition_level(
            thinking_processes, self_reflections, insights_discovered
        )
        
        # 전체 사고 품질 계산
        overall_thinking_quality = await self._calculate_overall_thinking_quality(quality_assessments)
        
        result = MetaCognitionResult(
            process_id=process_id,
            thinking_processes=thinking_processes,
            self_reflections=self_reflections,
            quality_assessments=quality_assessments,
            insights_discovered=insights_discovered,
            average_meta_cognition_level=average_meta_cognition_level,
            overall_thinking_quality=overall_thinking_quality,
            thinking_duration=thinking_duration,
            success=True
        )
        
        return result
    
    async def _calculate_average_meta_cognition_level(self, thinking_processes: List[ThinkingProcess],
                                                    self_reflections: List[SelfReflection],
                                                    meta_insights: List[MetaCognitionInsight]) -> float:
        """평균 메타 인식 수준 계산"""
        all_levels = []
        
        # 사고 과정의 메타 인식 수준
        for process in thinking_processes:
            all_levels.append(self._convert_meta_cognition_level_to_float(process.meta_cognition_level))
        
        # 성찰의 메타 인식 수준
        for reflection in self_reflections:
            all_levels.append(self._convert_meta_cognition_level_to_float(reflection.meta_cognition_level))
        
        # 통찰의 메타 인식 수준
        for insight in meta_insights:
            all_levels.append(self._convert_meta_cognition_level_to_float(insight.meta_cognition_level))
        
        if all_levels:
            return sum(all_levels) / len(all_levels)
        else:
            return 0.0
    
    def _convert_meta_cognition_level_to_float(self, meta_cognition_level: MetaCognitionLevel) -> float:
        """메타 인식 수준을 float로 변환"""
        level_map = {
            MetaCognitionLevel.BASIC: 0.25,
            MetaCognitionLevel.ENHANCED: 0.5,
            MetaCognitionLevel.ADVANCED: 0.75,
            MetaCognitionLevel.EXCEPTIONAL: 1.0
        }
        return level_map.get(meta_cognition_level, 0.5)
    
    async def _calculate_overall_thinking_quality(self, quality_assessments: List[ThinkingQualityAssessment]) -> float:
        """전체 사고 품질 계산"""
        if not quality_assessments:
            return 0.0
        
        quality_scores = []
        for assessment in quality_assessments:
            quality_score = self._convert_thinking_quality_to_float(assessment.overall_quality)
            quality_scores.append(quality_score)
        
        return sum(quality_scores) / len(quality_scores)
    
    def _convert_thinking_quality_to_float(self, thinking_quality: ThinkingQuality) -> float:
        """사고 품질을 float로 변환"""
        quality_map = {
            ThinkingQuality.POOR: 0.25,
            ThinkingQuality.FAIR: 0.5,
            ThinkingQuality.GOOD: 0.75,
            ThinkingQuality.EXCELLENT: 1.0
        }
        return quality_map.get(thinking_quality, 0.5)
    
    async def get_meta_cognition_summary(self) -> Dict[str, Any]:
        """메타 인식 요약 조회"""
        if not self.thinking_processes:
            return {"error": "메타 인식 데이터가 없습니다"}
        
        # 통계 계산
        total_processes = len(self.thinking_processes)
        total_reflections = len(self.self_reflections)
        total_assessments = len(self.quality_assessments)
        total_insights = len(self.meta_insights)
        
        # 평균 메타 인식 수준
        avg_meta_cognition_level = await self._calculate_average_meta_cognition_level(
            self.thinking_processes, self.self_reflections, self.meta_insights
        )
        
        # 평균 사고 품질
        avg_thinking_quality = await self._calculate_overall_thinking_quality(self.quality_assessments)
        
        return {
            "total_thinking_processes": total_processes,
            "total_reflections": total_reflections,
            "total_assessments": total_assessments,
            "total_insights": total_insights,
            "average_meta_cognition_level": avg_meta_cognition_level,
            "average_thinking_quality": avg_thinking_quality,
            "insight_discovery_rate": total_insights / max(total_processes, 1),
            "recent_processes": [
                {
                    "process_id": p.process_id,
                    "thinking_type": p.thinking_type,
                    "quality_score": p.quality_score,
                    "meta_cognition_level": p.meta_cognition_level.value,
                    "duration": p.duration
                }
                for p in self.thinking_processes[-5:]  # 최근 5개 과정
            ]
        }
