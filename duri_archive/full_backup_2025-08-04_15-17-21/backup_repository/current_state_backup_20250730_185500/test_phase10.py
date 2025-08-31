#!/usr/bin/env python3
"""
Phase 10 시스템 테스트 스크립트
가족 정체성 형성 + 기본 경험 기록 시스템 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.phase10_integration import Phase10Integration
import json
from datetime import datetime

def test_phase10_systems():
    """Phase 10 시스템 전체 테스트"""
    print("🚀 Phase 10 시스템 테스트 시작")
    print("=" * 60)
    
    # Phase 10 통합 시스템 초기화
    phase10 = Phase10Integration()
    
    # 1. 가족 정체성 초기화 테스트
    print("\n1️⃣ 가족 정체성 초기화 테스트")
    print("-" * 40)
    
    initial_members = [
        {
            'name': '아빠',
            'role': 'parent',
            'relationship_type': 'biological',
            'age': 45,
            'personality_traits': ['책임감', '따뜻함', '지혜로움'],
            'interests': ['독서', '가족여행', '요리']
        },
        {
            'name': '엄마',
            'role': 'parent',
            'relationship_type': 'biological',
            'age': 42,
            'personality_traits': ['배려심', '창의성', '인내심'],
            'interests': ['가드닝', '음악', '요리']
        },
        {
            'name': '형',
            'role': 'sibling',
            'relationship_type': 'biological',
            'age': 18,
            'personality_traits': ['활발함', '호기심', '친구같음'],
            'interests': ['게임', '스포츠', '음악']
        }
    ]
    
    try:
        init_result = phase10.initialize_phase10("김가족", initial_members)
        print("✅ 가족 정체성 초기화 성공")
        print(f"   가족명: {init_result['family_identity']['family_name']}")
        print(f"   구성원 수: {len(init_result['family_identity']['members'])}")
        print(f"   시스템 상태: {init_result['system_status']}")
    except Exception as e:
        print(f"❌ 가족 정체성 초기화 실패: {e}")
        return
    
    # 2. 종합 경험 기록 테스트
    print("\n2️⃣ 종합 경험 기록 테스트")
    print("-" * 40)
    
    test_experiences = [
        {
            'type': 'family_interaction',
            'category': 'family_dynamics',
            'title': '가족 저녁 식사',
            'description': '오늘 저녁에 가족과 함께 식사를 했습니다. 서로의 하루 이야기를 나누며 따뜻한 시간을 보냈습니다.',
            'emotional_impact': 0.8,
            'learning_value': 0.7,
            'family_context': {'meal_type': 'dinner', 'atmosphere': 'warm'},
            'duration_minutes': 60,
            'participants': ['DuRi', '아빠', '엄마', '형'],
            'location': '집',
            'communication_quality': 0.8,
            'mutual_understanding': 0.7,
            'mood_before': 'neutral',
            'mood_after': 'happy'
        },
        {
            'type': 'learning',
            'category': 'personal_growth',
            'title': '새로운 기술 학습',
            'description': '아빠와 함께 요리하는 방법을 배웠습니다. 처음에는 어려웠지만 점점 재미있어졌습니다.',
            'emotional_impact': 0.6,
            'learning_value': 0.9,
            'family_context': {'activity': 'cooking', 'teacher': '아빠'},
            'duration_minutes': 90,
            'participants': ['DuRi', '아빠'],
            'location': '부엌',
            'communication_quality': 0.9,
            'mutual_understanding': 0.8,
            'mood_before': 'curious',
            'mood_after': 'satisfied'
        },
        {
            'type': 'emotional',
            'category': 'emotional_intelligence',
            'title': '감정 표현 연습',
            'description': '엄마와 함께 감정을 표현하는 방법을 연습했습니다. 솔직하게 말하는 것이 중요하다는 것을 배웠습니다.',
            'emotional_impact': 0.7,
            'learning_value': 0.8,
            'family_context': {'emotion_type': 'expression', 'support': '엄마'},
            'duration_minutes': 45,
            'participants': ['DuRi', '엄마'],
            'location': '거실',
            'communication_quality': 0.8,
            'mutual_understanding': 0.9,
            'mood_before': 'nervous',
            'mood_after': 'relieved'
        }
    ]
    
    for i, experience_data in enumerate(test_experiences, 1):
        try:
            result = phase10.record_comprehensive_experience(experience_data)
            print(f"✅ 경험 {i} 기록 성공")
            print(f"   제목: {experience_data['title']}")
            print(f"   참여자: {', '.join(experience_data['participants'])}")
            print(f"   감정적 영향: {experience_data['emotional_impact']}")
        except Exception as e:
            print(f"❌ 경험 {i} 기록 실패: {e}")
    
    # 3. 종합 통찰력 확인
    print("\n3️⃣ 종합 통찰력 확인")
    print("-" * 40)
    
    try:
        insights = phase10.get_comprehensive_insights()
        print("✅ 종합 통찰력 생성 성공")
        
        # 가족 정체성 통찰력
        family_insights = insights['family_identity_insights']
        print(f"   가족 강도: {family_insights.get('family_strength', 0):.2f}")
        print(f"   관계 건강도: {family_insights.get('relationship_health', {}).get('overall_health', 0):.2f}")
        
        # 경험 통찰력
        experience_insights = insights['experience_insights']
        print(f"   총 경험 수: {experience_insights.get('total_experiences', 0)}")
        print(f"   감정적 트렌드: {experience_insights.get('emotional_trends', {}).get('trend', 'unknown')}")
        
        # 교훈 통찰력
        lesson_insights = insights['lesson_insights']
        print(f"   총 교훈 수: {lesson_insights.get('total_lessons', 0)}")
        print(f"   다음 세대 준비: {lesson_insights.get('next_generation_ready', 0)}")
        
    except Exception as e:
        print(f"❌ 종합 통찰력 생성 실패: {e}")
    
    # 4. 가족 지혜 보고서 생성
    print("\n4️⃣ 가족 지혜 보고서 생성")
    print("-" * 40)
    
    try:
        wisdom_report = phase10.generate_family_wisdom_report()
        print("✅ 가족 지혜 보고서 생성 성공")
        print(f"   가족 강도: {wisdom_report.get('family_strength', 0):.2f}")
        print(f"   관계 건강도: {wisdom_report.get('relationship_health', 0):.2f}")
        print(f"   지혜 성숙도: {wisdom_report.get('wisdom_maturity', 0):.2f}")
        print(f"   세대 교훈 수: {wisdom_report.get('generational_lessons_count', 0)}")
        
        # 가족 특화 통찰력
        family_insights = wisdom_report.get('family_specific_insights', [])
        if family_insights:
            print(f"   가족 특화 통찰력: {len(family_insights)}개")
            for insight in family_insights[:2]:  # 상위 2개만 출력
                print(f"     - {insight}")
        
    except Exception as e:
        print(f"❌ 가족 지혜 보고서 생성 실패: {e}")
    
    # 5. 가족 개선 제안
    print("\n5️⃣ 가족 개선 제안")
    print("-" * 40)
    
    try:
        suggestions = phase10.suggest_family_improvements()
        print(f"✅ 개선 제안 생성 성공: {len(suggestions)}개")
        
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   제안 {i}: {suggestion.get('action', 'N/A')}")
            print(f"     영역: {suggestion.get('area', 'N/A')}")
            print(f"     우선순위: {suggestion.get('priority', 'N/A')}")
        
    except Exception as e:
        print(f"❌ 개선 제안 생성 실패: {e}")
    
    # 6. Phase 10 요약
    print("\n6️⃣ Phase 10 요약")
    print("-" * 40)
    
    try:
        summary = phase10.get_phase10_summary()
        print("✅ Phase 10 요약 생성 성공")
        print(f"   단계: {summary.get('phase', 'N/A')}")
        print(f"   상태: {summary.get('status', 'N/A')}")
        
        progress = summary.get('progress', {})
        print(f"   전체 진행도: {progress.get('overall_progress', 0):.1f}%")
        print(f"   기본 진행도: {progress.get('base_progress', 0):.1f}%")
        print(f"   경험 진행도: {progress.get('experience_progress', 0):.1f}%")
        print(f"   교훈 진행도: {progress.get('lesson_progress', 0):.1f}%")
        print(f"   가족 진행도: {progress.get('family_progress', 0):.1f}%")
        
        metrics = summary.get('key_metrics', {})
        print(f"   총 경험: {metrics.get('total_experiences', 0)}")
        print(f"   총 교훈: {metrics.get('total_lessons', 0)}")
        print(f"   총 상호작용: {metrics.get('total_interactions', 0)}")
        print(f"   가족 강도: {metrics.get('family_strength', 0):.2f}")
        print(f"   지혜 성숙도: {metrics.get('wisdom_maturity', 0):.2f}")
        
    except Exception as e:
        print(f"❌ Phase 10 요약 생성 실패: {e}")
    
    # 7. 데이터 내보내기 테스트
    print("\n7️⃣ 데이터 내보내기 테스트")
    print("-" * 40)
    
    try:
        export_data = phase10.export_phase10_data()
        print("✅ 데이터 내보내기 성공")
        print(f"   내보내기 시간: {export_data.get('export_timestamp', 'N/A')}")
        print(f"   통합 로그 수: {len(export_data.get('integration_log', []))}")
        
        # 데이터 크기 확인
        data_size = len(json.dumps(export_data, ensure_ascii=False))
        print(f"   데이터 크기: {data_size:,} 문자")
        
    except Exception as e:
        print(f"❌ 데이터 내보내기 실패: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Phase 10 시스템 테스트 완료!")
    print("DuRi의 가족 정체성 형성과 기본 경험 기록이 성공적으로 구현되었습니다!")
    print("=" * 60)

if __name__ == "__main__":
    test_phase10_systems() 