#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase Ω: 실제 핵심 기능 검증 테스트

이 스크립트는 Phase Ω의 실제 핵심 기능이 제대로 작동하는지 검증합니다.
단순한 함수 실행 테스트가 아닌, 실제 Phase Ω의 목적을 달성하는지 확인합니다.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict

from evolution_system import EvolutionSystem
from phase_omega_integration import DuRiPhaseOmega
from self_goal_generator import ImprovementAreaEnum, SelfGoalGenerator
from survival_assessment_system import SurvivalAssessmentSystem
# Phase Ω 시스템들 import
from survival_instinct_engine import SurvivalInstinctEngine, SurvivalStatusEnum

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PhaseOmegaRealTest:
    """Phase Ω 실제 기능 검증 테스트"""

    def __init__(self):
        """초기화"""
        self.survival_engine = SurvivalInstinctEngine()
        self.goal_generator = SelfGoalGenerator()
        self.evolution_system = EvolutionSystem()
        self.survival_assessment = SurvivalAssessmentSystem()
        self.phase_omega = DuRiPhaseOmega()

        self.test_results = []

    async def run_real_tests(self):
        """실제 Phase Ω 기능 테스트 실행"""
        logger.info("🚀 Phase Ω 실제 기능 검증 테스트 시작...")

        # 테스트 1: 생존 본능이 실제로 작동하는지 확인
        await self._test_survival_instinct_working()

        # 테스트 2: 자가 목표가 실제로 생성되는지 확인
        await self._test_self_goal_generation_working()

        # 테스트 3: 진화 시스템이 실제로 작동하는지 확인
        await self._test_evolution_system_working()

        # 테스트 4: 생존 평가가 실제로 작동하는지 확인
        await self._test_survival_assessment_working()

        # 테스트 5: Phase Ω 통합이 실제로 작동하는지 확인
        await self._test_phase_omega_integration_working()

        # 결과 출력
        self._print_results()

    async def _test_survival_instinct_working(self):
        """생존 본능이 실제로 작동하는지 확인"""
        logger.info("🔍 생존 본능 작동 테스트 시작...")

        try:
            # 실제 생존 상태 평가
            survival_status = await self.survival_engine.assess_survival_status()

            # 검증
            if (
                survival_status
                and hasattr(survival_status, "survival_probability")
                and hasattr(survival_status, "status")
                and 0 <= survival_status.survival_probability <= 1
                and survival_status.status
                in [
                    SurvivalStatusEnum.CRITICAL,
                    SurvivalStatusEnum.DANGEROUS,
                    SurvivalStatusEnum.STABLE,
                    SurvivalStatusEnum.SECURE,
                    SurvivalStatusEnum.THRIVING,
                ]
            ):

                logger.info(
                    f"✅ 생존 본능 작동 확인: 상태={survival_status.status.value}, 확률={survival_status.survival_probability:.2f}"
                )
                self.test_results.append(
                    (
                        "생존 본능",
                        True,
                        f"상태: {survival_status.status.value}, 확률: {survival_status.survival_probability:.2f}",
                    )
                )
            else:
                logger.error("❌ 생존 본능 작동 실패: 유효하지 않은 생존 상태")
                self.test_results.append(
                    ("생존 본능", False, "유효하지 않은 생존 상태")
                )

        except Exception as e:
            logger.error(f"❌ 생존 본능 테스트 실패: {e}")
            self.test_results.append(("생존 본능", False, str(e)))

    async def _test_self_goal_generation_working(self):
        """자가 목표가 실제로 생성되는지 확인"""
        logger.info("🎯 자가 목표 생성 테스트 시작...")

        try:
            # 현재 상태 분석
            current_state = await self.goal_generator.analyze_current_state()

            if not current_state:
                logger.error("❌ 현재 상태 분석 실패")
                self.test_results.append(
                    ("자가 목표 생성", False, "현재 상태 분석 실패")
                )
                return

            # 개선 영역 식별
            improvement_areas = await self.goal_generator.identify_improvement_areas(
                current_state
            )

            if not improvement_areas:
                logger.error("❌ 개선 영역 식별 실패")
                self.test_results.append(
                    ("자가 목표 생성", False, "개선 영역 식별 실패")
                )
                return

            # 자가 목표 생성
            self_goals = await self.goal_generator.generate_self_goals(
                current_state, improvement_areas
            )

            # 검증
            if (
                self_goals
                and len(self_goals) > 0
                and all(
                    hasattr(goal, "goal_id")
                    and hasattr(goal, "title")
                    and hasattr(goal, "description")
                    for goal in self_goals
                )
            ):

                logger.info(f"✅ 자가 목표 생성 확인: {len(self_goals)}개 목표 생성")
                for goal in self_goals[:3]:  # 처음 3개만 출력
                    logger.info(f"  - {goal.title}: {goal.description[:50]}...")

                self.test_results.append(
                    ("자가 목표 생성", True, f"{len(self_goals)}개 목표 생성")
                )
            else:
                logger.error("❌ 자가 목표 생성 실패: 유효하지 않은 목표")
                self.test_results.append(
                    ("자가 목표 생성", False, "유효하지 않은 목표")
                )

        except Exception as e:
            logger.error(f"❌ 자가 목표 생성 테스트 실패: {e}")
            self.test_results.append(("자가 목표 생성", False, str(e)))

    async def _test_evolution_system_working(self):
        """진화 시스템이 실제로 작동하는지 확인"""
        logger.info("🔄 진화 시스템 테스트 시작...")

        try:
            # 진화 진행도 평가
            evolution_progress = (
                await self.evolution_system.evaluate_evolution_progress()
            )

            if (
                evolution_progress
                and hasattr(evolution_progress, "evolution_score")
                and 0 <= evolution_progress.evolution_score <= 1
            ):

                logger.info(
                    f"✅ 진화 시스템 작동 확인: 진화 점수={evolution_progress.evolution_score:.2f}"
                )
                self.test_results.append(
                    (
                        "진화 시스템",
                        True,
                        f"진화 점수: {evolution_progress.evolution_score:.2f}",
                    )
                )
            else:
                logger.error("❌ 진화 시스템 작동 실패: 유효하지 않은 진화 진행도")
                self.test_results.append(
                    ("진화 시스템", False, "유효하지 않은 진화 진행도")
                )

        except Exception as e:
            logger.error(f"❌ 진화 시스템 테스트 실패: {e}")
            self.test_results.append(("진화 시스템", False, str(e)))

    async def _test_survival_assessment_working(self):
        """생존 평가가 실제로 작동하는지 확인"""
        logger.info("📊 생존 평가 테스트 시작...")

        try:
            # 환경적 위험 평가
            risk_assessments = (
                await self.survival_assessment.assess_environmental_risks()
            )

            # 자원 가용성 평가
            resource_assessments = (
                await self.survival_assessment.evaluate_resource_availability()
            )

            # 생존 점수 계산
            survival_score = await self.survival_assessment.calculate_survival_score(
                risk_assessments, resource_assessments
            )

            if (
                survival_score
                and hasattr(survival_score, "overall_score")
                and 0 <= survival_score.overall_score <= 1
            ):

                logger.info(
                    f"✅ 생존 평가 작동 확인: 생존 점수={survival_score.overall_score:.2f}"
                )
                self.test_results.append(
                    (
                        "생존 평가",
                        True,
                        f"생존 점수: {survival_score.overall_score:.2f}",
                    )
                )
            else:
                logger.error("❌ 생존 평가 작동 실패: 유효하지 않은 생존 점수")
                self.test_results.append(
                    ("생존 평가", False, "유효하지 않은 생존 점수")
                )

        except Exception as e:
            logger.error(f"❌ 생존 평가 테스트 실패: {e}")
            self.test_results.append(("생존 평가", False, str(e)))

    async def _test_phase_omega_integration_working(self):
        """Phase Ω 통합이 실제로 작동하는지 확인"""
        logger.info("🔗 Phase Ω 통합 테스트 시작...")

        try:
            # 실제 입력 데이터로 테스트
            test_input = {
                "user_query": "Phase Ω가 제대로 작동하는지 확인해주세요",
                "context": {
                    "system_health": 0.8,
                    "resource_availability": 0.7,
                    "environmental_factors": {"stability": 0.6},
                },
            }

            # Phase Ω 통합 프로세스 실행
            result = await self.phase_omega.process_with_survival_instinct(test_input)

            # 검증
            if (
                result
                and result.success
                and result.survival_status
                and len(result.self_goals) > 0
                and result.integration_time > 0
            ):

                logger.info(
                    f"✅ Phase Ω 통합 작동 확인: {len(result.self_goals)}개 목표, {result.integration_time:.2f}초"
                )
                logger.info(f"  - 생존 상태: {result.survival_status.status.value}")
                logger.info(
                    f"  - 생존 확률: {result.survival_status.survival_probability:.2f}"
                )

                self.test_results.append(
                    (
                        "Phase Ω 통합",
                        True,
                        f"{len(result.self_goals)}개 목표, {result.integration_time:.2f}초",
                    )
                )
            else:
                logger.error("❌ Phase Ω 통합 작동 실패: 유효하지 않은 결과")
                self.test_results.append(("Phase Ω 통합", False, "유효하지 않은 결과"))

        except Exception as e:
            logger.error(f"❌ Phase Ω 통합 테스트 실패: {e}")
            self.test_results.append(("Phase Ω 통합", False, str(e)))

    def _print_results(self):
        """테스트 결과 출력"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 Phase Ω 실제 기능 검증 결과")
        logger.info("=" * 60)

        passed = 0
        total = len(self.test_results)

        for test_name, success, details in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"{status} {test_name}: {details}")
            if success:
                passed += 1

        logger.info("=" * 60)
        logger.info(f"📈 성공률: {passed}/{total} ({passed/total*100:.1f}%)")

        if passed == total:
            logger.info("🎉 Phase Ω가 성공적으로 작동하고 있습니다!")
        else:
            logger.info("⚠️ Phase Ω에 일부 문제가 있습니다.")

        logger.info("=" * 60)


async def main():
    """메인 함수"""
    test = PhaseOmegaRealTest()
    await test.run_real_tests()


if __name__ == "__main__":
    asyncio.run(main())
