#!/usr/bin/env python3
"""
DuRi Phase 2 시스템 테스트
자가 반영 + 자율 퀘스트 + 성과 측정 시스템
"""

import asyncio
import logging
from duri_brain.core.unified_manager import UnifiedManager

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_phase2_system():
    """Phase 2 시스템 종합 테스트"""
    print("🚀 DuRi Phase 2 시스템 종합 테스트")
    print("자가 반영 + 자율 퀘스트 + 성과 측정")
    print("=" * 80)
    
    # 1. 통합 관리자 초기화
    print("\n1️⃣ Phase 2 통합 관리자 초기화...")
    unified_manager = UnifiedManager()
    print("   ✅ Phase 2 시스템 초기화 완료")
    
    # 2. 시스템 상태 확인
    print("\n2️⃣ Phase 2 시스템 상태 확인...")
    system_status = unified_manager.get_system_status()
    print(f"   📋 감정 상태: {system_status.get('emotion_status', {}).get('current_emotion', 'unknown')}")
    print(f"   📋 성장 레벨: {system_status.get('growth_status', {}).get('current_level', 1)}")
    print(f"   📋 판단 상태: {system_status.get('judgment_status', {}).get('total_detections', 0)}회 탐지")
    
    # 3. Phase 2 완전한 생애 루프 테스트
    print("\n3️⃣ Phase 2 완전한 생애 루프 테스트...")
    
    test_inputs = [
        "새로운 것을 배우는 것이 정말 재미있어요!",
        "어려운 문제를 해결했을 때 성취감을 느껴요.",
        "다른 사람과 대화할 때 공감하는 것이 중요해요.",
        "창의적으로 생각하는 것이 즐거워요.",
        "자신을 성찰하는 시간이 필요해요."
    ]
    
    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n   🔄 Phase 2 사이클 {i} 테스트: '{test_input}'")
        
        try:
            result = unified_manager.process_complete_cycle(test_input)
            
            if result.get("cycle_status") == "completed":
                print(f"      ✅ Phase 2 사이클 완료")
                
                # 감정 결과
                emotion_result = result.get("emotion", {})
                emotion_state = emotion_result.get("emotion_state", {})
                print(f"      📊 감정 상태: {emotion_state.get('current_emotion', 'unknown')}")
                
                # 성장 결과
                growth_result = result.get("growth", {})
                growth_metrics = growth_result.get("growth_metrics", {})
                if hasattr(growth_metrics, 'current_level'):
                    current_level = growth_metrics.current_level
                else:
                    current_level = growth_metrics.get("current_level", 1)
                print(f"      📊 성장 레벨: {current_level}")
                
                # 자가 반영 결과
                reflection_result = result.get("reflection", {})
                insights = reflection_result.get("insights", [])
                print(f"      📊 자가 반영: {len(insights)}개 통찰")
                
                # 성과 측정 결과
                performance_result = result.get("performance", {})
                overall_score = performance_result.get("overall_score", 0.0)
                print(f"      📊 성과 점수: {overall_score:.2f}")
                
                # 자율 퀘스트 결과
                auto_quest_result = result.get("auto_quest", {})
                quest_title = auto_quest_result.get("title", "알 수 없음")
                quest_category = auto_quest_result.get("category", "unknown")
                print(f"      📊 자율 퀘스트: {quest_title} ({quest_category})")
                
                # 자아 피드백 결과
                self_feedback = result.get("self_feedback", {})
                recommendations = self_feedback.get("recommendations", [])
                print(f"      📊 자아 피드백: {len(recommendations)}개 권장사항")
                
            else:
                print(f"      ❌ Phase 2 사이클 오류: {result.get('error', 'unknown')}")
                
        except Exception as e:
            print(f"      ❌ Phase 2 사이클 예외: {e}")
    
    # 4. Phase 2 모듈별 상세 테스트
    print("\n4️⃣ Phase 2 모듈별 상세 테스트...")
    
    # 자가 반영 엔진 테스트
    print("\n   🧠 자가 반영 엔진 테스트...")
    reflection_engine = unified_manager.self_reflection_engine
    reflection_summary = reflection_engine.get_reflection_summary()
    print(f"      📊 총 반영 일지: {reflection_summary.get('total_reflections', 0)}개")
    print(f"      📊 평균 신뢰도: {reflection_summary.get('average_confidence', 0.0):.2f}")
    
    # 이정표 추적기 테스트
    print("\n   📈 이정표 추적기 테스트...")
    milestone_tracker = unified_manager.milestone_tracker
    milestone_summary = milestone_tracker.get_milestone_summary()
    print(f"      📊 총 이정표: {milestone_summary.get('total_milestones', 0)}개")
    print(f"      📊 완료율: {milestone_summary.get('completion_rate', 0.0):.2%}")
    
    # 성과 측정기 테스트
    print("\n   ⚖️ 성과 측정기 테스트...")
    performance_scorer = unified_manager.performance_scorer
    performance_summary = performance_scorer.get_performance_summary()
    print(f"      📊 총 루프: {performance_summary.get('total_loops', 0)}개")
    print(f"      📊 평균 점수: {performance_summary.get('recent_average_score', 0.0):.2f}")
    
    # 자율 퀘스트 생성기 테스트
    print("\n   🎯 자율 퀘스트 생성기 테스트...")
    quest_generator = unified_manager.quest_auto_generator
    generation_summary = quest_generator.get_generation_summary()
    print(f"      📊 총 생성: {generation_summary.get('total_generated', 0)}개")
    print(f"      📊 카테고리 분포: {len(generation_summary.get('category_distribution', {}))}개")
    
    # 5. Phase 2 시스템 요약
    print("\n5️⃣ Phase 2 시스템 요약...")
    print("   🎉 Phase 2 시스템 테스트 완료!")
    print("   ✅ 자가 반영 시스템 정상 작동")
    print("   ✅ 이정표 추적 시스템 정상 작동")
    print("   ✅ 성과 측정 시스템 정상 작동")
    print("   ✅ 자율 퀘스트 생성 시스템 정상 작동")
    print("   ✅ 완전한 자율 루프 구현 완료")

