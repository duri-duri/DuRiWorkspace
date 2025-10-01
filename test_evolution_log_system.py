#!/usr/bin/env python3
"""
진화 로그 정제 시스템 테스트
실제 대화 데이터 수집 및 분석 기능 검증
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Dict

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 모듈 import
from duri_modules.data.conversation_logger import conversation_logger
from duri_modules.unified.unified_conversation_processor import unified_processor


async def test_conversation_logging():
    """대화 로그 수집 테스트"""
    try:
        logger.info("🧠 대화 로그 수집 시스템 테스트 시작")

        # 1. 대화 세션 시작
        conversation_id = conversation_logger.start_conversation(
            "test_conversation_001"
        )
        logger.info(f"✅ 대화 세션 시작: {conversation_id}")

        # 2. 여러 대화 교환 로그
        test_exchanges = [
            {
                "user_input": "파이썬에서 리스트를 정렬하는 방법을 알려줘",
                "duri_response": "파이썬에서 리스트를 정렬하는 방법은 sort() 메서드나 sorted() 함수를 사용합니다.",
                "response_time": 1.2,
                "success": True,
                "learning_patterns": ["explanation_seeking", "example_based_learning"],
                "improvement_areas": ["더 구체적인 예시 제공 필요"],
            },
            {
                "user_input": "왜 sorted()와 sort()의 차이점이 뭔가요?",
                "duri_response": "sort()는 원본 리스트를 변경하고, sorted()는 새로운 정렬된 리스트를 반환합니다.",
                "response_time": 0.8,
                "success": True,
                "learning_patterns": ["explanation_seeking", "concept_clarification"],
                "improvement_areas": [],
            },
            {
                "user_input": "예시 코드를 보여줘",
                "duri_response": "numbers = [3, 1, 4, 1, 5]; numbers.sort() # 원본 변경\nsorted_numbers = sorted(numbers) # 새 리스트 생성",
                "response_time": 1.5,
                "success": True,
                "learning_patterns": ["example_based_learning", "code_demonstration"],
                "improvement_areas": ["코드 주석 추가 필요"],
            },
        ]

        for i, exchange in enumerate(test_exchanges, 1):
            conversation_logger.log_exchange(
                user_input=exchange["user_input"],
                duri_response=exchange["duri_response"],
                response_time=exchange["response_time"],
                success=exchange["success"],
                learning_patterns=exchange["learning_patterns"],
                improvement_areas=exchange["improvement_areas"],
            )
            logger.info(f"✅ 대화 교환 {i} 로그 완료")

        # 3. 대화 세션 종료 및 진화 로그 생성
        evolution_log = conversation_logger.end_conversation()
        logger.info(f"✅ 대화 세션 종료: {evolution_log.conversation_id}")

        # 4. 통계 정보 확인
        statistics = conversation_logger.get_conversation_statistics()
        logger.info(f"📊 대화 통계: {statistics.get('total_conversations', 0)}개 대화")

        # 5. 학습 패턴 추출
        learning_patterns = conversation_logger.extract_learning_patterns()
        logger.info(f"📈 학습 패턴: {len(learning_patterns)}개 패턴 발견")

        # 6. 개선 제안 확인
        improvement_suggestions = conversation_logger.get_improvement_suggestions()
        logger.info(f"🔧 개선 제안: {len(improvement_suggestions)}개 제안")

        return {
            "status": "success",
            "conversation_id": conversation_id,
            "evolution_log": evolution_log,
            "statistics": statistics,
            "learning_patterns": learning_patterns,
            "improvement_suggestions": improvement_suggestions,
        }

    except Exception as e:
        logger.error(f"❌ 대화 로그 수집 테스트 오류: {e}")
        return {"status": "error", "error": str(e)}


async def test_unified_processor_integration():
    """통합 처리 시스템과의 연동 테스트"""
    try:
        logger.info("🔄 통합 처리 시스템 연동 테스트 시작")

        # 1. 대화 처리 (로그 수집 포함)
        test_conversations = [
            {
                "user_input": "머신러닝 모델을 평가하는 방법은?",
                "duri_response": "머신러닝 모델 평가는 정확도, 정밀도, 재현율, F1-score 등을 사용합니다.",
            },
            {
                "user_input": "어떤 상황에서 어떤 지표를 사용해야 하나요?",
                "duri_response": "불균형 데이터에서는 F1-score, 이진 분류에서는 ROC-AUC를 주로 사용합니다.",
            },
        ]

        results = []
        for i, conv in enumerate(test_conversations, 1):
            result = await unified_processor.process_conversation(
                user_input=conv["user_input"], duri_response=conv["duri_response"]
            )
            results.append(result)
            logger.info(f"✅ 대화 처리 {i} 완료: 점수 {result.integrated_score:.3f}")

        # 2. 세션 종료 및 진화 로그 생성
        session_result = unified_processor.end_conversation_session()
        logger.info(f"✅ 세션 종료: {session_result.get('status', 'unknown')}")

        # 3. 진화 인사이트 확인
        evolution_insights = unified_processor.get_evolution_insights()
        logger.info(f"🧠 진화 인사이트: {evolution_insights.get('status', 'unknown')}")

        return {
            "status": "success",
            "processed_conversations": len(results),
            "session_result": session_result,
            "evolution_insights": evolution_insights,
        }

    except Exception as e:
        logger.error(f"❌ 통합 처리 연동 테스트 오류: {e}")
        return {"status": "error", "error": str(e)}


def print_evolution_log_summary(evolution_log):
    """진화 로그 요약 출력"""
    print("\n" + "=" * 80)
    print("📊 진화 로그 요약")
    print("=" * 80)
    print(f"대화 ID: {evolution_log.conversation_id}")
    print(f"시작 시간: {evolution_log.start_time}")
    print(f"종료 시간: {evolution_log.end_time}")
    print(f"총 교환 수: {evolution_log.total_exchanges}")
    print(f"평균 응답 시간: {evolution_log.average_response_time:.3f}초")
    print(f"학습 효율성: {evolution_log.learning_efficiency:.3f}")
    print(f"문제 해결 점수: {evolution_log.problem_solving_score:.3f}")
    print(f"자율성 레벨: {evolution_log.autonomy_level:.3f}")
    print(f"진화 패턴: {', '.join(evolution_log.evolution_patterns)}")
    print(f"핵심 인사이트: {', '.join(evolution_log.key_insights)}")
    print("=" * 80)


def print_statistics_summary(statistics):
    """통계 요약 출력"""
    print("\n" + "=" * 80)
    print("📈 대화 통계 요약")
    print("=" * 80)
    print(f"총 대화 수: {statistics.get('total_conversations', 0)}")
    print(f"총 교환 수: {statistics.get('total_exchanges', 0)}")
    print(f"평균 응답 시간: {statistics.get('average_response_time', 0.0):.3f}초")
    print(f"평균 학습 효율성: {statistics.get('average_learning_efficiency', 0.0):.3f}")
    print(f"평균 문제 해결 점수: {statistics.get('average_problem_solving', 0.0):.3f}")
    print(f"평균 자율성: {statistics.get('average_autonomy', 0.0):.3f}")

    # 진화 패턴
    evolution_patterns = statistics.get("evolution_patterns", {})
    if evolution_patterns:
        print(f"\n진화 패턴:")
        for pattern, count in evolution_patterns.items():
            print(f"  • {pattern}: {count}회")

    # 최근 트렌드
    recent_trends = statistics.get("recent_trends", {})
    if recent_trends:
        print(f"\n최근 트렌드:")
        for trend, status in recent_trends.items():
            print(f"  • {trend}: {status}")

    print("=" * 80)


async def main():
    """메인 테스트 함수"""
    try:
        logger.info("🚀 진화 로그 정제 시스템 테스트 시작")

        # 1. 대화 로그 수집 테스트
        print("\n1️⃣ 대화 로그 수집 테스트")
        log_test_result = await test_conversation_logging()

        if log_test_result.get("status") == "success":
            print("✅ 대화 로그 수집 테스트 성공")

            # 진화 로그 요약 출력
            evolution_log = log_test_result.get("evolution_log")
            if evolution_log:
                print_evolution_log_summary(evolution_log)

            # 통계 요약 출력
            statistics = log_test_result.get("statistics")
            if statistics:
                print_statistics_summary(statistics)
        else:
            print(
                f"❌ 대화 로그 수집 테스트 실패: {log_test_result.get('error', '알 수 없는 오류')}"
            )

        # 2. 통합 처리 시스템 연동 테스트
        print("\n2️⃣ 통합 처리 시스템 연동 테스트")
        integration_test_result = await test_unified_processor_integration()

        if integration_test_result.get("status") == "success":
            print("✅ 통합 처리 시스템 연동 테스트 성공")

            # 세션 결과 출력
            session_result = integration_test_result.get("session_result", {})
            if session_result.get("status") == "success":
                print(
                    f"✅ 세션 종료 성공: {session_result.get('evolution_log', {}).get('conversation_id', 'N/A')}"
                )

            # 진화 인사이트 출력
            evolution_insights = integration_test_result.get("evolution_insights", {})
            if evolution_insights.get("status") == "success":
                insights_data = evolution_insights.get("evolution_insights", {})
                print(
                    f"✅ 진화 인사이트 생성: {insights_data.get('evolution_summary', {}).get('total_conversations', 0)}개 대화 분석"
                )
        else:
            print(
                f"❌ 통합 처리 시스템 연동 테스트 실패: {integration_test_result.get('error', '알 수 없는 오류')}"
            )

        # 전체 테스트 결과 요약
        print("\n" + "=" * 80)
        print("🎯 전체 테스트 결과 요약")
        print("=" * 80)

        tests = [
            ("대화 로그 수집", log_test_result),
            ("통합 처리 연동", integration_test_result),
        ]

        success_count = 0
        for test_name, test_result in tests:
            status = test_result.get("status", "error")
            if status == "success":
                print(f"✅ {test_name}: 성공")
                success_count += 1
            else:
                print(f"❌ {test_name}: 실패")

        print(
            f"\n📊 성공률: {success_count}/{len(tests)} ({success_count/len(tests)*100:.1f}%)"
        )

        if success_count == len(tests):
            print("🎉 모든 테스트가 성공했습니다!")
            print("✅ 진화 로그 정제 시스템이 정상적으로 작동합니다.")
        elif success_count > 0:
            print("⚠️ 일부 테스트가 성공했습니다.")
        else:
            print("❌ 모든 테스트가 실패했습니다.")

        print("=" * 80)

        logger.info("🏁 진화 로그 정제 시스템 테스트 완료")

    except Exception as e:
        logger.error(f"❌ 메인 테스트 오류: {e}")


if __name__ == "__main__":
    asyncio.run(main())
