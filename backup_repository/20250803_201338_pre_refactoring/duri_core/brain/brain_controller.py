#!/usr/bin/env python3
"""
Brain Controller - DuRi Brain 시스템 제어기

Brain 시스템의 전체적인 제어를 담당하며,
감정-판단-반응 루프의 완전한 생명주기를 관리합니다.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from duri_common.logger import get_logger
from .emotion_recorder import EmotionRecorder, EmotionInput, DecisionRecord
from .feedback_collector import FeedbackCollector, ExternalFeedback, LoopResult, FeedbackType
from .loop_manager import LoopManager, LoopContext

logger = get_logger("duri_brain.brain_controller")


@dataclass
class BrainConfig:
    """Brain 시스템 설정"""
    data_dir: str = "brain_data"
    auto_feedback: bool = True
    enable_learning: bool = True
    max_loops_per_session: int = 1000
    backup_interval: int = 100  # 루프당 백업 간격


class BrainController:
    """DuRi Brain 시스템 제어기"""
    
    def __init__(self, config: Optional[BrainConfig] = None):
        """
        BrainController 초기화
        
        Args:
            config (BrainConfig, optional): Brain 설정
        """
        self.config = config or BrainConfig()
        self.loop_manager = LoopManager(self.config.data_dir)
        self.emotion_recorder = self.loop_manager.emotion_recorder
        self.feedback_collector = self.loop_manager.feedback_collector
        
        # 세션 관리
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.loop_counter = 0
        
        logger.info(f"BrainController 초기화 완료")
    
    def start_session(
        self, 
        session_id: str, 
        user_id: Optional[str] = None,
        environment: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        새로운 세션 시작
        
        Args:
            session_id (str): 세션 ID
            user_id (str, optional): 사용자 ID
            environment (str, optional): 환경 정보
            metadata (Dict, optional): 메타데이터
        
        Returns:
            bool: 세션 시작 성공 여부
        """
        if session_id in self.active_sessions:
            logger.warning(f"세션이 이미 존재합니다: {session_id}")
            return False
        
        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'environment': environment,
            'metadata': metadata or {},
            'start_time': datetime.now().isoformat(),
            'loop_count': 0,
            'last_activity': datetime.now().isoformat()
        }
        
        self.active_sessions[session_id] = session_data
        logger.info(f"새 세션 시작: {session_id}")
        return True
    
    def end_session(self, session_id: str) -> bool:
        """
        세션 종료
        
        Args:
            session_id (str): 세션 ID
        
        Returns:
            bool: 세션 종료 성공 여부
        """
        if session_id not in self.active_sessions:
            logger.warning(f"세션이 존재하지 않습니다: {session_id}")
            return False
        
        session_data = self.active_sessions[session_id]
        session_data['end_time'] = datetime.now().isoformat()
        session_data['total_loops'] = session_data['loop_count']
        
        # 세션 통계 저장
        self._save_session_statistics(session_data)
        
        del self.active_sessions[session_id]
        logger.info(f"세션 종료: {session_id} (총 {session_data['total_loops']}개 루프)")
        return True
    
    def process_emotion(
        self,
        emotion: str,
        intensity: float,
        session_id: str,
        context: Optional[Dict[str, Any]] = None,
        auto_feedback: Optional[bool] = None
    ) -> Tuple[EmotionInput, Dict[str, Any], ExternalFeedback, LoopResult]:
        """
        감정 처리 (완전한 루프)
        
        Args:
            emotion (str): 감정
            intensity (float): 감정 강도
            session_id (str): 세션 ID
            context (Dict, optional): 컨텍스트
            auto_feedback (bool, optional): 자동 피드백 여부
        
        Returns:
            Tuple: (감정입력, 의사결정, 피드백, 루프결과)
        """
        # 세션 검증
        if session_id not in self.active_sessions:
            raise ValueError(f"활성 세션이 아닙니다: {session_id}")
        
        # 세션 제한 확인
        session_data = self.active_sessions[session_id]
        if session_data['loop_count'] >= self.config.max_loops_per_session:
            raise ValueError(f"세션 루프 제한에 도달했습니다: {session_id}")
        
        # 루프 컨텍스트 생성
        loop_context = LoopContext(
            session_id=session_id,
            user_id=session_data.get('user_id'),
            environment=session_data.get('environment'),
            metadata=session_data.get('metadata')
        )
        
        # 자동 피드백 설정
        if auto_feedback is None:
            auto_feedback = self.config.auto_feedback
        
        # 루프 처리
        result = self.loop_manager.process_emotion_loop(
            emotion=emotion,
            intensity=intensity,
            context=context,
            loop_context=loop_context,
            auto_feedback=auto_feedback
        )
        
        # 세션 업데이트
        session_data['loop_count'] += 1
        session_data['last_activity'] = datetime.now().isoformat()
        self.loop_counter += 1
        
        # 백업 체크
        if self.loop_counter % self.config.backup_interval == 0:
            self._backup_system_data()
        
        logger.info(f"감정 처리 완료: {session_id} - {emotion} (루프 #{session_data['loop_count']})")
        return result
    
    def collect_external_feedback(
        self,
        loop_id: str,
        feedback_type: str,
        feedback_score: float,
        feedback_text: Optional[str] = None,
        source: Optional[str] = None
    ) -> ExternalFeedback:
        """
        외부 피드백 수집
        
        Args:
            loop_id (str): 루프 ID
            feedback_type (str): 피드백 타입
            feedback_score (float): 피드백 점수
            feedback_text (str, optional): 피드백 텍스트
            source (str, optional): 피드백 소스
        
        Returns:
            ExternalFeedback: 수집된 피드백
        """
        feedback = self.feedback_collector.collect_feedback(
            loop_id=loop_id,
            feedback_type=feedback_type,
            feedback_score=feedback_score,
            feedback_text=feedback_text,
            source=source or "external"
        )
        
        logger.info(f"외부 피드백 수집: {loop_id} - {feedback_type} (점수: {feedback_score:.2f})")
        return feedback
    
    def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """
        세션 통계 조회
        
        Args:
            session_id (str): 세션 ID
        
        Returns:
            Dict: 세션 통계
        """
        if session_id not in self.active_sessions:
            return {}
        
        session_data = self.active_sessions[session_id]
        
        # 세션의 루프 결과 조회
        loop_results = self.feedback_collector.get_loop_results(limit=1000)
        session_loops = [
            result for result in loop_results 
            if result.emotion_input.get('session_id') == session_id
        ]
        
        # 통계 계산
        total_loops = len(session_loops)
        if total_loops == 0:
            return {
                'session_id': session_id,
                'total_loops': 0,
                'avg_success_rate': 0.0,
                'emotion_distribution': {},
                'action_distribution': {}
            }
        
        avg_success_rate = sum(r.success_rate for r in session_loops) / total_loops
        
        # 감정 분포
        emotion_distribution = {}
        for result in session_loops:
            emotion = result.emotion_input['emotion']
            emotion_distribution[emotion] = emotion_distribution.get(emotion, 0) + 1
        
        # 액션 분포
        action_distribution = {}
        for result in session_loops:
            action = result.decision['action']
            action_distribution[action] = action_distribution.get(action, 0) + 1
        
        return {
            'session_id': session_id,
            'user_id': session_data.get('user_id'),
            'environment': session_data.get('environment'),
            'start_time': session_data.get('start_time'),
            'last_activity': session_data.get('last_activity'),
            'total_loops': total_loops,
            'avg_success_rate': avg_success_rate,
            'emotion_distribution': emotion_distribution,
            'action_distribution': action_distribution
        }
    
    def get_system_overview(self) -> Dict[str, Any]:
        """
        시스템 전체 개요 조회
        
        Returns:
            Dict: 시스템 개요
        """
        # 기본 통계
        system_stats = self.loop_manager.get_system_statistics()
        
        # 활성 세션 정보
        active_sessions = {}
        for session_id, session_data in self.active_sessions.items():
            active_sessions[session_id] = {
                'user_id': session_data.get('user_id'),
                'environment': session_data.get('environment'),
                'loop_count': session_data['loop_count'],
                'start_time': session_data.get('start_time'),
                'last_activity': session_data.get('last_activity')
            }
        
        # 학습 데이터 요약
        learning_data = self.loop_manager.get_learning_data(limit=1000)
        learning_summary = {
            'total_records': len(learning_data),
            'avg_success_rate': sum(d['success_rate'] for d in learning_data) / len(learning_data) if learning_data else 0.0,
            'emotion_count': len(set(d['emotion'] for d in learning_data)),
            'action_count': len(set(d['action'] for d in learning_data))
        }
        
        return {
            'system_statistics': system_stats,
            'active_sessions': active_sessions,
            'learning_summary': learning_summary,
            'total_loops_processed': self.loop_counter,
            'config': {
                'auto_feedback': self.config.auto_feedback,
                'enable_learning': self.config.enable_learning,
                'max_loops_per_session': self.config.max_loops_per_session
            }
        }
    
    def export_learning_data(self, output_path: str, session_id: Optional[str] = None) -> bool:
        """
        학습 데이터 내보내기
        
        Args:
            output_path (str): 출력 파일 경로
            session_id (str, optional): 특정 세션만 내보내기
        
        Returns:
            bool: 내보내기 성공 여부
        """
        try:
            if session_id:
                # 특정 세션의 루프 결과만 조회
                loop_results = self.feedback_collector.get_loop_results(limit=10000)
                session_loops = [
                    result for result in loop_results 
                    if result.emotion_input.get('session_id') == session_id
                ]
                
                learning_data = []
                for result in session_loops:
                    learning_data.append({
                        'emotion': result.emotion_input['emotion'],
                        'intensity': result.emotion_input['intensity'],
                        'action': result.decision['action'],
                        'confidence': result.decision['confidence'],
                        'success_rate': result.success_rate,
                        'feedback_type': result.feedback.feedback_type.value,
                        'loop_duration': result.loop_duration,
                        'timestamp': result.emotion_input['timestamp'],
                        'session_id': session_id
                    })
            else:
                # 전체 학습 데이터
                learning_data = self.loop_manager.get_learning_data(limit=10000)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(learning_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"학습 데이터 내보내기 완료: {output_path} ({len(learning_data)}개)")
            return True
            
        except Exception as e:
            logger.error(f"학습 데이터 내보내기 실패: {e}")
            return False
    
    def backup_system(self, backup_dir: str) -> bool:
        """
        시스템 백업
        
        Args:
            backup_dir (str): 백업 디렉토리
        
        Returns:
            bool: 백업 성공 여부
        """
        try:
            import shutil
            from datetime import datetime
            
            # 백업 디렉토리 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"brain_backup_{timestamp}")
            os.makedirs(backup_path, exist_ok=True)
            
            # 데이터 디렉토리 복사
            if os.path.exists(self.config.data_dir):
                shutil.copytree(self.config.data_dir, os.path.join(backup_path, "data"))
            
            # 시스템 상태 저장
            system_state = {
                'active_sessions': self.active_sessions,
                'loop_counter': self.loop_counter,
                'config': self.config.__dict__,
                'backup_timestamp': datetime.now().isoformat()
            }
            
            with open(os.path.join(backup_path, "system_state.json"), 'w') as f:
                json.dump(system_state, f, indent=2)
            
            logger.info(f"시스템 백업 완료: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"시스템 백업 실패: {e}")
            return False
    
    def _save_session_statistics(self, session_data: Dict[str, Any]):
        """세션 통계 저장"""
        try:
            sessions_dir = os.path.join(self.config.data_dir, "sessions")
            os.makedirs(sessions_dir, exist_ok=True)
            
            filename = f"session_{session_data['session_id']}.json"
            filepath = os.path.join(sessions_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"세션 통계 저장 실패: {e}")
    
    def _backup_system_data(self):
        """시스템 데이터 백업"""
        try:
            backup_dir = os.path.join(self.config.data_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"auto_backup_{timestamp}")
            
            self.backup_system(backup_path)
            
        except Exception as e:
            logger.error(f"자동 백업 실패: {e}")
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> bool:
        """
        오래된 데이터 정리
        
        Args:
            days_to_keep (int): 보관할 일수
        
        Returns:
            bool: 정리 성공 여부
        """
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # 오래된 감정 입력 파일 정리
            emotions_dir = os.path.join(self.config.data_dir, "emotions")
            if os.path.exists(emotions_dir):
                for filename in os.listdir(emotions_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(emotions_dir, filename)
                        file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                        if file_time < cutoff_date:
                            os.remove(filepath)
            
            # 오래된 피드백 파일 정리
            feedback_dir = os.path.join(self.config.data_dir, "feedback")
            if os.path.exists(feedback_dir):
                for filename in os.listdir(feedback_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(feedback_dir, filename)
                        file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                        if file_time < cutoff_date:
                            os.remove(filepath)
            
            logger.info(f"오래된 데이터 정리 완료 (보관일수: {days_to_keep}일)")
            return True
            
        except Exception as e:
            logger.error(f"데이터 정리 실패: {e}")
            return False 