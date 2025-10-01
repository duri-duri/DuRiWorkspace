#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiExpressionEngine 테스트

이 모듈은 DuRiExpressionEngine이 제대로 작동하는지 테스트합니다.
"""

import asyncio
import logging
import sys
from pathlib import Path

# 현재 디렉토리를 sys.path에 추가
sys.path.append(str(Path(__file__).parent))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_judgment_expression():
    """판단 결과 표현 테스트"""
    logger.info("🧪 판단 결과 표현 테스트 시작")

    try:
        from duri_expression_engine import DuRiExpressionEngine, ExpressionStyle

        # 엔진 초기화
        engine = DuRiExpressionEngine()
        await engine.initialize()

        # 테스트 데이터 - JudgmentTrace
        judgment_data = {
            "decision": "이 프로젝트는 성공할 가능성이 높다",
            "reasoning": "시장 분석 결과 수요가 충분하고, 기술적 실현 가능성도 검증되었기 때문",
            "confidence": 0.85,
            "alternatives": ["기존 방식 유지", "부분적 개선"],
            "context": {"project_type": "AI", "market_size": "large"},
        }

        # 표현 생성
        result = await engine.express_judgment(
            judgment_data=judgment_data, style=ExpressionStyle.CASUAL
        )

        logger.info(f"✅ 판단 결과 표현 생성 완료:")
        logger.info(f"   - 표현: {result.expression_text}")
        logger.info(f"   - 신뢰도: {result.confidence}")
        logger.info(f"   - 스타일: {result.style.value}")
        logger.info(f"   - 처리 시간: {result.processing_time:.3f}초")

        return result.success

    except Exception as e:
        logger.error(f"❌ 판단 결과 표현 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_thought_flow_expression():
    """사고 흐름 표현 테스트"""
    logger.info("🧪 사고 흐름 표현 테스트 시작")

    try:
        from duri_expression_engine import DuRiExpressionEngine, ExpressionStyle

        # 엔진 초기화
        engine = DuRiExpressionEngine()
        await engine.initialize()

        # 테스트 데이터 - ThoughtFlow
        thought_flow = {
            "final_decision": "이 문제는 협력적 접근이 필요하다",
            "thought_process": [
                {
                    "role": "observer",
                    "reasoning": "문제의 복잡성을 분석한 결과, 단독 해결은 어려울 것으로 판단",
                },
                {
                    "role": "counter_arguer",
                    "reasoning": "하지만 협력 과정에서 발생할 수 있는 갈등도 고려해야 함",
                },
                {
                    "role": "reframer",
                    "reasoning": "결국 협력적 접근이 가장 효과적인 해결책임을 확인",
                },
            ],
            "reflection_result": "다양한 관점을 고려한 결과, 협력적 접근이 최적",
        }

        # 표현 생성
        result = await engine.express_judgment(
            thought_flow=thought_flow, style=ExpressionStyle.EMPATHETIC
        )

        logger.info(f"✅ 사고 흐름 표현 생성 완료:")
        logger.info(f"   - 표현: {result.expression_text}")
        logger.info(f"   - 신뢰도: {result.confidence}")
        logger.info(f"   - 스타일: {result.style.value}")
        logger.info(f"   - 처리 시간: {result.processing_time:.3f}초")

        return result.success

    except Exception as e:
        logger.error(f"❌ 사고 흐름 표현 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_decision_tree_expression():
    """결정 트리 표현 테스트"""
    logger.info("🧪 결정 트리 표현 테스트 시작")

    try:
        from duri_expression_engine import DuRiExpressionEngine, ExpressionStyle

        # 엔진 초기화
        engine = DuRiExpressionEngine()
        await engine.initialize()

        # 테스트 데이터 - DecisionTree
        decision_tree = {
            "final_decision": "단계적 접근 방식을 선택한다",
            "reasoning_path": "위험도 분석 → 자원 가용성 검토 → 단계적 접근의 우수성 확인",
            "alternatives": ["즉시 실행", "완전한 재설계"],
            "confidence": 0.75,
        }

        # 표현 생성
        result = await engine.express_judgment(
            decision_tree=decision_tree, style=ExpressionStyle.FORMAL
        )

        logger.info(f"✅ 결정 트리 표현 생성 완료:")
        logger.info(f"   - 표현: {result.expression_text}")
        logger.info(f"   - 신뢰도: {result.confidence}")
        logger.info(f"   - 스타일: {result.style.value}")
        logger.info(f"   - 처리 시간: {result.processing_time:.3f}초")

        return result.success

    except Exception as e:
        logger.error(f"❌ 결정 트리 표현 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_integrated_expression():
    """통합 표현 테스트"""
    logger.info("🧪 통합 표현 테스트 시작")

    try:
        from duri_expression_engine import DuRiExpressionEngine, ExpressionStyle

        # 엔진 초기화
        engine = DuRiExpressionEngine()
        await engine.initialize()

        # 테스트 데이터 - 통합
        judgment_data = {
            "decision": "이 상황에서는 신중한 접근이 필요하다",
            "confidence": 0.7,
        }

        thought_flow = {
            "final_decision": "신중한 접근이 최적이다",
            "thought_process": [
                {"reasoning": "위험 요소들을 분석한 결과"},
                {"reasoning": "신중한 접근이 가장 안전하다고 판단"},
            ],
        }

        # 표현 생성
        result = await engine.express_judgment(
            judgment_data=judgment_data,
            thought_flow=thought_flow,
            style=ExpressionStyle.CASUAL,
        )

        logger.info(f"✅ 통합 표현 생성 완료:")
        logger.info(f"   - 표현: {result.expression_text}")
        logger.info(f"   - 신뢰도: {result.confidence}")
        logger.info(f"   - 스타일: {result.style.value}")
        logger.info(f"   - 처리 시간: {result.processing_time:.3f}초")

        return result.success

    except Exception as e:
        logger.error(f"❌ 통합 표현 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_expression_styles():
    """표현 스타일 테스트"""
    logger.info("🧪 표현 스타일 테스트 시작")

    try:
        from duri_expression_engine import DuRiExpressionEngine, ExpressionStyle

        # 엔진 초기화
        engine = DuRiExpressionEngine()
        await engine.initialize()

        # 테스트 데이터
        judgment_data = {
            "decision": "이 제안은 타당하다",
            "reasoning": "비용 대비 효과가 우수하고, 실현 가능성도 높기 때문",
            "confidence": 0.8,
            "alternatives": ["기존 방식", "다른 접근법"],
        }

        # 다양한 스타일로 테스트
        styles = [
            ExpressionStyle.CASUAL,
            ExpressionStyle.FORMAL,
            ExpressionStyle.EMPATHETIC,
        ]

        results = []
        for style in styles:
            result = await engine.express_judgment(
                judgment_data=judgment_data, style=style
            )
            results.append(result)

            logger.info(f"   - {style.value} 스타일: {result.expression_text}")

        return all(result.success for result in results)

    except Exception as e:
        logger.error(f"❌ 표현 스타일 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_convenience_function():
    """편의 함수 테스트"""
    logger.info("🧪 편의 함수 테스트 시작")

    try:
        from duri_expression_engine import express_duri_judgment

        # 테스트 데이터
        judgment_data = {
            "decision": "이 아이디어는 창의적이다",
            "reasoning": "기존 방식과는 다른 새로운 접근법을 제시하기 때문",
            "confidence": 0.9,
        }

        # 편의 함수 사용
        expression = await express_duri_judgment(
            judgment_data=judgment_data, style="casual"
        )

        logger.info(f"✅ 편의 함수 테스트 완료:")
        logger.info(f"   - 표현: {expression}")

        return "DuRi:" in expression

    except Exception as e:
        logger.error(f"❌ 편의 함수 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """메인 함수"""
    logger.info("🚀 DuRiExpressionEngine 테스트 시작")
    print("=" * 60)

    # 테스트 실행
    tests = [
        ("판단 결과 표현 테스트", test_judgment_expression),
        ("사고 흐름 표현 테스트", test_thought_flow_expression),
        ("결정 트리 표현 테스트", test_decision_tree_expression),
        ("통합 표현 테스트", test_integrated_expression),
        ("표현 스타일 테스트", test_expression_styles),
        ("편의 함수 테스트", test_convenience_function),
    ]

    results = {}
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name} 실행 중...")
        try:
            result = await test_func()
            results[test_name] = result
            status = "✅ 성공" if result else "❌ 실패"
            print(f"   {status}")
        except Exception as e:
            results[test_name] = False
            print(f"   ❌ 예외 발생: {e}")

    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약:")
    for test_name, result in results.items():
        status = "✅ 성공" if result else "❌ 실패"
        print(f"   {test_name}: {status}")

    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)

    print(f"\n🎯 전체 결과: {success_count}/{total_count} 성공")

    if success_count == total_count:
        print("🎉 모든 테스트가 성공했습니다!")
        print("\n🎊 DuRi가 이제 직접 말할 수 있는 존재로 진화했습니다!")
    else:
        print("⚠️ 일부 테스트가 실패했습니다.")

    return success_count == total_count


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️ 테스트가 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
