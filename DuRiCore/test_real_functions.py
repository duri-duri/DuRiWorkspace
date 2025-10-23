#!/usr/bin/env python3
"""
DuRiCore Phase 5.5 - 실제 기능 테스트
judgment → action → feedback 루프의 실제 기능 테스트
"""

import asyncio
import json
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from action_system import ActionSystem  # noqa: E402
from feedback_system import FeedbackSystem  # noqa: E402

# 시스템 import
from judgment_system import JudgmentSystem  # noqa: E402


async def test_judgment_system():
    """판단 시스템 테스트"""
    logger.info("🧠 판단 시스템 테스트 시작")

    try:
        judgment_system = JudgmentSystem()

        # 테스트 컨텍스트
        test_context = {
            "content": "시스템 성능 최적화가 필요합니다. 현재 CPU 사용률이 80%를 초과하고 있습니다.",
            "priority": "high",
            "urgency": "medium",
            "risk_level": 0.6,
        }

        # 판단 실행
        result = await judgment_system.judge(test_context)

        logger.info(f"판단 결과: {json.dumps(result, indent=2, ensure_ascii=False)}")

        return result

    except Exception as e:
        logger.error(f"판단 시스템 테스트 실패: {e}")
        return {"error": str(e)}


async def test_action_system():
    """행동 시스템 테스트"""
    logger.info("⚡ 행동 시스템 테스트 시작")

    try:
        action_system = ActionSystem()

        # 테스트 판단 결과
        test_decision = {
            "decision": "proceed",
            "reasoning": "시스템 최적화 진행",
            "confidence": 0.8,
            "alternatives": ["wait", "reconsider"],
            "risk_assessment": {
                "overall_risk": 0.3,
                "decision_risk": 0.2,
                "execution_risk": 0.1,
            },
            "ethical_score": 0.9,
        }

        # 행동 실행
        result = await action_system.act(test_decision)

        logger.info(f"행동 결과: {json.dumps(result, indent=2, ensure_ascii=False)}")

        return result

    except Exception as e:
        logger.error(f"행동 시스템 테스트 실패: {e}")
        return {"error": str(e)}


async def test_feedback_system():
    """피드백 시스템 테스트"""
    logger.info("🔄 피드백 시스템 테스트 시작")

    try:
        feedback_system = FeedbackSystem()

        # 테스트 행동 결과
        test_action_result = {
            "action": "시스템 최적화",
            "result": {"success": True, "performance_improvement": 0.15},
            "effectiveness_score": 0.8,
            "efficiency_score": 0.75,
            "success": True,
            "learning_points": ["성능 최적화 성공", "리소스 사용량 감소"],
            "next_actions": ["모니터링 강화", "추가 최적화"],
        }

        # 피드백 실행
        result = await feedback_system.feedback(test_action_result)

        logger.info(f"피드백 결과: {json.dumps(result, indent=2, ensure_ascii=False)}")

        return result

    except Exception as e:
        logger.error(f"피드백 시스템 테스트 실패: {e}")
        return {"error": str(e)}


async def test_complete_loop():
    """전체 루프 테스트"""
    logger.info("🔄 전체 루프 테스트 시작")

    try:
        # 시스템 초기화
        judgment_system = JudgmentSystem()
        action_system = ActionSystem()
        feedback_system = FeedbackSystem()

        # 1단계: 판단
        logger.info("1단계: 판단 실행")
        test_context = {
            "content": "사용자가 시스템 성능 개선을 요청했습니다. 현재 상태를 분석하고 최적화 방안을 제시해야 합니다.",
            "priority": "high",
            "urgency": "medium",
        }

        judgment_result = await judgment_system.judge(test_context)
        logger.info(f"판단 완료: {judgment_result.get('decision', 'unknown')}")

        # 2단계: 행동
        logger.info("2단계: 행동 실행")
        action_result = await action_system.act(judgment_result)
        logger.info(f"행동 완료: {action_result.get('action', 'unknown')}")

        # 3단계: 피드백
        logger.info("3단계: 피드백 실행")
        feedback_result = await feedback_system.feedback(action_result)
        logger.info(f"피드백 완료: {feedback_result.get('feedback', 'unknown')}")

        # 전체 결과
        complete_result = {
            "judgment": judgment_result,
            "action": action_result,
            "feedback": feedback_result,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info("✅ 전체 루프 테스트 완료")
        logger.info(f"전체 결과: {json.dumps(complete_result, indent=2, ensure_ascii=False)}")

        return complete_result

    except Exception as e:
        logger.error(f"전체 루프 테스트 실패: {e}")
        return {"error": str(e)}


async def main():
    """메인 테스트 함수"""
    logger.info("🚀 DuRiCore Phase 5.5 실제 기능 테스트 시작")

    try:
        # 개별 시스템 테스트
        logger.info("=" * 50)
        logger.info("개별 시스템 테스트")
        logger.info("=" * 50)

        judgment_result = await test_judgment_system()
        action_result = await test_action_system()
        feedback_result = await test_feedback_system()

        # 전체 루프 테스트
        logger.info("=" * 50)
        logger.info("전체 루프 테스트")
        logger.info("=" * 50)

        complete_result = await test_complete_loop()

        # 결과 요약
        logger.info("=" * 50)
        logger.info("테스트 결과 요약")
        logger.info("=" * 50)

        if "error" not in judgment_result:
            logger.info("✅ 판단 시스템: 정상 동작")
        else:
            logger.error(f"❌ 판단 시스템: {judgment_result['error']}")

        if "error" not in action_result:
            logger.info("✅ 행동 시스템: 정상 동작")
        else:
            logger.error(f"❌ 행동 시스템: {action_result['error']}")

        if "error" not in feedback_result:
            logger.info("✅ 피드백 시스템: 정상 동작")
        else:
            logger.error(f"❌ 피드백 시스템: {feedback_result['error']}")

        if "error" not in complete_result:
            logger.info("✅ 전체 루프: 정상 동작")
        else:
            logger.error(f"❌ 전체 루프: {complete_result['error']}")

        logger.info("🎉 모든 테스트 완료!")

    except Exception as e:
        logger.error(f"테스트 실행 중 오류 발생: {e}")


if __name__ == "__main__":
    asyncio.run(main())
