#!/usr/bin/env python3
"""
Loop Orchestrator - Core, Brain, Evolution 간의 전체 루프 조율

감정 입력 → Core 판단 → Brain 실행 → Evolution 학습의 전체 루프를 관리합니다.
"""

import os
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from duri_common.logger import get_logger
from duri_common.config.config import Config

logger = get_logger("duri_core.loop_orchestrator")
config = Config()


@dataclass
class LoopSession:
    """루프 세션 데이터"""
    session_id: str
    emotion: str
    intensity: float
    context: Dict[str, Any]
    timestamp: str
    status: str = "started"  # started, core_processed, brain_processed, evolution_processed, completed, failed


@dataclass
class CoreDecision:
    """Core 판단 결과"""
    session_id: str
    emotion: str
    decision: str
    confidence: float
    reasoning: Dict[str, Any]
    timestamp: str


@dataclass
class BrainExecution:
    """Brain 실행 결과"""
    session_id: str
    action: str
    success: bool
    result_score: float
    execution_time: float
    feedback: str
    metadata: Dict[str, Any]
    timestamp: str


@dataclass
class EvolutionLearning:
    """Evolution 학습 결과"""
    session_id: str
    emotion: str
    action: str
    success: bool
    learning_rate: float
    pattern_updated: bool
    insights_generated: List[str]
    timestamp: str


