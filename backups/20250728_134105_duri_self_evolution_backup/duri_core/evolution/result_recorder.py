#!/usr/bin/env python3
"""
Result Recorder - 실행 결과 기록 시스템

행동 실행 결과를 기록하고 성공/실패 통계를 누적 저장합니다.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from duri_common.logger import get_logger
from .action_executor import ExecutionResult, ExecutionContext

logger = get_logger("duri_evolution.result_recorder")


@dataclass
class RecordedResult:
    """기록된 결과"""
    result_id: str
    emotion: str
    action: str
    success: bool
    result_score: float
    execution_time: float
    feedback_text: str
    context: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: str
    session_id: Optional[str] = None


@dataclass
class ExperienceEntry:
    """경험 데이터 엔트리"""
    emotion_action_pair: str
    emotion: str
    action: str
    total_attempts: int
    successful_attempts: int
    avg_score: float
    avg_execution_time: float
    success_rate: float
    last_updated: str
    metadata: Dict[str, Any]


class ResultRecorder:
    """실행 결과 기록기"""
    
    def __init__(self, data_dir: str = "evolution_data", log_file: str = "evolution_log.json"):
        """
        ResultRecorder 초기화
        
        Args:
            data_dir (str): 데이터 저장 디렉토리
            log_file (str): 로그 파일 경로
        """
        self.data_dir = data_dir
        self.results_dir = os.path.join(data_dir, "results")
        self.experience_dir = os.path.join(data_dir, "experience")
        self.statistics_dir = os.path.join(data_dir, "statistics")
        self.log_file = log_file
        
        # 디렉토리 생성
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.experience_dir, exist_ok=True)
        os.makedirs(self.statistics_dir, exist_ok=True)
        
        # 파일이 없으면 생성
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                pass
        
        logger.info(f"ResultRecorder 초기화 완료: {data_dir}")
    
    def record_execution_result(
        self,
        execution_result: ExecutionResult,
        context: ExecutionContext
    ) -> RecordedResult:
        """
        실행 결과 기록
        
        Args:
            execution_result (ExecutionResult): 실행 결과
            context (ExecutionContext): 실행 컨텍스트
        
        Returns:
            RecordedResult: 기록된 결과
        """
        result_id = self._generate_result_id(execution_result, context)
        
        recorded_result = RecordedResult(
            result_id=result_id,
            emotion=context.emotion,
            action=execution_result.action,
            success=execution_result.success,
            result_score=execution_result.result_score,
            execution_time=execution_result.execution_time,
            feedback_text=execution_result.feedback_text,
            context=asdict(context),
            metadata=execution_result.metadata,
            timestamp=execution_result.timestamp,
            session_id=context.session_id
        )
        
        # 결과 저장
        self._save_result(recorded_result)
        
        # 경험 데이터 업데이트
        self._update_experience_data(recorded_result)
        
        # 통계 업데이트
        self._update_statistics(recorded_result)
        
        logger.info(f"실행 결과 기록: {result_id} - {context.emotion} -> {execution_result.action} (성공: {execution_result.success})")
        return recorded_result
    
    def get_result_history(
        self,
        emotion: Optional[str] = None,
        action: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 100
    ) -> List[RecordedResult]:
        """
        결과 히스토리 조회
        
        Args:
            emotion (str, optional): 특정 감정 필터링
            action (str, optional): 특정 액션 필터링
            session_id (str, optional): 특정 세션 필터링
            limit (int): 조회할 최대 개수
        
        Returns:
            List[RecordedResult]: 결과 히스토리
        """
        history = []
        
        try:
            # 모든 결과 파일 읽기
            for filename in os.listdir(self.results_dir):
                if not filename.endswith('.json'):
                    continue
                
                filepath = os.path.join(self.results_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    recorded_result = RecordedResult(**data)
                    
                    # 필터링
                    if emotion and recorded_result.emotion != emotion:
                        continue
                    if action and recorded_result.action != action:
                        continue
                    if session_id and recorded_result.session_id != session_id:
                        continue
                    
                    history.append(recorded_result)
            
            # 시간순 정렬 (최신순)
            history.sort(key=lambda x: x.timestamp, reverse=True)
            
            # 개수 제한
            return history[:limit]
            
        except Exception as e:
            logger.error(f"결과 히스토리 조회 실패: {e}")
            return []
    
    def get_experience_data(
        self,
        emotion: Optional[str] = None,
        action: Optional[str] = None,
        min_attempts: int = 0
    ) -> List[ExperienceEntry]:
        """
        경험 데이터 조회
        
        Args:
            emotion (str, optional): 특정 감정 필터링
            action (str, optional): 특정 액션 필터링
            min_attempts (int): 최소 시도 횟수 필터링
        
        Returns:
            List[ExperienceEntry]: 경험 데이터 목록
        """
        experience_data = []
        
        try:
            # 모든 경험 파일 읽기
            for filename in os.listdir(self.experience_dir):
                if not filename.endswith('.json'):
                    continue
                
                filepath = os.path.join(self.experience_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    experience_entry = ExperienceEntry(**data)
                    
                    # 필터링
                    if emotion and experience_entry.emotion != emotion:
                        continue
                    if action and experience_entry.action != action:
                        continue
                    if experience_entry.total_attempts < min_attempts:
                        continue
                    
                    experience_data.append(experience_entry)
            
            # 성공률순 정렬 (높은 순)
            experience_data.sort(key=lambda x: x.success_rate, reverse=True)
            
            return experience_data
            
        except Exception as e:
            logger.error(f"경험 데이터 조회 실패: {e}")
            return []
    
    def get_success_rate_for_combination(
        self,
        emotion: str,
        action: str
    ) -> Optional[float]:
        """
        특정 감정-액션 조합의 성공률 조회
        
        Args:
            emotion (str): 감정
            action (str): 액션
        
        Returns:
            Optional[float]: 성공률 (0.0 ~ 1.0), 데이터가 없으면 None
        """
        pair_key = f"{emotion}_{action}"
        filename = f"experience_{pair_key}.json"
        filepath = os.path.join(self.experience_dir, filename)
        
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('success_rate', 0.0)
        except Exception as e:
            logger.error(f"성공률 조회 실패: {emotion} -> {action} - {e}")
        
        return None
    
    def get_emotion_action_statistics(self) -> Dict[str, Any]:
        """
        감정-액션 조합별 통계 조회
        
        Returns:
            Dict: 감정-액션 통계
        """
        experience_data = self.get_experience_data()
        
        stats = {}
        for entry in experience_data:
            key = f"{entry.emotion}_{entry.action}"
            stats[key] = {
                'emotion': entry.emotion,
                'action': entry.action,
                'total_attempts': entry.total_attempts,
                'successful_attempts': entry.successful_attempts,
                'success_rate': entry.success_rate,
                'avg_score': entry.avg_score,
                'avg_execution_time': entry.avg_execution_time,
                'last_updated': entry.last_updated
            }
        
        return stats
    
    def get_overall_statistics(self) -> Dict[str, Any]:
        """
        전체 통계 조회
        
        Returns:
            Dict: 전체 통계
        """
        try:
            stats_file = os.path.join(self.statistics_dir, "overall_statistics.json")
            if os.path.exists(stats_file):
                with open(stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"전체 통계 조회 실패: {e}")
        
        return {}
    
    def _generate_result_id(self, execution_result: ExecutionResult, context: ExecutionContext) -> str:
        """결과 ID 생성"""
        timestamp = execution_result.timestamp.replace(':', '-').replace('.', '-')
        return f"result_{context.emotion}_{execution_result.action}_{timestamp}"
    
    def _save_result(self, recorded_result: RecordedResult):
        """결과를 파일로 저장"""
        try:
            filename = f"result_{recorded_result.result_id}.json"
            filepath = os.path.join(self.results_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(recorded_result), f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"결과 저장 실패: {e}")
    
    def _update_experience_data(self, recorded_result: RecordedResult):
        """경험 데이터 업데이트"""
        try:
            pair_key = f"{recorded_result.emotion}_{recorded_result.action}"
            filename = f"experience_{pair_key}.json"
            filepath = os.path.join(self.experience_dir, filename)
            
            # 기존 경험 데이터 읽기
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    experience_entry = ExperienceEntry(**data)
            else:
                # 새로운 경험 엔트리 생성
                experience_entry = ExperienceEntry(
                    emotion_action_pair=pair_key,
                    emotion=recorded_result.emotion,
                    action=recorded_result.action,
                    total_attempts=0,
                    successful_attempts=0,
                    avg_score=0.0,
                    avg_execution_time=0.0,
                    success_rate=0.0,
                    last_updated=datetime.now().isoformat(),
                    metadata={}
                )
            
            # 통계 업데이트
            experience_entry.total_attempts += 1
            if recorded_result.success:
                experience_entry.successful_attempts += 1
            
            # 평균값 업데이트
            total_attempts = experience_entry.total_attempts
            experience_entry.avg_score = (
                (experience_entry.avg_score * (total_attempts - 1) + recorded_result.result_score) 
                / total_attempts
            )
            experience_entry.avg_execution_time = (
                (experience_entry.avg_execution_time * (total_attempts - 1) + recorded_result.execution_time) 
                / total_attempts
            )
            
            # 성공률 계산
            experience_entry.success_rate = experience_entry.successful_attempts / total_attempts
            experience_entry.last_updated = datetime.now().isoformat()
            
            # 메타데이터 업데이트
            if 'recent_results' not in experience_entry.metadata:
                experience_entry.metadata['recent_results'] = []
            
            recent_results = experience_entry.metadata['recent_results']
            recent_results.append({
                'success': recorded_result.success,
                'score': recorded_result.result_score,
                'timestamp': recorded_result.timestamp
            })
            
            # 최근 10개만 유지
            if len(recent_results) > 10:
                experience_entry.metadata['recent_results'] = recent_results[-10:]
            
            # 경험 데이터 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(experience_entry), f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"경험 데이터 업데이트 실패: {e}")
    
    def _update_statistics(self, recorded_result: RecordedResult):
        """전체 통계 업데이트"""
        try:
            stats_file = os.path.join(self.statistics_dir, "overall_statistics.json")
            
            # 기존 통계 읽기
            if os.path.exists(stats_file):
                with open(stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
            else:
                stats = {
                    'total_results': 0,
                    'successful_results': 0,
                    'overall_success_rate': 0.0,
                    'avg_score': 0.0,
                    'avg_execution_time': 0.0,
                    'emotion_counts': {},
                    'action_counts': {},
                    'last_updated': datetime.now().isoformat()
                }
            
            # 통계 업데이트
            stats['total_results'] += 1
            if recorded_result.success:
                stats['successful_results'] += 1
            
            # 평균값 업데이트
            total_results = stats['total_results']
            stats['avg_score'] = (
                (stats['avg_score'] * (total_results - 1) + recorded_result.result_score) 
                / total_results
            )
            stats['avg_execution_time'] = (
                (stats['avg_execution_time'] * (total_results - 1) + recorded_result.execution_time) 
                / total_results
            )
            
            # 성공률 계산
            stats['overall_success_rate'] = stats['successful_results'] / total_results
            
            # 감정별 카운트
            emotion = recorded_result.emotion
            if emotion not in stats['emotion_counts']:
                stats['emotion_counts'][emotion] = 0
            stats['emotion_counts'][emotion] += 1
            
            # 액션별 카운트
            action = recorded_result.action
            if action not in stats['action_counts']:
                stats['action_counts'][action] = 0
            stats['action_counts'][action] += 1
            
            stats['last_updated'] = datetime.now().isoformat()
            
            # 통계 저장
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"통계 업데이트 실패: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """기록 통계 조회"""
        try:
            result_count = len([f for f in os.listdir(self.results_dir) if f.endswith('.json')])
            experience_count = len([f for f in os.listdir(self.experience_dir) if f.endswith('.json')])
            
            overall_stats = self.get_overall_statistics()
            
            return {
                'total_results': result_count,
                'total_experience_entries': experience_count,
                'overall_statistics': overall_stats
            }
            
        except Exception as e:
            logger.error(f"통계 조회 실패: {e}")
            return {}
    
    def write_result(self, emotion: str, action: str, result: dict):
        """
        감정, 행동, 실행 결과를 받아 evolution_log.json 파일에 append 방식으로 저장
        Args:
            emotion (str): 감정
            action (str): 행동
            result (dict): 실행 결과
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'emotion': emotion,
            'action': action,
            'result': result
        }
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def log_action_result(self, emotion: str, action: str, success: bool, details: str, timestamp: str = None):
        """
        행동 실행 결과를 decision_log.json에 append 형태로 저장하여 판단 히스토리 추적
        Args:
            emotion (str): 감정
            action (str): 행동
            success (bool): 성공 여부
            details (str): 실행 상세 내용
            timestamp (str, optional): 타임스탬프 (None이면 현재 시간)
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        decision_log_file = os.path.join(self.data_dir, "decision_log.json")
        
        log_entry = {
            'timestamp': timestamp,
            'emotion': emotion,
            'action': action,
            'success': success,
            'details': details,
            'session_id': None  # 향후 세션 ID 추가 가능
        }
        
        try:
            with open(decision_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            
            logger.info(f"판단 히스토리 저장: {emotion} -> {action} ({'성공' if success else '실패'})")
            
        except Exception as e:
            logger.error(f"판단 히스토리 저장 실패: {e}")
    
    def get_decision_history(self, emotion: str = None, action: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        판단 히스토리 조회
        Args:
            emotion (str, optional): 특정 감정 필터링
            action (str, optional): 특정 행동 필터링
            limit (int): 조회할 최대 개수
        Returns:
            List[Dict[str, Any]]: 판단 히스토리 목록
        """
        decision_log_file = os.path.join(self.data_dir, "decision_log.json")
        
        if not os.path.exists(decision_log_file):
            return []
        
        history = []
        try:
            with open(decision_log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        
                        # 필터링
                        if emotion and entry.get('emotion') != emotion:
                            continue
                        if action and entry.get('action') != action:
                            continue
                        
                        history.append(entry)
            
            # 시간순 정렬 (최신순)
            history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return history[:limit] 

        except Exception as e:
            logger.error(f"판단 히스토리 조회 실패: {e}")
            return []
