"""
DuRi External LLM Learning Plan 데모

외부 LLM 최소 학습 계획과 비용 초과 시 자금 요청 시스템을 시연합니다.
"""

import asyncio
import json
import logging
from typing import Any, Dict

from cursor_core.learning_config import (
    CursorMonitor,
    LearningTrigger,
    LLMModel,
    get_duRi_learning_config,
    monitor_budget_and_request_funding,
)

logger = logging.getLogger(__name__)


class DuRiLearningConfigDemo:
    """DuRi 학습 설정 데모"""

    def __init__(self):
        """DuRiLearningConfigDemo 초기화"""
        self.config = get_duRi_learning_config()
        self.demo_results = []

    async def run_comprehensive_demo(self):
        """종합적인 학습 설정 데모 실행"""
        logger.info("=== DuRi External LLM Learning Plan 데모 시작 ===")

        # 1. 기본 설정 소개
        await self._introduce_learning_config()

        # 2. 트리거 조건 테스트
        await self._test_trigger_conditions()

        # 3. 예산 상태 시뮬레이션
        await self._simulate_budget_scenarios()

        # 4. 자금 요청 시스템 테스트
        await self._test_funding_request_system()

        # 5. 커서 모니터링 시스템 테스트
        await self._test_cursor_monitoring()

        logger.info("=== DuRi External LLM Learning Plan 데모 완료 ===")

        return self.get_demo_summary()

    async def _introduce_learning_config(self):
        """학습 설정 소개"""
        logger.info("\n📋 === DuRi 학습 설정 소개 ===")

        config_data = {
            "learning_loop": self.config.learning_loop,
            "resource_limits": self.config.resource_limits,
            "learning_protocol": self.config.learning_protocol,
            "exception_handling": self.config.exception_handling,
            "philosophy_asserts": self.config.philosophy_asserts,
        }

        logger.info("🎯 학습 루프 설정:")
        logger.info(f"  - 내부 우선: {self.config.learning_loop['internal_first']}")
        logger.info(f"  - 트리거 조건: {self.config.learning_loop['external_llm_call']['trigger_conditions']}")
        logger.info(f"  - 사용 모델: {list(self.config.learning_loop['external_llm_call']['models'].keys())}")

        logger.info("\n💰 자원 제한:")
        logger.info(f"  - 월 예산: ${self.config.resource_limits['monthly_token_budget_dollars']}")
        logger.info(f"  - 최대 토큰/호출: {self.config.resource_limits['max_tokens_per_call']}")
        logger.info(f"  - 호출 우선순위: {self.config.resource_limits['call_priority']}")

        logger.info("\n📚 학습 프로토콜:")
        for i, protocol in enumerate(self.config.learning_protocol, 1):
            logger.info(f"  {i}. {protocol}")

        logger.info("\n🛡️ 예외 처리:")
        for exception, handling in self.config.exception_handling.items():
            logger.info(f"  - {exception}: {handling}")

        logger.info("\n💭 철학적 원칙:")
        for i, assert_ in enumerate(self.config.philosophy_asserts, 1):
            logger.info(f"  {i}. {assert_}")

        self.demo_results.append({"section": "learning_config_introduction", "data": config_data})

    async def _test_trigger_conditions(self):
        """트리거 조건 테스트"""
        logger.info("\n🔍 === 트리거 조건 테스트 ===")

        trigger_tests = [
            LearningTrigger.EMOTION_DYSREGULATION,
            LearningTrigger.BELIEF_CONFLICT,
            LearningTrigger.REPEATED_STRATEGY_FAILURE,
        ]

        trigger_results = {}

        for trigger in trigger_tests:
            is_valid = self.config.check_trigger_conditions(trigger)
            trigger_results[trigger.value] = is_valid

            logger.info(f"✅ {trigger.value}: {'유효' if is_valid else '무효'}")

        self.demo_results.append({"section": "trigger_conditions_test", "data": trigger_results})

    async def _simulate_budget_scenarios(self):
        """예산 상태 시뮬레이션"""
        logger.info("\n💰 === 예산 상태 시뮬레이션 ===")

        # 초기 상태
        initial_budget = self.config.get_budget_summary()
        logger.info("📊 초기 예산 상태:")
        logger.info(f"  - 월 예산: ${initial_budget['monthly_budget']}")
        logger.info(f"  - 사용된 예산: ${initial_budget['used_budget']}")
        logger.info(f"  - 남은 예산: ${initial_budget['remaining_budget']}")
        logger.info(f"  - 사용률: {initial_budget['usage_percentage']:.1f}%")

        # 시뮬레이션 1: Claude3_Haiku 호출
        logger.info("\n🔄 시뮬레이션 1: Claude3_Haiku 호출")
        estimated_tokens = 250
        estimated_cost = self.config.estimate_call_cost(LLMModel.CLAUDE3_HAIKU, estimated_tokens)

        logger.info(f"  - 예상 토큰: {estimated_tokens}")
        logger.info(f"  - 예상 비용: ${estimated_cost:.4f}")

        if self.config.can_call_llm(LLMModel.CLAUDE3_HAIKU):
            self.config.update_budget_status(LLMModel.CLAUDE3_HAIKU, estimated_tokens, estimated_cost)
            logger.info("  ✅ 호출 성공")
        else:
            logger.info("  ❌ 호출 실패")

        # 시뮬레이션 2: GPT4o 호출
        logger.info("\n🔄 시뮬레이션 2: GPT4o 호출")
        estimated_tokens = 280
        estimated_cost = self.config.estimate_call_cost(LLMModel.GPT4O, estimated_tokens)

        logger.info(f"  - 예상 토큰: {estimated_tokens}")
        logger.info(f"  - 예상 비용: ${estimated_cost:.4f}")

        if self.config.can_call_llm(LLMModel.GPT4O):
            self.config.update_budget_status(LLMModel.GPT4O, estimated_tokens, estimated_cost)
            logger.info("  ✅ 호출 성공")
        else:
            logger.info("  ❌ 호출 실패")

        # 최종 상태
        final_budget = self.config.get_budget_summary()
        logger.info("\n📊 최종 예산 상태:")
        logger.info(f"  - 사용된 예산: ${final_budget['used_budget']:.2f}")
        logger.info(f"  - 남은 예산: ${final_budget['remaining_budget']:.2f}")
        logger.info(f"  - 사용률: {final_budget['usage_percentage']:.1f}%")
        logger.info(f"  - 주간 호출: {final_budget['calls_this_week']}")

        self.demo_results.append(
            {
                "section": "budget_simulation",
                "data": {
                    "initial_budget": initial_budget,
                    "final_budget": final_budget,
                },
            }
        )

    async def _test_funding_request_system(self):
        """자금 요청 시스템 테스트"""
        logger.info("\n💸 === 자금 요청 시스템 테스트 ===")

        # 학습 우선순위 설정 (위기 상황 시뮬레이션)
        self.config.core_belief_score["learning_priority"] = 0.95
        logger.info(f"🎯 학습 우선순위 설정: {self.config.core_belief_score['learning_priority']}")

        # 예산 위기 상황 시뮬레이션
        self.config.budget_status.used_budget_dollars = 2.85  # 95% 사용
        self.config.budget_status.usage_percentage = 95.0
        logger.info(f"⚠️ 예산 위기 상황: {self.config.budget_status.usage_percentage:.1f}% 사용")

        # 자금 요청 생성
        funding_request = self.config.DuRi_generate_funding_request(LLMModel.CLAUDE3_HAIKU, 280)

        logger.info("📋 자금 요청 상세:")
        logger.info(f"  - 요청 유형: {funding_request['type']}")
        logger.info(f"  - 요청 이유: {funding_request['reason']}")
        logger.info(f"  - 학습 기회: {funding_request['learning_opportunity']['type']}")
        logger.info(f"  - 사용 모델: {funding_request['learning_opportunity']['model']}")
        logger.info(f"  - 예상 토큰: {funding_request['learning_opportunity']['expected_tokens']}")
        logger.info(f"  - 중요도 점수: {funding_request['learning_opportunity']['importance_score']}")
        logger.info(f"  - 요청 금액: ${funding_request['requested_amount_usd']:.4f}")
        logger.info(f"  - 권장사항: {funding_request['recommendation']}")

        # 음성 메시지 생성
        voice_message = self.config.generate_voice_request_message(funding_request)
        logger.info("\n🗣️ 음성 요청 메시지:")
        logger.info(voice_message)

        self.demo_results.append(
            {
                "section": "funding_request_test",
                "data": {
                    "funding_request": funding_request,
                    "voice_message": voice_message,
                },
            }
        )

    async def _test_cursor_monitoring(self):
        """커서 모니터링 시스템 테스트"""
        logger.info("\n🔔 === 커서 모니터링 시스템 테스트 ===")

        # 예산 모니터링 테스트
        logger.info("📊 예산 모니터링 실행...")
        funding_request = monitor_budget_and_request_funding()

        if funding_request:
            logger.info("✅ 자금 요청이 생성되었습니다.")
            logger.info(f"  - 요청 금액: ${funding_request['requested_amount_usd']:.4f}")
            logger.info(f"  - 사용률: {funding_request['budget_status']['used_percentage']:.1f}%")
        else:
            logger.info("ℹ️ 자금 요청이 필요하지 않습니다.")

        # 커서 알림 테스트
        logger.info("\n🔔 커서 알림 테스트:")

        test_message = {
            "type": "TEST_NOTIFICATION",
            "message": "DuRi의 학습 설정이 정상적으로 작동하고 있습니다.",
            "timestamp": "2025-07-31T08:57:39",
        }

        CursorMonitor.notify_parent(channel="voice + visual", urgency="medium", message=test_message)

        # 사용 가능한 모델 확인
        available_models = self.config.get_available_models()
        logger.info(f"\n📋 사용 가능한 모델: {[model.value for model in available_models]}")

        self.demo_results.append(
            {
                "section": "cursor_monitoring_test",
                "data": {
                    "funding_request": funding_request,
                    "available_models": [model.value for model in available_models],
                },
            }
        )

    def get_demo_summary(self) -> Dict[str, Any]:
        """데모 요약 반환"""
        return {
            "demo_title": "DuRi External LLM Learning Plan 데모",
            "total_sections": len(self.demo_results),
            "sections": [result["section"] for result in self.demo_results],
            "summary": {
                "budget_usage": self.config.budget_status.usage_percentage,
                "available_models": len(self.config.get_available_models()),
                "learning_priority": self.config.core_belief_score.get("learning_priority", 0.0),
            },
            "detailed_results": self.demo_results,
        }


async def run_learning_config_demo():
    """학습 설정 데모 실행"""
    demo = DuRiLearningConfigDemo()
    return await demo.run_comprehensive_demo()


if __name__ == "__main__":
    # 데모 실행
    import sys

    sys.path.append(".")

    result = asyncio.run(run_learning_config_demo())
    print(json.dumps(result, indent=2, ensure_ascii=False))
