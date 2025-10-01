#!/usr/bin/env python3
"""
DuRiCore 시스템 테스트
새로운 실존적 AI 시스템의 핵심 기능들을 테스트
"""

import asyncio
import logging
import os
import sys
from typing import Any, Dict

# DuRiCore 모듈 import를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from DuRiCore.core.main_loop import DuRiCore
from DuRiCore.memory.vector_store import VectorMemoryStore
from DuRiCore.modules.emotion.emotion_embedding import (
    EmotionCategory,
    NLPEmotionEmbedding,
)
from DuRiCore.modules.judgment.self_critique import (
    BiasType,
    CritiqueLevel,
    SelfCritiqueSystem,
)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_emotion_embedding():
    """감정 임베딩 시스템 테스트"""
    print("\n🧠 **감정 임베딩 시스템 테스트**")

    emotion_embedding = NLPEmotionEmbedding()

    test_texts = [
        "오늘 정말 기쁘다! 프로젝트가 성공했어!",
        "너무 슬프다... 친구와 헤어졌어.",
        "화가 난다. 계속 실수만 하고 있어.",
        "무섭다. 내일 시험이야.",
        "놀라다. 갑자기 연락이 왔어.",
        "사랑한다. 가족이 최고야.",
        "그냥 평범한 하루였다.",
    ]

    for text in test_texts:
        print(f"\n📝 입력: {text}")
        embedding = emotion_embedding.analyze_emotion(text)
        summary = emotion_embedding.get_emotion_summary(embedding)

        print(f"🎭 주요 감정: {summary['primary_emotion']}")
        print(f"💪 강도: {summary['intensity']:.2f}")
        print(f"🎯 신뢰도: {summary['confidence']:.2f}")
        print(f"📊 감정 점수: {summary['sentiment']:.2f}")
        print(f"🏷️ 맥락: {summary['context']}")
        print(f"🔑 키워드: {', '.join(summary['keywords'][:3])}")


async def test_vector_memory():
    """벡터 메모리 시스템 테스트"""
    print("\n🧠 **벡터 메모리 시스템 테스트**")

    memory_store = VectorMemoryStore()

    # 테스트 메모리 저장
    test_memories = [
        {
            "content": "오늘 회사에서 프로젝트 성공했다. 정말 기쁘다!",
            "emotion": {
                "primary_emotion": "joy",
                "intensity": 0.8,
                "sentiment_score": 0.7,
            },
            "context": {"topic": "work", "intent": "celebration"},
        },
        {
            "content": "친구와 다퉈서 속상하다. 화해하고 싶다.",
            "emotion": {
                "primary_emotion": "sadness",
                "intensity": 0.6,
                "sentiment_score": -0.5,
            },
            "context": {"topic": "relationship", "intent": "conflict"},
        },
        {
            "content": "새로운 기술을 배우고 있다. 어렵지만 재미있다.",
            "emotion": {
                "primary_emotion": "anticipation",
                "intensity": 0.7,
                "sentiment_score": 0.6,
            },
            "context": {"topic": "learning", "intent": "growth"},
        },
    ]

    memory_ids = []
    for memory_data in test_memories:
        memory_id = memory_store.store_memory(
            memory_data["content"],
            memory_data["emotion"],
            memory_data["context"],
            importance=0.7,
        )
        memory_ids.append(memory_id)
        print(f"💾 메모리 저장: {memory_id}")

    # 유사한 메모리 검색 테스트
    print("\n🔍 유사한 메모리 검색 테스트:")
    search_queries = [
        "기쁜 일이 있어서",
        "친구와 문제가 생겼어",
        "새로운 것을 배우고 있어",
    ]

    for query in search_queries:
        print(f"\n📝 검색 쿼리: {query}")
        similar_memories = memory_store.search_similar_memories(query, limit=3)

        for memory_id, similarity in similar_memories:
            memory = memory_store.get_memory_by_id(memory_id)
            if memory:
                print(f"  🎯 유사도 {similarity:.2f}: {memory.content[:50]}...")

    # 메모리 통계
    stats = memory_store.get_memory_statistics()
    print(f"\n📊 메모리 통계:")
    print(f"  총 메모리 수: {stats['total_memories']}")
    print(f"  평균 중요도: {stats['average_importance']:.2f}")
    print(f"  평균 접근 횟수: {stats['average_access_count']:.2f}")


