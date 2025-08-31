#!/usr/bin/env python3
"""
Action Executor - 행동 실행 시스템

Core의 의사결정에 따라 실제 행동을 실행하고 결과를 반환합니다.
"""

import time
import random
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from duri_common.logger import get_logger

logger = get_logger("duri_evolution.action_executor")


class ActionType(Enum):
    """행동 타입"""
    REFLECT = "reflect"
    WAIT = "wait"
    CONSOLE = "console"
    ACT = "act"
    OBSERVE = "observe"


@dataclass
class ExecutionContext:
    """실행 컨텍스트"""
    emotion: str
    intensity: float
    confidence: float
    environment: Optional[str] = None
    user_context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None


@dataclass
class ExecutionResult:
    """실행 결과"""
    action: str
    success: bool
    execution_time: float
    result_score: float  # 0.0 ~ 1.0
    feedback_text: str
    metadata: Dict[str, Any]
    timestamp: str


class ActionExecutor:
    """
    감정과 행동을 받아 실행 결과를 반환하는 실행기
    """
    def execute(self, emotion: str, action: str) -> dict:
        """
        감정과 행동을 받아 70% 확률로 성공 여부를 판단
        Args:
            emotion (str): 감정
            action (str): 행동
        Returns:
            dict: {'success': bool, 'details': str}
        """
        success = random.random() < 0.7
        details = (
            f"Action '{action}' for emotion '{emotion}' was successful."
            if success else
            f"Action '{action}' for emotion '{emotion}' failed."
        )
        return {'success': success, 'details': details}

    def __init__(self):
        """ActionExecutor 초기화"""
        self.execution_history = []
        logger.info("ActionExecutor 초기화 완료")
    
    def execute_action(
        self, 
        action: str, 
        context: ExecutionContext
    ) -> ExecutionResult:
        """
        행동 실행
        
        Args:
            action (str): 실행할 행동
            context (ExecutionContext): 실행 컨텍스트
        
        Returns:
            ExecutionResult: 실행 결과
        """
        start_time = time.time()
        
        try:
            # 행동 타입 검증
            action_type = self._validate_action(action)
            
            # 행동 실행
            if action_type == ActionType.REFLECT:
                result = self._execute_reflect(context)
            elif action_type == ActionType.WAIT:
                result = self._execute_wait(context)
            elif action_type == ActionType.CONSOLE:
                result = self._execute_console(context)
            elif action_type == ActionType.ACT:
                result = self._execute_act(context)
            elif action_type == ActionType.OBSERVE:
                result = self._execute_observe(context)
            else:
                result = self._execute_default(context)
            
            execution_time = time.time() - start_time
            
            # 실행 결과 생성
            execution_result = ExecutionResult(
                action=action,
                success=result['success'],
                execution_time=execution_time,
                result_score=result['score'],
                feedback_text=result['feedback'],
                metadata=result['metadata'],
                timestamp=datetime.now().isoformat()
            )
            
            # 실행 히스토리 저장
            self.execution_history.append(execution_result)
            
            logger.info(f"행동 실행 완료: {action} - 성공: {result['success']}, 점수: {result['score']:.2f}")
            return execution_result
            
        except Exception as e:
            logger.error(f"행동 실행 실패: {action} - {e}")
            execution_time = time.time() - start_time
            
            # 실패 결과 반환
            return ExecutionResult(
                action=action,
                success=False,
                execution_time=execution_time,
                result_score=0.0,
                feedback_text=f"실행 실패: {str(e)}",
                metadata={"error": str(e)},
                timestamp=datetime.now().isoformat()
            )
    
    def _validate_action(self, action: str) -> ActionType:
        """행동 타입 검증"""
        try:
            return ActionType(action.lower())
        except ValueError:
            logger.warning(f"알 수 없는 행동 타입: {action}, 기본값 사용")
            return ActionType.REFLECT
    
    def _execute_reflect(self, context: ExecutionContext) -> Dict[str, Any]:
        """성찰 행동 실행"""
        # 감정 강도와 신뢰도에 따른 성공률 계산
        base_success_rate = 0.8
        emotion_bonus = {
            'happy': 0.1, 'grateful': 0.1, 'inspired': 0.1,
            'sad': -0.05, 'angry': -0.1, 'frustration': -0.1
        }
        
        bonus = emotion_bonus.get(context.emotion.lower(), 0.0)
        success_rate = min(1.0, base_success_rate + bonus + context.confidence * 0.1)
        
        # 성공 여부 결정
        success = random.random() < success_rate
        
        if success:
            feedback = f"성찰이 효과적이었습니다. {context.emotion} 감정이 조화롭게 처리되었습니다."
            score = success_rate
        else:
            feedback = f"성찰이 충분하지 않았습니다. {context.emotion} 감정이 여전히 남아있습니다."
            score = success_rate * 0.5
        
        return {
            'success': success,
            'score': score,
            'feedback': feedback,
            'metadata': {
                'emotion': context.emotion,
                'intensity': context.intensity,
                'confidence': context.confidence,
                'success_rate': success_rate
            }
        }
    
    def _execute_wait(self, context: ExecutionContext) -> Dict[str, Any]:
        """대기 행동 실행"""
        # 분노 관련 감정에서 대기가 효과적
        anger_emotions = ['angry', 'frustration']
        base_success_rate = 0.6
        
        if context.emotion.lower() in anger_emotions:
            base_success_rate = 0.8
        
        # 강도가 높을수록 대기 효과 감소
        intensity_penalty = context.intensity * 0.2
        success_rate = max(0.3, base_success_rate - intensity_penalty)
        
        success = random.random() < success_rate
        
        if success:
            feedback = f"대기가 효과적이었습니다. {context.emotion} 감정이 진정되었습니다."
            score = success_rate
        else:
            feedback = f"대기가 충분하지 않았습니다. {context.emotion} 감정이 여전히 강합니다."
            score = success_rate * 0.4
        
        return {
            'success': success,
            'score': score,
            'feedback': feedback,
            'metadata': {
                'emotion': context.emotion,
                'intensity': context.intensity,
                'success_rate': success_rate,
                'wait_effective': context.emotion.lower() in anger_emotions
            }
        }
    
    def _execute_console(self, context: ExecutionContext) -> Dict[str, Any]:
        """위로 행동 실행"""
        # 슬픔 관련 감정에서 위로가 효과적
        sadness_emotions = ['sad', 'regret', 'guilt', 'shame']
        base_success_rate = 0.7
        
        if context.emotion.lower() in sadness_emotions:
            base_success_rate = 0.9
        
        # 신뢰도가 높을수록 위로 효과 증가
        confidence_bonus = context.confidence * 0.2
        success_rate = min(1.0, base_success_rate + confidence_bonus)
        
        success = random.random() < success_rate
        
        if success:
            feedback = f"위로가 효과적이었습니다. {context.emotion} 감정이 완화되었습니다."
            score = success_rate
        else:
            feedback = f"위로가 충분하지 않았습니다. {context.emotion} 감정이 여전히 깊습니다."
            score = success_rate * 0.6
        
        return {
            'success': success,
            'score': score,
            'feedback': feedback,
            'metadata': {
                'emotion': context.emotion,
                'intensity': context.intensity,
                'confidence': context.confidence,
                'success_rate': success_rate,
                'console_effective': context.emotion.lower() in sadness_emotions
            }
        }
    
    def _execute_act(self, context: ExecutionContext) -> Dict[str, Any]:
        """행동 행동 실행"""
        # 긍정적 감정에서 행동이 효과적
        positive_emotions = ['happy', 'inspired', 'proud']
        base_success_rate = 0.6
        
        if context.emotion.lower() in positive_emotions:
            base_success_rate = 0.8
        
        # 강도가 높을수록 행동 효과 증가
        intensity_bonus = context.intensity * 0.3
        success_rate = min(1.0, base_success_rate + intensity_bonus)
        
        success = random.random() < success_rate
        
        if success:
            feedback = f"행동이 효과적이었습니다. {context.emotion} 감정이 긍정적으로 활용되었습니다."
            score = success_rate
        else:
            feedback = f"행동이 적절하지 않았습니다. {context.emotion} 감정이 제대로 활용되지 않았습니다."
            score = success_rate * 0.5
        
        return {
            'success': success,
            'score': score,
            'feedback': feedback,
            'metadata': {
                'emotion': context.emotion,
                'intensity': context.intensity,
                'success_rate': success_rate,
                'act_effective': context.emotion.lower() in positive_emotions
            }
        }
    
    def _execute_observe(self, context: ExecutionContext) -> Dict[str, Any]:
        """관찰 행동 실행"""
        # 호기심 관련 감정에서 관찰이 효과적
        curiosity_emotions = ['curiosity', 'awe']
        base_success_rate = 0.8
        
        if context.emotion.lower() in curiosity_emotions:
            base_success_rate = 0.95
        
        # 신뢰도가 높을수록 관찰 효과 증가
        confidence_bonus = context.confidence * 0.15
        success_rate = min(1.0, base_success_rate + confidence_bonus)
        
        success = random.random() < success_rate
        
        if success:
            feedback = f"관찰이 효과적이었습니다. {context.emotion} 감정이 깊이 있게 이해되었습니다."
            score = success_rate
        else:
            feedback = f"관찰이 충분하지 않았습니다. {context.emotion} 감정이 제대로 파악되지 않았습니다."
            score = success_rate * 0.7
        
        return {
            'success': success,
            'score': score,
            'feedback': feedback,
            'metadata': {
                'emotion': context.emotion,
                'intensity': context.intensity,
                'confidence': context.confidence,
                'success_rate': success_rate,
                'observe_effective': context.emotion.lower() in curiosity_emotions
            }
        }
    
    def _execute_default(self, context: ExecutionContext) -> Dict[str, Any]:
        """기본 행동 실행"""
        base_success_rate = 0.5
        success_rate = min(1.0, base_success_rate + context.confidence * 0.1)
        
        success = random.random() < success_rate
        
        feedback = f"기본 행동이 실행되었습니다. {context.emotion} 감정에 대한 처리가 시도되었습니다."
        score = success_rate * 0.8 if success else success_rate * 0.3
        
        return {
            'success': success,
            'score': score,
            'feedback': feedback,
            'metadata': {
                'emotion': context.emotion,
                'intensity': context.intensity,
                'confidence': context.confidence,
                'success_rate': success_rate,
                'default_action': True
            }
        }
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """실행 통계 조회"""
        if not self.execution_history:
            return {}
        
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for result in self.execution_history if result.success)
        success_rate = successful_executions / total_executions
        
        # 행동별 통계
        action_stats = {}
        for result in self.execution_history:
            action = result.action
            if action not in action_stats:
                action_stats[action] = {
                    'total': 0,
                    'success': 0,
                    'avg_score': 0.0,
                    'avg_time': 0.0
                }
            
            stats = action_stats[action]
            stats['total'] += 1
            if result.success:
                stats['success'] += 1
            stats['avg_score'] += result.result_score
            stats['avg_time'] += result.execution_time
        
        # 평균 계산
        for action in action_stats:
            stats = action_stats[action]
            total = stats['total']
            stats['success_rate'] = stats['success'] / total
            stats['avg_score'] /= total
            stats['avg_time'] /= total
        
        return {
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'overall_success_rate': success_rate,
            'action_statistics': action_stats
        }
    
    def get_recent_executions(self, limit: int = 10) -> list:
        """최근 실행 결과 조회"""
        return self.execution_history[-limit:] if self.execution_history else [] 