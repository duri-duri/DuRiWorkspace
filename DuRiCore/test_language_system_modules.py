#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 언어 시스템 모듈 테스트

분할된 언어 시스템 모듈들이 정상적으로 작동하는지 테스트합니다.
"""

import asyncio
import logging
from typing import Dict, Any

from language_system.core.integrated_language_system import IntegratedLanguageUnderstandingGenerationSystem
from language_system.core.data_structures import LanguageGenerationType

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_language_system_modules():
    """언어 시스템 모듈 테스트"""
    try:
        logger.info("=== 언어 시스템 모듈 테스트 시작 ===")
        
        # 통합 언어 시스템 초기화
        language_system = IntegratedLanguageUnderstandingGenerationSystem()
        
        # 테스트 케이스들
        test_cases = [
            {
                "text": "안녕하세요! 오늘 날씨가 정말 좋네요.",
                "context": {"user_id": "test_user", "session_id": "test_session"},
                "generation_type": LanguageGenerationType.CONVERSATIONAL_RESPONSE,
                "description": "일반적인 인사말 테스트"
            },
            {
                "text": "학습에 대한 조언을 구하고 싶어요.",
                "context": {"topic": "학습", "user_level": "beginner"},
                "generation_type": LanguageGenerationType.CONTEXTUAL_GENERATION,
                "description": "학습 관련 맥락 기반 생성 테스트"
            },
            {
                "text": "정말 기뻐요! 오늘 시험에서 좋은 성적을 받았어요.",
                "context": {"emotion": "기쁨", "intensity": 0.8},
                "generation_type": LanguageGenerationType.EMOTIONAL_EXPRESSION,
                "description": "감정적 표현 생성 테스트"
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"\n--- 테스트 케이스 {i}: {test_case['description']} ---")
            
            try:
                # 언어 처리 실행
                result = await language_system.process_language(
                    text=test_case["text"],
                    context=test_case["context"],
                    generation_type=test_case["generation_type"]
                )
                
                # 결과 분석
                understanding_result = result.understanding_result
                generation_result = result.generation_result
                
                logger.info(f"✅ 테스트 성공:")
                logger.info(f"  - 입력 텍스트: {test_case['text']}")
                logger.info(f"  - 이해 의도: {understanding_result.intent}")
                logger.info(f"  - 감정 톤: {understanding_result.emotional_tone}")
                logger.info(f"  - 생성 텍스트: {generation_result.generated_text}")
                logger.info(f"  - 통합 점수: {result.integration_score:.2f}")
                
                results.append({
                    "test_case": i,
                    "description": test_case["description"],
                    "success": True,
                    "integration_score": result.integration_score,
                    "processing_time": result.system_performance.get("processing_time", 0)
                })
                
            except Exception as e:
                logger.error(f"❌ 테스트 실패: {e}")
                results.append({
                    "test_case": i,
                    "description": test_case["description"],
                    "success": False,
                    "error": str(e)
                })
        
        # 전체 결과 요약
        logger.info("\n=== 테스트 결과 요약 ===")
        successful_tests = [r for r in results if r["success"]]
        failed_tests = [r for r in results if not r["success"]]
        
        logger.info(f"총 테스트 수: {len(results)}")
        logger.info(f"성공: {len(successful_tests)}")
        logger.info(f"실패: {len(failed_tests)}")
        
        if successful_tests:
            avg_integration_score = sum(r["integration_score"] for r in successful_tests) / len(successful_tests)
            avg_processing_time = sum(r["processing_time"] for r in successful_tests) / len(successful_tests)
            logger.info(f"평균 통합 점수: {avg_integration_score:.2f}")
            logger.info(f"평균 처리 시간: {avg_processing_time:.2f}초")
        
        if failed_tests:
            logger.error("실패한 테스트:")
            for test in failed_tests:
                logger.error(f"  - 테스트 {test['test_case']}: {test['description']} - {test['error']}")
        
        # 시스템 상태 조회
        system_status = await language_system.get_system_status()
        logger.info(f"\n시스템 상태: {system_status['status']}")
        logger.info(f"버전: {system_status['version']}")
        
        return results
        
    except Exception as e:
        logger.error(f"테스트 실행 중 오류 발생: {e}")
        return []

if __name__ == "__main__":
    # 테스트 실행
    asyncio.run(test_language_system_modules())