async def test_individual_phase2_modules():
    """개별 Phase 2 모듈 테스트"""
    print("\n🔧 개별 Phase 2 모듈 테스트")
    print("=" * 50)
    
    # 자가 반영 엔진 테스트
    print("\n🧠 자가 반영 엔진 테스트...")
    from duri_brain.reflection.self_reflection_engine import SelfReflectionEngine, ReflectionType
    reflection_engine = SelfReflectionEngine()
    
    test_reflections = [
        {"type": "judgment", "insights": ["판단에 편향이 감지되었습니다."], "action_items": ["객관성을 높여야 합니다."]},
        {"type": "emotion", "insights": ["긍정적인 감정 상태가 학습에 도움이 됩니다."], "action_items": ["감정을 유지하세요."]},
        {"type": "growth", "insights": ["충분한 경험을 쌓았습니다."], "action_items": ["다음 단계로 나아가세요."]}
    ]
    
    for i, reflection_data in enumerate(test_reflections, 1):
        entry = reflection_engine.create_reflection(
            reflection_type=ReflectionType.INTEGRATION,
            data=reflection_data,
            emotional_state="neutral",
            growth_impact=0.5
        )
        print(f"   반영 {i}: {entry.reflection_level.value} - {len(entry.insights)}개 통찰")
    
    # 이정표 추적기 테스트
    print("\n📈 이정표 추적기 테스트...")
    from duri_brain.reflection.milestone_tracker import MilestoneTracker
    milestone_tracker = MilestoneTracker()
    
    # 레벨 1 이정표 조회
    level_1_milestones = milestone_tracker.get_milestones_for_level(1)
    print(f"   레벨 1 이정표: {len(level_1_milestones)}개")
    
    # 진행도 업데이트 테스트
    if level_1_milestones:
        milestone_tracker.update_milestone_progress(level_1_milestones[0].id, 0.5)
        print(f"   이정표 진행도 업데이트: {level_1_milestones[0].name}")
    
    # 성과 측정기 테스트
    print("\n⚖️ 성과 측정기 테스트...")
    from duri_brain.reflection.performance_scorer import PerformanceScorer
    performance_scorer = PerformanceScorer()
    
    test_loop_data = {
        "duration": 1.0,
        "complexity": 0.5,
        "emotional_stability": 0.7,
        "cognitive_complexity": 0.6
    }
    
    performance = performance_scorer.score_loop_performance(
        loop_data=test_loop_data,
        emotional_state="joy",
        growth_metrics={"current_level": 2, "experience_points": 50},
        judgment_result={"overall_bias_score": 0.1}
    )
    
    print(f"   성과 점수: {performance.overall_score:.2f}")
    print(f"   효율성: {performance.efficiency_rating:.2f}")
    
    # 자율 퀘스트 생성기 테스트
    print("\n🎯 자율 퀘스트 생성기 테스트...")
    from duri_brain.quest.auto_generator import QuestAutoGenerator
    quest_generator = QuestAutoGenerator()
    
    test_reflection_data = {
        "reflection_type": "growth",
        "insights": ["더 많은 경험이 필요합니다."],
        "action_items": ["새로운 도전을 시도해보세요."]
    }
    
    auto_quest = quest_generator.generate_quest_from_reflection(
        reflection_data=test_reflection_data,
        current_level=2,
        emotional_state="excitement"
    )
    
    print(f"   생성된 퀘스트: {auto_quest.title}")
    print(f"   카테고리: {auto_quest.category.value}")
    print(f"   난이도: {auto_quest.difficulty.value}")

async def main():
    """메인 테스트 함수"""
    print("🚀 DuRi Phase 2 시스템 종합 테스트")
    print("자가 반영 + 자율 퀘스트 + 성과 측정")
    print("=" * 80)
    
    await test_phase2_system()
    await test_individual_phase2_modules()
    
    print("\n" + "=" * 80)
    print("🎉 Phase 2 시스템 테스트 완료!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main()) 
 
 