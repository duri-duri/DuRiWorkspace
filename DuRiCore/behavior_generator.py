#!/usr/bin/env python3
"""
DuRiCore Phase 5 Day 4 - 행동 생성 엔진
의사결정 결과를 기반으로 구체적인 행동 계획을 생성하는 시스템
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class BehaviorType(Enum):
    """행동 타입 열거형"""

    RESPONSE = "response"  # 응답 행동
    ANALYSIS = "analysis"  # 분석 행동
    LEARNING = "learning"  # 학습 행동
    OPTIMIZATION = "optimization"  # 최적화 행동
    CREATION = "creation"  # 생성 행동
    INTERACTION = "interaction"  # 상호작용 행동


class BehaviorStrategy(Enum):
    """행동 전략 열거형"""

    IMMEDIATE = "immediate"  # 즉시 실행
    SEQUENTIAL = "sequential"  # 순차 실행
    PARALLEL = "parallel"  # 병렬 실행
    CONDITIONAL = "conditional"  # 조건부 실행
    ADAPTIVE = "adaptive"  # 적응적 실행


@dataclass
class BehaviorPlan:
    """행동 계획"""

    behavior_id: str
    behavior_type: BehaviorType
    strategy: BehaviorStrategy
    description: str
    steps: List[Dict[str, Any]]
    expected_outcome: Dict[str, Any]
    success_criteria: List[str]
    risk_assessment: Dict[str, float]
    resource_requirements: Dict[str, Any]
    time_estimate: float
    priority: float
    created_at: datetime


@dataclass
class BehaviorTemplate:
    """행동 템플릿"""

    template_id: str
    behavior_type: BehaviorType
    strategy: BehaviorStrategy
    base_steps: List[Dict[str, Any]]
    default_criteria: List[str]
    resource_profile: Dict[str, Any]
    time_profile: Dict[str, float]


class BehaviorGenerator:
    """행동 생성 엔진"""

    def __init__(self):
        self.behavior_templates = self._initialize_templates()
        self.strategy_weights = {
            "urgency": 0.35,
            "complexity": 0.25,
            "importance": 0.20,
            "resource_availability": 0.20,
        }

        # 행동 패턴 데이터베이스
        self.behavior_patterns = {}
        self.success_patterns = {}
        self.failure_patterns = {}

        logger.info("행동 생성 엔진 초기화 완료")

    def _initialize_templates(self) -> Dict[str, BehaviorTemplate]:
        """행동 템플릿 초기화"""
        templates = {}

        # 응답 행동 템플릿
        templates["immediate_response"] = BehaviorTemplate(
            template_id="immediate_response",
            behavior_type=BehaviorType.RESPONSE,
            strategy=BehaviorStrategy.IMMEDIATE,
            base_steps=[
                {"step": "상황 인식", "duration": 0.1, "resources": ["cpu"]},
                {"step": "응답 생성", "duration": 0.2, "resources": ["cpu", "memory"]},
                {"step": "응답 전송", "duration": 0.1, "resources": ["network"]},
            ],
            default_criteria=["응답 시간 < 1초", "정확도 > 90%"],
            resource_profile={"cpu": 0.8, "memory": 0.6, "network": 0.4},
            time_profile={"min": 0.1, "max": 1.0, "avg": 0.4},
        )

        # 분석 행동 템플릿
        templates["data_analysis"] = BehaviorTemplate(
            template_id="data_analysis",
            behavior_type=BehaviorType.ANALYSIS,
            strategy=BehaviorStrategy.SEQUENTIAL,
            base_steps=[
                {"step": "데이터 수집", "duration": 5.0, "resources": ["storage"]},
                {
                    "step": "데이터 전처리",
                    "duration": 10.0,
                    "resources": ["cpu", "memory"],
                },
                {"step": "분석 수행", "duration": 30.0, "resources": ["cpu", "memory"]},
                {"step": "결과 정리", "duration": 5.0, "resources": ["cpu", "storage"]},
            ],
            default_criteria=["분석 완료", "결과 저장", "정확도 > 85%"],
            resource_profile={"cpu": 0.9, "memory": 0.8, "storage": 0.7},
            time_profile={"min": 30.0, "max": 300.0, "avg": 120.0},
        )

        # 학습 행동 템플릿
        templates["learning_action"] = BehaviorTemplate(
            template_id="learning_action",
            behavior_type=BehaviorType.LEARNING,
            strategy=BehaviorStrategy.ADAPTIVE,
            base_steps=[
                {
                    "step": "학습 데이터 준비",
                    "duration": 10.0,
                    "resources": ["storage"],
                },
                {"step": "모델 학습", "duration": 60.0, "resources": ["cpu", "memory"]},
                {"step": "성능 평가", "duration": 15.0, "resources": ["cpu", "memory"]},
                {"step": "모델 업데이트", "duration": 5.0, "resources": ["storage"]},
            ],
            default_criteria=["학습 완료", "성능 향상", "모델 저장"],
            resource_profile={"cpu": 0.8, "memory": 0.9, "storage": 0.6},
            time_profile={"min": 60.0, "max": 600.0, "avg": 180.0},
        )

        # 최적화 행동 템플릿
        templates["optimization_task"] = BehaviorTemplate(
            template_id="optimization_task",
            behavior_type=BehaviorType.OPTIMIZATION,
            strategy=BehaviorStrategy.CONDITIONAL,
            base_steps=[
                {
                    "step": "현재 상태 분석",
                    "duration": 20.0,
                    "resources": ["cpu", "memory"],
                },
                {
                    "step": "최적화 방안 탐색",
                    "duration": 30.0,
                    "resources": ["cpu", "memory"],
                },
                {
                    "step": "최적화 적용",
                    "duration": 40.0,
                    "resources": ["cpu", "memory", "storage"],
                },
                {"step": "효과 검증", "duration": 20.0, "resources": ["cpu", "memory"]},
            ],
            default_criteria=["성능 향상", "최적화 완료", "효과 검증"],
            resource_profile={"cpu": 0.9, "memory": 0.8, "storage": 0.5},
            time_profile={"min": 60.0, "max": 1800.0, "avg": 600.0},
        )

        return templates

    async def generate_behavior_plan(
        self,
        decision_result: Dict[str, Any],
        available_resources: Dict[str, float],
        constraints: Dict[str, Any],
    ) -> BehaviorPlan:
        """행동 계획 생성"""
        try:
            # 1. 행동 타입 결정
            behavior_type = await self._determine_behavior_type(decision_result)

            # 2. 전략 선택
            strategy = await self._select_strategy(decision_result, constraints)

            # 3. 템플릿 선택 및 커스터마이징
            template = await self._select_template(behavior_type, strategy)
            customized_steps = await self._customize_steps(template, decision_result)

            # 4. 성공 기준 정의
            success_criteria = await self._define_success_criteria(template, decision_result)

            # 5. 위험 평가
            risk_assessment = await self._assess_risks(decision_result, customized_steps)

            # 6. 리소스 요구사항 계산
            resource_requirements = await self._calculate_resource_requirements(
                template, customized_steps, available_resources
            )

            # 7. 시간 추정
            time_estimate = await self._estimate_time(template, customized_steps)

            # 8. 우선순위 계산
            priority = await self._calculate_priority(decision_result, constraints)

            # 9. 행동 계획 생성
            behavior_id = f"behavior_{int(time.time())}_{hash(str(decision_result)) % 10000}"

            return BehaviorPlan(
                behavior_id=behavior_id,
                behavior_type=behavior_type,
                strategy=strategy,
                description=await self._generate_description(decision_result, behavior_type),
                steps=customized_steps,
                expected_outcome=await self._generate_expected_outcome(decision_result),
                success_criteria=success_criteria,
                risk_assessment=risk_assessment,
                resource_requirements=resource_requirements,
                time_estimate=time_estimate,
                priority=priority,
                created_at=datetime.now(),
            )

        except Exception as e:
            logger.error(f"행동 계획 생성 실패: {e}")
            raise

    async def _determine_behavior_type(self, decision_result: Dict[str, Any]) -> BehaviorType:
        """행동 타입 결정"""
        situation_type = decision_result.get("situation_type", "")
        urgency = decision_result.get("urgency_level", 0.0)
        complexity = decision_result.get("complexity_score", 0.0)

        if urgency > 0.8:
            return BehaviorType.RESPONSE
        elif "learning" in situation_type:
            return BehaviorType.LEARNING
        elif complexity > 0.7:
            return BehaviorType.ANALYSIS
        elif "optimization" in decision_result.get("decision", ""):
            return BehaviorType.OPTIMIZATION
        elif "create" in decision_result.get("decision", ""):
            return BehaviorType.CREATION
        else:
            return BehaviorType.INTERACTION

    async def _select_strategy(self, decision_result: Dict[str, Any], constraints: Dict[str, Any]) -> BehaviorStrategy:
        """전략 선택"""
        urgency = decision_result.get("urgency_level", 0.0)
        complexity = decision_result.get("complexity_score", 0.0)
        resource_availability = constraints.get("resource_availability", 0.5)

        # 전략 점수 계산
        strategy_scores = {
            BehaviorStrategy.IMMEDIATE: urgency * 0.8 + (1 - complexity) * 0.2,
            BehaviorStrategy.SEQUENTIAL: complexity * 0.6 + (1 - urgency) * 0.4,
            BehaviorStrategy.PARALLEL: resource_availability * 0.7 + complexity * 0.3,
            BehaviorStrategy.CONDITIONAL: (1 - urgency) * 0.8 + complexity * 0.2,
            BehaviorStrategy.ADAPTIVE: complexity * 0.5 + resource_availability * 0.5,
        }

        # 최고 점수 전략 선택
        return max(strategy_scores, key=strategy_scores.get)

    async def _select_template(self, behavior_type: BehaviorType, strategy: BehaviorStrategy) -> BehaviorTemplate:
        """템플릿 선택"""
        # 행동 타입에 따른 템플릿 매핑
        template_mapping = {
            BehaviorType.RESPONSE: "immediate_response",
            BehaviorType.ANALYSIS: "data_analysis",
            BehaviorType.LEARNING: "learning_action",
            BehaviorType.OPTIMIZATION: "optimization_task",
        }

        template_key = template_mapping.get(behavior_type, "immediate_response")
        return self.behavior_templates[template_key]

    async def _customize_steps(
        self, template: BehaviorTemplate, decision_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """단계 커스터마이징"""
        customized_steps = []

        for step in template.base_steps:
            # 의사결정 결과에 따른 단계 조정
            adjusted_step = step.copy()

            # 복잡도에 따른 시간 조정
            complexity = decision_result.get("complexity_score", 0.5)
            adjusted_step["duration"] *= 1 + complexity * 0.5

            # 긴급도에 따른 우선순위 조정
            urgency = decision_result.get("urgency_level", 0.0)
            adjusted_step["priority"] = urgency

            customized_steps.append(adjusted_step)

        return customized_steps

    async def _define_success_criteria(self, template: BehaviorTemplate, decision_result: Dict[str, Any]) -> List[str]:
        """성공 기준 정의"""
        criteria = template.default_criteria.copy()

        # 의사결정 결과에 따른 추가 기준
        if decision_result.get("urgency_level", 0.0) > 0.8:
            criteria.append("응답 시간 < 0.5초")

        if decision_result.get("complexity_score", 0.0) > 0.7:
            criteria.append("정확도 > 95%")

        return criteria

    async def _assess_risks(self, decision_result: Dict[str, Any], steps: List[Dict[str, Any]]) -> Dict[str, float]:
        """위험 평가"""
        risks = {}

        # 시간 위험
        total_duration = sum(step.get("duration", 0) for step in steps)
        risks["time_risk"] = min(total_duration / 300.0, 1.0)  # 5분 기준

        # 복잡도 위험
        complexity = decision_result.get("complexity_score", 0.0)
        risks["complexity_risk"] = complexity

        # 리소스 위험
        resource_count = sum(len(step.get("resources", [])) for step in steps)
        risks["resource_risk"] = min(resource_count / 10.0, 1.0)

        # 전체 위험도
        risks["total_risk"] = (risks["time_risk"] + risks["complexity_risk"] + risks["resource_risk"]) / 3

        return risks

    async def _calculate_resource_requirements(
        self,
        template: BehaviorTemplate,
        steps: List[Dict[str, Any]],
        available_resources: Dict[str, float],
    ) -> Dict[str, Any]:
        """리소스 요구사항 계산"""
        requirements = {}

        # 템플릿의 리소스 프로필 기반
        for resource, intensity in template.resource_profile.items():
            requirements[resource] = {
                "required": intensity,
                "available": available_resources.get(resource, 0.0),
                "sufficient": available_resources.get(resource, 0.0) >= intensity,
            }

        return requirements

    async def _estimate_time(self, template: BehaviorTemplate, steps: List[Dict[str, Any]]) -> float:
        """시간 추정"""
        # 단계별 시간 합계
        total_time = sum(step.get("duration", 0) for step in steps)

        # 템플릿의 시간 프로필 고려
        avg_time = template.time_profile["avg"]

        # 가중 평균
        estimated_time = (total_time + avg_time) / 2

        return min(estimated_time, template.time_profile["max"])

    async def _calculate_priority(self, decision_result: Dict[str, Any], constraints: Dict[str, Any]) -> float:
        """우선순위 계산"""
        urgency = decision_result.get("urgency_level", 0.0)
        importance = decision_result.get("importance", 0.0)
        complexity = decision_result.get("complexity_score", 0.0)
        resource_availability = constraints.get("resource_availability", 0.5)

        # 가중 평균
        priority = (
            urgency * self.strategy_weights["urgency"]
            + importance * self.strategy_weights["importance"]
            + complexity * self.strategy_weights["complexity"]
            + resource_availability * self.strategy_weights["resource_availability"]
        )

        return min(priority, 1.0)

    async def _generate_description(self, decision_result: Dict[str, Any], behavior_type: BehaviorType) -> str:
        """행동 설명 생성"""
        decision = decision_result.get("decision", "")
        reasoning = decision_result.get("reasoning", "")

        type_descriptions = {
            BehaviorType.RESPONSE: "응답 행동",
            BehaviorType.ANALYSIS: "분석 행동",
            BehaviorType.LEARNING: "학습 행동",
            BehaviorType.OPTIMIZATION: "최적화 행동",
            BehaviorType.CREATION: "생성 행동",
            BehaviorType.INTERACTION: "상호작용 행동",
        }

        return f"{type_descriptions[behavior_type]}: {decision} - {reasoning}"

    async def _generate_expected_outcome(self, decision_result: Dict[str, Any]) -> Dict[str, Any]:
        """예상 결과 생성"""
        return {
            "goal": decision_result.get("decision", ""),
            "quality": ("높음" if decision_result.get("confidence", 0.0) > 0.7 else "보통"),
            "impact": ("높음" if decision_result.get("importance", 0.0) > 0.7 else "보통"),
            "timeline": ("즉시" if decision_result.get("urgency_level", 0.0) > 0.8 else "일반"),
        }


async def test_behavior_generator():
    """행동 생성 엔진 테스트"""
    print("=== DuRiCore Phase 5 Day 4 - 행동 생성 엔진 테스트 ===")

    # 행동 생성 엔진 초기화
    generator = BehaviorGenerator()

    # 테스트용 의사결정 결과들
    test_decisions = [
        {
            "decision": "urgent_response",
            "reasoning": "긴급한 상황에 대한 즉시 대응",
            "situation_type": "emergency",
            "urgency_level": 0.9,
            "importance": 0.8,
            "complexity_score": 0.3,
            "confidence": 0.85,
        },
        {
            "decision": "data_analysis",
            "reasoning": "복잡한 데이터 분석 수행",
            "situation_type": "analysis",
            "urgency_level": 0.4,
            "importance": 0.7,
            "complexity_score": 0.8,
            "confidence": 0.75,
        },
        {
            "decision": "learning_optimization",
            "reasoning": "학습 모델 최적화",
            "situation_type": "learning",
            "urgency_level": 0.2,
            "importance": 0.6,
            "complexity_score": 0.7,
            "confidence": 0.8,
        },
    ]

    available_resources = {"cpu": 0.8, "memory": 0.7, "storage": 0.6, "network": 0.9}

    constraints = {"time_limit": 600, "resource_availability": 0.7}

    for i, decision in enumerate(test_decisions, 1):
        print(f"\n{i}. 행동 계획 생성 테스트")
        print(f"의사결정: {decision['decision']}")
        print(f"이유: {decision['reasoning']}")

        # 행동 계획 생성
        behavior_plan = await generator.generate_behavior_plan(decision, available_resources, constraints)

        print("생성된 행동 계획:")
        print(f"- 행동 ID: {behavior_plan.behavior_id}")
        print(f"- 행동 타입: {behavior_plan.behavior_type.value}")
        print(f"- 전략: {behavior_plan.strategy.value}")
        print(f"- 우선순위: {behavior_plan.priority:.3f}")
        print(f"- 예상 소요시간: {behavior_plan.time_estimate:.1f}초")
        print(f"- 단계 수: {len(behavior_plan.steps)}")
        print(f"- 성공 기준: {behavior_plan.success_criteria}")
        print(f"- 위험도: {behavior_plan.risk_assessment['total_risk']:.3f}")

    print("\n=== 테스트 완료 ===")


if __name__ == "__main__":
    asyncio.run(test_behavior_generator())
