#!/usr/bin/env python3
"""
Decision making utilities for DuRi emotion processing system
"""

import logging
logger = logging.getLogger("core_decision")

from duri_core.core.logging import get_last_result_for_emotion
from duri_core.core.stats import choose_best_action
from duri_common.logger import get_logger
from duri_common.config.emotion_labels import ALL_EMOTIONS, is_valid_emotion, get_all_emotions
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# ReinforcementEngine import
try:
    from brain.reinforcement_engine import ReinforcementEngine
    _reinforcement_engine_available = True
except Exception as e:
    logger.warning(f"ReinforcementEngine import 실패: {e}")
    _reinforcement_engine_available = False

# BiasDetector import
try:
    from duri_core.core.bias_detector import create_bias_detector, BiasDetector
    _bias_detector_available = True
except Exception as e:
    logger.warning(f"BiasDetector import 실패: {e}")
    _bias_detector_available = False

# ResultRecorder import
try:
    from evolution.result_recorder import ResultRecorder
    _result_recorder_available = True
except Exception as e:
    logger.warning(f"ResultRecorder import 실패: {e}")
    _result_recorder_available = False

logger2 = get_logger("duri_core.decision")


@dataclass
class CoreDecision:
    """Core 의사결정 결과"""
    action: str
    confidence: float
    method: str
    reason: str
    fallback: bool = False
    bias_flag: bool = False
    bias_details: Optional[Dict[str, Any]] = None
    adjusted_parameters: Optional[Dict[str, Any]] = None


