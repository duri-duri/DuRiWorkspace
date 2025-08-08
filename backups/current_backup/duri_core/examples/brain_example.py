#!/usr/bin/env python3
"""
DuRi Brain 시스템 사용 예제

감정-판단-반응 루프의 완전한 생명주기를 시연합니다.
"""

import sys
import os
import json
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain import BrainController, BrainConfig


def main():
    """Brain 시스템 예제 실행"""
    print("DuRi Brain 시스템 예제")
    print("=" * 50)
    
    # 1. Brain 시스템 초기화
    print("\n1. Brain 시스템 초기화...")
    config = BrainConfig(
        data_dir="example_brain_data",
        auto_feedback=True,
        enable_learning=True,
        max_loops_per_session=100
    )
    
    brain = BrainController(config)
    print("✓ Brain 시스템 초기화 완료")
    
    # 2. 세션 시작
    print("\n2. 세션 시작...")
    session_id = f"example_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    success = brain.start_session(
        session_id=session_id,
        user_id="example_user",
        environment="test_environment",
        metadata={"purpose": "demonstration"}
    )
    
    if not success:
        print("✗ 세션 시작 실패")
        return
    
    print(f"✓ 세션 시작 완료: {session_id}")
    
    # 3. 다양한 감정 처리
    print("\n3. 감정 처리 시연...")
    
    emotions_to_test = [
        ("happy", 0.8, "긍정적인 상황에서의 기쁨"),
        ("angry", 0.6, "약간의 분노 상황"),
        ("sad", 0.7, "슬픈 상황"),
        ("curiosity", 0.9, "강한 호기심"),
        ("frustration", 0.5, "좌절감"),
        ("regret", 0.8, "후회하는 상황")
    ]
    
    for emotion, intensity, description in emotions_to_test:
        print(f"\n  처리 중: {emotion} (강도: {intensity:.1f}) - {description}")
        
        try:
            emotion_input, decision, feedback, loop_result = brain.process_emotion(
                emotion=emotion,
                intensity=intensity,
                session_id=session_id,
                context={"description": description}
            )
            
            print(f"    ✓ 감정 입력: {emotion_input.emotion} (강도: {emotion_input.intensity:.2f})")
            print(f"    ✓ 의사결정: {decision['action']} (신뢰도: {decision['confidence']:.2f})")
            print(f"    ✓ 피드백: {feedback.feedback_type.value} (점수: {feedback.feedback_score:.2f})")
            print(f"    ✓ 루프 결과: 성공률 {loop_result.success_rate:.2f}, 지속시간 {loop_result.loop_duration:.2f}초")
            
        except Exception as e:
            print(f"    ✗ 처리 실패: {e}")
    
    # 4. 외부 피드백 수집 시연
    print("\n4. 외부 피드백 수집 시연...")
    
    # 실제로는 외부 시스템에서 피드백을 받아야 하지만, 예제에서는 시뮬레이션
    loop_results = brain.feedback_collector.get_loop_results(limit=1)
    if loop_results:
        loop_id = loop_results[0].loop_id
        
        external_feedback = brain.collect_external_feedback(
            loop_id=loop_id,
            feedback_type="success",
            feedback_score=0.85,
            feedback_text="외부 시스템에서 수집된 긍정적 피드백",
            source="external_system"
        )
        
        print(f"    ✓ 외부 피드백 수집: {external_feedback.feedback_type.value} (점수: {external_feedback.feedback_score:.2f})")
    
    # 5. 세션 통계 조회
    print("\n5. 세션 통계 조회...")
    session_stats = brain.get_session_statistics(session_id)
    
    print(f"    세션 ID: {session_stats['session_id']}")
    print(f"    총 루프 수: {session_stats['total_loops']}")
    print(f"    평균 성공률: {session_stats['avg_success_rate']:.2f}")
    print(f"    감정 분포: {session_stats['emotion_distribution']}")
    print(f"    액션 분포: {session_stats['action_distribution']}")
    
    # 6. 학습 데이터 조회
    print("\n6. 학습 데이터 조회...")
    learning_data = brain.loop_manager.get_learning_data(limit=10)
    
    print(f"    총 학습 데이터: {len(learning_data)}개")
    for i, data in enumerate(learning_data[:3]):  # 처음 3개만 표시
        print(f"    {i+1}. {data['emotion']} -> {data['action']} (성공률: {data['success_rate']:.2f})")
    
    # 7. 성능 인사이트 조회
    print("\n7. 성능 인사이트 조회...")
    insights = brain.loop_manager.get_performance_insights()
    
    if insights:
        overall = insights.get('overall', {})
        print(f"    전체 루프 수: {overall.get('total_loops', 0)}")
        print(f"    평균 성공률: {overall.get('avg_success_rate', 0):.2f}")
        print(f"    평균 지속시간: {overall.get('avg_duration', 0):.2f}초")
        
        emotion_perf = insights.get('emotion_performance', {})
        print(f"    감정별 성능:")
        for emotion, perf in list(emotion_perf.items())[:3]:  # 처음 3개만 표시
            print(f"      {emotion}: 성공률 {perf.get('avg_success_rate', 0):.2f}")
    
    # 8. 시스템 개요 조회
    print("\n8. 시스템 개요 조회...")
    overview = brain.get_system_overview()
    
    print(f"    총 처리된 루프: {overview['total_loops_processed']}")
    print(f"    활성 세션 수: {len(overview['active_sessions'])}")
    
    learning_summary = overview.get('learning_summary', {})
    print(f"    학습 데이터 요약:")
    print(f"      총 레코드: {learning_summary.get('total_records', 0)}")
    print(f"      평균 성공률: {learning_summary.get('avg_success_rate', 0):.2f}")
    print(f"      감정 종류: {learning_summary.get('emotion_count', 0)}")
    print(f"      액션 종류: {learning_summary.get('action_count', 0)}")
    
    # 9. 학습 데이터 내보내기
    print("\n9. 학습 데이터 내보내기...")
    output_path = f"example_learning_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    success = brain.export_learning_data(output_path, session_id)
    if success:
        print(f"    ✓ 학습 데이터 내보내기 완료: {output_path}")
    else:
        print("    ✗ 학습 데이터 내보내기 실패")
    
    # 10. 세션 종료
    print("\n10. 세션 종료...")
    success = brain.end_session(session_id)
    if success:
        print(f"    ✓ 세션 종료 완료: {session_id}")
    else:
        print("    ✗ 세션 종료 실패")
    
    # 11. 시스템 백업
    print("\n11. 시스템 백업...")
    backup_dir = "example_backups"
    success = brain.backup_system(backup_dir)
    if success:
        print(f"    ✓ 시스템 백업 완료: {backup_dir}")
    else:
        print("    ✗ 시스템 백업 실패")
    
    print("\n" + "=" * 50)
    print("DuRi Brain 시스템 예제 완료!")
    print("\n생성된 파일들:")
    print(f"  - 데이터 디렉토리: {config.data_dir}")
    print(f"  - 학습 데이터: {output_path}")
    print(f"  - 백업 디렉토리: {backup_dir}")


if __name__ == "__main__":
    main() 