#!/usr/bin/env python3
"""
Learning Processor - Evolution 학습 처리기

Brain의 실행 결과를 받아서 학습하고 패턴을 업데이트하는 역할을 합니다.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from duri_common.logger import get_logger
from duri_common.config.config import Config

logger = get_logger("duri_evolution.learning_processor")
config = Config()


class LearningProcessor:
    """학습 처리기"""
    
    def __init__(self, data_dir: str = "loop_data"):
        """
        LearningProcessor 초기화
        
        Args:
            data_dir (str): 데이터 디렉토리
        """
        self.data_dir = data_dir
        self.queue_dir = os.path.join(data_dir, "queue")
        self.evolution_dir = os.path.join(data_dir, "evolution")
        self.patterns_dir = os.path.join(data_dir, "patterns")
        
        # 디렉토리 생성
        os.makedirs(self.evolution_dir, exist_ok=True)
        os.makedirs(self.patterns_dir, exist_ok=True)
        
        logger.info("LearningProcessor 초기화 완료")
    
    def process_pending_learning(self) -> int:
        """
        대기 중인 학습 요청 처리
        
        Returns:
            int: 처리된 요청 수
        """
        processed_count = 0
        
        try:
            # Evolution 큐에서 대기 중인 요청 확인
            evolution_queue_files = [f for f in os.listdir(self.queue_dir) 
                                   if f.startswith("evolution_") and f.endswith(".json")]
            
            for filename in evolution_queue_files:
                filepath = os.path.join(self.queue_dir, filename)
                session_id = filename.replace("evolution_", "").replace(".json", "")
                
                try:
                    # 요청 데이터 읽기
                    with open(filepath, 'r', encoding='utf-8') as f:
                        execution_data = json.load(f)
                    
                    # 학습 처리
                    learning_result = self._process_learning(execution_data)
                    if learning_result:
                        # 학습 결과 저장
                        self._save_learning_result(session_id, learning_result)
                        
                        # 큐 파일 삭제
                        os.remove(filepath)
                        
                        processed_count += 1
                        logger.info(f"학습 처리 완료: {session_id} - 패턴 업데이트: {learning_result['pattern_updated']}")
                    
                except Exception as e:
                    logger.error(f"학습 처리 실패: {session_id} - {e}")
                    # 실패한 요청은 큐에서 제거
                    if os.path.exists(filepath):
                        os.remove(filepath)
            
            return processed_count
            
        except Exception as e:
            logger.error(f"학습 처리 중 오류: {e}")
            return processed_count
    
    def _process_learning(self, execution_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        실행 결과에 대한 학습 처리
        
        Args:
            execution_data (Dict): 실행 데이터
        
        Returns:
            Optional[Dict]: 학습 결과
        """
        try:
            session_id = execution_data.get("session_id", "")
            emotion = execution_data.get("metadata", {}).get("emotion", "")
            action = execution_data.get("action", "")
            success = execution_data.get("success", False)
            result_score = execution_data.get("result_score", 0.0)
            
            # 학습률 계산
            learning_rate = self._calculate_learning_rate(success, result_score)
            
            # 패턴 업데이트
            pattern_updated = self._update_pattern(emotion, action, success, result_score)
            
            # 인사이트 생성
            insights = self._generate_insights(emotion, action, success, result_score)
            
            return {
                "session_id": session_id,
                "emotion": emotion,
                "action": action,
                "success": success,
                "learning_rate": learning_rate,
                "pattern_updated": pattern_updated,
                "insights_generated": insights,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"학습 처리 실패: {e}")
            return None
    
    def _calculate_learning_rate(self, success: bool, result_score: float) -> float:
        """
        학습률 계산
        
        Args:
            success (bool): 성공 여부
            result_score (float): 결과 점수
        
        Returns:
            float: 학습률
        """
        base_learning_rate = 0.1
        
        if success:
            # 성공한 경우 결과 점수에 따라 학습률 조정
            learning_rate = base_learning_rate * (1.0 + result_score)
        else:
            # 실패한 경우 더 높은 학습률 (실패에서 더 많이 배움)
            learning_rate = base_learning_rate * (1.5 + (1.0 - result_score))
        
        return min(learning_rate, 0.5)  # 최대 0.5로 제한
    
    def _update_pattern(self, emotion: str, action: str, success: bool, result_score: float) -> bool:
        """
        패턴 업데이트
        
        Args:
            emotion (str): 감정
            action (str): 행동
            success (bool): 성공 여부
            result_score (float): 결과 점수
        
        Returns:
            bool: 패턴 업데이트 여부
        """
        try:
            pattern_key = f"{emotion}_{action}"
            pattern_file = os.path.join(self.patterns_dir, f"{pattern_key}.json")
            
            # 기존 패턴 로드
            if os.path.exists(pattern_file):
                with open(pattern_file, 'r', encoding='utf-8') as f:
                    pattern = json.load(f)
            else:
                pattern = {
                    "emotion": emotion,
                    "action": action,
                    "total_attempts": 0,
                    "successful_attempts": 0,
                    "total_score": 0.0,
                    "avg_score": 0.0,
                    "success_rate": 0.0,
                    "last_updated": datetime.now().isoformat()
                }
            
            # 패턴 업데이트
            pattern["total_attempts"] += 1
            if success:
                pattern["successful_attempts"] += 1
            
            pattern["total_score"] += result_score
            pattern["avg_score"] = pattern["total_score"] / pattern["total_attempts"]
            pattern["success_rate"] = pattern["successful_attempts"] / pattern["total_attempts"]
            pattern["last_updated"] = datetime.now().isoformat()
            
            # 패턴 저장
            with open(pattern_file, 'w', encoding='utf-8') as f:
                json.dump(pattern, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            logger.error(f"패턴 업데이트 실패: {e}")
            return False
    
    def _generate_insights(self, emotion: str, action: str, success: bool, result_score: float) -> List[str]:
        """
        인사이트 생성
        
        Args:
            emotion (str): 감정
            action (str): 행동
            success (bool): 성공 여부
            result_score (float): 결과 점수
        
        Returns:
            List[str]: 생성된 인사이트 목록
        """
        insights = []
        
        # 성공률 기반 인사이트
        if success and result_score > 0.8:
            insights.append(f"{emotion} 감정에 대한 {action} 행동이 매우 효과적입니다.")
        elif success and result_score > 0.6:
            insights.append(f"{emotion} 감정에 대한 {action} 행동이 효과적입니다.")
        elif not success and result_score < 0.3:
            insights.append(f"{emotion} 감정에 대한 {action} 행동이 효과적이지 않습니다.")
        
        # 감정별 특별 인사이트
        if emotion == "angry" and success:
            insights.append("분노 상황에서의 대응이 성공적입니다.")
        elif emotion == "sad" and success:
            insights.append("슬픔 상황에서의 위로가 효과적입니다.")
        elif emotion == "happy" and success:
            insights.append("기쁨 상황에서의 축하가 적절했습니다.")
        
        # 행동별 특별 인사이트
        if action == "deep_breathing_exercise" and success:
            insights.append("호흡 운동이 진정 효과가 있습니다.")
        elif action == "hug_and_speak_softly" and success:
            insights.append("부드러운 터치와 말이 위로에 효과적입니다.")
        
        return insights
    
    def _save_learning_result(self, session_id: str, result: Dict[str, Any]):
        """학습 결과 저장"""
        filepath = os.path.join(self.evolution_dir, f"{session_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    
    def get_pattern(self, emotion: str, action: str) -> Optional[Dict[str, Any]]:
        """
        패턴 조회
        
        Args:
            emotion (str): 감정
            action (str): 행동
        
        Returns:
            Optional[Dict]: 패턴 정보
        """
        pattern_key = f"{emotion}_{action}"
        pattern_file = os.path.join(self.patterns_dir, f"{pattern_key}.json")
        
        if os.path.exists(pattern_file):
            with open(pattern_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def get_all_patterns(self) -> List[Dict[str, Any]]:
        """
        모든 패턴 조회
        
        Returns:
            List[Dict]: 패턴 목록
        """
        patterns = []
        
        try:
            for filename in os.listdir(self.patterns_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.patterns_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        pattern = json.load(f)
                        patterns.append(pattern)
        except Exception as e:
            logger.error(f"패턴 조회 실패: {e}")
        
        return patterns


class EvolutionService:
    """Evolution 서비스"""
    
    def __init__(self, data_dir: str = "loop_data"):
        """
        EvolutionService 초기화
        
        Args:
            data_dir (str): 데이터 디렉토리
        """
        self.processor = LearningProcessor(data_dir)
        
        logger.info("EvolutionService 초기화 완료")
    
    def process_learning(self) -> int:
        """
        대기 중인 학습 처리
        
        Returns:
            int: 처리된 요청 수
        """
        return self.processor.process_pending_learning()
    
    def get_learning_result(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        학습 결과 조회
        
        Args:
            session_id (str): 세션 ID
        
        Returns:
            Optional[Dict]: 학습 결과
        """
        filepath = os.path.join(self.processor.evolution_dir, f"{session_id}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def get_pattern(self, emotion: str, action: str) -> Optional[Dict[str, Any]]:
        """
        패턴 조회
        
        Args:
            emotion (str): 감정
            action (str): 행동
        
        Returns:
            Optional[Dict]: 패턴 정보
        """
        return self.processor.get_pattern(emotion, action)
    
    def get_all_patterns(self) -> List[Dict[str, Any]]:
        """
        모든 패턴 조회
        
        Returns:
            List[Dict]: 패턴 목록
        """
        return self.processor.get_all_patterns()


# 전역 인스턴스
evolution_service = EvolutionService() 