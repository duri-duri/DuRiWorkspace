#!/usr/bin/env python3
"""
DuRiCore Phase 5.5.3 - 창의적 사고 시스템
패턴 인식, 혁신적 해결책 생성, 자기 반성 및 개선 시스템
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import math
import statistics
import time
import random

# 기존 패턴 분석 시스템 import
from learning_pattern_analyzer import LearningPatternAnalyzer, PatternType, LearningPattern

logger = logging.getLogger(__name__)

class CreativeThinkingType(Enum):
    """창의적 사고 타입 열거형"""
    PATTERN_RECOGNITION = "pattern_recognition"    # 패턴 인식
    INNOVATIVE_SOLUTION = "innovative_solution"    # 혁신적 해결책
    SELF_REFLECTION = "self_reflection"           # 자기 반성
    DIVERGENT_THINKING = "divergent_thinking"      # 발산적 사고
    CONVERGENT_THINKING = "convergent_thinking"    # 수렴적 사고

class InnovationLevel(Enum):
    """혁신 수준 열거형"""
    INCREMENTAL = "incremental"      # 점진적 개선
    MODULAR = "modular"              # 모듈적 혁신
    RADICAL = "radical"              # 급진적 혁신
    DISRUPTIVE = "disruptive"        # 파괴적 혁신

@dataclass
class CreativeInsight:
    """창의적 통찰"""
    insight_id: str
    insight_type: CreativeThinkingType
    content: str
    confidence: float
    novelty_score: float
    usefulness_score: float
    implementation_difficulty: float
    created_at: datetime
    
    def get(self, key: str, default=None):
        """딕셔너리 스타일 접근을 위한 get 메서드"""
        return getattr(self, key, default)

@dataclass
class InnovativeSolution:
    """혁신적 해결책"""
    solution_id: str
    problem_description: str
    solution_approach: str
    innovation_level: InnovationLevel
    novelty_score: float
    feasibility_score: float
    impact_score: float
    usefulness_score: float
    implementation_difficulty: float
    implementation_steps: List[str]
    risk_assessment: Dict[str, float]
    created_at: datetime

@dataclass
class SelfReflectionReport:
    """자기 반성 보고서"""
    reflection_id: str
    thinking_process_analysis: Dict[str, Any]
    cognitive_biases_identified: List[str]
    improvement_areas: List[str]
    strengths_identified: List[str]
    learning_insights: List[str]
    action_plan: List[str]
    created_at: datetime

class CreativeThinkingSystem:
    """창의적 사고 시스템"""
    
    def __init__(self):
        # 기존 패턴 분석 시스템 통합
        self.pattern_analyzer = LearningPatternAnalyzer()
        
        # 창의적 사고 데이터
        self.creative_insights = []
        self.innovative_solutions = []
        self.self_reflections = []
        
        # 창의적 사고 설정
        self.min_novelty_threshold = 0.6
        self.min_usefulness_threshold = 0.5
        self.max_implementation_difficulty = 0.8
        
        # 창의적 사고 가중치
        self.creative_weights = {
            "novelty": 0.4,
            "usefulness": 0.3,
            "feasibility": 0.2,
            "impact": 0.1
        }
        
        logger.info("창의적 사고 시스템 초기화 완료")
    
    async def analyze_patterns(self, data: Dict[str, Any]) -> List[CreativeInsight]:
        """복잡한 패턴 분석"""
        try:
            insights = []
            
            # 기존 패턴 분석 시스템 활용
            behavior_traces = data.get('behavior_traces', [])
            performance_history = data.get('performance_history', [])
            
            # 성공 패턴 분석
            success_patterns = await self.pattern_analyzer.analyze_success_patterns(behavior_traces)
            
            # 실패 패턴 분석
            failure_patterns = await self.pattern_analyzer.analyze_failure_patterns(behavior_traces)
            
            # 패턴에서 창의적 통찰 도출
            for pattern in success_patterns + failure_patterns:
                insight = await self._extract_creative_insight_from_pattern(pattern)
                if insight:
                    insights.append(insight)
            
            # 새로운 패턴 발견
            novel_patterns = await self._discover_novel_patterns(data)
            insights.extend(novel_patterns)
            
            logger.info(f"패턴 분석 완료: {len(insights)}개 통찰 발견")
            return insights
            
        except Exception as e:
            logger.error(f"패턴 분석 실패: {e}")
            return []
    
    async def generate_innovative_solutions(self, problem_context: Dict[str, Any]) -> List[InnovativeSolution]:
        """혁신적 해결책 생성"""
        try:
            solutions = []
            
            # 문제 분석
            problem_analysis = await self._analyze_problem(problem_context)
            
            # 발산적 사고로 다양한 접근법 생성
            divergent_approaches = await self._generate_divergent_approaches(problem_analysis)
            
            # 수렴적 사고로 최적 해결책 도출
            for approach in divergent_approaches:
                solution = await self._converge_to_solution(approach, problem_analysis)
                if solution:
                    solutions.append(solution)
            
            # 혁신 수준 평가 및 분류
            for solution in solutions:
                solution.innovation_level = await self._assess_innovation_level(solution)
            
            # 실행 가능성 및 영향도 평가
            for solution in solutions:
                solution.feasibility_score = await self._assess_feasibility(solution)
                solution.impact_score = await self._assess_impact(solution)
            
            logger.info(f"혁신적 해결책 생성 완료: {len(solutions)}개 해결책")
            return solutions
            
        except Exception as e:
            logger.error(f"혁신적 해결책 생성 실패: {e}")
            return []
    
    async def self_reflect(self, thinking_process: Dict[str, Any]) -> SelfReflectionReport:
        """자기 반성 및 개선"""
        try:
            # 사고 과정 분석
            thinking_analysis = await self._analyze_thinking_process(thinking_process)
            
            # 인지 편향 식별
            cognitive_biases = await self._identify_cognitive_biases(thinking_process)
            
            # 개선 영역 식별
            improvement_areas = await self._identify_improvement_areas(thinking_analysis)
            
            # 강점 식별
            strengths = await self._identify_strengths(thinking_analysis)
            
            # 학습 통찰 도출
            learning_insights = await self._extract_learning_insights(thinking_process)
            
            # 행동 계획 수립
            action_plan = await self._create_action_plan(improvement_areas, learning_insights)
            
            # 자기 반성 보고서 생성
            reflection_report = SelfReflectionReport(
                reflection_id=f"reflection_{int(time.time() * 1000)}",
                thinking_process_analysis=thinking_analysis,
                cognitive_biases_identified=cognitive_biases,
                improvement_areas=improvement_areas,
                strengths_identified=strengths,
                learning_insights=learning_insights,
                action_plan=action_plan,
                created_at=datetime.now()
            )
            
            self.self_reflections.append(reflection_report)
            
            logger.info("자기 반성 완료")
            return reflection_report
            
        except Exception as e:
            logger.error(f"자기 반성 실패: {e}")
            return await self._create_empty_reflection_report()
    
    async def _extract_creative_insight_from_pattern(self, pattern: LearningPattern) -> Optional[CreativeInsight]:
        """패턴에서 창의적 통찰 도출"""
        try:
            # 패턴의 특성을 분석하여 창의적 통찰 생성
            if pattern.confidence > self.min_novelty_threshold:
                insight_content = f"패턴 발견: {pattern.pattern_type.value} 패턴 (신뢰도: {pattern.confidence:.2f})"
                
                insight = CreativeInsight(
                    insight_id=f"insight_{int(time.time() * 1000)}",
                    insight_type=CreativeThinkingType.PATTERN_RECOGNITION,
                    content=insight_content,
                    confidence=pattern.confidence,
                    novelty_score=min(pattern.confidence * 0.8, 1.0),
                    usefulness_score=pattern.success_rate,
                    implementation_difficulty=0.3,
                    created_at=datetime.now()
                )
                
                return insight
            return None
            
        except Exception as e:
            logger.warning(f"패턴에서 통찰 도출 실패: {e}")
            return None
    
    async def _discover_novel_patterns(self, data: Dict[str, Any]) -> List[CreativeInsight]:
        """새로운 패턴 발견"""
        try:
            novel_insights = []
            
            # 데이터에서 새로운 패턴 탐색
            # 여기서는 간단한 예시로 구현
            if random.random() > 0.7:  # 30% 확률로 새로운 패턴 발견
                insight = CreativeInsight(
                    insight_id=f"novel_insight_{int(time.time() * 1000)}",
                    insight_type=CreativeThinkingType.PATTERN_RECOGNITION,
                    content="새로운 패턴 발견: 예상치 못한 상관관계 식별",
                    confidence=0.6,
                    novelty_score=0.8,
                    usefulness_score=0.7,
                    implementation_difficulty=0.4,
                    created_at=datetime.now()
                )
                novel_insights.append(insight)
            
            return novel_insights
            
        except Exception as e:
            logger.warning(f"새로운 패턴 발견 실패: {e}")
            return []
    
    async def _analyze_problem(self, problem_context: Dict[str, Any]) -> Dict[str, Any]:
        """문제 분석"""
        try:
            analysis = {
                'problem_type': problem_context.get('type', 'unknown'),
                'complexity': problem_context.get('complexity', 0.5),
                'urgency': problem_context.get('urgency', 0.5),
                'constraints': problem_context.get('constraints', []),
                'stakeholders': problem_context.get('stakeholders', []),
                'resources': problem_context.get('resources', [])
            }
            return analysis
            
        except Exception as e:
            logger.warning(f"문제 분석 실패: {e}")
            return {}
    
    async def _generate_divergent_approaches(self, problem_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """발산적 사고로 다양한 접근법 생성"""
        try:
            approaches = []
            
            # 다양한 접근법 생성
            approach_types = [
                'traditional', 'innovative', 'radical', 'hybrid', 
                'reverse', 'lateral', 'systematic', 'intuitive'
            ]
            
            for approach_type in approach_types:
                approach = {
                    'type': approach_type,
                    'description': f"{approach_type} 접근법",
                    'novelty_score': random.uniform(0.3, 0.9),
                    'feasibility_score': random.uniform(0.4, 0.8)
                }
                approaches.append(approach)
            
            return approaches
            
        except Exception as e:
            logger.warning(f"발산적 접근법 생성 실패: {e}")
            return []
    
    async def _converge_to_solution(self, approach: Dict[str, Any], problem_analysis: Dict[str, Any]) -> Optional[InnovativeSolution]:
        """수렴적 사고로 해결책 도출"""
        try:
            if approach['feasibility_score'] > 0.5:
                solution = InnovativeSolution(
                    solution_id=f"solution_{int(time.time() * 1000)}",
                    problem_description=problem_analysis.get('problem_type', 'unknown'),
                    solution_approach=approach['description'],
                    innovation_level=InnovationLevel.MODULAR,
                    novelty_score=approach['novelty_score'],
                    feasibility_score=approach['feasibility_score'],
                    impact_score=random.uniform(0.5, 0.9),
                    usefulness_score=random.uniform(0.5, 0.9),
                    implementation_difficulty=random.uniform(0.2, 0.7),
                    implementation_steps=[
                        "1단계: 접근법 분석",
                        "2단계: 실행 계획 수립",
                        "3단계: 시범 실행",
                        "4단계: 결과 평가"
                    ],
                    risk_assessment={
                        'technical_risk': random.uniform(0.2, 0.6),
                        'resource_risk': random.uniform(0.1, 0.5),
                        'timeline_risk': random.uniform(0.2, 0.7)
                    },
                    created_at=datetime.now()
                )
                return solution
            return None
            
        except Exception as e:
            logger.warning(f"해결책 도출 실패: {e}")
            return None
    
    async def _assess_innovation_level(self, solution: InnovativeSolution) -> InnovationLevel:
        """혁신 수준 평가"""
        try:
            if solution.novelty_score > 0.8:
                return InnovationLevel.DISRUPTIVE
            elif solution.novelty_score > 0.6:
                return InnovationLevel.RADICAL
            elif solution.novelty_score > 0.4:
                return InnovationLevel.MODULAR
            else:
                return InnovationLevel.INCREMENTAL
                
        except Exception as e:
            logger.warning(f"혁신 수준 평가 실패: {e}")
            return InnovationLevel.INCREMENTAL
    
    async def _assess_feasibility(self, solution: InnovativeSolution) -> float:
        """실행 가능성 평가"""
        try:
            # 간단한 실행 가능성 계산
            feasibility = (solution.feasibility_score + 
                         (1 - solution.implementation_difficulty)) / 2
            return min(feasibility, 1.0)
            
        except Exception as e:
            logger.warning(f"실행 가능성 평가 실패: {e}")
            return 0.5
    
    async def _assess_impact(self, solution: InnovativeSolution) -> float:
        """영향도 평가"""
        try:
            # 영향도 계산
            impact = (solution.novelty_score + solution.usefulness_score) / 2
            return min(impact, 1.0)
            
        except Exception as e:
            logger.warning(f"영향도 평가 실패: {e}")
            return 0.5
    
    async def _analyze_thinking_process(self, thinking_process: Dict[str, Any]) -> Dict[str, Any]:
        """사고 과정 분석"""
        try:
            analysis = {
                'clarity': thinking_process.get('clarity', 0.5),
                'logic': thinking_process.get('logic', 0.5),
                'creativity': thinking_process.get('creativity', 0.5),
                'efficiency': thinking_process.get('efficiency', 0.5),
                'bias_detection': thinking_process.get('bias_detection', 0.5)
            }
            return analysis
            
        except Exception as e:
            logger.warning(f"사고 과정 분석 실패: {e}")
            return {}
    
    async def _identify_cognitive_biases(self, thinking_process: Dict[str, Any]) -> List[str]:
        """인지 편향 식별"""
        try:
            biases = []
            
            # 일반적인 인지 편향들
            common_biases = [
                'confirmation_bias', 'anchoring_bias', 'availability_bias',
                'overconfidence_bias', 'groupthink_bias', 'status_quo_bias'
            ]
            
            # 간단한 편향 탐지 (실제로는 더 복잡한 로직 필요)
            for bias in common_biases:
                if random.random() > 0.7:  # 30% 확률로 편향 발견
                    biases.append(bias)
            
            return biases
            
        except Exception as e:
            logger.warning(f"인지 편향 식별 실패: {e}")
            return []
    
    async def _identify_improvement_areas(self, thinking_analysis: Dict[str, Any]) -> List[str]:
        """개선 영역 식별"""
        try:
            improvement_areas = []
            
            # 낮은 점수 영역을 개선 영역으로 식별
            for area, score in thinking_analysis.items():
                if score < 0.6:
                    improvement_areas.append(f"{area}_improvement")
            
            return improvement_areas
            
        except Exception as e:
            logger.warning(f"개선 영역 식별 실패: {e}")
            return []
    
    async def _identify_strengths(self, thinking_analysis: Dict[str, Any]) -> List[str]:
        """강점 식별"""
        try:
            strengths = []
            
            # 높은 점수 영역을 강점으로 식별
            for area, score in thinking_analysis.items():
                if score > 0.7:
                    strengths.append(f"{area}_strength")
            
            return strengths
            
        except Exception as e:
            logger.warning(f"강점 식별 실패: {e}")
            return []
    
    async def _extract_learning_insights(self, thinking_process: Dict[str, Any]) -> List[str]:
        """학습 통찰 도출"""
        try:
            insights = [
                "사고 과정의 체계적 분석 필요",
                "창의적 사고와 논리적 사고의 균형 중요",
                "지속적인 자기 반성과 개선 필요"
            ]
            return insights
            
        except Exception as e:
            logger.warning(f"학습 통찰 도출 실패: {e}")
            return []
    
    async def _create_action_plan(self, improvement_areas: List[str], learning_insights: List[str]) -> List[str]:
        """행동 계획 수립"""
        try:
            action_plan = []
            
            for area in improvement_areas:
                action_plan.append(f"개선 계획: {area} 강화")
            
            for insight in learning_insights:
                action_plan.append(f"학습 계획: {insight} 적용")
            
            return action_plan
            
        except Exception as e:
            logger.warning(f"행동 계획 수립 실패: {e}")
            return []
    
    async def _create_empty_reflection_report(self) -> SelfReflectionReport:
        """빈 자기 반성 보고서 생성"""
        return SelfReflectionReport(
            reflection_id=f"empty_reflection_{int(time.time() * 1000)}",
            thinking_process_analysis={},
            cognitive_biases_identified=[],
            improvement_areas=[],
            strengths_identified=[],
            learning_insights=[],
            action_plan=[],
            created_at=datetime.now()
        )

async def test_creative_thinking_system():
    """창의적 사고 시스템 테스트"""
    print("=== 창의적 사고 시스템 테스트 시작 ===")
    
    # 창의적 사고 시스템 생성
    creative_system = CreativeThinkingSystem()
    
    # 테스트 데이터
    test_data = {
        'behavior_traces': [
            {'action': 'test_action', 'success': True, 'performance': 0.8},
            {'action': 'test_action', 'success': False, 'performance': 0.3}
        ],
        'performance_history': [
            {'score': 0.8, 'timestamp': datetime.now()},
            {'score': 0.9, 'timestamp': datetime.now()}
        ]
    }
    
    # 1. 패턴 분석 테스트
    print("1. 패턴 분석 테스트")
    insights = await creative_system.analyze_patterns(test_data)
    print(f"발견된 통찰: {len(insights)}개")
    
    # 2. 혁신적 해결책 생성 테스트
    print("2. 혁신적 해결책 생성 테스트")
    problem_context = {
        'type': 'performance_optimization',
        'complexity': 0.7,
        'urgency': 0.8
    }
    solutions = await creative_system.generate_innovative_solutions(problem_context)
    print(f"생성된 해결책: {len(solutions)}개")
    
    # 3. 자기 반성 테스트
    print("3. 자기 반성 테스트")
    thinking_process = {
        'clarity': 0.6,
        'logic': 0.7,
        'creativity': 0.8,
        'efficiency': 0.5
    }
    reflection = await creative_system.self_reflect(thinking_process)
    print(f"자기 반성 완료: {reflection.reflection_id}")
    
    print("=== 창의적 사고 시스템 테스트 완료 ===")

if __name__ == "__main__":
    asyncio.run(test_creative_thinking_system()) 