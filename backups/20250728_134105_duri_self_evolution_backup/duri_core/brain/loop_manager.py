#!/usr/bin/env python3
"""
Loop Manager - 감정-판단-반응 루프 관리 시스템

감정 입력부터 피드백 수집까지의 전체 루프를 관리하고,
Core에게 학습 데이터를 제공합니다.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from duri_common.logger import get_logger
from duri_core.core.stats import update_action_stats
from .emotion_recorder import EmotionRecorder, EmotionInput, DecisionRecord
from .feedback_collector import FeedbackCollector, ExternalFeedback, LoopResult, FeedbackType

logger = get_logger("duri_brain.loop_manager")


@dataclass
class LoopContext:
    """루프 컨텍스트"""
    session_id: str
    user_id: Optional[str] = None
    environment: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class LoopManager:
    """감정-판단-반응 루프 관리자"""
    
    def __init__(self, data_dir: str = "brain_data"):
        """
        LoopManager 초기화
        
        Args:
            data_dir (str): 데이터 저장 디렉토리
        """
        self.data_dir = data_dir
        self.emotion_recorder = EmotionRecorder(data_dir)
        self.feedback_collector = FeedbackCollector(data_dir)
        
        # Core 관련 경로
        self.evolution_log_path = os.path.join(data_dir, "evolution_log.json")
        self.stats_path = os.path.join(data_dir, "action_stats.json")
        
        # 초기화
        self._initialize_core_data()
        
        logger.info(f"LoopManager 초기화 완료: {data_dir}")
    
    def process_emotion_loop(
        self,
        emotion: str,
        intensity: float,
        context: Optional[Dict[str, Any]] = None,
        loop_context: Optional[LoopContext] = None,
        auto_feedback: bool = True
    ) -> Tuple[EmotionInput, Dict[str, Any], ExternalFeedback, LoopResult]:
        """
        완전한 감정-판단-반응 루프 처리
        
        Args:
            emotion (str): 감정
            intensity (float): 감정 강도
            context (Dict, optional): 감정 컨텍스트
            loop_context (LoopContext, optional): 루프 컨텍스트
            auto_feedback (bool): 자동 피드백 생성 여부
        
        Returns:
            Tuple: (감정입력, 의사결정, 피드백, 루프결과)
        """
        from duri_core.core.decision import create_decision  # ✅ 지연 import로 순환 참조 차단

        # 1. 감정 입력 기록
        emotion_input = self.emotion_recorder.record_emotion_input(
            emotion=emotion,
            intensity=intensity,
            context=context,
            source=loop_context.environment if loop_context else None,
            session_id=loop_context.session_id if loop_context else None
        )
        
        # 2. Core에게 의사결정 요청
        decision = create_decision(
            emotion=emotion,
            evolution_log_path=self.evolution_log_path,
            stats_path=self.stats_path
        )
        
        # 3. 의사결정 기록
        decision_record = self.emotion_recorder.record_decision(
            emotion_input=emotion_input,
            decision=decision
        )
        
        # 4. 피드백 수집
        if auto_feedback:
            feedback = self.feedback_collector.collect_automatic_feedback(
                loop_id=decision_record.loop_id,
                decision=decision,
                emotion=emotion
            )
        else:
            # 수동 피드백을 위해 대기 (실제 구현에서는 외부 시스템과 연동)
            feedback = self._wait_for_external_feedback(decision_record.loop_id)
        
        # 5. 완전한 루프 결과 생성
        loop_result = self.feedback_collector.create_complete_loop(
            emotion_input=emotion_input.__dict__,
            decision=decision,
            feedback=feedback
        )
        
        # 6. Core 통계 업데이트
        self._update_core_statistics(emotion, decision, feedback)
        
        logger.info(f"완전한 루프 처리 완료: {decision_record.loop_id}")
        return emotion_input, decision, feedback, loop_result
    
    def get_learning_data(
        self,
        emotion: Optional[str] = None,
        action: Optional[str] = None,
        min_success_rate: float = 0.0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Core 학습용 데이터 조회
        
        Args:
            emotion (str, optional): 특정 감정 필터링
            action (str, optional): 특정 액션 필터링
            min_success_rate (float): 최소 성공률 필터링
            limit (int): 조회할 최대 개수
        
        Returns:
            List[Dict]: 학습 데이터 목록
        """
        loop_results = self.feedback_collector.get_loop_results(
            emotion=emotion,
            action=action,
            limit=limit
        )
        
        learning_data = []
        for result in loop_results:
            if result.success_rate >= min_success_rate:
                learning_data.append({
                    'emotion': result.emotion_input['emotion'],
                    'intensity': result.emotion_input['intensity'],
                    'action': result.decision['action'],
                    'confidence': result.decision['confidence'],
                    'success_rate': result.success_rate,
                    'feedback_type': result.feedback.feedback_type.value,
                    'loop_duration': result.loop_duration,
                    'timestamp': result.emotion_input['timestamp']
                })
        
        return learning_data
    
    def get_emotion_action_statistics(self) -> Dict[str, Any]:
        """
        감정-액션 조합별 통계 조회
        
        Returns:
            Dict: 감정-액션 통계
        """
        loop_results = self.feedback_collector.get_loop_results(limit=1000)
        
        stats = {}
        for result in loop_results:
            emotion = result.emotion_input['emotion']
            action = result.decision['action']
            key = f"{emotion}_{action}"
            
            if key not in stats:
                stats[key] = {
                    'total': 0,
                    'success': 0,
                    'fail': 0,
                    'avg_success_rate': 0.0,
                    'avg_confidence': 0.0,
                    'avg_duration': 0.0
                }
            
            stats[key]['total'] += 1
            if result.success_rate >= 0.7:  # 성공 기준
                stats[key]['success'] += 1
            else:
                stats[key]['fail'] += 1
            
            # 평균값 업데이트
            current = stats[key]
            current['avg_success_rate'] = (
                (current['avg_success_rate'] * (current['total'] - 1) + result.success_rate) 
                / current['total']
            )
            current['avg_confidence'] = (
                (current['avg_confidence'] * (current['total'] - 1) + result.decision['confidence']) 
                / current['total']
            )
            current['avg_duration'] = (
                (current['avg_duration'] * (current['total'] - 1) + result.loop_duration) 
                / current['total']
            )
        
        return stats
    
    def get_performance_insights(self) -> Dict[str, Any]:
        """
        성능 인사이트 조회
        
        Returns:
            Dict: 성능 인사이트
        """
        loop_results = self.feedback_collector.get_loop_results(limit=1000)
        
        if not loop_results:
            return {}
        
        # 전체 통계
        total_loops = len(loop_results)
        avg_success_rate = sum(r.success_rate for r in loop_results) / total_loops
        avg_duration = sum(r.loop_duration for r in loop_results) / total_loops
        
        # 감정별 성능
        emotion_performance = {}
        for result in loop_results:
            emotion = result.emotion_input['emotion']
            if emotion not in emotion_performance:
                emotion_performance[emotion] = {
                    'count': 0,
                    'total_success_rate': 0.0,
                    'total_duration': 0.0
                }
            
            perf = emotion_performance[emotion]
            perf['count'] += 1
            perf['total_success_rate'] += result.success_rate
            perf['total_duration'] += result.loop_duration
        
        # 평균 계산
        for emotion in emotion_performance:
            perf = emotion_performance[emotion]
            perf['avg_success_rate'] = perf['total_success_rate'] / perf['count']
            perf['avg_duration'] = perf['total_duration'] / perf['count']
            del perf['total_success_rate']
            del perf['total_duration']
        
        # 액션별 성능
        action_performance = {}
        for result in loop_results:
            action = result.decision['action']
            if action not in action_performance:
                action_performance[action] = {
                    'count': 0,
                    'total_success_rate': 0.0,
                    'total_confidence': 0.0
                }
            
            perf = action_performance[action]
            perf['count'] += 1
            perf['total_success_rate'] += result.success_rate
            perf['total_confidence'] += result.decision['confidence']
        
        # 평균 계산
        for action in action_performance:
            perf = action_performance[action]
            perf['avg_success_rate'] = perf['total_success_rate'] / perf['count']
            perf['avg_confidence'] = perf['total_confidence'] / perf['count']
            del perf['total_success_rate']
            del perf['total_confidence']
        
        return {
            'overall': {
                'total_loops': total_loops,
                'avg_success_rate': avg_success_rate,
                'avg_duration': avg_duration
            },
            'emotion_performance': emotion_performance,
            'action_performance': action_performance
        }
    
    def export_training_data(self, output_path: str) -> bool:
        """
        Core 학습용 데이터 내보내기
        
        Args:
            output_path (str): 출력 파일 경로
        
        Returns:
            bool: 내보내기 성공 여부
        """
        try:
            learning_data = self.get_learning_data(limit=10000)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(learning_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"학습 데이터 내보내기 완료: {output_path} ({len(learning_data)}개)")
            return True
            
        except Exception as e:
            logger.error(f"학습 데이터 내보내기 실패: {e}")
            return False
    
    def _initialize_core_data(self):
        """Core 데이터 초기화"""
        # 진화 로그 초기화
        if not os.path.exists(self.evolution_log_path):
            with open(self.evolution_log_path, 'w') as f:
                json.dump([], f)
        
        # 액션 통계 초기화
        if not os.path.exists(self.stats_path):
            initial_stats = {
                "emotions": {},
                "actions": {},
                "emotion_action_pairs": {},
                "last_updated": datetime.now().isoformat()
            }
            with open(self.stats_path, 'w') as f:
                json.dump(initial_stats, f, indent=2)
    
    def _wait_for_external_feedback(self, loop_id: str) -> ExternalFeedback:
        """
        외부 피드백 대기 (실제 구현에서는 외부 시스템과 연동)
        
        Args:
            loop_id (str): 루프 ID
        
        Returns:
            ExternalFeedback: 외부 피드백
        """
        # 실제 구현에서는 외부 시스템에서 피드백을 받아야 함
        # 현재는 기본 피드백 반환
        return self.feedback_collector.collect_feedback(
            loop_id=loop_id,
            feedback_type=FeedbackType.NEUTRAL,
            feedback_score=0.5,
            feedback_text="기본 피드백 (외부 시스템 연동 필요)",
            source="external"
        )
    
    def _update_core_statistics(
        self, 
        emotion: str, 
        decision: Dict[str, Any], 
        feedback: ExternalFeedback
    ):
        """Core 통계 업데이트"""
        try:
            action = decision.get('action', 'unknown')
            result = 'success' if feedback.feedback_score >= 0.7 else 'fail'
            
            # Core 통계 업데이트
            update_action_stats(
                emotion=emotion,
                action=action,
                result=result,
                stats_path=self.stats_path
            )
            
            # 진화 로그 업데이트
            evolution_entry = {
                "emotion": emotion,
                "decision": decision,
                "result": result,
                "feedback_score": feedback.feedback_score,
                "timestamp": datetime.now().isoformat()
            }
            
            # 기존 로그 읽기
            try:
                with open(self.evolution_log_path, 'r') as f:
                    evolution_log = json.load(f)
            except:
                evolution_log = []
            
            # 새 엔트리 추가
            evolution_log.append(evolution_entry)
            
            # 로그 저장 (최근 1000개만 유지)
            if len(evolution_log) > 1000:
                evolution_log = evolution_log[-1000:]
            
            with open(self.evolution_log_path, 'w') as f:
                json.dump(evolution_log, f, indent=2)
            
            logger.info(f"Core 통계 업데이트: {emotion} -> {action} ({result})")
            
        except Exception as e:
            logger.error(f"Core 통계 업데이트 실패: {e}")
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """전체 시스템 통계 조회"""
        emotion_stats = self.emotion_recorder.get_statistics()
        feedback_stats = self.feedback_collector.get_statistics()
        performance_insights = self.get_performance_insights()
        
        return {
            'emotion_recorder': emotion_stats,
            'feedback_collector': feedback_stats,
            'performance_insights': performance_insights,
            'total_loops': feedback_stats.get('total_loops', 0),
            'average_success_rate': feedback_stats.get('average_feedback_score', 0.0)
        } 
