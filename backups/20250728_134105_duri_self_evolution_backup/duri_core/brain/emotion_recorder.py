#!/usr/bin/env python3
"""
Emotion Recorder - 감정 입력 기록 시스템

감정 입력의 발생 시점과 내용을 기록하여 
Core의 의사결정 과정을 추적할 수 있도록 합니다.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from duri_common.logger import get_logger

logger = get_logger("duri_brain.emotion_recorder")


@dataclass
class EmotionInput:
    """감정 입력 데이터 구조"""
    emotion: str
    intensity: float
    timestamp: str
    context: Optional[Dict[str, Any]] = None
    source: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class DecisionRecord:
    """의사결정 기록 데이터 구조"""
    emotion_input: EmotionInput
    decision: Dict[str, Any]
    decision_timestamp: str
    loop_id: str


class EmotionRecorder:
    """감정 입력 기록기"""
    
    def __init__(self, data_dir: str = "brain_data"):
        """
        EmotionRecorder 초기화
        
        Args:
            data_dir (str): 데이터 저장 디렉토리
        """
        self.data_dir = data_dir
        self.emotions_dir = os.path.join(data_dir, "emotions")
        self.decisions_dir = os.path.join(data_dir, "decisions")
        self.loops_dir = os.path.join(data_dir, "loops")
        
        # 디렉토리 생성
        os.makedirs(self.emotions_dir, exist_ok=True)
        os.makedirs(self.decisions_dir, exist_ok=True)
        os.makedirs(self.loops_dir, exist_ok=True)
        
        logger.info(f"EmotionRecorder 초기화 완료: {data_dir}")
    
    def record_emotion_input(
        self, 
        emotion: str, 
        intensity: float, 
        context: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> EmotionInput:
        """
        감정 입력 기록
        
        Args:
            emotion (str): 감정
            intensity (float): 감정 강도 (0.0 ~ 1.0)
            context (Dict, optional): 컨텍스트 정보
            source (str, optional): 감정 소스
            session_id (str, optional): 세션 ID
        
        Returns:
            EmotionInput: 기록된 감정 입력
        """
        timestamp = datetime.now().isoformat()
        
        emotion_input = EmotionInput(
            emotion=emotion,
            intensity=intensity,
            timestamp=timestamp,
            context=context or {},
            source=source,
            session_id=session_id
        )
        
        # 감정 입력 저장
        self._save_emotion_input(emotion_input)
        
        logger.info(f"감정 입력 기록: {emotion} (강도: {intensity:.2f})")
        return emotion_input
    
    def record_decision(
        self, 
        emotion_input: EmotionInput, 
        decision: Dict[str, Any]
    ) -> DecisionRecord:
        """
        의사결정 기록
        
        Args:
            emotion_input (EmotionInput): 감정 입력
            decision (Dict): Core의 의사결정 결과
        
        Returns:
            DecisionRecord: 기록된 의사결정
        """
        decision_timestamp = datetime.now().isoformat()
        loop_id = self._generate_loop_id(emotion_input, decision_timestamp)
        
        decision_record = DecisionRecord(
            emotion_input=emotion_input,
            decision=decision,
            decision_timestamp=decision_timestamp,
            loop_id=loop_id
        )
        
        # 의사결정 저장
        self._save_decision_record(decision_record)
        
        logger.info(f"의사결정 기록: {loop_id} - {decision.get('action', 'unknown')}")
        return decision_record
    
    def get_emotion_history(
        self, 
        emotion: Optional[str] = None, 
        limit: int = 100
    ) -> List[EmotionInput]:
        """
        감정 입력 히스토리 조회
        
        Args:
            emotion (str, optional): 특정 감정 필터링
            limit (int): 조회할 최대 개수
        
        Returns:
            List[EmotionInput]: 감정 입력 히스토리
        """
        history = []
        
        try:
            # 모든 감정 파일 읽기
            for filename in os.listdir(self.emotions_dir):
                if not filename.endswith('.json'):
                    continue
                
                filepath = os.path.join(self.emotions_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    emotion_input = EmotionInput(**data)
                    
                    # 감정 필터링
                    if emotion and emotion_input.emotion != emotion:
                        continue
                    
                    history.append(emotion_input)
            
            # 시간순 정렬 (최신순)
            history.sort(key=lambda x: x.timestamp, reverse=True)
            
            # 개수 제한
            return history[:limit]
            
        except Exception as e:
            logger.error(f"감정 히스토리 조회 실패: {e}")
            return []
    
    def get_decision_history(
        self, 
        emotion: Optional[str] = None, 
        limit: int = 100
    ) -> List[DecisionRecord]:
        """
        의사결정 히스토리 조회
        
        Args:
            emotion (str, optional): 특정 감정 필터링
            limit (int): 조회할 최대 개수
        
        Returns:
            List[DecisionRecord]: 의사결정 히스토리
        """
        history = []
        
        try:
            # 모든 의사결정 파일 읽기
            for filename in os.listdir(self.decisions_dir):
                if not filename.endswith('.json'):
                    continue
                
                filepath = os.path.join(self.decisions_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # EmotionInput 객체 생성
                    emotion_data = data['emotion_input']
                    emotion_input = EmotionInput(**emotion_data)
                    
                    # DecisionRecord 객체 생성
                    decision_record = DecisionRecord(
                        emotion_input=emotion_input,
                        decision=data['decision'],
                        decision_timestamp=data['decision_timestamp'],
                        loop_id=data['loop_id']
                    )
                    
                    # 감정 필터링
                    if emotion and decision_record.emotion_input.emotion != emotion:
                        continue
                    
                    history.append(decision_record)
            
            # 시간순 정렬 (최신순)
            history.sort(key=lambda x: x.decision_timestamp, reverse=True)
            
            # 개수 제한
            return history[:limit]
            
        except Exception as e:
            logger.error(f"의사결정 히스토리 조회 실패: {e}")
            return []
    
    def _save_emotion_input(self, emotion_input: EmotionInput):
        """감정 입력을 파일로 저장"""
        try:
            timestamp = emotion_input.timestamp.replace(':', '-').replace('.', '-')
            filename = f"emotion_{emotion_input.emotion}_{timestamp}.json"
            filepath = os.path.join(self.emotions_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(emotion_input), f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"감정 입력 저장 실패: {e}")
    
    def _save_decision_record(self, decision_record: DecisionRecord):
        """의사결정 기록을 파일로 저장"""
        try:
            filename = f"decision_{decision_record.loop_id}.json"
            filepath = os.path.join(self.decisions_dir, filename)
            
            data = {
                'emotion_input': asdict(decision_record.emotion_input),
                'decision': decision_record.decision,
                'decision_timestamp': decision_record.decision_timestamp,
                'loop_id': decision_record.loop_id
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"의사결정 기록 저장 실패: {e}")
    
    def _generate_loop_id(self, emotion_input: EmotionInput, decision_timestamp: str) -> str:
        """루프 ID 생성"""
        timestamp = emotion_input.timestamp.replace(':', '-').replace('.', '-')
        return f"loop_{emotion_input.emotion}_{timestamp}"
    
    def get_statistics(self) -> Dict[str, Any]:
        """기록 통계 조회"""
        try:
            emotion_count = len([f for f in os.listdir(self.emotions_dir) if f.endswith('.json')])
            decision_count = len([f for f in os.listdir(self.decisions_dir) if f.endswith('.json')])
            
            # 감정별 통계
            emotion_stats = {}
            for emotion_input in self.get_emotion_history():
                emotion = emotion_input.emotion
                if emotion not in emotion_stats:
                    emotion_stats[emotion] = {'count': 0, 'avg_intensity': 0.0}
                
                emotion_stats[emotion]['count'] += 1
                emotion_stats[emotion]['avg_intensity'] += emotion_input.intensity
            
            # 평균 강도 계산
            for emotion in emotion_stats:
                count = emotion_stats[emotion]['count']
                if count > 0:
                    emotion_stats[emotion]['avg_intensity'] /= count
            
            return {
                'total_emotions': emotion_count,
                'total_decisions': decision_count,
                'emotion_statistics': emotion_stats
            }
            
        except Exception as e:
            logger.error(f"통계 조회 실패: {e}")
            return {} 