#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-3: 학습 시스템 모듈 테스트

모든 학습 시스템 모듈의 import 및 기본 기능을 테스트합니다.
"""

import asyncio
from datetime import datetime, timedelta
import logging
import os
import sys
from typing import Any, Dict

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_core_modules():
    """Core 모듈 테스트"""
    logger.info("🔍 Core 모듈 테스트 시작")

    try:
        # Core 모듈 import 테스트
        from DuRiCore.learning_system.core import (
            EvolutionSession,
            EvolutionType,
            KnowledgeEvolution,
            KnowledgeEvolutionSystem,
            KnowledgeItem,
            KnowledgeQuality,
            LearningEngine,
            LearningOptimizationSystem,
            LearningProcess,
            LearningProcessType,
            LearningResult,
            LearningSession,
            LearningSessionStatus,
            OptimizationResult,
            OptimizationStatus,
            OptimizationStrategy,
            OptimizationTarget,
            OptimizationType,
            PerformanceMetrics,
        )

        # LearningEngine 인스턴스 생성 테스트
        learning_engine = LearningEngine()
        logger.info(f"✅ LearningEngine 생성 성공: {type(learning_engine)}")

        # KnowledgeEvolutionSystem 인스턴스 생성 테스트
        knowledge_evolution = KnowledgeEvolutionSystem()
        logger.info(
            f"✅ KnowledgeEvolutionSystem 생성 성공: {type(knowledge_evolution)}"
        )

        # LearningOptimizationSystem 인스턴스 생성 테스트
        learning_optimization = LearningOptimizationSystem()
        logger.info(
            f"✅ LearningOptimizationSystem 생성 성공: {type(learning_optimization)}"
        )

        logger.info("✅ Core 모듈 테스트 완료")
        return True

    except Exception as e:
        logger.error(f"❌ Core 모듈 테스트 실패: {e}")
        return False


def test_strategies_modules():
    """Strategies 모듈 테스트"""
    logger.info("🔍 Strategies 모듈 테스트 시작")

    try:
        # Strategies 모듈 import 테스트
        from DuRiCore.learning_system.strategies import (
            AdaptationResult,
            AdaptationType,
            AdaptiveLearningStrategy,
            CognitiveMetaLearningMetrics,
            CognitiveMetaLearningState,
            CognitiveMetaLearningStrategy,
            CuriosityTrigger,
            LearningActivity,
            LearningData,
            LearningEfficiency,
            LearningGoal,
            LearningModel,
            LearningOutcome,
            LearningPattern,
            LearningResult,
            LearningStatus,
            LearningStrategy,
            LearningType,
            MetaCognitionInsight,
            MetaCognitionLevel,
            MetaCognitionResult,
            MetaCognitionStrategy,
            MetaLearningProcess,
            MetaLearningStage,
            MetaLearningType,
            ReflectionType,
            SelfDirectedLearningResult,
            SelfDirectedLearningStrategy,
            SelfDiscoveredProblem,
            SelfReflection,
            ThinkingProcess,
            ThinkingQuality,
            ThinkingQualityAssessment,
        )

        # SelfDirectedLearningStrategy 인스턴스 생성 테스트
        self_directed_learning = SelfDirectedLearningStrategy()
        logger.info(
            f"✅ SelfDirectedLearningStrategy 생성 성공: {type(self_directed_learning)}"
        )

        # AdaptiveLearningStrategy 인스턴스 생성 테스트
        adaptive_learning = AdaptiveLearningStrategy()
        logger.info(f"✅ AdaptiveLearningStrategy 생성 성공: {type(adaptive_learning)}")

        # MetaCognitionStrategy 인스턴스 생성 테스트
        meta_cognition = MetaCognitionStrategy()
        logger.info(f"✅ MetaCognitionStrategy 생성 성공: {type(meta_cognition)}")

        # CognitiveMetaLearningStrategy 인스턴스 생성 테스트
        cognitive_meta_learning = CognitiveMetaLearningStrategy()
        logger.info(
            f"✅ CognitiveMetaLearningStrategy 생성 성공: {type(cognitive_meta_learning)}"
        )

        logger.info("✅ Strategies 모듈 테스트 완료")
        return True

    except Exception as e:
        logger.error(f"❌ Strategies 모듈 테스트 실패: {e}")
        return False


def test_integration_modules():
    """Integration 모듈 테스트"""
    logger.info("🔍 Integration 모듈 테스트 시작")

    try:
        # Integration 모듈 import 테스트
        from DuRiCore.learning_system.integration import (
            IntegratedKnowledge,
            IntegratedLearningResult,
            IntegrationMethod,
            IntegrationSession,
            IntegrationStatus,
            IntegrationType,
            KnowledgeIntegrationSession,
            KnowledgeIntegrationSystem,
            KnowledgeQuality,
            KnowledgeSource,
            LearningIntegrationSystem,
            LearningStrategyResult,
        )

        # LearningIntegrationSystem 인스턴스 생성 테스트
        learning_integration = LearningIntegrationSystem()
        logger.info(
            f"✅ LearningIntegrationSystem 생성 성공: {type(learning_integration)}"
        )

        # KnowledgeIntegrationSystem 인스턴스 생성 테스트
        knowledge_integration = KnowledgeIntegrationSystem()
        logger.info(
            f"✅ KnowledgeIntegrationSystem 생성 성공: {type(knowledge_integration)}"
        )

        logger.info("✅ Integration 모듈 테스트 완료")
        return True

    except Exception as e:
        logger.error(f"❌ Integration 모듈 테스트 실패: {e}")
        return False


def test_monitoring_modules():
    """Monitoring 모듈 테스트"""
    logger.info("🔍 Monitoring 모듈 테스트 시작")

    try:
        # Monitoring 모듈 import 테스트
        from DuRiCore.learning_system.monitoring import (
            AdvancedLearningMonitoringSystem,
            LearningEvent,
            LearningIssue,
            LearningIssueType,
            LearningMetrics,
            LearningMonitoringSystem,
            LearningPattern,
            LearningPhase,
            LearningPrediction,
            MonitoringLevel,
            MonitoringSession,
            MonitoringStatus,
            OptimizationRecommendation,
        )

        # LearningMonitoringSystem 인스턴스 생성 테스트
        learning_monitoring = LearningMonitoringSystem()
        logger.info(
            f"✅ LearningMonitoringSystem 생성 성공: {type(learning_monitoring)}"
        )

        # AdvancedLearningMonitoringSystem 인스턴스 생성 테스트
        advanced_monitoring = AdvancedLearningMonitoringSystem()
        logger.info(
            f"✅ AdvancedLearningMonitoringSystem 생성 성공: {type(advanced_monitoring)}"
        )

        logger.info("✅ Monitoring 모듈 테스트 완료")
        return True

    except Exception as e:
        logger.error(f"❌ Monitoring 모듈 테스트 실패: {e}")
        return False


async def test_async_functionality():
    """비동기 기능 테스트"""
    logger.info("🔍 비동기 기능 테스트 시작")

    try:
        from DuRiCore.learning_system.monitoring import AdvancedLearningMonitoringSystem

        # AdvancedLearningMonitoringSystem 인스턴스 생성
        monitoring_system = AdvancedLearningMonitoringSystem()

        # 테스트 데이터 생성
        test_session_data = {
            "session_id": "test_session_001",
            "performance_scores": [0.7, 0.8, 0.75, 0.6, 0.65],
            "engagement_scores": [0.8, 0.7, 0.6, 0.5, 0.4],
            "efficiency_scores": [0.6, 0.7, 0.65, 0.5, 0.45],
            "quality_scores": [0.8, 0.75, 0.7, 0.65, 0.6],
            "timestamps": [
                datetime.now() - timedelta(hours=4),
                datetime.now() - timedelta(hours=3),
                datetime.now() - timedelta(hours=2),
                datetime.now() - timedelta(hours=1),
                datetime.now(),
            ],
            "learning_actions": ["read", "practice", "review", "test", "reflect"],
            "progress": 0.6,
            "start_time": datetime.now() - timedelta(hours=4),
        }

        # 학습 패턴 분석 테스트
        patterns = await monitoring_system.analyze_learning_patterns(test_session_data)
        logger.info(f"✅ 학습 패턴 분석 성공: {len(patterns)}개 패턴 발견")

        # 학습 이슈 감지 테스트
        issues = await monitoring_system.detect_learning_issues(test_session_data)
        logger.info(f"✅ 학습 이슈 감지 성공: {len(issues)}개 이슈 발견")

        # 학습 결과 예측 테스트
        predictions = await monitoring_system.predict_learning_outcomes(
            test_session_data
        )
        logger.info(f"✅ 학습 결과 예측 성공: {len(predictions)}개 예측 생성")

        # 최적화 추천 생성 테스트
        recommendations = await monitoring_system.generate_optimization_recommendations(
            test_session_data
        )
        logger.info(f"✅ 최적화 추천 생성 성공: {len(recommendations)}개 추천 생성")

        # 모니터링 리포트 생성 테스트
        report = await monitoring_system.get_monitoring_report("test_session_001")
        logger.info(
            f"✅ 모니터링 리포트 생성 성공: {report.get('monitoring_level', 'unknown')}"
        )

        logger.info("✅ 비동기 기능 테스트 완료")
        return True

    except Exception as e:
        logger.error(f"❌ 비동기 기능 테스트 실패: {e}")
        return False


def test_package_import():
    """패키지 전체 import 테스트"""
    logger.info("🔍 패키지 전체 import 테스트 시작")

    try:
        # 전체 패키지 import 테스트
        from DuRiCore.learning_system import (
            AdaptiveLearningStrategy,
            AdvancedLearningMonitoringSystem,
            CognitiveMetaLearningStrategy,
            KnowledgeEvolutionSystem,
            KnowledgeIntegrationSystem,
            LearningEngine,
            LearningIntegrationSystem,
            LearningMonitoringSystem,
            LearningOptimizationSystem,
            MetaCognitionStrategy,
            SelfDirectedLearningStrategy,
        )

        logger.info("✅ 패키지 전체 import 성공")
        return True

    except Exception as e:
        logger.error(f"❌ 패키지 전체 import 실패: {e}")
        return False


def main():
    """메인 테스트 함수"""
    logger.info("🚀 DuRiCore Phase 2-3 학습 시스템 모듈 테스트 시작")

    test_results = []

    # 1. Core 모듈 테스트
    test_results.append(("Core 모듈", test_core_modules()))

    # 2. Strategies 모듈 테스트
    test_results.append(("Strategies 모듈", test_strategies_modules()))

    # 3. Integration 모듈 테스트
    test_results.append(("Integration 모듈", test_integration_modules()))

    # 4. Monitoring 모듈 테스트
    test_results.append(("Monitoring 모듈", test_monitoring_modules()))

    # 5. 패키지 전체 import 테스트
    test_results.append(("패키지 전체 import", test_package_import()))

    # 6. 비동기 기능 테스트
    async_result = asyncio.run(test_async_functionality())
    test_results.append(("비동기 기능", async_result))

    # 결과 요약
    logger.info("\n" + "=" * 50)
    logger.info("📊 테스트 결과 요약")
    logger.info("=" * 50)

    passed_tests = 0
    total_tests = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed_tests += 1

    logger.info(f"\n총 테스트: {total_tests}개")
    logger.info(f"통과: {passed_tests}개")
    logger.info(f"실패: {total_tests - passed_tests}개")
    logger.info(f"성공률: {(passed_tests/total_tests)*100:.1f}%")

    if passed_tests == total_tests:
        logger.info("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        return 0
    else:
        logger.error("⚠️ 일부 테스트가 실패했습니다.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
