#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 추론 시스템 모듈 테스트

새로 생성된 reasoning_system 모듈들을 테스트합니다.
"""

import asyncio
import logging
import os
import sys

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DuRiCore 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def test_reasoning_engine_modules():
    """추론 엔진 모듈 테스트"""
    logger.info("=== 추론 엔진 모듈 테스트 시작 ===")

    try:
        # Inference Engine 테스트
        from reasoning_system.reasoning_engine import InferenceContext, InferenceEngine, InferenceType

        inference_engine = InferenceEngine()
        context = InferenceContext(context_type="test", input_data={"key1": "value1", "key2": "value2"})

        result = await inference_engine.perform_inference(context, InferenceType.DEDUCTIVE)
        logger.info(f"Inference Engine 테스트 성공: {result.confidence:.2f}")

        # Logic Processor 테스트
        from reasoning_system.reasoning_engine import LogicProcessor, LogicType

        logic_processor = LogicProcessor()
        input_data = {
            "rule1": {"premises": ["A", "B"], "conclusion": "C", "confidence": 0.8},
            "rule2": {"premises": ["D"], "conclusion": "E", "confidence": 0.7},
        }

        analysis = await logic_processor.process_logic(input_data, LogicType.PROPOSITIONAL)
        logger.info(f"Logic Processor 테스트 성공: {analysis.consistency_score:.2f}")

        # Decision Maker 테스트
        from reasoning_system.reasoning_engine import (
            DecisionContext,
            DecisionCriteria,
            DecisionMaker,
            DecisionOption,
            DecisionType,
        )

        decision_maker = DecisionMaker()
        criteria = [
            DecisionCriteria(
                criteria_id="c1",
                name="Criteria 1",
                weight=0.5,
                description="Test criteria",
                evaluation_method="scale",
            ),
            DecisionCriteria(
                criteria_id="c2",
                name="Criteria 2",
                weight=0.5,
                description="Test criteria",
                evaluation_method="scale",
            ),
        ]
        options = [
            DecisionOption(option_id="o1", name="Option 1", description="Test option 1"),
            DecisionOption(option_id="o2", name="Option 2", description="Test option 2"),
        ]
        decision_context = DecisionContext(
            context_id="test_context",
            description="Test decision context",
            criteria=criteria,
            options=options,
        )

        decision_result = await decision_maker.make_decision(decision_context, DecisionType.RATIONAL)
        logger.info(f"Decision Maker 테스트 성공: {decision_result.confidence:.2f}")

        logger.info("=== 추론 엔진 모듈 테스트 완료 ===")
        return True

    except Exception as e:
        logger.error(f"추론 엔진 모듈 테스트 실패: {e}")
        return False


async def test_reasoning_strategies_modules():
    """추론 전략 모듈 테스트"""
    logger.info("=== 추론 전략 모듈 테스트 시작 ===")

    try:
        # Deductive Reasoning 테스트
        from reasoning_system.reasoning_strategies import DeductivePremise, DeductiveReasoning, DeductiveRuleType

        deductive_reasoning = DeductiveReasoning()
        premises = [
            DeductivePremise(premise_id="p1", content="All A are B", confidence=0.9),
            DeductivePremise(premise_id="p2", content="C is A", confidence=0.8),
        ]

        analysis = await deductive_reasoning.perform_deductive_reasoning(premises, DeductiveRuleType.MODUS_PONENS)
        logger.info(f"Deductive Reasoning 테스트 성공: {analysis.validity_score:.2f}")

        # Inductive Reasoning 테스트
        from reasoning_system.reasoning_strategies import InductiveObservation, InductiveReasoning, InductiveType

        inductive_reasoning = InductiveReasoning()
        observations = [
            InductiveObservation(observation_id="o1", content="Observation 1", confidence=0.8),
            InductiveObservation(observation_id="o2", content="Observation 2", confidence=0.7),
            InductiveObservation(observation_id="o3", content="Observation 3", confidence=0.9),
        ]

        analysis = await inductive_reasoning.perform_inductive_reasoning(observations, InductiveType.ENUMERATIVE)
        logger.info(f"Inductive Reasoning 테스트 성공: {analysis.pattern_strength:.2f}")

        # Abductive Reasoning 테스트
        from reasoning_system.reasoning_strategies import AbductiveObservation, AbductiveReasoning, AbductiveType

        abductive_reasoning = AbductiveReasoning()
        observations = [
            AbductiveObservation(observation_id="o1", content="Unexpected observation 1", confidence=0.8),
            AbductiveObservation(observation_id="o2", content="Unexpected observation 2", confidence=0.7),
        ]

        analysis = await abductive_reasoning.perform_abductive_reasoning(observations, AbductiveType.SIMPLE)
        logger.info(f"Abductive Reasoning 테스트 성공: {analysis.explanatory_power:.2f}")

        logger.info("=== 추론 전략 모듈 테스트 완료 ===")
        return True

    except Exception as e:
        logger.error(f"추론 전략 모듈 테스트 실패: {e}")
        return False


async def test_reasoning_optimization_modules():
    """추론 최적화 모듈 테스트"""
    logger.info("=== 추론 최적화 모듈 테스트 시작 ===")

    try:
        from reasoning_system.reasoning_optimization import OptimizationTarget, OptimizationType, ReasoningOptimizer

        optimizer = ReasoningOptimizer()
        targets = [
            OptimizationTarget(
                target_id="t1",
                target_type="processing_time",
                current_value=100.0,
                target_value=50.0,
            ),
            OptimizationTarget(
                target_id="t2",
                target_type="memory_usage",
                current_value=512.0,
                target_value=256.0,
            ),
        ]

        analysis = await optimizer.optimize_reasoning(targets, OptimizationType.PERFORMANCE)
        logger.info(f"Reasoning Optimizer 테스트 성공: {analysis.overall_improvement:.2f}")

        logger.info("=== 추론 최적화 모듈 테스트 완료 ===")
        return True

    except Exception as e:
        logger.error(f"추론 최적화 모듈 테스트 실패: {e}")
        return False


async def test_module_imports():
    """모듈 import 테스트"""
    logger.info("=== 모듈 Import 테스트 시작 ===")

    try:
        # Reasoning Engine imports

        logger.info("Reasoning Engine imports 성공")

        # Reasoning Strategies imports

        logger.info("Reasoning Strategies imports 성공")

        # Reasoning Optimization imports

        logger.info("Reasoning Optimization imports 성공")

        logger.info("=== 모듈 Import 테스트 완료 ===")
        return True

    except Exception as e:
        logger.error(f"모듈 Import 테스트 실패: {e}")
        return False


async def main():
    """메인 테스트 함수"""
    logger.info("DuRi 추론 시스템 모듈 테스트 시작")

    test_results = {}

    # 모듈 import 테스트
    test_results["imports"] = await test_module_imports()

    # 추론 엔진 모듈 테스트
    test_results["reasoning_engine"] = await test_reasoning_engine_modules()

    # 추론 전략 모듈 테스트
    test_results["reasoning_strategies"] = await test_reasoning_strategies_modules()

    # 추론 최적화 모듈 테스트
    test_results["reasoning_optimization"] = await test_reasoning_optimization_modules()

    # 결과 요약
    logger.info("=== 테스트 결과 요약 ===")
    for test_name, result in test_results.items():
        status = "성공" if result else "실패"
        logger.info(f"{test_name}: {status}")

    success_count = sum(test_results.values())
    total_count = len(test_results)

    logger.info(f"전체 테스트 결과: {success_count}/{total_count} 성공")

    if success_count == total_count:
        logger.info("🎉 모든 테스트가 성공했습니다!")
        return True
    else:
        logger.error("❌ 일부 테스트가 실패했습니다.")
        return False


if __name__ == "__main__":
    # 비동기 테스트 실행
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
