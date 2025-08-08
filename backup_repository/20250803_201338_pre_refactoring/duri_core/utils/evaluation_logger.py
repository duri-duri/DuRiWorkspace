"""
DuRi 평가 로그 관리 시스템

평가 기준별 상세 스코어 로그를 저장하고 관리합니다.
"""

import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class EvaluationLogger:
    """평가 로그 관리자"""
    
    def __init__(self, log_dir: str = "logs/evaluations"):
        """EvaluationLogger 초기화"""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 스레드 안전을 위한 락
        self._lock = threading.RLock()
        
        # 로그 파일별 핸들러
        self._handlers: Dict[str, Any] = {}
        
        logger.info("EvaluationLogger 초기화 완료")
    
    def log_evaluation(self, evaluation_type: str, evaluation_data: Dict[str, Any]):
        """
        평가 로그를 저장합니다.
        
        Args:
            evaluation_type: 평가 유형 (survival, dream, learning)
            evaluation_data: 평가 데이터
        """
        try:
            with self._lock:
                # 타임스탬프 추가
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'evaluation_type': evaluation_type,
                    **evaluation_data
                }
                
                # 로그 파일 경로
                log_file = self.log_dir / f"{evaluation_type}_evaluations.jsonl"
                
                # 로그 저장
                with open(log_file, 'a', encoding='utf-8') as f:
                    json.dump(log_entry, f, ensure_ascii=False)
                    f.write('\n')
                
                logger.debug(f"평가 로그 저장 완료: {evaluation_type}")
                
        except Exception as e:
            logger.error(f"평가 로그 저장 실패: {e}")
    
    def log_survival_evaluation(self, strategy_id: str, performance_score: float, 
                               emotion_score: float, combined_score: float,
                               action: str, confidence: float, reasoning: List[str]):
        """생존 평가 로그를 저장합니다."""
        self.log_evaluation("survival", {
            'strategy_id': strategy_id,
            'performance_score': performance_score,
            'emotion_score': emotion_score,
            'combined_score': combined_score,
            'action': action,
            'confidence': confidence,
            'reasoning': reasoning
        })
    
    def log_dream_evaluation(self, dream_id: str, performance_score: float,
                           novelty_score: float, stability_score: float,
                           efficiency_score: float, combined_score: float,
                           result: str, confidence: float, eureka_detected: bool):
        """Dream 평가 로그를 저장합니다."""
        self.log_evaluation("dream", {
            'dream_id': dream_id,
            'performance_score': performance_score,
            'novelty_score': novelty_score,
            'stability_score': stability_score,
            'efficiency_score': efficiency_score,
            'combined_score': combined_score,
            'result': result,
            'confidence': confidence,
            'eureka_detected': eureka_detected
        })
    
    def log_learning_evaluation(self, strategy_id: str, improvement_type: str,
                              improvement_score: float, confidence_gain: float,
                              changes_made: List[str], success: bool):
        """학습 평가 로그를 저장합니다."""
        self.log_evaluation("learning", {
            'strategy_id': strategy_id,
            'improvement_type': improvement_type,
            'improvement_score': improvement_score,
            'confidence_gain': confidence_gain,
            'changes_made': changes_made,
            'success': success
        })
    
    def get_evaluation_logs(self, evaluation_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """평가 로그를 조회합니다."""
        try:
            with self._lock:
                log_file = self.log_dir / f"{evaluation_type}_evaluations.jsonl"
                
                if not log_file.exists():
                    return []
                
                logs = []
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            logs.append(json.loads(line))
                
                # 최신 순으로 정렬하고 제한
                logs.sort(key=lambda x: x['timestamp'], reverse=True)
                return logs[:limit]
                
        except Exception as e:
            logger.error(f"평가 로그 조회 실패: {e}")
            return []
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """오래된 로그를 정리합니다."""
        try:
            with self._lock:
                cutoff_date = datetime.now() - timedelta(days=days_to_keep)
                
                for log_file in self.log_dir.glob("*_evaluations.jsonl"):
                    temp_file = log_file.with_suffix('.tmp')
                    
                    with open(log_file, 'r', encoding='utf-8') as f_in, \
                         open(temp_file, 'w', encoding='utf-8') as f_out:
                        
                        for line in f_in:
                            if line.strip():
                                log_entry = json.loads(line)
                                log_timestamp = datetime.fromisoformat(log_entry['timestamp'])
                                
                                if log_timestamp > cutoff_date:
                                    f_out.write(line)
                    
                    # 임시 파일을 원본 파일로 교체
                    temp_file.replace(log_file)
                    
                logger.info(f"{days_to_keep}일 이전 로그 정리 완료")
                
        except Exception as e:
            logger.error(f"로그 정리 실패: {e}")

# 싱글톤 인스턴스
_evaluation_logger = None

def get_evaluation_logger() -> EvaluationLogger:
    """EvaluationLogger 싱글톤 인스턴스 반환"""
    global _evaluation_logger
    if _evaluation_logger is None:
        _evaluation_logger = EvaluationLogger()
    return _evaluation_logger 