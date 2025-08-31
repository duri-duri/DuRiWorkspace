#!/usr/bin/env python3
"""
Decision Processor - Core 의사결정 처리기

감정 데이터를 받아서 적절한 의사결정을 내리는 역할을 합니다.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from duri_common.logger import get_logger
from duri_common.config.config import Config
from duri_core.core.loop_orchestrator import LoopOrchestrator, CoreDecision
from .decision import create_decision
from .stats import choose_best_action
from .bias_detector import create_bias_detector, BiasDetector

logger = get_logger("duri_core.decision_processor")
config = Config()


class DecisionProcessor:
    """판단 처리기"""
    
    def __init__(self, loop_orchestrator: LoopOrchestrator):
        """
        DecisionProcessor 초기화
        
        Args:
            loop_orchestrator (LoopOrchestrator): 루프 오케스트레이터
        """
        self.orchestrator = loop_orchestrator
        self.queue_dir = os.path.join(loop_orchestrator.data_dir, "queue")
        
        logger.info("DecisionProcessor 초기화 완료")
    
    def process_pending_decisions(self) -> int:
        """
        대기 중인 판단 요청 처리
        
        Returns:
            int: 처리된 요청 수
        """
        processed_count = 0
        
        try:
            # Core 큐에서 대기 중인 요청 확인
            core_queue_files = [f for f in os.listdir(self.queue_dir) 
                              if f.startswith("core_") and f.endswith(".json")]
            
            for filename in core_queue_files:
                filepath = os.path.join(self.queue_dir, filename)
                session_id = filename.replace("core_", "").replace(".json", "")
                
                try:
                    # 요청 데이터 읽기
                    with open(filepath, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    # 판단 처리
                    decision = self._make_decision(session_data)
                    if decision:
                        # 판단 결과 저장
                        self._save_decision_result(session_id, decision)
                        
                        # 큐 파일 삭제
                        os.remove(filepath)
                        
                        processed_count += 1
                        logger.info(f"판단 처리 완료: {session_id} - {decision.decision}")
                    
                except Exception as e:
                    logger.error(f"판단 처리 실패: {session_id} - {e}")
                    # 실패한 요청은 큐에서 제거
                    if os.path.exists(filepath):
                        os.remove(filepath)
            
            return processed_count
            
        except Exception as e:
            logger.error(f"판단 처리 중 오류: {e}")
            return processed_count
    
    def _make_decision(self, session_data: Dict[str, Any]) -> Optional[CoreDecision]:
        """
        감정에 대한 판단 생성
        
        Args:
            session_data (Dict): 세션 데이터
        
        Returns:
            Optional[CoreDecision]: 판단 결과
        """
        try:
            emotion = session_data.get("emotion", "")
            intensity = session_data.get("intensity", 0.5)
            context = session_data.get("context", {})
            session_id = session_data.get("session_id", "")
            
            # 감정별 판단 로직
            decision, confidence, reasoning = self._analyze_emotion(emotion, intensity, context)
            
            return CoreDecision(
                session_id=session_id,
                emotion=emotion,
                decision=decision,
                confidence=confidence,
                reasoning=reasoning,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"판단 생성 실패: {e}")
            return None
    
    def _analyze_emotion(self, emotion: str, intensity: float, context: Dict[str, Any]) -> tuple:
        """
        감정 분석 및 판단
        
        Args:
            emotion (str): 감정
            intensity (float): 감정 강도
            context (Dict): 컨텍스트
        
        Returns:
            tuple: (판단, 신뢰도, 추론)
        """
        # 기본 감정별 판단 매핑
        emotion_decisions = {
            "happy": "celebrate",
            "sad": "comfort",
            "angry": "calm_down",
            "fear": "reassure",
            "surprise": "explain",
            "disgust": "avoid",
            "trust": "encourage",
            "anticipation": "prepare"
        }
        
        # 감정 강도에 따른 신뢰도 조정
        base_confidence = 0.7
        intensity_factor = min(intensity * 1.5, 1.0)
        confidence = base_confidence * intensity_factor
        
        # 기본 판단
        decision = emotion_decisions.get(emotion.lower(), "observe")
        
        # 컨텍스트 기반 조정
        if context.get("urgent", False):
            decision = "act_immediately"
            confidence = min(confidence + 0.2, 1.0)
        
        if context.get("social", False):
            if decision == "celebrate":
                decision = "share_joy"
            elif decision == "comfort":
                decision = "offer_support"
        
        # 추론 정보 구성
        reasoning = {
            "emotion": emotion,
            "intensity": intensity,
            "base_decision": emotion_decisions.get(emotion.lower(), "observe"),
            "context_factors": list(context.keys()),
            "confidence_factors": {
                "base_confidence": base_confidence,
                "intensity_factor": intensity_factor,
                "context_adjustment": context.get("urgent", False) or context.get("social", False)
            }
        }
        
        return decision, confidence, reasoning
    
    def _save_decision_result(self, session_id: str, decision: CoreDecision):
        """판단 결과 저장"""
        filepath = os.path.join(self.orchestrator.core_dir, f"{session_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "session_id": decision.session_id,
                "emotion": decision.emotion,
                "decision": decision.decision,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning,
                "timestamp": decision.timestamp
            }, f, indent=2, ensure_ascii=False)


class CoreService:
    """Core 서비스"""
    
    def __init__(self, data_dir: str = "loop_data"):
        """
        CoreService 초기화
        
        Args:
            data_dir (str): 데이터 디렉토리
        """
        self.orchestrator = LoopOrchestrator(data_dir)
        self.processor = DecisionProcessor(self.orchestrator)
        
        logger.info("CoreService 초기화 완료")
    
    def start_emotion_loop(self, emotion: str, intensity: float = 0.5, context: Optional[Dict[str, Any]] = None) -> str:
        """
        감정 루프 시작
        
        Args:
            emotion (str): 감정
            intensity (float): 감정 강도
            context (Dict, optional): 컨텍스트
        
        Returns:
            str: 세션 ID
        """
        return self.orchestrator.start_emotion_loop(emotion, intensity, context)
    
    def process_decisions(self) -> int:
        """
        대기 중인 판단 처리
        
        Returns:
            int: 처리된 요청 수
        """
        return self.processor.process_pending_decisions()
    
    def get_loop_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        루프 상태 조회
        
        Args:
            session_id (str): 세션 ID
        
        Returns:
            Optional[Dict]: 루프 상태
        """
        return self.orchestrator.get_loop_status(session_id)
    
    def get_recent_sessions(self, limit: int = 10) -> list:
        """
        최근 세션 조회
        
        Args:
            limit (int): 조회할 최대 개수
        
        Returns:
            list: 세션 목록
        """
        return self.orchestrator.get_recent_sessions(limit)


# 전역 인스턴스
core_service = CoreService() 