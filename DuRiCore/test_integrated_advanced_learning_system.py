#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase 1-3 Week 3 Day 13 - 통합 고급 학습 시스템 테스트

기존 학습 관련 시스템들과의 통합 및 새로운 고급 학습 기능들의 테스트
"""

import asyncio
from datetime import datetime
import json
import logging
import time
from typing import Any, Dict, List

# 테스트 대상 시스템 import
try:
    from integrated_advanced_learning_system import (
        ContinuousLearningEngine,
        IntegratedAdvancedLearningSystem,
        KnowledgeEvolutionSystem,
        KnowledgeIntegrationSystem,
        KnowledgeSource,
        LearningEfficiencyOptimizer,
        LearningEvolutionType,
    )
except ImportError as e:
    logging.error(f"시스템 import 실패: {e}")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AdvancedLearningSystemTester:
    """고급 학습 시스템 테스터"""

    def __init__(self):
        self.system = IntegratedAdvancedLearningSystem()
        self.test_results = []

    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """종합 테스트 실행"""
        logger.info("=== Day 13 고급 학습 시스템 종합 테스트 시작 ===")

        start_time = time.time()

        # 1. 기본 기능 테스트
        basic_test_result = await self._test_basic_functionality()

        # 2. 지속적 학습 엔진 테스트
        continuous_learning_result = await self._test_continuous_learning_engine()

        # 3. 지식 진화 시스템 테스트
        knowledge_evolution_result = await self._test_knowledge_evolution_system()

        # 4. 학습 효율성 최적화 테스트
        efficiency_optimization_result = (
            await self._test_learning_efficiency_optimizer()
        )

        # 5. 지식 통합 시스템 테스트
        knowledge_integration_result = await self._test_knowledge_integration_system()

        # 6. 통합 시스템 테스트
        integrated_system_result = await self._test_integrated_system()

        # 7. 성능 테스트
        performance_result = await self._test_performance()

        # 8. 결과 종합
        total_time = time.time() - start_time

        comprehensive_result = {
            "test_timestamp": datetime.now().isoformat(),
            "total_test_time": total_time,
            "basic_functionality": basic_test_result,
            "continuous_learning_engine": continuous_learning_result,
            "knowledge_evolution_system": knowledge_evolution_result,
            "learning_efficiency_optimizer": efficiency_optimization_result,
            "knowledge_integration_system": knowledge_integration_result,
            "integrated_system": integrated_system_result,
            "performance": performance_result,
            "overall_success_rate": self._calculate_overall_success_rate(
                [
                    basic_test_result,
                    continuous_learning_result,
                    knowledge_evolution_result,
                    efficiency_optimization_result,
                    knowledge_integration_result,
                    integrated_system_result,
                ]
            ),
        }

        logger.info(
            f"=== Day 13 고급 학습 시스템 종합 테스트 완료 (소요시간: {total_time:.2f}초) ==="
        )
        return comprehensive_result

    async def _test_basic_functionality(self) -> Dict[str, Any]:
        """기본 기능 테스트"""
        logger.info("1. 기본 기능 테스트 시작")

        try:
            # 시스템 초기화 테스트
            status = await self.system.get_system_status()

            # 성능 리포트 테스트
            report = await self.system.get_performance_report()

            result = {
                "status": "success",
                "system_status": status,
                "performance_report": report,
                "message": "기본 기능 테스트 성공",
            }

            logger.info("✅ 기본 기능 테스트 성공")
            return result

        except Exception as e:
            logger.error(f"❌ 기본 기능 테스트 실패: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "기본 기능 테스트 실패",
            }

    async def _test_continuous_learning_engine(self) -> Dict[str, Any]:
        """지속적 학습 엔진 테스트"""
        logger.info("2. 지속적 학습 엔진 테스트 시작")

        try:
            engine = ContinuousLearningEngine()

            # 테스트 컨텍스트
            test_context = {
                "type": "cognitive",
                "content": "지속적 학습 엔진의 지식 획득 및 통찰 발견 능력 테스트",
                "difficulty": 0.7,
                "domain": "cognitive",
            }

            # 지속적 학습 실행
            session = await engine.start_continuous_learning(test_context)

            result = {
                "status": "success",
                "session_id": session.session_id,
                "knowledge_gained_count": len(session.knowledge_gained),
                "insights_discovered_count": len(session.insights_discovered),
                "efficiency_score": session.efficiency_score,
                "evolution_score": session.evolution_score,
                "message": "지속적 학습 엔진 테스트 성공",
            }

            logger.info(
                f"✅ 지속적 학습 엔진 테스트 성공 (지식: {len(session.knowledge_gained)}개, 통찰: {len(session.insights_discovered)}개)"
            )
            return result

        except Exception as e:
            logger.error(f"❌ 지속적 학습 엔진 테스트 실패: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "지속적 학습 엔진 테스트 실패",
            }

    async def _test_knowledge_evolution_system(self) -> Dict[str, Any]:
        """지식 진화 시스템 테스트"""
        logger.info("3. 지식 진화 시스템 테스트 시작")

        try:
            system = KnowledgeEvolutionSystem()

            # 테스트 데이터
            original_knowledge = {
                "concept": "기본 학습",
                "confidence": 0.5,
                "domain": "general",
            }

            new_information = {
                "concept": "고급 학습",
                "confidence": 0.8,
                "domain": "advanced",
                "new_features": ["지속적 학습", "지식 진화", "효율성 최적화"],
            }

            # 지식 진화 실행
            evolution = await system.evolve_knowledge(
                original_knowledge, new_information
            )

            result = {
                "status": "success",
                "evolution_id": evolution.evolution_id,
                "evolution_factors_count": len(evolution.evolution_factors),
                "confidence_change": evolution.confidence_change,
                "relevance_score": evolution.relevance_score,
                "integration_level": evolution.integration_level,
                "message": "지식 진화 시스템 테스트 성공",
            }

            logger.info(
                f"✅ 지식 진화 시스템 테스트 성공 (진화 요인: {len(evolution.evolution_factors)}개)"
            )
            return result

        except Exception as e:
            logger.error(f"❌ 지식 진화 시스템 테스트 실패: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "지식 진화 시스템 테스트 실패",
            }

    async def _test_learning_efficiency_optimizer(self) -> Dict[str, Any]:
        """학습 효율성 최적화 테스트"""
        logger.info("4. 학습 효율성 최적화 테스트 시작")

        try:
            optimizer = LearningEfficiencyOptimizer()

            # 테스트 세션 생성
            from integrated_advanced_learning_system import (
                ContinuousLearningSession,
                LearningEvolutionType,
            )

            test_session = ContinuousLearningSession(
                session_id="test_session",
                learning_type=LearningEvolutionType.CONTINUOUS_LEARNING,
                start_time=datetime.now(),
                learning_content={
                    "type": "practical",
                    "content": "학습 효율성 최적화 테스트를 위한 실용적 학습 내용",
                    "difficulty": 0.6,
                    "domain": "practical",
                },
                knowledge_gained=["효율성 최적화", "학습 전략", "성과 측정"],
                insights_discovered=["개인화된 학습", "적응적 접근"],
                efficiency_score=0.7,
                evolution_score=0.6,
            )

            # 효율성 최적화 실행
            efficiency = await optimizer.optimize_learning_efficiency(test_session)

            result = {
                "status": "success",
                "efficiency_id": efficiency.efficiency_id,
                "speed_score": efficiency.speed_score,
                "quality_score": efficiency.quality_score,
                "retention_score": efficiency.retention_score,
                "application_score": efficiency.application_score,
                "overall_efficiency": efficiency.overall_efficiency,
                "optimization_suggestions_count": len(
                    efficiency.optimization_suggestions
                ),
                "message": "학습 효율성 최적화 테스트 성공",
            }

            logger.info(
                f"✅ 학습 효율성 최적화 테스트 성공 (전체 효율성: {efficiency.overall_efficiency:.2f})"
            )
            return result

        except Exception as e:
            logger.error(f"❌ 학습 효율성 최적화 테스트 실패: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "학습 효율성 최적화 테스트 실패",
            }

    async def _test_knowledge_integration_system(self) -> Dict[str, Any]:
        """지식 통합 시스템 테스트"""
        logger.info("5. 지식 통합 시스템 테스트 시작")

        try:
            system = KnowledgeIntegrationSystem()

            # 테스트 데이터
            source_knowledge = [
                {"domain": "cognitive", "concepts": ["분석", "추론", "논리"]},
                {"domain": "emotional", "concepts": ["감정 인식", "감정 조절"]},
                {"domain": "creative", "concepts": ["창의적 사고", "혁신"]},
            ]

            # 지식 통합 실행
            integration = await system.integrate_knowledge(
                source_knowledge, "hierarchical"
            )

            result = {
                "status": "success",
                "integration_id": integration.integration_id,
                "integration_method": integration.integration_method,
                "coherence_score": integration.coherence_score,
                "completeness_score": integration.completeness_score,
                "accessibility_score": integration.accessibility_score,
                "message": "지식 통합 시스템 테스트 성공",
            }

            logger.info(
                f"✅ 지식 통합 시스템 테스트 성공 (일관성: {integration.coherence_score:.2f})"
            )
            return result

        except Exception as e:
            logger.error(f"❌ 지식 통합 시스템 테스트 실패: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "지식 통합 시스템 테스트 실패",
            }

    async def _test_integrated_system(self) -> Dict[str, Any]:
        """통합 시스템 테스트"""
        logger.info("6. 통합 시스템 테스트 시작")

        try:
            # 테스트 컨텍스트
            test_context = {
                "type": "comprehensive",
                "content": "Day 13 고급 학습 시스템의 통합 기능 테스트 - 지속적 학습, 지식 진화, 효율성 최적화, 지식 통합을 포함한 종합적인 학습 시스템",
                "difficulty": 0.8,
                "domain": "integrated",
            }

            # 통합 시스템 실행
            result = await self.system.process_advanced_learning(test_context)

            test_result = {
                "status": "success",
                "result_id": result.result_id,
                "overall_learning_score": result.overall_learning_score,
                "evolution_progress": result.evolution_progress,
                "efficiency_improvement": result.efficiency_improvement,
                "integration_success": result.integration_success,
                "continuous_learning_sessions_count": len(
                    result.continuous_learning_sessions
                ),
                "knowledge_evolutions_count": len(result.knowledge_evolutions),
                "learning_efficiencies_count": len(result.learning_efficiencies),
                "knowledge_integrations_count": len(result.knowledge_integrations),
                "message": "통합 시스템 테스트 성공",
            }

            logger.info(
                f"✅ 통합 시스템 테스트 성공 (전체 학습 점수: {result.overall_learning_score:.2f})"
            )
            return test_result

        except Exception as e:
            logger.error(f"❌ 통합 시스템 테스트 실패: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "통합 시스템 테스트 실패",
            }

    async def _test_performance(self) -> Dict[str, Any]:
        """성능 테스트"""
        logger.info("7. 성능 테스트 시작")

        try:
            # 성능 테스트를 위한 반복 실행
            test_contexts = [
                {
                    "type": "cognitive",
                    "content": "인지적 학습 테스트",
                    "difficulty": 0.5,
                },
                {
                    "type": "emotional",
                    "content": "감정적 학습 테스트",
                    "difficulty": 0.6,
                },
                {
                    "type": "creative",
                    "content": "창의적 학습 테스트",
                    "difficulty": 0.7,
                },
            ]

            start_time = time.time()
            results = []

            for i, context in enumerate(test_contexts, 1):
                logger.info(f"  성능 테스트 {i}/3 실행 중...")
                result = await self.system.process_advanced_learning(context)
                results.append(result.overall_learning_score)

            total_time = time.time() - start_time
            average_score = sum(results) / len(results) if results else 0.0

            performance_result = {
                "status": "success",
                "total_execution_time": total_time,
                "average_execution_time": total_time / len(test_contexts),
                "average_learning_score": average_score,
                "test_count": len(test_contexts),
                "message": "성능 테스트 성공",
            }

            logger.info(
                f"✅ 성능 테스트 성공 (평균 실행시간: {total_time/len(test_contexts):.2f}초, 평균 점수: {average_score:.2f})"
            )
            return performance_result

        except Exception as e:
            logger.error(f"❌ 성능 테스트 실패: {e}")
            return {"status": "error", "error": str(e), "message": "성능 테스트 실패"}

    def _calculate_overall_success_rate(
        self, test_results: List[Dict[str, Any]]
    ) -> float:
        """전체 성공률 계산"""
        successful_tests = sum(
            1 for result in test_results if result.get("status") == "success"
        )
        total_tests = len(test_results)

        return successful_tests / total_tests if total_tests > 0 else 0.0

    def save_test_results(self, results: Dict[str, Any], filename: str = None):
        """테스트 결과 저장"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = (
                f"test_results_integrated_advanced_learning_system_{timestamp}.json"
            )

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)

            logger.info(f"테스트 결과가 {filename}에 저장되었습니다.")

        except Exception as e:
            logger.error(f"테스트 결과 저장 실패: {e}")


async def main():
    """메인 테스트 함수"""
    logger.info("🚀 Day 13 고급 학습 시스템 테스트 시작")

    # 테스터 초기화
    tester = AdvancedLearningSystemTester()

    # 종합 테스트 실행
    results = await tester.run_comprehensive_test()

    # 결과 출력
    logger.info("\n=== 테스트 결과 요약 ===")
    logger.info(f"전체 성공률: {results['overall_success_rate']:.1%}")
    logger.info(f"총 테스트 시간: {results['total_test_time']:.2f}초")

    # 각 테스트 결과 출력
    for test_name, test_result in results.items():
        if test_name not in [
            "test_timestamp",
            "total_test_time",
            "overall_success_rate",
        ]:
            status = test_result.get("status", "unknown")
            logger.info(f"{test_name}: {status}")

    # 결과 저장
    tester.save_test_results(results)

    logger.info("🎉 Day 13 고급 학습 시스템 테스트 완료!")
    return results


if __name__ == "__main__":
    asyncio.run(main())