class LoopOrchestrator:
    """루프 오케스트레이터"""
    
    def __init__(self, data_dir: str = "loop_data"):
        """
        LoopOrchestrator 초기화
        
        Args:
            data_dir (str): 데이터 저장 디렉토리
        """
        self.data_dir = data_dir
        self.sessions_dir = os.path.join(data_dir, "sessions")
        self.core_dir = os.path.join(data_dir, "core")
        self.brain_dir = os.path.join(data_dir, "brain")
        self.evolution_dir = os.path.join(data_dir, "evolution")
        self.queue_dir = os.path.join(data_dir, "queue")
        
        # 디렉토리 생성
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(self.core_dir, exist_ok=True)
        os.makedirs(self.brain_dir, exist_ok=True)
        os.makedirs(self.evolution_dir, exist_ok=True)
        os.makedirs(self.queue_dir, exist_ok=True)
        
        logger.info(f"LoopOrchestrator 초기화 완료: {data_dir}")
    
    def start_emotion_loop(
        self,
        emotion: str,
        intensity: float = 0.5,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        감정 루프 시작
        
        Args:
            emotion (str): 감정
            intensity (float): 감정 강도 (0.0 ~ 1.0)
            context (Dict, optional): 컨텍스트 정보
        
        Returns:
            str: 세션 ID
        """
        session_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # 세션 생성
        session = LoopSession(
            session_id=session_id,
            emotion=emotion,
            intensity=intensity,
            context=context or {},
            timestamp=timestamp
        )
        
        # 세션 저장
        self._save_session(session)
        
        # Core 큐에 감정 전달
        self._queue_to_core(session)
        
        logger.info(f"감정 루프 시작: {session_id} - {emotion} (강도: {intensity})")
        return session_id
    
    def process_core_decision(self, session_id: str) -> Optional[CoreDecision]:
        """
        Core 판단 처리
        
        Args:
            session_id (str): 세션 ID
        
        Returns:
            Optional[CoreDecision]: Core 판단 결과
        """
        try:
            # Core 큐에서 판단 결과 확인
            core_result = self._get_core_result(session_id)
            if not core_result:
                return None
            
            # Core 판단 결과 저장
            decision = CoreDecision(
                session_id=session_id,
                emotion=core_result.get("emotion", ""),
                decision=core_result.get("decision", ""),
                confidence=core_result.get("confidence", 0.0),
                reasoning=core_result.get("reasoning", {}),
                timestamp=datetime.now().isoformat()
            )
            
            self._save_core_decision(decision)
            
            # Brain 큐에 판단 결과 전달
            self._queue_to_brain(decision)
            
            # 세션 상태 업데이트
            self._update_session_status(session_id, "core_processed")
            
            logger.info(f"Core 판단 처리 완료: {session_id} - {decision.decision}")
            return decision
            
        except Exception as e:
            logger.error(f"Core 판단 처리 실패: {session_id} - {e}")
            self._update_session_status(session_id, "failed")
            return None
    
    def process_brain_execution(self, session_id: str) -> Optional[BrainExecution]:
        """
        Brain 실행 처리
        
        Args:
            session_id (str): 세션 ID
        
        Returns:
            Optional[BrainExecution]: Brain 실행 결과
        """
        try:
            # Brain 큐에서 실행 결과 확인
            brain_result = self._get_brain_result(session_id)
            if not brain_result:
                return None
            
            # Brain 실행 결과 저장
            execution = BrainExecution(
                session_id=session_id,
                action=brain_result.get("action", ""),
                success=brain_result.get("success", False),
                result_score=brain_result.get("result_score", 0.0),
                execution_time=brain_result.get("execution_time", 0.0),
                feedback=brain_result.get("feedback", ""),
                metadata=brain_result.get("metadata", {}),
                timestamp=datetime.now().isoformat()
            )
            
            self._save_brain_execution(execution)
            
            # Evolution 큐에 실행 결과 전달
            self._queue_to_evolution(execution)
            
            # 세션 상태 업데이트
            self._update_session_status(session_id, "brain_processed")
            
            logger.info(f"Brain 실행 처리 완료: {session_id} - {execution.action} (성공: {execution.success})")
            return execution
            
        except Exception as e:
            logger.error(f"Brain 실행 처리 실패: {session_id} - {e}")
            self._update_session_status(session_id, "failed")
            return None
    
    def process_evolution_learning(self, session_id: str) -> Optional[EvolutionLearning]:
        """
        Evolution 학습 처리
        
        Args:
            session_id (str): 세션 ID
        
        Returns:
            Optional[EvolutionLearning]: Evolution 학습 결과
        """
        try:
            # Evolution 큐에서 학습 결과 확인
            evolution_result = self._get_evolution_result(session_id)
            if not evolution_result:
                return None
            
            # Evolution 학습 결과 저장
            learning = EvolutionLearning(
                session_id=session_id,
                emotion=evolution_result.get("emotion", ""),
                action=evolution_result.get("action", ""),
                success=evolution_result.get("success", False),
                learning_rate=evolution_result.get("learning_rate", 0.0),
                pattern_updated=evolution_result.get("pattern_updated", False),
                insights_generated=evolution_result.get("insights_generated", []),
                timestamp=datetime.now().isoformat()
            )
            
            self._save_evolution_learning(learning)
            
            # 세션 상태 업데이트
            self._update_session_status(session_id, "evolution_processed")
            
            logger.info(f"Evolution 학습 처리 완료: {session_id} - 패턴 업데이트: {learning.pattern_updated}")
            return learning
            
        except Exception as e:
            logger.error(f"Evolution 학습 처리 실패: {session_id} - {e}")
            self._update_session_status(session_id, "failed")
            return None
    
    def complete_loop(self, session_id: str) -> bool:
        """
        루프 완료 처리
        
        Args:
            session_id (str): 세션 ID
        
        Returns:
            bool: 완료 성공 여부
        """
        try:
            self._update_session_status(session_id, "completed")
            logger.info(f"루프 완료: {session_id}")
            return True
        except Exception as e:
            logger.error(f"루프 완료 처리 실패: {session_id} - {e}")
            return False
    
    def get_loop_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        루프 상태 조회
        
        Args:
            session_id (str): 세션 ID
        
        Returns:
            Optional[Dict]: 루프 상태 정보
        """
        try:
            # 세션 정보 조회
            session = self._get_session(session_id)
            if not session:
                return None
            
            # 각 단계별 결과 조회
            core_decision = self._get_core_decision(session_id)
            brain_execution = self._get_brain_execution(session_id)
            evolution_learning = self._get_evolution_learning(session_id)
            
            return {
                "session": asdict(session),
                "core_decision": asdict(core_decision) if core_decision else None,
                "brain_execution": asdict(brain_execution) if brain_execution else None,
                "evolution_learning": asdict(evolution_learning) if evolution_learning else None,
                "loop_complete": session.status == "completed"
            }
            
        except Exception as e:
            logger.error(f"루프 상태 조회 실패: {session_id} - {e}")
            return None
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        최근 세션 목록 조회
        
        Args:
            limit (int): 조회할 최대 개수
        
        Returns:
            List[Dict]: 세션 목록
        """
        try:
            sessions = []
            session_files = sorted(
                [f for f in os.listdir(self.sessions_dir) if f.endswith('.json')],
                reverse=True
            )[:limit]
            
            for filename in session_files:
                filepath = os.path.join(self.sessions_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    sessions.append(session_data)
            
            return sessions
            
        except Exception as e:
            logger.error(f"최근 세션 조회 실패: {e}")
            return []
    
    # ========================================
    # 내부 메서드들
    # ========================================
    
    def _save_session(self, session: LoopSession):
        """세션 저장"""
        filepath = os.path.join(self.sessions_dir, f"{session.session_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(session), f, indent=2, ensure_ascii=False)
    
    def _get_session(self, session_id: str) -> Optional[LoopSession]:
        """세션 조회"""
        filepath = os.path.join(self.sessions_dir, f"{session_id}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return LoopSession(**data)
        return None
    
    def _update_session_status(self, session_id: str, status: str):
        """세션 상태 업데이트"""
        session = self._get_session(session_id)
        if session:
            session.status = status
            self._save_session(session)
    
    def _queue_to_core(self, session: LoopSession):
        """Core 큐에 감정 전달"""
        filepath = os.path.join(self.queue_dir, f"core_{session.session_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(session), f, indent=2, ensure_ascii=False)
    
    def _get_core_result(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Core 결과 조회"""
        filepath = os.path.join(self.core_dir, f"{session_id}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def _save_core_decision(self, decision: CoreDecision):
        """Core 판단 결과 저장"""
        filepath = os.path.join(self.core_dir, f"{decision.session_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(decision), f, indent=2, ensure_ascii=False)
    
    def _get_core_decision(self, session_id: str) -> Optional[CoreDecision]:
        """Core 판단 결과 조회"""
        filepath = os.path.join(self.core_dir, f"{session_id}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return CoreDecision(**data)
        return None
    
    def _queue_to_brain(self, decision: CoreDecision):
        """Brain 큐에 판단 결과 전달"""
        filepath = os.path.join(self.queue_dir, f"brain_{decision.session_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(decision), f, indent=2, ensure_ascii=False)
    
    def _get_brain_result(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Brain 결과 조회"""
        filepath = os.path.join(self.brain_dir, f"{session_id}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def _save_brain_execution(self, execution: BrainExecution):
        """Brain 실행 결과 저장"""
        filepath = os.path.join(self.brain_dir, f"{execution.session_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(execution), f, indent=2, ensure_ascii=False)
    
    def _get_brain_execution(self, session_id: str) -> Optional[BrainExecution]:
        """Brain 실행 결과 조회"""
        filepath = os.path.join(self.brain_dir, f"{session_id}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return BrainExecution(**data)
        return None
    
    def _queue_to_evolution(self, execution: BrainExecution):
        """Evolution 큐에 실행 결과 전달"""
        filepath = os.path.join(self.queue_dir, f"evolution_{execution.session_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(execution), f, indent=2, ensure_ascii=False)
    
    def _get_evolution_result(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Evolution 결과 조회"""
        filepath = os.path.join(self.evolution_dir, f"{session_id}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def _save_evolution_learning(self, learning: EvolutionLearning):
        """Evolution 학습 결과 저장"""
        filepath = os.path.join(self.evolution_dir, f"{learning.session_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(learning), f, indent=2, ensure_ascii=False)
    
    def _get_evolution_learning(self, session_id: str) -> Optional[EvolutionLearning]:
        """Evolution 학습 결과 조회"""
        filepath = os.path.join(self.evolution_dir, f"{session_id}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return EvolutionLearning(**data)
        return None 