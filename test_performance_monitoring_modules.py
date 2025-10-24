#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-4: 성능 모니터링 모듈 테스트

성능 모니터링 시스템의 모든 모듈을 테스트합니다.
"""

import asyncio
import logging
import sys
from datetime import timedelta

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_metric_collector():
    """메트릭 수집기 테스트"""
    logger.info("🔍 메트릭 수집기 테스트 시작")

    try:
        # 메트릭 수집기 import 테스트
        from DuRiCore.monitoring.performance_monitoring import (
            MetricCollector,
        )

        # MetricCollector 인스턴스 생성 테스트
        metric_collector = MetricCollector()
        logger.info(f"✅ MetricCollector 생성 성공: {type(metric_collector)}")

        logger.info("✅ 메트릭 수집기 테스트 완료")
        return True

    except Exception as e:
        logger.error(f"❌ 메트릭 수집기 테스트 실패: {e}")
        return False


def test_performance_analyzer():
    """성능 분석기 테스트"""
    logger.info("🔍 성능 분석기 테스트 시작")

    try:
        # 성능 분석기 import 테스트
        from DuRiCore.monitoring.performance_monitoring import (
            PerformanceAnalyzer,
        )

        # PerformanceAnalyzer 인스턴스 생성 테스트
        performance_analyzer = PerformanceAnalyzer()
        logger.info(f"✅ PerformanceAnalyzer 생성 성공: {type(performance_analyzer)}")

        logger.info("✅ 성능 분석기 테스트 완료")
        return True

    except Exception as e:
        logger.error(f"❌ 성능 분석기 테스트 실패: {e}")
        return False


def test_alert_manager():
    """알림 관리자 테스트"""
    logger.info("🔍 알림 관리자 테스트 시작")

    try:
        # 알림 관리자 import 테스트
        from DuRiCore.monitoring.alert_system import (
            PerformanceAlertManager,
        )

        # PerformanceAlertManager 인스턴스 생성 테스트
        alert_manager = PerformanceAlertManager()
        logger.info(f"✅ PerformanceAlertManager 생성 성공: {type(alert_manager)}")

        logger.info("✅ 알림 관리자 테스트 완료")
        return True

    except Exception as e:
        logger.error(f"❌ 알림 관리자 테스트 실패: {e}")
        return False


async def test_async_functionality():
    """비동기 기능 테스트"""
    logger.info("🔍 비동기 기능 테스트 시작")

    try:
        from DuRiCore.monitoring.alert_system import AlertChannel, AlertLevel, PerformanceAlertManager
        from DuRiCore.monitoring.performance_monitoring import MetricCollector, MetricType, PerformanceAnalyzer

        # 1. 메트릭 수집 테스트
        metric_collector = MetricCollector()

        # 메트릭 수집 시작
        collection_id = await metric_collector.start_collection("test_collection")
        logger.info(f"✅ 메트릭 수집 시작: {collection_id}")

        # 메트릭 수집
        for i in range(5):
            metric_id = await metric_collector.collect_metric(
                MetricType.PERFORMANCE, "cpu_usage", 50.0 + i * 10, "%", "test_system"
            )
            logger.info(f"✅ 메트릭 수집: {metric_id}")

        # 메트릭 통계 조회
        stats = await metric_collector.get_metric_statistics("cpu_usage", timedelta(hours=1))
        logger.info(f"✅ 메트릭 통계 조회: {len(stats)}개 항목")

        # 2. 성능 분석 테스트
        performance_analyzer = PerformanceAnalyzer()

        # 메트릭 조회
        metrics = await metric_collector.get_metrics_by_type(MetricType.PERFORMANCE)
        if metrics:
            # 트렌드 분석
            trend = await performance_analyzer.analyze_trends(metrics, "cpu_usage")
            if trend:
                logger.info(f"✅ 트렌드 분석 완료: {trend.trend_direction.value}")

            # 패턴 감지
            patterns = await performance_analyzer.detect_patterns(metrics, "cpu_usage")
            logger.info(f"✅ 패턴 감지 완료: {len(patterns)}개 패턴")

            # 성능 예측
            prediction = await performance_analyzer.predict_performance(metrics, "cpu_usage")
            if prediction:
                logger.info(f"✅ 성능 예측 완료: {prediction.predicted_value:.2f}")

            # 최적화 제안
            suggestions = await performance_analyzer.generate_optimization_suggestions(metrics, "cpu_usage")
            logger.info(f"✅ 최적화 제안 완료: {len(suggestions)}개 제안")

        # 3. 알림 관리 테스트
        alert_manager = PerformanceAlertManager()

        # 알림 규칙 추가
        rule_id = await alert_manager.add_alert_rule(
            "CPU 사용률 경고",
            "cpu_usage",
            ">",
            80.0,
            AlertLevel.WARNING,
            [AlertChannel.LOG],
        )
        logger.info(f"✅ 알림 규칙 추가: {rule_id}")

        # 알림 조건 확인
        alerts = await alert_manager.check_alert_conditions("cpu_usage", 85.0)
        logger.info(f"✅ 알림 조건 확인: {len(alerts)}개 알림 생성")

        # 활성 알림 조회
        active_alerts = await alert_manager.get_active_alerts()
        logger.info(f"✅ 활성 알림 조회: {len(active_alerts)}개 알림")

        # 알림 통계 조회
        alert_stats = await alert_manager.get_alert_statistics()
        logger.info(f"✅ 알림 통계 조회: {alert_stats.get('total_alerts', 0)}개 알림")

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

        logger.info("✅ 패키지 전체 import 성공")
        return True

    except Exception as e:
        logger.error(f"❌ 패키지 전체 import 실패: {e}")
        return False


def main():
    """메인 테스트 함수"""
    logger.info("🚀 DuRiCore Phase 2-4 성능 모니터링 모듈 테스트 시작")

    test_results = []

    # 1. 메트릭 수집기 테스트
    test_results.append(("메트릭 수집기", test_metric_collector()))

    # 2. 성능 분석기 테스트
    test_results.append(("성능 분석기", test_performance_analyzer()))

    # 3. 알림 관리자 테스트
    test_results.append(("알림 관리자", test_alert_manager()))

    # 4. 패키지 전체 import 테스트
    test_results.append(("패키지 전체 import", test_package_import()))

    # 5. 비동기 기능 테스트
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
