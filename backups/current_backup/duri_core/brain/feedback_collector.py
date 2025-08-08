#!/usr/bin/env python3
"""
Feedback Collector - 외부 반응 수집 시스템

Core가 내린 판단 이후 외부 반응(결과, 피드백)을 수집하여 
감정-판단-반응 루프를 완성합니다.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from duri_common.logger import get_logger

logger = get_logger("duri_brain.feedback_collector")


class FeedbackType(Enum):
    """피드백 타입"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"


@dataclass
class ExternalFeedback:
    """외부 피드백 데이터 구조"""
    loop_id: str
    feedback_type: FeedbackType
    feedback_score: float  # 0.0 ~ 1.0
    feedback_text: Optional[str] = None
    timestamp: Optional[str] = None
    source: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class LoopResult:
    """완전한 루프 결과 데이터 구조"""
    loop_id: str
    emotion_input: Dict[str, Any]
    decision: Dict[str, Any]
    feedback: ExternalFeedback
    loop_duration: float  # 초 단위
    success_rate: float  # 0.0 ~ 1.0


class FeedbackCollector:
    """외부 피드백 수집기"""
    
    def __init__(self, data_dir: str = "brain_data"):
        """
        FeedbackCollector 초기화
        
        Args:
            data_dir (str): 데이터 저장 디렉토리
        """
        self.data_dir = data_dir
        self.feedback_dir = os.path.join(data_dir, "feedback")
        self.loops_dir = os.path.join(data_dir, "loops")
        
        # 디렉토리 생성
        os.makedirs(self.feedback_dir, exist_ok=True)
        os.makedirs(self.loops_dir, exist_ok=True)
        
        logger.info(f"FeedbackCollector 초기화 완료: {data_dir}")
    
    def collect_feedback(
        self,
        loop_id: str,
        feedback_type: Union[FeedbackType, str],
        feedback_score: float,
        feedback_text: Optional[str] = None,
        source: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ExternalFeedback:
        """
        외부 피드백 수집
        
        Args:
            loop_id (str): 루프 ID
            feedback_type (FeedbackType or str): 피드백 타입
            feedback_score (float): 피드백 점수 (0.0 ~ 1.0)
            feedback_text (str, optional): 피드백 텍스트
            source (str, optional): 피드백 소스
            context (Dict, optional): 컨텍스트 정보
            metadata (Dict, optional): 메타데이터
        
        Returns:
            ExternalFeedback: 수집된 피드백
        """
        # FeedbackType 변환
        if isinstance(feedback_type, str):
            try:
                feedback_type = FeedbackType(feedback_type.lower())
            except ValueError:
                feedback_type = FeedbackType.UNKNOWN
        
        # 점수 범위 검증
        feedback_score = max(0.0, min(1.0, feedback_score))
        
        timestamp = datetime.now().isoformat()
        
        feedback = ExternalFeedback(
            loop_id=loop_id,
            feedback_type=feedback_type,
            feedback_score=feedback_score,
            feedback_text=feedback_text,
            timestamp=timestamp,
            source=source,
            context=context or {},
            metadata=metadata or {}
        )
        
        # 피드백 저장
        self._save_feedback(feedback)
        
        logger.info(f"피드백 수집: {loop_id} - {feedback_type.value} (점수: {feedback_score:.2f})")
        return feedback
    
    def collect_automatic_feedback(
        self,
        loop_id: str,
        decision: Dict[str, Any],
        emotion: str,
        expected_outcome: Optional[str] = None
    ) -> ExternalFeedback:
        """
        자동 피드백 수집 (규칙 기반)
        
        Args:
            loop_id (str): 루프 ID
            decision (Dict): Core의 의사결정
            emotion (str): 감정
            expected_outcome (str, optional): 예상 결과
        
        Returns:
            ExternalFeedback: 자동 생성된 피드백
        """
        action = decision.get('action', 'unknown')
        confidence = decision.get('confidence', 0.5)
        
        # 감정-액션 조합에 따른 기본 성공률
        success_rates = {
            # 분노 관련 감정들
            'angry': {'wait': 0.7, 'reflect': 0.6, 'console': 0.5},
            'frustration': {'wait': 0.8, 'reflect': 0.7, 'console': 0.6},
            
            # 슬픔 관련 감정들
            'sad': {'console': 0.8, 'reflect': 0.7, 'wait': 0.6},
            'regret': {'console': 0.9, 'reflect': 0.8, 'wait': 0.5},
            'guilt': {'console': 0.9, 'reflect': 0.8, 'wait': 0.4},
            'shame': {'console': 0.8, 'reflect': 0.7, 'wait': 0.5},
            
            # 긍정적 감정들
            'happy': {'reflect': 0.9, 'act': 0.8, 'observe': 0.7},
            'grateful': {'reflect': 0.9, 'act': 0.8, 'observe': 0.7},
            'inspired': {'act': 0.9, 'reflect': 0.8, 'observe': 0.7},
            'proud': {'reflect': 0.9, 'act': 0.8, 'observe': 0.7},
            'relief': {'reflect': 0.8, 'observe': 0.7, 'act': 0.6},
            
            # 호기심 관련 감정들
            'curiosity': {'observe': 0.9, 'reflect': 0.8, 'act': 0.7},
            'awe': {'observe': 0.9, 'reflect': 0.8, 'act': 0.7},
        }
        
        # 기본 성공률 계산
        emotion_rates = success_rates.get(emotion.lower(), {})
        base_success_rate = emotion_rates.get(action, 0.6)
        
        # 신뢰도에 따른 조정
        adjusted_score = base_success_rate * confidence + 0.3 * (1 - confidence)
        
        # 피드백 타입 결정
        if adjusted_score >= 0.8:
            feedback_type = FeedbackType.SUCCESS
        elif adjusted_score >= 0.6:
            feedback_type = FeedbackType.PARTIAL
        elif adjusted_score >= 0.4:
            feedback_type = FeedbackType.NEUTRAL
        else:
            feedback_type = FeedbackType.FAILURE
        
        feedback_text = f"자동 피드백: {emotion} -> {action} (예상 성공률: {adjusted_score:.2f})"
        
        return self.collect_feedback(
            loop_id=loop_id,
            feedback_type=feedback_type,
            feedback_score=adjusted_score,
            feedback_text=feedback_text,
            source="automatic",
            context={
                "emotion": emotion,
                "action": action,
                "confidence": confidence,
                "expected_outcome": expected_outcome
            }
        )
    
    def create_complete_loop(
        self,
        emotion_input: Dict[str, Any],
        decision: Dict[str, Any],
        feedback: ExternalFeedback
    ) -> LoopResult:
        """
        완전한 루프 결과 생성
        
        Args:
            emotion_input (Dict): 감정 입력
            decision (Dict): 의사결정
            feedback (ExternalFeedback): 피드백
        
        Returns:
            LoopResult: 완전한 루프 결과
        """
        # 루프 지속 시간 계산
        emotion_timestamp = datetime.fromisoformat(emotion_input['timestamp'])
        feedback_timestamp = datetime.fromisoformat(feedback.timestamp)
        loop_duration = (feedback_timestamp - emotion_timestamp).total_seconds()
        
        # 성공률 계산
        success_rate = feedback.feedback_score
        
        loop_result = LoopResult(
            loop_id=feedback.loop_id,
            emotion_input=emotion_input,
            decision=decision,
            feedback=feedback,
            loop_duration=loop_duration,
            success_rate=success_rate
        )
        
        # 루프 결과 저장
        self._save_loop_result(loop_result)
        
        logger.info(f"완전한 루프 생성: {feedback.loop_id} (성공률: {success_rate:.2f})")
        return loop_result
    
    def get_feedback_history(
        self,
        loop_id: Optional[str] = None,
        feedback_type: Optional[FeedbackType] = None,
        limit: int = 100
    ) -> List[ExternalFeedback]:
        """
        피드백 히스토리 조회
        
        Args:
            loop_id (str, optional): 특정 루프 ID 필터링
            feedback_type (FeedbackType, optional): 특정 피드백 타입 필터링
            limit (int): 조회할 최대 개수
        
        Returns:
            List[ExternalFeedback]: 피드백 히스토리
        """
        history = []
        
        try:
            # 모든 피드백 파일 읽기
            for filename in os.listdir(self.feedback_dir):
                if not filename.endswith('.json'):
                    continue
                
                filepath = os.path.join(self.feedback_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # FeedbackType 변환
                    feedback_type_str = data['feedback_type']
                    try:
                        data['feedback_type'] = FeedbackType(feedback_type_str)
                    except ValueError:
                        data['feedback_type'] = FeedbackType.UNKNOWN
                    
                    feedback = ExternalFeedback(**data)
                    
                    # 필터링
                    if loop_id and feedback.loop_id != loop_id:
                        continue
                    if feedback_type and feedback.feedback_type != feedback_type:
                        continue
                    
                    history.append(feedback)
            
            # 시간순 정렬 (최신순)
            history.sort(key=lambda x: x.timestamp or "", reverse=True)
            
            # 개수 제한
            return history[:limit]
            
        except Exception as e:
            logger.error(f"피드백 히스토리 조회 실패: {e}")
            return []
    
    def get_loop_results(
        self,
        emotion: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[LoopResult]:
        """
        루프 결과 조회
        
        Args:
            emotion (str, optional): 특정 감정 필터링
            action (str, optional): 특정 액션 필터링
            limit (int): 조회할 최대 개수
        
        Returns:
            List[LoopResult]: 루프 결과 목록
        """
        results = []
        
        try:
            # 모든 루프 결과 파일 읽기
            for filename in os.listdir(self.loops_dir):
                if not filename.endswith('.json'):
                    continue
                
                filepath = os.path.join(self.loops_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # FeedbackType 변환
                    feedback_data = data['feedback']
                    feedback_type_str = feedback_data['feedback_type']
                    try:
                        feedback_data['feedback_type'] = FeedbackType(feedback_type_str)
                    except ValueError:
                        feedback_data['feedback_type'] = FeedbackType.UNKNOWN
                    
                    feedback = ExternalFeedback(**feedback_data)
                    
                    # LoopResult 객체 생성
                    loop_result = LoopResult(
                        loop_id=data['loop_id'],
                        emotion_input=data['emotion_input'],
                        decision=data['decision'],
                        feedback=feedback,
                        loop_duration=data['loop_duration'],
                        success_rate=data['success_rate']
                    )
                    
                    # 필터링
                    if emotion and loop_result.emotion_input.get('emotion') != emotion:
                        continue
                    if action and loop_result.decision.get('action') != action:
                        continue
                    
                    results.append(loop_result)
            
            # 성공률순 정렬 (높은 순)
            results.sort(key=lambda x: x.success_rate, reverse=True)
            
            # 개수 제한
            return results[:limit]
            
        except Exception as e:
            logger.error(f"루프 결과 조회 실패: {e}")
            return []
    
    def _save_feedback(self, feedback: ExternalFeedback):
        """피드백을 파일로 저장"""
        try:
            filename = f"feedback_{feedback.loop_id}.json"
            filepath = os.path.join(self.feedback_dir, filename)
            
            data = asdict(feedback)
            data['feedback_type'] = feedback.feedback_type.value
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"피드백 저장 실패: {e}")
    
    def _save_loop_result(self, loop_result: LoopResult):
        """루프 결과를 파일로 저장"""
        try:
            filename = f"loop_{loop_result.loop_id}.json"
            filepath = os.path.join(self.loops_dir, filename)
            
            data = {
                'loop_id': loop_result.loop_id,
                'emotion_input': loop_result.emotion_input,
                'decision': loop_result.decision,
                'feedback': asdict(loop_result.feedback),
                'loop_duration': loop_result.loop_duration,
                'success_rate': loop_result.success_rate
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"루프 결과 저장 실패: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """피드백 통계 조회"""
        try:
            feedback_count = len([f for f in os.listdir(self.feedback_dir) if f.endswith('.json')])
            loop_count = len([f for f in os.listdir(self.loops_dir) if f.endswith('.json')])
            
            # 피드백 타입별 통계
            type_stats = {feedback_type.value: 0 for feedback_type in FeedbackType}
            total_score = 0.0
            score_count = 0
            
            for feedback in self.get_feedback_history():
                type_stats[feedback.feedback_type.value] += 1
                total_score += feedback.feedback_score
                score_count += 1
            
            avg_score = total_score / score_count if score_count > 0 else 0.0
            
            return {
                'total_feedback': feedback_count,
                'total_loops': loop_count,
                'feedback_type_statistics': type_stats,
                'average_feedback_score': avg_score
            }
            
        except Exception as e:
            logger.error(f"피드백 통계 조회 실패: {e}")
            return {} 