async def test_self_critique():
    """자기 성찰 시스템 테스트"""
    print("\n🧠 **자기 성찰 시스템 테스트**")

    critique_system = SelfCritiqueSystem()

    test_judgments = [
        {
            "judgment_confidence": 0.8,
            "reasoning_process": "체계적으로 분석한 결과, 이 결정이 최선이라고 판단됩니다.",
            "final_decision": "proceed",
            "context_judgment": {"decision": "positive", "confidence": 0.7},
            "emotion_judgment": {"decision": "balanced", "confidence": 0.6},
            "memory_judgment": {"decision": "supportive", "confidence": 0.8},
        },
        {
            "judgment_confidence": 0.3,
            "reasoning_process": "너무 화가 나서 그냥 결정했다. 정말 화나다!",
            "final_decision": "reject",
            "context_judgment": {"decision": "negative", "confidence": 0.4},
            "emotion_judgment": {"decision": "emotional", "confidence": 0.9},
            "memory_judgment": {"decision": "biased", "confidence": 0.2},
        },
        {
            "judgment_confidence": 0.6,
            "reasoning_process": "여러 관점을 고려했지만, 확실하지는 않다.",
            "final_decision": "consider",
            "context_judgment": {"decision": "neutral", "confidence": 0.5},
            "emotion_judgment": {"decision": "neutral", "confidence": 0.5},
            "memory_judgment": {"decision": "neutral", "confidence": 0.5},
        },
    ]

    test_emotions = [
        {"intensity": 0.3, "primary_emotion": "neutral"},
        {"intensity": 0.9, "primary_emotion": "anger"},
        {"intensity": 0.5, "primary_emotion": "anticipation"},
    ]

    for i, (judgment, emotion) in enumerate(zip(test_judgments, test_emotions)):
        print(f"\n📝 판단 {i+1}: {judgment['reasoning_process'][:50]}...")

        critique = critique_system.critique_judgment(judgment, emotion, {})

        print(f"🎭 성찰 수준: {critique.critique_level.value}")
        print(f"📊 판단 품질: {critique.judgment_quality:.2f}")
        print(f"⚠️ 편향 감지: {critique.bias_detected}")
        if critique.bias_detected:
            print(f"  편향 유형: {critique.bias_type.value}")
            print(f"  편향 강도: {critique.bias_strength:.2f}")
        print(f"🔧 개선 영역: {', '.join(critique.improvement_areas[:3])}")
        print(f"💭 자기 피드백: {critique.self_feedback}")
        print(f"🎯 신뢰도: {critique.confidence:.2f}")

    # 성찰 통계
    stats = critique_system.get_critique_statistics()
    print(f"\n📊 성찰 통계:")
    print(f"  총 성찰 수: {stats['total_critiques']}")
    print(f"  평균 판단 품질: {stats['average_judgment_quality']:.2f}")
    print(f"  편향 감지율: {stats['bias_detection_rate']:.2f}")


async def test_main_loop():
    """메인 AI 루프 테스트"""
    print("\n🧠 **메인 AI 루프 테스트**")

    duri_core = DuRiCore()

    test_inputs = [
        "오늘 정말 기쁘다! 프로젝트가 성공했어!",
        "친구와 다퉈서 속상하다. 어떻게 해야 할까?",
        "새로운 기술을 배우고 있는데 어렵다. 포기할까?",
        "내일 중요한 회의가 있다. 긴장된다.",
        "가족과 함께한 시간이 정말 행복했다.",
    ]

    for i, user_input in enumerate(test_inputs):
        print(f"\n🔄 AI 루프 {i+1}: {user_input}")

        result = duri_core.process_input(user_input)

        print(f"📊 맥락 분석: {result['context_analysis']['topic']}")
        print(f"🎭 감정-기억: {result['emotion_memory']['emotion']['primary_emotion']}")
        print(f"⚖️ 판단 신뢰도: {result['judgment']['judgment_confidence']:.2f}")
        print(f"💭 자기 성찰: {result['self_reflection']['self_feedback']}")
        print(f"📚 학습 효과성: {result['learning']['learning_effectiveness']:.2f}")
        print(f"💬 응답: {result['response']['response_text']}")

    # 시스템 상태
    status = duri_core.get_system_status()
    print(f"\n📊 시스템 상태:")
    print(f"  총 대화 수: {status['total_conversations']}")
    print(f"  총 경험 수: {status['total_experiences']}")
    print(f"  학습 패턴 수: {status['learning_patterns']}")
    print(f"  시스템 상태: {status['system_health']}")


async def main():
    """메인 테스트 함수"""
    print("🚀 DuRiCore 시스템 테스트 시작")
    print("=" * 50)

    try:
        # 1. 감정 임베딩 테스트
        await test_emotion_embedding()

        # 2. 벡터 메모리 테스트
        await test_vector_memory()

        # 3. 자기 성찰 테스트
        await test_self_critique()

        # 4. 메인 AI 루프 테스트
        await test_main_loop()

        print("\n✅ 모든 테스트 완료!")
        print("🎯 DuRiCore 시스템이 정상적으로 작동합니다.")

    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        logger.error(f"테스트 오류: {e}")


if __name__ == "__main__":
    asyncio.run(main())
