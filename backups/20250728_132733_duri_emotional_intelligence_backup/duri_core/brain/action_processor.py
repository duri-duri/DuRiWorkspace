#!/usr/bin/env python3
"""
Action Processor - Brain 행동 실행 처리기

Core의 판단을 받아서 행동을 실행하고 결과를 Evolution으로 전달하는 역할을 합니다.
"""

import os
import json
import time
import random
from datetime import datetime
from typing import Dict, Any, Optional
from duri_common.logger import get_logger
from duri_common.config.config import Config

logger = get_logger("duri_brain.action_processor")
config = Config()


class ActionProcessor:
    """행동 실행 처리기"""
    
    def __init__(self, data_dir: str = "loop_data"):
        """
        ActionProcessor 초기화
        
        Args:
            data_dir (str): 데이터 디렉토리
        """
        self.data_dir = data_dir
        self.queue_dir = os.path.join(data_dir, "queue")
        self.brain_dir = os.path.join(data_dir, "brain")
        
        # 디렉토리 생성
        os.makedirs(self.brain_dir, exist_ok=True)
        
        logger.info("ActionProcessor 초기화 완료")
    
    def process_pending_actions(self) -> int:
        """
        대기 중인 행동 요청 처리
        
        Returns:
            int: 처리된 요청 수
        """
        processed_count = 0
        
        try:
            # Brain 큐에서 대기 중인 요청 확인
            brain_queue_files = [f for f in os.listdir(self.queue_dir) 
                               if f.startswith("brain_") and f.endswith(".json")]
            
            for filename in brain_queue_files:
                filepath = os.path.join(self.queue_dir, filename)
                session_id = filename.replace("brain_", "").replace(".json", "")
                
                try:
                    # 요청 데이터 읽기
                    with open(filepath, 'r', encoding='utf-8') as f:
                        decision_data = json.load(f)
                    
                    # 행동 실행
                    execution_result = self._execute_action(decision_data)
                    if execution_result:
                        # 실행 결과 저장
                        self._save_execution_result(session_id, execution_result)
                        
                        # 큐 파일 삭제
                        os.remove(filepath)
                        
                        processed_count += 1
                        logger.info(f"행동 실행 완료: {session_id} - {execution_result['action']}")
                    
                except Exception as e:
                    logger.error(f"행동 실행 실패: {session_id} - {e}")
                    # 실패한 요청은 큐에서 제거
                    if os.path.exists(filepath):
                        os.remove(filepath)
            
            return processed_count
            
        except Exception as e:
            logger.error(f"행동 처리 중 오류: {e}")
            return processed_count
    
    def _execute_action(self, decision_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        판단에 따른 행동 실행
        
        Args:
            decision_data (Dict): 판단 데이터
        
        Returns:
            Optional[Dict]: 실행 결과
        """
        try:
            session_id = decision_data.get("session_id", "")
            emotion = decision_data.get("emotion", "")
            decision = decision_data.get("decision", "")
            confidence = decision_data.get("confidence", 0.0)
            
            # 행동 매핑
            action = self._map_decision_to_action(decision, emotion)
            
            # 행동 실행 시뮬레이션
            start_time = time.time()
            success, result_score, feedback = self._simulate_action_execution(action, confidence)
            execution_time = time.time() - start_time
            
            return {
                "session_id": session_id,
                "action": action,
                "success": success,
                "result_score": result_score,
                "execution_time": execution_time,
                "feedback": feedback,
                "metadata": {
                    "emotion": emotion,
                    "decision": decision,
                    "confidence": confidence,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"행동 실행 실패: {e}")
            return None
    
    def _map_decision_to_action(self, decision: str, emotion: str) -> str:
        """
        판단을 행동으로 매핑
        
        Args:
            decision (str): 판단
            emotion (str): 감정
        
        Returns:
            str: 행동
        """
        # 기본 행동 매핑
        action_mapping = {
            "celebrate": "dance_and_sing",
            "comfort": "hug_and_speak_softly",
            "calm_down": "deep_breathing_exercise",
            "reassure": "gentle_touch_and_words",
            "explain": "detailed_explanation",
            "avoid": "step_back_and_observe",
            "encourage": "positive_reinforcement",
            "prepare": "gather_resources",
            "act_immediately": "quick_response",
            "share_joy": "social_celebration",
            "offer_support": "emotional_support",
            "observe": "careful_observation"
        }
        
        return action_mapping.get(decision, "observe")
    
    def _simulate_action_execution(self, action: str, confidence: float) -> tuple:
        """
        행동 실행 시뮬레이션
        
        Args:
            action (str): 행동
            confidence (float): 신뢰도
        
        Returns:
            tuple: (성공 여부, 결과 점수, 피드백)
        """
        # 신뢰도 기반 성공 확률
        base_success_rate = 0.8
        success_rate = base_success_rate * confidence
        
        # 랜덤 성공/실패 결정
        success = random.random() < success_rate
        
        # 결과 점수 계산
        if success:
            result_score = min(confidence + random.uniform(0.1, 0.3), 1.0)
            feedback = self._generate_success_feedback(action)
        else:
            result_score = max(confidence - random.uniform(0.2, 0.4), 0.0)
            feedback = self._generate_failure_feedback(action)
        
        return success, result_score, feedback
    
    def _generate_success_feedback(self, action: str) -> str:
        """성공 피드백 생성"""
        feedback_templates = {
            "dance_and_sing": "춤과 노래로 기쁨을 표현했습니다. 분위기가 밝아졌습니다.",
            "hug_and_speak_softly": "부드러운 말과 포옹으로 위로를 전했습니다. 안정감을 느낍니다.",
            "deep_breathing_exercise": "깊은 호흡 운동으로 마음이 진정되었습니다.",
            "gentle_touch_and_words": "부드러운 터치와 말로 안심시켰습니다.",
            "detailed_explanation": "자세한 설명으로 이해를 도왔습니다.",
            "step_back_and_observe": "적절한 거리를 두고 관찰했습니다.",
            "positive_reinforcement": "긍정적인 강화로 동기를 부여했습니다.",
            "gather_resources": "필요한 자원을 준비했습니다.",
            "quick_response": "신속한 대응으로 상황을 개선했습니다.",
            "social_celebration": "함께 기쁨을 나누었습니다.",
            "emotional_support": "정서적 지원을 제공했습니다.",
            "careful_observation": "신중한 관찰로 상황을 파악했습니다."
        }
        
        return feedback_templates.get(action, "행동이 성공적으로 실행되었습니다.")
    
    def _generate_failure_feedback(self, action: str) -> str:
        """실패 피드백 생성"""
        feedback_templates = {
            "dance_and_sing": "춤과 노래가 상황에 맞지 않았습니다. 다른 접근이 필요합니다.",
            "hug_and_speak_softly": "포옹이 거부되었습니다. 개인 공간을 존중해야 합니다.",
            "deep_breathing_exercise": "호흡 운동이 효과적이지 않았습니다. 다른 방법을 시도해보겠습니다.",
            "gentle_touch_and_words": "터치가 불편해했습니다. 말로만 위로를 시도하겠습니다.",
            "detailed_explanation": "설명이 복잡했습니다. 더 간단하게 설명하겠습니다.",
            "step_back_and_observe": "관찰만으로는 부족했습니다. 적극적인 개입이 필요합니다.",
            "positive_reinforcement": "긍정적 강화가 효과적이지 않았습니다. 다른 동기 부여 방법을 찾겠습니다.",
            "gather_resources": "자원 수집이 지연되었습니다. 우선순위를 재조정하겠습니다.",
            "quick_response": "신속한 대응이 부적절했습니다. 더 신중한 접근이 필요합니다.",
            "social_celebration": "사회적 축하가 부적절했습니다. 개인적인 축하로 변경하겠습니다.",
            "emotional_support": "정서적 지원이 효과적이지 않았습니다. 다른 지원 방법을 찾겠습니다.",
            "careful_observation": "관찰만으로는 상황 개선이 어렵습니다. 적극적인 개입이 필요합니다."
        }
        
        return feedback_templates.get(action, "행동 실행에 실패했습니다. 다른 방법을 시도하겠습니다.")
    
    def _save_execution_result(self, session_id: str, result: Dict[str, Any]):
        """실행 결과 저장"""
        filepath = os.path.join(self.brain_dir, f"{session_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)


class BrainService:
    """Brain 서비스"""
    
    def __init__(self, data_dir: str = "loop_data"):
        """
        BrainService 초기화
        
        Args:
            data_dir (str): 데이터 디렉토리
        """
        self.processor = ActionProcessor(data_dir)
        
        logger.info("BrainService 초기화 완료")
    
    def process_actions(self) -> int:
        """
        대기 중인 행동 처리
        
        Returns:
            int: 처리된 요청 수
        """
        return self.processor.process_pending_actions()
    
    def get_execution_result(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        실행 결과 조회
        
        Args:
            session_id (str): 세션 ID
        
        Returns:
            Optional[Dict]: 실행 결과
        """
        filepath = os.path.join(self.processor.brain_dir, f"{session_id}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None


# 전역 인스턴스
brain_service = BrainService() 