#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase 1-3 Week 3 Day 12 - 통합 언어 이해 및 생성 시스템 테스트

통합 언어 이해 및 생성 시스템의 기능을 검증하는 테스트 스크립트
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List

# 시스템 import
from integrated_language_understanding_generation_system import (
    IntegratedLanguageUnderstandingGenerationSystem, LanguageGenerationType,
    LanguageUnderstandingType)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class IntegratedLanguageSystemTester:
    """통합 언어 시스템 테스터"""

    def __init__(self):
        self.system = IntegratedLanguageUnderstandingGenerationSystem()
        self.test_results = []

    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """종합 테스트 실행"""
        logger.info("🚀 통합 언어 이해 및 생성 시스템 종합 테스트 시작")

        start_time = time.time()

        # 1. 기본 기능 테스트
        basic_test_results = await self._test_basic_functionality()

        # 2. 언어 이해 테스트
        understanding_test_results = await self._test_language_understanding()

        # 3. 언어 생성 테스트
        generation_test_results = await self._test_language_generation()

        # 4. 다국어 처리 테스트
        multilingual_test_results = await self._test_multilingual_processing()

        # 5. 성능 테스트
        performance_test_results = await self._test_performance()

        # 6. 통합 테스트
        integration_test_results = await self._test_integration()

        # 결과 통합
        total_time = time.time() - start_time

        comprehensive_results = {
            "test_summary": {
                "total_tests": len(self.test_results),
                "successful_tests": len([r for r in self.test_results if r.get("success", False)]),
                "failed_tests": len([r for r in self.test_results if not r.get("success", False)]),
                "total_time": total_time,
                "timestamp": datetime.now().isoformat(),
            },
            "test_categories": {
                "basic_functionality": basic_test_results,
                "language_understanding": understanding_test_results,
                "language_generation": generation_test_results,
                "multilingual_processing": multilingual_test_results,
                "performance": performance_test_results,
                "integration": integration_test_results,
            },
            "detailed_results": self.test_results,
        }

        # 결과 출력
        self._print_test_summary(comprehensive_results)

        return comprehensive_results

    async def _test_basic_functionality(self) -> Dict[str, Any]:
        """기본 기능 테스트"""
        logger.info("📋 기본 기능 테스트 시작")

        test_cases = [
            {
                "name": "시스템 초기화 테스트",
                "text": "안녕하세요",
                "context": {"topic": "인사"},
                "expected_type": LanguageGenerationType.CONVERSATIONAL_RESPONSE,
            },
            {
                "name": "빈 텍스트 처리 테스트",
                "text": "",
                "context": {},
                "expected_type": LanguageGenerationType.CONVERSATIONAL_RESPONSE,
            },
        ]

        results = []
        for test_case in test_cases:
            try:
                result = await self.system.process_language(
                    text=test_case["text"],
                    context=test_case["context"],
                    generation_type=test_case["expected_type"],
                )

                success = (
                    result.understanding_result is not None
                    and result.generation_result is not None
                    and result.integration_score > 0
                )

                test_result = {
                    "name": test_case["name"],
                    "success": success,
                    "understanding_score": result.understanding_result.confidence_score,
                    "generation_score": result.generation_result.confidence_score,
                    "integration_score": result.integration_score,
                }

                results.append(test_result)
                self.test_results.append(test_result)

                logger.info(f"✅ {test_case['name']}: {'성공' if success else '실패'}")

            except Exception as e:
                logger.error(f"❌ {test_case['name']} 실패: {e}")
                results.append({"name": test_case["name"], "success": False, "error": str(e)})
                self.test_results.append(results[-1])

        return {
            "total_tests": len(test_cases),
            "successful_tests": len([r for r in results if r.get("success", False)]),
            "results": results,
        }

    async def _test_language_understanding(self) -> Dict[str, Any]:
        """언어 이해 테스트"""
        logger.info("🧠 언어 이해 테스트 시작")

        test_cases = [
            {
                "name": "감정 분석 테스트",
                "text": "오늘 정말 기뻐요! 새로운 것을 배웠어요.",
                "context": {"topic": "학습"},
                "expected_emotion": "기쁨",
            },
            {
                "name": "의도 인식 테스트",
                "text": "어려운 문제를 해결하는 방법을 알려주세요.",
                "context": {"topic": "문제해결"},
                "expected_intent": "질문",
            },
            {
                "name": "맥락 이해 테스트",
                "text": "가족과 함께하는 시간이 가장 소중해요.",
                "context": {"topic": "가족"},
                "expected_context": "가족",
            },
        ]

        results = []
        for test_case in test_cases:
            try:
                result = await self.system.process_language(
                    text=test_case["text"], context=test_case["context"]
                )

                # 예상 결과와 실제 결과 비교
                understanding_result = result.understanding_result

                success = True
                if "expected_emotion" in test_case:
                    success = (
                        success
                        and test_case["expected_emotion"] in understanding_result.emotional_tone
                    )
                if "expected_intent" in test_case:
                    success = (
                        success and test_case["expected_intent"] in understanding_result.intent
                    )
                if "expected_context" in test_case:
                    success = (
                        success
                        and test_case["expected_context"] in understanding_result.context_meaning
                    )

                test_result = {
                    "name": test_case["name"],
                    "success": success,
                    "understanding_score": understanding_result.confidence_score,
                    "detected_emotion": understanding_result.emotional_tone,
                    "detected_intent": understanding_result.intent,
                    "detected_context": understanding_result.context_meaning,
                }

                results.append(test_result)
                self.test_results.append(test_result)

                logger.info(f"✅ {test_case['name']}: {'성공' if success else '실패'}")

            except Exception as e:
                logger.error(f"❌ {test_case['name']} 실패: {e}")
                results.append({"name": test_case["name"], "success": False, "error": str(e)})
                self.test_results.append(results[-1])

        return {
            "total_tests": len(test_cases),
            "successful_tests": len([r for r in results if r.get("success", False)]),
            "results": results,
        }

    async def _test_language_generation(self) -> Dict[str, Any]:
        """언어 생성 테스트"""
        logger.info("✍️ 언어 생성 테스트 시작")

        test_cases = [
            {
                "name": "대화 응답 생성 테스트",
                "text": "안녕하세요",
                "context": {"topic": "인사"},
                "generation_type": LanguageGenerationType.CONVERSATIONAL_RESPONSE,
            },
            {
                "name": "감정적 표현 생성 테스트",
                "text": "정말 슬퍼요",
                "context": {"topic": "감정", "emotion": "슬픔"},
                "generation_type": LanguageGenerationType.EMOTIONAL_EXPRESSION,
            },
            {
                "name": "맥락 기반 생성 테스트",
                "text": "학습에 대해 이야기해요",
                "context": {"topic": "학습"},
                "generation_type": LanguageGenerationType.CONTEXTUAL_GENERATION,
            },
            {
                "name": "창의적 글쓰기 테스트",
                "text": "창의적인 이야기를 해주세요",
                "context": {"topic": "창의성"},
                "generation_type": LanguageGenerationType.CREATIVE_WRITING,
            },
        ]

        results = []
        for test_case in test_cases:
            try:
                result = await self.system.process_language(
                    text=test_case["text"],
                    context=test_case["context"],
                    generation_type=test_case["generation_type"],
                )

                generation_result = result.generation_result

                success = (
                    generation_result.generated_text is not None
                    and len(generation_result.generated_text.strip()) > 0
                    and generation_result.confidence_score > 0.3
                )

                test_result = {
                    "name": test_case["name"],
                    "success": success,
                    "generation_score": generation_result.confidence_score,
                    "generated_text": generation_result.generated_text,
                    "emotional_expression": generation_result.emotional_expression,
                    "contextual_relevance": generation_result.contextual_relevance,
                }

                results.append(test_result)
                self.test_results.append(test_result)

                logger.info(f"✅ {test_case['name']}: {'성공' if success else '실패'}")
                logger.info(f"   생성된 텍스트: {generation_result.generated_text[:50]}...")

            except Exception as e:
                logger.error(f"❌ {test_case['name']} 실패: {e}")
                results.append({"name": test_case["name"], "success": False, "error": str(e)})
                self.test_results.append(results[-1])

        return {
            "total_tests": len(test_cases),
            "successful_tests": len([r for r in results if r.get("success", False)]),
            "results": results,
        }

    async def _test_multilingual_processing(self) -> Dict[str, Any]:
        """다국어 처리 테스트"""
        logger.info("🌍 다국어 처리 테스트 시작")

        test_cases = [
            {
                "name": "한국어 처리 테스트",
                "text": "안녕하세요. 반갑습니다.",
                "context": {"language": "ko"},
                "expected_language": "ko",
            },
            {
                "name": "영어 처리 테스트",
                "text": "Hello, how are you?",
                "context": {"language": "en"},
                "expected_language": "en",
            },
            {
                "name": "일본어 처리 테스트",
                "text": "こんにちは、お元気ですか？",
                "context": {"language": "ja"},
                "expected_language": "ja",
            },
        ]

        results = []
        for test_case in test_cases:
            try:
                result = await self.system.process_language(
                    text=test_case["text"], context=test_case["context"]
                )

                multilingual_analysis = result.understanding_result.multilingual_analysis

                success = (
                    multilingual_analysis.get("multilingual_support", False)
                    and multilingual_analysis.get("detected_language")
                    == test_case["expected_language"]
                )

                test_result = {
                    "name": test_case["name"],
                    "success": success,
                    "detected_language": multilingual_analysis.get("detected_language"),
                    "multilingual_support": multilingual_analysis.get("multilingual_support"),
                }

                results.append(test_result)
                self.test_results.append(test_result)

                logger.info(f"✅ {test_case['name']}: {'성공' if success else '실패'}")

            except Exception as e:
                logger.error(f"❌ {test_case['name']} 실패: {e}")
                results.append({"name": test_case["name"], "success": False, "error": str(e)})
                self.test_results.append(results[-1])

        return {
            "total_tests": len(test_cases),
            "successful_tests": len([r for r in results if r.get("success", False)]),
            "results": results,
        }

    async def _test_performance(self) -> Dict[str, Any]:
        """성능 테스트"""
        logger.info("⚡ 성능 테스트 시작")

        test_cases = [
            {
                "name": "단일 처리 성능 테스트",
                "text": "안녕하세요. 오늘 날씨가 정말 좋네요.",
                "context": {"topic": "일상"},
            },
            {
                "name": "복잡한 텍스트 처리 성능 테스트",
                "text": "오늘은 정말 특별한 날이에요. 새로운 기술을 배우고, 가족과 함께 즐거운 시간을 보냈어요. 정말 행복하고 감사한 하루였습니다.",
                "context": {"topic": "일상", "emotion": "기쁨"},
            },
        ]

        results = []
        for test_case in test_cases:
            try:
                start_time = time.time()

                result = await self.system.process_language(
                    text=test_case["text"], context=test_case["context"]
                )

                processing_time = time.time() - start_time

                # 성능 기준: 5초 이내 처리
                success = processing_time < 5.0

                test_result = {
                    "name": test_case["name"],
                    "success": success,
                    "processing_time": processing_time,
                    "understanding_score": result.understanding_result.confidence_score,
                    "generation_score": result.generation_result.confidence_score,
                    "integration_score": result.integration_score,
                }

                results.append(test_result)
                self.test_results.append(test_result)

                logger.info(
                    f"✅ {test_case['name']}: {'성공' if success else '실패'} ({processing_time:.2f}초)"
                )

            except Exception as e:
                logger.error(f"❌ {test_case['name']} 실패: {e}")
                results.append({"name": test_case["name"], "success": False, "error": str(e)})
                self.test_results.append(results[-1])

        return {
            "total_tests": len(test_cases),
            "successful_tests": len([r for r in results if r.get("success", False)]),
            "results": results,
        }

    async def _test_integration(self) -> Dict[str, Any]:
        """통합 테스트"""
        logger.info("🔗 통합 테스트 시작")

        test_cases = [
            {
                "name": "전체 워크플로우 테스트",
                "text": "오늘 정말 기뻐요! 새로운 것을 배웠고, 가족과 함께 즐거운 시간을 보냈어요.",
                "context": {"topic": "일상", "emotion": "기쁨"},
                "generation_type": LanguageGenerationType.EMOTIONAL_EXPRESSION,
            },
            {
                "name": "복합 기능 테스트",
                "text": "어려운 문제를 해결하는 방법을 알려주세요. 정말 도움이 필요해요.",
                "context": {"topic": "문제해결", "intent": "질문"},
                "generation_type": LanguageGenerationType.CONTEXTUAL_GENERATION,
            },
        ]

        results = []
        for test_case in test_cases:
            try:
                result = await self.system.process_language(
                    text=test_case["text"],
                    context=test_case["context"],
                    generation_type=test_case["generation_type"],
                )

                # 통합 점수 기준: 0.6 이상
                success = result.integration_score >= 0.6

                test_result = {
                    "name": test_case["name"],
                    "success": success,
                    "integration_score": result.integration_score,
                    "understanding_score": result.understanding_result.confidence_score,
                    "generation_score": result.generation_result.confidence_score,
                    "generated_text": result.generation_result.generated_text,
                }

                results.append(test_result)
                self.test_results.append(test_result)

                logger.info(
                    f"✅ {test_case['name']}: {'성공' if success else '실패'} (통합점수: {result.integration_score:.2f})"
                )

            except Exception as e:
                logger.error(f"❌ {test_case['name']} 실패: {e}")
                results.append({"name": test_case["name"], "success": False, "error": str(e)})
                self.test_results.append(results[-1])

        return {
            "total_tests": len(test_cases),
            "successful_tests": len([r for r in results if r.get("success", False)]),
            "results": results,
        }

    def _print_test_summary(self, results: Dict[str, Any]):
        """테스트 결과 요약 출력"""
        summary = results["test_summary"]

        logger.info("\n" + "=" * 60)
        logger.info("🎯 통합 언어 이해 및 생성 시스템 테스트 결과 요약")
        logger.info("=" * 60)
        logger.info(f"📊 전체 테스트: {summary['total_tests']}개")
        logger.info(f"✅ 성공한 테스트: {summary['successful_tests']}개")
        logger.info(f"❌ 실패한 테스트: {summary['failed_tests']}개")
        logger.info(f"⏱️  총 소요시간: {summary['total_time']:.2f}초")
        logger.info(f"📅 테스트 시간: {summary['timestamp']}")

        # 카테고리별 결과
        logger.info("\n📋 카테고리별 결과:")
        for category, category_results in results["test_categories"].items():
            success_rate = (
                category_results["successful_tests"] / category_results["total_tests"]
            ) * 100
            logger.info(
                f"  {category}: {category_results['successful_tests']}/{category_results['total_tests']} ({success_rate:.1f}%)"
            )

        # 전체 성공률
        overall_success_rate = (summary["successful_tests"] / summary["total_tests"]) * 100
        logger.info(f"\n🎉 전체 성공률: {overall_success_rate:.1f}%")

        if overall_success_rate >= 80:
            logger.info("🎊 테스트 결과: 우수")
        elif overall_success_rate >= 60:
            logger.info("👍 테스트 결과: 양호")
        else:
            logger.info("⚠️  테스트 결과: 개선 필요")

        logger.info("=" * 60)


async def main():
    """메인 함수"""
    logger.info("🚀 DuRi 통합 언어 이해 및 생성 시스템 테스트 시작")

    # 테스터 초기화
    tester = IntegratedLanguageSystemTester()

    # 종합 테스트 실행
    results = await tester.run_comprehensive_tests()

    # 결과 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_integrated_language_system_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    logger.info(f"📄 테스트 결과가 {filename}에 저장되었습니다.")

    return results


if __name__ == "__main__":
    # 테스트 실행
    asyncio.run(main())
