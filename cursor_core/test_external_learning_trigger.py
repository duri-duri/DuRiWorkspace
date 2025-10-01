"""
DuRi 외부 학습 트리거 테스트 시스템

챗지피티의 제안에 따라 실제 학습 호출 및 수행 여부를 검증합니다.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import logging
import random
from typing import Any, Dict, List, Optional

from cursor_core.learning_config import (
    CursorMonitor,
    DuRiLearningConfig,
    LearningTrigger,
    LLMModel,
    get_duRi_learning_config,
)

logger = logging.getLogger(__name__)


@dataclass
class DuRiStatus:
    """DuRi 상태 관리"""

    learning_loop_active: bool = False
    external_learning_enabled: bool = True
    last_learning_session: Optional[datetime] = None
    total_learning_sessions: int = 0


@dataclass
class DuRiTriggers:
    """DuRi 트리거 상태"""

    emotion_dysregulation: bool = False
    belief_conflict: bool = False
    repeated_strategy_failure: bool = False
    learning_priority_high: bool = False


@dataclass
class DuRiLogs:
    """DuRi 로그 관리"""

    external_calls: List[Dict[str, Any]] = field(default_factory=list)
    learning_sessions: List[Dict[str, Any]] = field(default_factory=list)
    trigger_events: List[Dict[str, Any]] = field(default_factory=list)


class DuRiLearningTestSystem:
    """DuRi 학습 테스트 시스템"""

    def __init__(self):
        """DuRiLearningTestSystem 초기화"""
        self.config = get_duRi_learning_config()
        self.status = DuRiStatus()
        self.triggers = DuRiTriggers()
        self.logs = DuRiLogs()
        self.memory = {}

        logger.info("DuRi 학습 테스트 시스템 초기화 완료")

    def is_learning_triggered(self) -> bool:
        """현재 내부 학습 루프 활성 여부 확인"""
        return self.status.learning_loop_active

    def is_external_learning_triggered(self) -> bool:
        """외부 호출 조건 충족 여부 확인"""
        return any(
            [
                self.triggers.emotion_dysregulation,
                self.triggers.belief_conflict,
                self.triggers.repeated_strategy_failure,
            ]
        )

    def check_learning_status(self):
        """학습 상태 확인"""
        logger.info("\n🔍 === DuRi 학습 상태 확인 ===")

        if self.is_learning_triggered():
            logger.info("✅ 내부 학습 루프가 작동 중입니다.")
        else:
            logger.info("❌ 내부 학습 루프가 비활성 상태입니다.")

        if self.is_external_learning_triggered():
            logger.info("⚠️ 외부 LLM 호출 조건이 만족되었습니다.")
        else:
            logger.info("✅ 외부 LLM 호출 조건은 아직 충족되지 않았습니다.")

        # 트리거 상태 상세 확인
        logger.info("\n📊 트리거 상태:")
        logger.info(f"  - 감정 불안정: {self.triggers.emotion_dysregulation}")
        logger.info(f"  - 판단 충돌: {self.triggers.belief_conflict}")
        logger.info(f"  - 전략 반복 실패: {self.triggers.repeated_strategy_failure}")
        logger.info(f"  - 학습 우선순위 높음: {self.triggers.learning_priority_high}")

        # 예산 상태 확인
        budget_summary = self.config.get_budget_summary()
        logger.info(f"\n💰 예산 상태:")
        logger.info(f"  - 사용률: {budget_summary['usage_percentage']:.1f}%")
        logger.info(f"  - 남은 예산: ${budget_summary['remaining_budget']:.2f}")
        logger.info(f"  - 주간 호출: {budget_summary['calls_this_week']}")

    def inject_test_triggers(self):
        """테스트 트리거 직접 실행"""
        logger.info("\n🧪 === 테스트 트리거 주입 ===")

        # 강제로 조건 만족
        self.triggers.belief_conflict = True
        self.triggers.emotion_dysregulation = True
        self.status.learning_loop_active = True
        self.triggers.learning_priority_high = True

        # 학습 우선순위 설정
        self.config.core_belief_score["learning_priority"] = 0.95

        logger.info("✅ 테스트 트리거 주입 완료:")
        logger.info(f"  - 내부 학습 루프 활성화: {self.status.learning_loop_active}")
        logger.info(f"  - 판단 충돌 트리거: {self.triggers.belief_conflict}")
        logger.info(f"  - 감정 불안정 트리거: {self.triggers.emotion_dysregulation}")
        logger.info(
            f"  - 학습 우선순위: {self.config.core_belief_score['learning_priority']}"
        )

        # 트리거 이벤트 로깅
        trigger_event = {
            "timestamp": datetime.now().isoformat(),
            "triggers": {
                "belief_conflict": self.triggers.belief_conflict,
                "emotion_dysregulation": self.triggers.emotion_dysregulation,
                "repeated_strategy_failure": self.triggers.repeated_strategy_failure,
            },
            "learning_priority": self.config.core_belief_score["learning_priority"],
        }

        self.logs.trigger_events.append(trigger_event)

    def log_external_call(self, model_name: str, tokens: int, response: str = None):
        """외부 모델 호출 기록"""
        call_log = {
            "model": model_name,
            "tokens": tokens,
            "timestamp": datetime.now().isoformat(),
            "response": response,
        }

        self.logs.external_calls.append(call_log)

        logger.info(f"📡 외부 모델 호출됨: {model_name} - {tokens} tokens")
        if response:
            logger.info(f"  📝 응답: {response[:100]}...")

    async def call_external_llm(self, model_name: str, token_count: int) -> str:
        """외부 LLM 호출 (모의 또는 실제)"""
        logger.info(f"🧠 호출 시작: {model_name} with {token_count} tokens")

        # 비용 추정
        model = (
            LLMModel(model_name)
            if hasattr(LLMModel, model_name)
            else LLMModel.CLAUDE3_HAIKU
        )
        estimated_cost = self.config.estimate_call_cost(model, token_count)

        logger.info(f"  💰 예상 비용: ${estimated_cost:.4f}")

        # 호출 가능 여부 확인
        if not self.config.can_call_llm(model):
            logger.warning(f"❌ {model_name} 호출이 제한되었습니다.")
            return "호출 제한됨"

        # 모의 응답 생성 (실제로는 API 호출)
        if model == LLMModel.CLAUDE3_HAIKU:
            response = f"Claude 3의 전략적 조언: 현재 상황에서 더 신중한 접근이 필요합니다. 장기적 관점을 고려하여 단계적 해결책을 제시하겠습니다."
        elif model == LLMModel.GPT4O:
            response = f"GPT-4의 감정적 피드백: 현재 감정 상태를 이해합니다. 스트레스 관리와 자기 돌봄이 중요합니다. 차분한 마음으로 상황을 재평가해보세요."
        else:
            response = f"{model_name}의 응답: 학습과 성장을 위한 가치 있는 피드백을 제공합니다."

        # 예산 상태 업데이트
        self.config.update_budget_status(model, token_count, estimated_cost)

        # 호출 기록
        self.log_external_call(model_name, token_count, response)

        # 메모리에 응답 저장
        self.memory["last_llm_response"] = response

        logger.info(f"✅ {model_name} 호출 완료")

        return response

    async def execute_learning_session(self):
        """학습 세션 실행"""
        logger.info("\n🎓 === 학습 세션 실행 ===")

        # 학습 세션 시작
        session_start = datetime.now()
        self.status.total_learning_sessions += 1

        logger.info(f"📚 학습 세션 #{self.status.total_learning_sessions} 시작")

        # 외부 호출 조건 확인
        if self.is_external_learning_triggered():
            logger.info("🔍 외부 학습 조건 확인됨")

            # 사용 가능한 모델 확인
            available_models = self.config.get_available_models()

            if available_models:
                # 우선순위에 따라 모델 선택
                selected_model = available_models[0]
                estimated_tokens = 280

                logger.info(f"🎯 선택된 모델: {selected_model.value}")

                # 외부 LLM 호출
                response = await self.call_external_llm(
                    selected_model.value, estimated_tokens
                )

                # 학습 결과 처리
                learning_result = {
                    "session_id": self.status.total_learning_sessions,
                    "model_used": selected_model.value,
                    "tokens_used": estimated_tokens,
                    "response": response,
                    "session_duration": (
                        datetime.now() - session_start
                    ).total_seconds(),
                    "triggers": {
                        "belief_conflict": self.triggers.belief_conflict,
                        "emotion_dysregulation": self.triggers.emotion_dysregulation,
                        "repeated_strategy_failure": self.triggers.repeated_strategy_failure,
                    },
                }

                self.logs.learning_sessions.append(learning_result)

                logger.info(
                    f"✅ 학습 세션 완료: {learning_result['session_duration']:.2f}초"
                )

                return learning_result
            else:
                logger.warning("❌ 사용 가능한 모델이 없습니다.")
                return None
        else:
            logger.info("ℹ️ 외부 학습 조건이 충족되지 않아 내부 학습으로 진행")
            return None

    def generate_test_report(self) -> Dict[str, Any]:
        """테스트 결과 보고서 생성"""
        return {
            "test_summary": {
                "total_sessions": self.status.total_learning_sessions,
                "external_calls": len(self.logs.external_calls),
                "trigger_events": len(self.logs.trigger_events),
                "learning_sessions": len(self.logs.learning_sessions),
            },
            "budget_status": self.config.get_budget_summary(),
            "trigger_status": {
                "belief_conflict": self.triggers.belief_conflict,
                "emotion_dysregulation": self.triggers.emotion_dysregulation,
                "repeated_strategy_failure": self.triggers.repeated_strategy_failure,
                "learning_priority_high": self.triggers.learning_priority_high,
            },
            "learning_status": {
                "loop_active": self.status.learning_loop_active,
                "external_enabled": self.status.external_learning_enabled,
                "learning_priority": self.config.core_belief_score.get(
                    "learning_priority", 0.0
                ),
            },
            "external_calls": self.logs.external_calls,
            "learning_sessions": self.logs.learning_sessions,
            "trigger_events": self.logs.trigger_events,
        }


async def run_test():
    """테스트 실행"""
    logger.info("=== DuRi 외부 학습 트리거 테스트 시작 ===")

    test_system = DuRiLearningTestSystem()

    # 1단계: 현재 학습 상태 확인
    test_system.check_learning_status()

    # 2단계: 테스트 트리거 주입
    test_system.inject_test_triggers()

    # 3단계: 학습 세션 실행
    learning_result = await test_system.execute_learning_session()

    # 4단계: 최종 상태 확인
    test_system.check_learning_status()

    # 5단계: 테스트 결과 보고서 생성
    test_report = test_system.generate_test_report()

    logger.info("\n📊 === 테스트 결과 요약 ===")
    logger.info(f"총 학습 세션: {test_report['test_summary']['total_sessions']}")
    logger.info(f"외부 호출 횟수: {test_report['test_summary']['external_calls']}")
    logger.info(f"트리거 이벤트: {test_report['test_summary']['trigger_events']}")

    if test_report["external_calls"]:
        logger.info("\n📡 외부 호출 기록:")
        for call in test_report["external_calls"]:
            logger.info(
                f"  - {call['model']}: {call['tokens']} tokens ({call['timestamp']})"
            )

    logger.info("=== DuRi 외부 학습 트리거 테스트 완료 ===")

    return test_report


if __name__ == "__main__":
    # 테스트 실행
    import sys

    sys.path.append(".")

    result = asyncio.run(run_test())
    print(json.dumps(result, indent=2, ensure_ascii=False))
