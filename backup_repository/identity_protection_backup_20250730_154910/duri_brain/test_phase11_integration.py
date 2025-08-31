#!/usr/bin/env python3
"""
Phase 11 통합 테스트 시스템

기능:
- Phase 11의 모든 시스템 통합 테스트
- 시스템 간 상호작용 검증
- 데이터 흐름 및 연동 테스트
- 전체 Phase 11 성능 평가
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.text_learning_service import TextBasedLearningSystem
from app.services.subtitle_learning_service import SubtitleBasedLearningSystem
from app.services.llm_interface_service import LLMInterface
from app.services.basic_conversation_service import BasicConversationSystem
from app.services.family_conversation_precision_service import FamilyConversationPrecisionSystem
from app.services.developmental_thinking_conversation_service import DevelopmentalThinkingConversationSystem

import json
from datetime import datetime

def test_phase11_integration():
    """Phase 11 통합 테스트"""
    print("🧠 Phase 11 통합 테스트 시작...")
    
    # 가족 맥락 설정
    family_context = {
        'family_type': 'nuclear',
        'children_count': 2,
        'children_ages': [5, 8],
        'family_values': ['사랑', '소통', '성장', '창의성'],
        'age': 5
    }
    
    # 1. 텍스트 학습 시스템 테스트
    print("\n📚 1. 텍스트 학습 시스템 테스트")
    text_learning = TextBasedLearningSystem()
    
    sample_content = {
        'title': '가족과 함께하는 창의적 학습 방법',
        'content': '창의력을 키우는 것은 가족과의 소통에서 시작됩니다. 아이들과 함께 그림을 그리거나 이야기를 나누는 것이 좋은 방법입니다.',
        'text_type': 'article',
        'source_url': 'https://example.com/creative-learning',
        'author': '가족 교육 전문가'
    }
    
    text_content = text_learning.add_text_content(sample_content)
    extracted_knowledge = text_learning.extract_knowledge_from_text(text_content.id)
    print(f"✅ 텍스트 학습: {len(extracted_knowledge.key_concepts)}개 키 컨셉 추출")
    
    # 2. 자막 학습 시스템 테스트
    print("\n📹 2. 자막 학습 시스템 테스트")
    subtitle_learning = SubtitleBasedLearningSystem()
    
    sample_video = {
        'title': '가족과 함께하는 창의적 놀이',
        'description': '아이들과 함께할 수 있는 창의적인 놀이 방법을 소개합니다.',
        'video_type': 'family_content',
        'duration_seconds': 600,
        'source_url': 'https://youtube.com/watch?v=example',
        'channel_name': '가족 놀이 채널'
    }
    
    video_content = subtitle_learning.add_video_content(sample_video)
    sample_subtitles = [
        {'start_time': 0.0, 'end_time': 30.0, 'text': '안녕하세요! 오늘은 가족과 함께할 수 있는 창의적인 놀이를 소개해드릴게요.'},
        {'start_time': 30.0, 'end_time': 60.0, 'text': '먼저 준비물을 보시면 종이와 색연필이 필요합니다.'}
    ]
    
    subtitle_segments = subtitle_learning.add_subtitle_segments(video_content.id, sample_subtitles)
    visual_knowledge = subtitle_learning.extract_visual_knowledge_from_video(video_content.id)
    print(f"✅ 자막 학습: {len(visual_knowledge.key_concepts)}개 키 컨셉 추출")
    
    # 3. LLM 인터페이스 테스트
    print("\n🤖 3. LLM 인터페이스 테스트")
    llm_interface = LLMInterface()
    
    learning_question = "아이의 창의력을 키우는 방법을 알려주세요."
    learning_response = llm_interface.get_learning_help(learning_question, family_context)
    print(f"✅ LLM 학습 도움: {learning_response.response_quality.value} 품질")
    
    # 4. 기본 대화 시스템 테스트
    print("\n💬 4. 기본 대화 시스템 테스트")
    conversation_system = BasicConversationSystem()
    
    session = conversation_system.start_conversation("member_1", "엄마", "mother", family_context)
    conversation_response = conversation_system.process_message(
        session.id, "member_1", "엄마", "아이의 창의력을 키우고 싶어요."
    )
    print(f"✅ 기본 대화: {conversation_response.response_style.value} 스타일")
    
    # 5. 가족 정밀도 시스템 테스트
    print("\n🎯 5. 가족 정밀도 시스템 테스트")
    precision_system = FamilyConversationPrecisionSystem()
    
    precision_analysis = precision_system.analyze_conversation_precision(
        "아이의 창의력을 키우고 싶어요.", family_context
    )
    precision_response = precision_system.generate_precision_enhanced_response(
        "아이의 창의력을 키우고 싶어요.", family_context, precision_analysis
    )
    print(f"✅ 가족 정밀도: {precision_response.confidence_score:.2f} 신뢰도")
    
    # 6. 발전적 사고 시스템 테스트
    print("\n🧠 6. 발전적 사고 시스템 테스트")
    developmental_system = DevelopmentalThinkingConversationSystem()
    
    growth_analysis = developmental_system.analyze_developmental_thinking(
        "아이의 창의력을 키우고 싶어요.", family_context
    )
    developmental_response = developmental_system.generate_developmental_response(
        "아이의 창의력을 키우고 싶어요.", family_context, growth_analysis
    )
    print(f"✅ 발전적 사고: {developmental_response.confidence_score:.2f} 신뢰도")
    
    # 7. 시스템 간 데이터 연동 테스트
    print("\n🔄 7. 시스템 간 데이터 연동 테스트")
    
    # 텍스트 학습 → LLM 연동
    text_recommendations = text_learning.get_learning_recommendations(family_context)
    if text_recommendations:
        llm_followup = llm_interface.get_knowledge_answer(
            f"'{text_recommendations[0]['text_content']['title']}'에 대해 더 자세히 알려주세요.",
            family_context
        )
        print(f"✅ 텍스트→LLM 연동: {llm_followup.response_quality.value} 품질")
    
    # 자막 학습 → 대화 시스템 연동
    visual_recommendations = subtitle_learning.get_visual_learning_recommendations(family_context)
    if visual_recommendations:
        conversation_followup = conversation_system.process_message(
            session.id, "member_1", "엄마", 
            f"'{visual_recommendations[0]['video_content']['title']}' 영상을 보여주세요."
        )
        print(f"✅ 자막→대화 연동: {conversation_followup.response_style.value} 스타일")
    
    # 8. 통합 성능 평가
    print("\n📊 8. 통합 성능 평가")
    
    # 각 시스템의 통계 수집
    text_stats = text_learning.get_learning_statistics()
    subtitle_stats = subtitle_learning.get_visual_learning_statistics()
    llm_stats = llm_interface.get_llm_statistics()
    conversation_stats = conversation_system.get_conversation_statistics()
    precision_stats = precision_system.get_precision_statistics()
    developmental_stats = developmental_system.get_developmental_statistics()
    
    # 전체 성능 점수 계산
    total_systems = 6
    active_systems = sum([
        1 if text_stats.get('total_contents', 0) > 0 else 0,
        1 if subtitle_stats.get('total_videos', 0) > 0 else 0,
        1 if llm_stats.get('total_queries', 0) > 0 else 0,
        1 if conversation_stats.get('total_sessions', 0) > 0 else 0,
        1 if precision_stats.get('total_analyses', 0) > 0 else 0,
        1 if developmental_stats.get('total_analyses', 0) > 0 else 0
    ])
    
    system_activation_rate = active_systems / total_systems
    print(f"✅ 시스템 활성화율: {system_activation_rate:.2f} ({active_systems}/{total_systems})")
    
    # 평균 신뢰도 계산
    confidence_scores = [
        text_stats.get('average_confidence', 0),
        subtitle_stats.get('average_confidence', 0),
        llm_stats.get('average_confidence', 0),
        conversation_stats.get('average_confidence', 0),
        precision_stats.get('average_confidence', 0),
        developmental_stats.get('average_confidence', 0)
    ]
    avg_confidence = sum(confidence_scores) / len(confidence_scores)
    print(f"✅ 평균 신뢰도: {avg_confidence:.2f}")
    
    # 9. 데이터 내보내기 테스트
    print("\n💾 9. 데이터 내보내기 테스트")
    
    export_data = {
        'text_learning': text_learning.export_learning_data(),
        'subtitle_learning': subtitle_learning.export_visual_learning_data(),
        'llm_interface': llm_interface.export_llm_data(),
        'conversation': conversation_system.export_conversation_data(),
        'precision': precision_system.export_precision_data(),
        'developmental': developmental_system.export_developmental_data(),
        'integration_test_date': datetime.now().isoformat()
    }
    
    print(f"✅ 통합 데이터 내보내기: {len(export_data)}개 시스템")
    
    # 10. Phase 11 완료 요약
    print("\n🎉 Phase 11 통합 테스트 완료!")
    print(f"📋 테스트된 시스템: {total_systems}개")
    print(f"✅ 활성화된 시스템: {active_systems}개")
    print(f"📊 평균 신뢰도: {avg_confidence:.2f}")
    print(f"🔄 시스템 연동: 텍스트→LLM, 자막→대화")
    print(f"💾 데이터 내보내기: 완료")
    
    return {
        'total_systems': total_systems,
        'active_systems': active_systems,
        'activation_rate': system_activation_rate,
        'average_confidence': avg_confidence,
        'export_data': export_data
    }

if __name__ == "__main__":
    test_phase11_integration() 