class DecisionEngine:
    """의사결정 엔진"""
    
    def __init__(self):
        """DecisionEngine 초기화"""
        # ReinforcementEngine 초기화
        if _reinforcement_engine_available:
            try:
                self.reinforcement_engine = ReinforcementEngine()
                self.reinforcement_engine_available = True
                logger2.info("ReinforcementEngine 초기화 성공")
            except Exception as e:
                logger2.warning(f"ReinforcementEngine 초기화 실패: {e}")
                self.reinforcement_engine = None
                self.reinforcement_engine_available = False
        else:
            self.reinforcement_engine = None
            self.reinforcement_engine_available = False
        
        # BiasDetector 초기화
        if _bias_detector_available:
            try:
                self.bias_detector = create_bias_detector()
                self.bias_detector_available = True
                logger2.info("BiasDetector 초기화 성공")
            except Exception as e:
                logger2.warning(f"BiasDetector 초기화 실패: {e}")
                self.bias_detector = None
                self.bias_detector_available = False
        else:
            self.bias_detector = None
            self.bias_detector_available = False
        
        # ResultRecorder 초기화
        if _result_recorder_available:
            try:
                self.result_recorder = ResultRecorder()
                self.result_recorder_available = True
                logger2.info("ResultRecorder 초기화 성공")
            except Exception as e:
                logger2.warning(f"ResultRecorder 초기화 실패: {e}")
                self.result_recorder = None
                self.result_recorder_available = False
        else:
            self.result_recorder = None
            self.result_recorder_available = False
        
        # 편향 조정 파라미터
        self.bias_adjustment_params = {
            'epsilon_boost': 0.2,  # 편향 감지 시 ε값 증가
            'confidence_reduction': 0.1,  # 신뢰도 감소
            'exploration_boost': True  # 탐험 증가
        }
    
    def create_decision(self, emotion: str, evolution_log_path: str, stats_path: Optional[str] = None) -> CoreDecision:
        """
        감정에 기반한 의사결정 생성
        
        Args:
            emotion (str): 감정
            evolution_log_path (str): 진화 로그 경로
            stats_path (str, optional): 액션 통계 경로
        
        Returns:
            CoreDecision: 의사결정 결과
        """
        # 감정 유효성 검사 및 fallback 처리
        if not is_valid_emotion(emotion):
            logger2.warning(f"알 수 없는 감정: {emotion}, 기본 의사결정 사용")
            return CoreDecision(
                action="observe",
                confidence=0.5,
                method="fallback",
                reason=f"Unknown emotion: {emotion}",
                fallback=True
            )
        
        # 편향 감지 및 분석
        bias_flag, bias_details, adjusted_params = self._check_bias_and_adjust(emotion)
        
        # ReinforcementEngine 기반 판단 시도
        if self.reinforcement_engine_available and self.reinforcement_engine is not None:
            try:
                # 편향이 감지된 경우 ε값 조정 (scaffold)
                if bias_flag and adjusted_params:
                    self._apply_bias_adjustments(adjusted_params)
                
                action = self.reinforcement_engine.choose_action(emotion)
                if action:
                    logger2.info(f"ReinforcementEngine 기반 의사결정: {emotion} -> {action}")
                    return CoreDecision(
                        action=action,
                        confidence=0.9,
                        method="reinforcement_engine",
                        reason="ε-greedy policy",
                        fallback=False,
                        bias_flag=bias_flag,
                        bias_details=bias_details,
                        adjusted_parameters=adjusted_params
                    )
            except Exception as e:
                logger2.warning(f"ReinforcementEngine 판단 실패: {e}, fallback 사용")

        # 액션 통계가 있는 경우 통계 기반 의사결정 사용
        if stats_path:
            try:
                stats_decision = choose_best_action(emotion, stats_path)
                
                # 통계 기반 결과에 감정별 특별 규칙 적용
                final_decision = self._apply_emotion_rules(emotion, stats_decision)
                final_decision.method = "statistics_with_rules"
                final_decision.bias_flag = bias_flag
                final_decision.bias_details = bias_details
                final_decision.adjusted_parameters = adjusted_params
                
                return final_decision
                
            except Exception as e:
                logger2.warning(f"통계 기반 의사결정 실패: {e}, 기본 로직 사용")
        
        # 기본 의사결정 로직 (동적 감정 검사)
        last_result = get_last_result_for_emotion(emotion, evolution_log_path)
        emotion_lower = emotion.lower()
        
        # 분노 관련 감정들
        anger_related = ["angry", "frustration"]
        if emotion_lower in anger_related:
            if last_result == "fail":
                decision = CoreDecision(action="wait", confidence=0.6, method="rule_based", reason="anger_fail")
            else:
                decision = CoreDecision(action="reflect", confidence=0.95, method="rule_based", reason="anger_success")
        
        # 슬픔 관련 감정들
        elif emotion_lower in ["sad", "regret", "guilt", "shame"]:
            if last_result == "fail":
                decision = CoreDecision(action="console", confidence=0.7, method="rule_based", reason="sadness_fail")
            else:
                decision = CoreDecision(action="reflect", confidence=0.95, method="rule_based", reason="sadness_success")
        
        # 긍정적 감정들
        elif emotion_lower in ["happy", "grateful", "inspired", "proud", "relief"]:
            decision = CoreDecision(action="reflect", confidence=0.95, method="rule_based", reason="positive_emotion")
        
        # 호기심 관련 감정들
        elif emotion_lower in ["curious", "awe"]:
            decision = CoreDecision(action="observe", confidence=0.9, method="rule_based", reason="curiosity")
        
        # 기타 감정들 (기본값)
        else:
            decision = CoreDecision(action="reflect", confidence=0.95, method="rule_based", reason="default")

        # 편향 정보 추가
        decision.bias_flag = bias_flag
        decision.bias_details = bias_details
        decision.adjusted_parameters = adjusted_params
        
        logger2.info(f"기본 의사결정: {emotion} -> {decision.action} (신뢰도: {decision.confidence})")
        return decision
    
    def _check_bias_and_adjust(self, emotion: str) -> tuple[bool, Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        편향 감지 및 조정 파라미터 생성
        
        Args:
            emotion (str): 현재 감정
        
        Returns:
            tuple: (편향_감지_여부, 편향_상세정보, 조정_파라미터)
        """
        if not self.bias_detector_available or not self.bias_detector:
            logger2.debug("BiasDetector가 사용 불가능하여 편향 감지를 건너뜁니다.")
            return False, None, None
        
        try:
            # ResultRecorder에서 실제 히스토리 수집
            emotion_history = self._get_recent_emotion_history(emotion)
            action_history = self._get_recent_action_history()
            
            # 히스토리 데이터 검증
            if not emotion_history and not action_history:
                logger2.debug("히스토리 데이터가 부족하여 편향 감지를 건너뜁니다.")
                return False, None, None
            
            logger2.info(f"편향 감지 시작: 감정 히스토리 {len(emotion_history)}개, 행동 히스토리 {len(action_history)}개")
            
            # BiasDetector에 실제 히스토리 전달하여 편향 감지 실행
            detections = self.bias_detector.run_bias_detection(emotion_history, action_history)
            
            if detections:
                logger2.info(f"편향 감지 완료: {len(detections)}개 편향 발견")
                
                # 모든 편향을 로그에 기록
                for detection in detections:
                    logger2.info(f"편향 감지: {detection.bias_type.value} - {detection.severity} (신뢰도: {detection.confidence:.2f})")
                
                # 심각한 편향 필터링 (high, critical)
                critical_bias = [d for d in detections if d.severity in ['high', 'critical']]
                medium_bias = [d for d in detections if d.severity == 'medium']
                low_bias = [d for d in detections if d.severity == 'low']
                
                if critical_bias:
                    logger2.warning(f"심각한 편향 감지: {len(critical_bias)}개")
                    
                    # 편향 상세 정보 구성
                    bias_details = {
                        'detections': [
                            {
                                'type': d.bias_type.value,
                                'severity': d.severity,
                                'confidence': d.confidence,
                                'description': d.description,
                                'recommendations': d.recommendations
                            }
                            for d in detections  # 모든 편향 포함
                        ],
                        'critical_detections': [
                            {
                                'type': d.bias_type.value,
                                'severity': d.severity,
                                'confidence': d.confidence,
                                'description': d.description,
                                'recommendations': d.recommendations
                            }
                            for d in critical_bias
                        ],
                        'total_detections': len(detections),
                        'critical_count': len(critical_bias),
                        'medium_count': len(medium_bias),
                        'low_count': len(low_bias),
                        'emotion_history_count': len(emotion_history),
                        'action_history_count': len(action_history)
                    }
                    
                    # 조정 파라미터 생성
                    adjusted_params = self._generate_bias_adjustments(critical_bias)
                    
                    logger2.info(f"편향 조정 파라미터 생성: {list(adjusted_params.keys())}")
                    return True, bias_details, adjusted_params
                
                elif medium_bias:
                    logger2.info(f"중간 수준 편향 감지: {len(medium_bias)}개 (조정 없음)")
                    # 중간 수준 편향은 감지하지만 조정하지 않음
                    bias_details = {
                        'detections': [
                            {
                                'type': d.bias_type.value,
                                'severity': d.severity,
                                'confidence': d.confidence,
                                'description': d.description,
                                'recommendations': d.recommendations
                            }
                            for d in detections
                        ],
                        'total_detections': len(detections),
                        'critical_count': 0,
                        'medium_count': len(medium_bias),
                        'low_count': len(low_bias),
                        'emotion_history_count': len(emotion_history),
                        'action_history_count': len(action_history)
                    }
                    return True, bias_details, None
                
                else:
                    logger2.debug(f"낮은 수준 편향만 감지: {len(low_bias)}개 (조정 없음)")
                    return False, None, None
            
            else:
                logger2.debug("편향이 감지되지 않았습니다.")
                return False, None, None
            
        except Exception as e:
            logger2.error(f"편향 감지 실패: {e}")
            return False, None, None
    
    def _generate_bias_adjustments(self, critical_bias: List) -> Dict[str, Any]:
        """
        편향에 따른 조정 파라미터 생성 (scaffold)
        
        Args:
            critical_bias: 심각한 편향 목록
        
        Returns:
            Dict[str, Any]: 조정 파라미터
        """
        adjustments = {}
        
        for bias in critical_bias:
            if bias.bias_type.value == 'emotion_bias':
                # 감정 편향 시 ε값 증가로 탐험 강화
                adjustments['epsilon_boost'] = self.bias_adjustment_params['epsilon_boost']
                adjustments['exploration_mode'] = True
                
            elif bias.bias_type.value == 'action_bias':
                # 행동 편향 시 신뢰도 감소
                adjustments['confidence_reduction'] = self.bias_adjustment_params['confidence_reduction']
                
            elif bias.bias_type.value == 'pattern_bias':
                # 패턴 편향 시 완전 탐험 모드
                adjustments['full_exploration'] = True
                adjustments['epsilon_boost'] = 0.5
        
        return adjustments
    
    def _apply_bias_adjustments(self, adjusted_params: Dict[str, Any]):
        """
        편향 조정 파라미터 적용
        
        Args:
            adjusted_params: 조정 파라미터
        """
        if not self.reinforcement_engine_available or not self.reinforcement_engine:
            logger2.warning("ReinforcementEngine이 사용 불가능하여 편향 조정을 건너뜁니다.")
            return
        
        try:
            original_epsilon = self.reinforcement_engine.epsilon
            adjustments_applied = []
            
            # 1. 기본 ε값 증가 (epsilon_boost)
            if 'epsilon_boost' in adjusted_params:
                boost_value = adjusted_params['epsilon_boost']
                new_epsilon = min(1.0, original_epsilon + boost_value)
                self.reinforcement_engine.epsilon = new_epsilon
                adjustments_applied.append(f"ε값 증가: {original_epsilon:.2f} -> {new_epsilon:.2f} (+{boost_value:.2f})")
            
            # 2. 완전 탐험 모드 (full_exploration)
            if 'full_exploration' in adjusted_params:
                self.reinforcement_engine.epsilon = 1.0  # 완전 랜덤 탐험
                adjustments_applied.append(f"완전 탐험 모드: ε값 {original_epsilon:.2f} -> 1.00")
            
            # 3. 탐험 모드 (exploration_mode)
            if 'exploration_mode' in adjusted_params:
                # 현재 ε값이 낮으면 중간 수준으로 증가
                if self.reinforcement_engine.epsilon < 0.5:
                    self.reinforcement_engine.epsilon = 0.5
                    adjustments_applied.append(f"탐험 모드: ε값 {original_epsilon:.2f} -> 0.50")
            
            # 4. 신뢰도 감소 (confidence_reduction)
            if 'confidence_reduction' in adjusted_params:
                reduction = adjusted_params['confidence_reduction']
                # ReinforcementEngine에 confidence 속성이 있다면 조정
                if hasattr(self.reinforcement_engine, 'confidence'):
                    current_confidence = self.reinforcement_engine.confidence
                    new_confidence = max(0.1, current_confidence - reduction)
                    self.reinforcement_engine.confidence = new_confidence
                    adjustments_applied.append(f"신뢰도 감소: {current_confidence:.2f} -> {new_confidence:.2f} (-{reduction:.2f})")
                else:
                    adjustments_applied.append("신뢰도 감소: ReinforcementEngine에 confidence 속성이 없음")
            
            # 5. 편향 타입별 특별 조정
            if 'bias_type' in adjusted_params:
                bias_type = adjusted_params['bias_type']
                if bias_type == 'emotion_bias':
                    # 감정 편향: 더 강한 탐험 유도
                    if self.reinforcement_engine.epsilon < 0.7:
                        self.reinforcement_engine.epsilon = 0.7
                        adjustments_applied.append(f"감정 편향 조정: ε값 {original_epsilon:.2f} -> 0.70")
                
                elif bias_type == 'action_bias':
                    # 행동 편향: 다양한 행동 시도 유도
                    if self.reinforcement_engine.epsilon < 0.6:
                        self.reinforcement_engine.epsilon = 0.6
                        adjustments_applied.append(f"행동 편향 조정: ε값 {original_epsilon:.2f} -> 0.60")
                
                elif bias_type == 'pattern_bias':
                    # 패턴 편향: 패턴 깨기 위한 강한 탐험
                    self.reinforcement_engine.epsilon = 0.8
                    adjustments_applied.append(f"패턴 편향 조정: ε값 {original_epsilon:.2f} -> 0.80")
                
                elif bias_type == 'temporal_bias':
                    # 시간 편향: 시간대별 다양한 경험 유도
                    if self.reinforcement_engine.epsilon < 0.5:
                        self.reinforcement_engine.epsilon = 0.5
                        adjustments_applied.append(f"시간 편향 조정: ε값 {original_epsilon:.2f} -> 0.50")
                
                elif bias_type == 'intensity_bias':
                    # 강도 편향: 다양한 강도 시도 유도
                    if self.reinforcement_engine.epsilon < 0.6:
                        self.reinforcement_engine.epsilon = 0.6
                        adjustments_applied.append(f"강도 편향 조정: ε값 {original_epsilon:.2f} -> 0.60")
                
                elif bias_type == 'frequency_bias':
                    # 빈도 편향: 균등한 분포 유도
                    if self.reinforcement_engine.epsilon < 0.7:
                        self.reinforcement_engine.epsilon = 0.7
                        adjustments_applied.append(f"빈도 편향 조정: ε값 {original_epsilon:.2f} -> 0.70")
            
            # 6. 조정 결과 로깅
            if adjustments_applied:
                final_epsilon = self.reinforcement_engine.epsilon
                logger2.info(f"편향 조정 완료: {len(adjustments_applied)}개 조정 적용")
                for adjustment in adjustments_applied:
                    logger2.info(f"  - {adjustment}")
                logger2.info(f"최종 ε값: {final_epsilon:.2f}")
                
                # 조정 히스토리 저장 (선택사항)
                if hasattr(self, 'bias_adjustment_history'):
                    self.bias_adjustment_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'original_epsilon': original_epsilon,
                        'final_epsilon': final_epsilon,
                        'adjustments': adjustments_applied,
                        'adjusted_params': adjusted_params
                    })
            else:
                logger2.debug("적용할 편향 조정이 없습니다.")
                
        except Exception as e:
            logger2.error(f"편향 조정 파라미터 적용 실패: {e}")
            # 실패 시 원래 ε값으로 복원 시도
            try:
                if hasattr(self, 'original_epsilon'):
                    self.reinforcement_engine.epsilon = self.original_epsilon
                    logger2.info(f"편향 조정 실패로 ε값을 원래 값으로 복원: {self.original_epsilon:.2f}")
            except Exception as restore_error:
                logger2.error(f"ε값 복원 실패: {restore_error}")
    
    def _get_recent_emotion_history(self, emotion: str) -> List[Dict[str, Any]]:
        """
        최근 감정 히스토리 수집
        
        Args:
            emotion (str): 현재 감정
        
        Returns:
            List[Dict[str, Any]]: 감정 히스토리
        """
        if self.result_recorder_available and self.result_recorder:
            try:
                # ResultRecorder에서 최근 판단 히스토리 가져오기
                decision_history = self.result_recorder.get_decision_history(
                    emotion=emotion, 
                    limit=20  # 최근 20개
                )
                
                # 감정 히스토리 형태로 변환
                emotion_history = []
                for entry in decision_history:
                    emotion_history.append({
                        'emotion': entry.get('emotion', emotion),
                        'timestamp': entry.get('timestamp', ''),
                        'intensity': 0.7 if entry.get('success', False) else 0.3,  # 성공/실패에 따른 강도
                        'action': entry.get('action', ''),
                        'success': entry.get('success', False)
                    })
                
                logger2.debug(f"ResultRecorder에서 {len(emotion_history)}개 감정 히스토리 수집")
                return emotion_history
                
            except Exception as e:
                logger2.warning(f"ResultRecorder에서 감정 히스토리 수집 실패: {e}")
        
        # ResultRecorder가 없거나 실패한 경우 더미 데이터 반환
        logger2.debug("ResultRecorder 없음, 더미 감정 히스토리 사용")
        return [
            {'emotion': emotion, 'timestamp': '2025-06-28T10:00:00', 'intensity': 0.7},
            {'emotion': emotion, 'timestamp': '2025-06-28T09:30:00', 'intensity': 0.8},
            {'emotion': emotion, 'timestamp': '2025-06-28T09:00:00', 'intensity': 0.6}
        ]
    
    def _get_recent_action_history(self) -> List[Dict[str, Any]]:
        """
        최근 행동 히스토리 수집
        
        Args:
            List[Dict[str, Any]]: 행동 히스토리
        """
        if self.result_recorder_available and self.result_recorder:
            try:
                # ResultRecorder에서 최근 판단 히스토리 가져오기
                decision_history = self.result_recorder.get_decision_history(limit=20)
                
                # 행동 히스토리 형태로 변환
                action_history = []
                for entry in decision_history:
                    action_history.append({
                        'action': entry.get('action', ''),
                        'timestamp': entry.get('timestamp', ''),
                        'emotion': entry.get('emotion', ''),
                        'success': entry.get('success', False)
                    })
                
                logger2.debug(f"ResultRecorder에서 {len(action_history)}개 행동 히스토리 수집")
                return action_history
                
            except Exception as e:
                logger2.warning(f"ResultRecorder에서 행동 히스토리 수집 실패: {e}")
        
        # ResultRecorder가 없거나 실패한 경우 더미 데이터 반환
        logger2.debug("ResultRecorder 없음, 더미 행동 히스토리 사용")
        return [
            {'action': 'reflect', 'timestamp': '2025-06-28T10:00:00'},
            {'action': 'wait', 'timestamp': '2025-06-28T09:30:00'},
            {'action': 'reflect', 'timestamp': '2025-06-28T09:00:00'}
        ]
    
    def _apply_emotion_rules(self, emotion: str, stats_decision: dict) -> CoreDecision:
        """
        통계 기반 의사결정에 감정별 특별 규칙 적용
        
        Args:
            emotion (str): 감정
            stats_decision (dict): 통계 기반 의사결정 결과
        
        Returns:
            CoreDecision: 규칙이 적용된 최종 의사결정
        """
        emotion_lower = emotion.lower()
        action = stats_decision["action"]
        confidence = stats_decision["confidence"]
        
        # 분노 관련 감정들에 대한 특별 규칙
        anger_related = ["angry", "frustration"]
        if emotion_lower in anger_related:
            if confidence < 0.6:
                action = "wait"
                confidence = 0.6
        
        # 슬픔 관련 감정들에 대한 특별 규칙
        sadness_related = ["sad", "regret", "guilt", "shame"]
        if emotion_lower in sadness_related:
            if confidence < 0.7:
                action = "console"
                confidence = 0.7
        
        # 긍정적 감정들에 대한 특별 규칙
        positive_emotions = ["happy", "grateful", "inspired", "proud", "relief"]
        if emotion_lower in positive_emotions:
            if confidence < 0.8:
                action = "reflect"
                confidence = 0.8
        
        # 호기심 관련 감정들에 대한 특별 규칙
        curiosity_related = ["curious", "awe"]
        if emotion_lower in curiosity_related:
            if confidence < 0.7:
                action = "observe"
                confidence = 0.7
        
        # 규칙이 적용되었는지 확인
        rule_applied = (
            action != stats_decision["action"] or 
            confidence != stats_decision["confidence"]
        )
        
        return CoreDecision(
            action=action,
            confidence=round(confidence, 2),
            method="statistics_with_rules",
            reason="emotion_rules_applied",
            original_action=stats_decision["action"],
            original_confidence=stats_decision["confidence"],
            rule_applied=rule_applied
        )


# 전역 DecisionEngine 인스턴스
_decision_engine = DecisionEngine()


def create_decision(emotion, evolution_log_path, stats_path=None):
    """
    기존 함수 인터페이스 유지 (하위 호환성)
    """
    decision = _decision_engine.create_decision(emotion, evolution_log_path, stats_path)
    
    # 기존 딕셔너리 형태로 변환
    result = {
        "action": decision.action,
        "confidence": decision.confidence,
        "method": decision.method,
        "reason": decision.reason,
        "fallback": decision.fallback,
        "bias_flag": decision.bias_flag,
        "bias_details": decision.bias_details,
        "adjusted_parameters": decision.adjusted_parameters
    }
    
    return result


def apply_emotion_rules(emotion: str, stats_decision: dict) -> dict:
    """
    기존 함수 인터페이스 유지 (하위 호환성)
    """
    decision = _decision_engine._apply_emotion_rules(emotion, stats_decision)
    
    return {
        "action": decision.action,
        "confidence": decision.confidence,
        "original_action": getattr(decision, 'original_action', None),
        "original_confidence": getattr(decision, 'original_confidence', None),
        "rule_applied": getattr(decision, 'rule_applied', False)
    }


def create_evolution_payload(emotion, decision):
    """
    진화 로그용 페이로드 생성
    """
    return {
        "emotion": emotion,
        "decision": decision,
        "result": "success"
    } 