"""
DuRi Memory System - Analysis Repository Service
분석 전용 저장소 서비스
"""
import logging
import json
import hashlib
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from sqlalchemy import text
from sqlalchemy.orm import Session
from ..database.database import get_db_session
from ..decorators.memory_logger import log_important_event, log_system_event

logger = logging.getLogger(__name__)

class AnalysisStatus(Enum):
    """분석 상태"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AnalysisResult:
    """분석 결과 데이터 클래스"""
    analysis_id: str
    analysis_type: str
    status: AnalysisStatus
    parameters: Dict[str, Any]
    results: Dict[str, Any]
    execution_time_ms: int
    memory_usage_mb: float
    created_at: datetime

class AnalysisRepositoryService:
    """분석 전용 저장소 서비스"""
    
    def __init__(self):
        self.db = next(get_db_session())
    
    def save_analysis_result(
        self,
        analysis_id: str,
        analysis_type: str,
        parameters: Dict[str, Any],
        results: Dict[str, Any],
        execution_time_ms: int,
        memory_usage_mb: float,
        status: str = "completed"
    ) -> bool:
        """분석 결과 저장"""
        try:
            query = text("""
                INSERT INTO analysis_results 
                (analysis_id, analysis_type, status, parameters, results, execution_time_ms, memory_usage_mb)
                VALUES (:analysis_id, :analysis_type, :status, :parameters, :results, :execution_time_ms, :memory_usage_mb)
                ON CONFLICT (analysis_id) 
                DO UPDATE SET 
                    status = EXCLUDED.status,
                    results = EXCLUDED.results,
                    execution_time_ms = EXCLUDED.execution_time_ms,
                    memory_usage_mb = EXCLUDED.memory_usage_mb,
                    updated_at = CURRENT_TIMESTAMP
            """)
            
            self.db.execute(query, {
                "analysis_id": analysis_id,
                "analysis_type": analysis_type,
                "status": status,
                "parameters": json.dumps(parameters),
                "results": json.dumps(results),
                "execution_time_ms": execution_time_ms,
                "memory_usage_mb": memory_usage_mb
            })
            
            self.db.commit()
            
            log_important_event(
                f"분석 결과 저장: {analysis_id}",
                f"타입: {analysis_type}, 실행시간: {execution_time_ms}ms",
                importance_score=50
            )
            
            return True
            
        except Exception as e:
            logger.error(f"분석 결과 저장 실패: {e}")
            self.db.rollback()
            return False
    
    def get_analysis_result(self, analysis_id: str) -> Optional[AnalysisResult]:
        """분석 결과 조회"""
        try:
            query = text("""
                SELECT analysis_id, analysis_type, status, parameters, results, 
                       execution_time_ms, memory_usage_mb, created_at
                FROM analysis_results 
                WHERE analysis_id = :analysis_id
            """)
            
            result = self.db.execute(query, {"analysis_id": analysis_id}).fetchone()
            
            if result:
                return AnalysisResult(
                    analysis_id=result.analysis_id,
                    analysis_type=result.analysis_type,
                    status=AnalysisStatus(result.status),
                    parameters=json.loads(result.parameters) if result.parameters else {},
                    results=json.loads(result.results) if result.results else {},
                    execution_time_ms=result.execution_time_ms or 0,
                    memory_usage_mb=float(result.memory_usage_mb or 0),
                    created_at=result.created_at
                )
            
            return None
            
        except Exception as e:
            logger.error(f"분석 결과 조회 실패: {e}")
            return None
    
    def save_pattern_cache(
        self,
        pattern_type: str,
        pattern_data: Dict[str, Any],
        memory_ids: List[int],
        confidence_score: float = 0.0
    ) -> bool:
        """패턴 캐시 저장"""
        try:
            # 패턴 해시 생성
            pattern_hash = hashlib.md5(
                json.dumps(pattern_data, sort_keys=True).encode()
            ).hexdigest()
            
            query = text("""
                INSERT INTO pattern_cache 
                (pattern_hash, pattern_type, pattern_data, frequency, confidence_score, memory_ids)
                VALUES (:pattern_hash, :pattern_type, :pattern_data, 1, :confidence_score, :memory_ids)
                ON CONFLICT (pattern_hash) 
                DO UPDATE SET 
                    frequency = pattern_cache.frequency + 1,
                    last_detected = CURRENT_TIMESTAMP,
                    memory_ids = array_cat(pattern_cache.memory_ids, :memory_ids),
                    updated_at = CURRENT_TIMESTAMP
            """)
            
            self.db.execute(query, {
                "pattern_hash": pattern_hash,
                "pattern_type": pattern_type,
                "pattern_data": json.dumps(pattern_data),
                "confidence_score": confidence_score,
                "memory_ids": memory_ids
            })
            
            self.db.commit()
            
            log_system_event(
                f"패턴 캐시 저장: {pattern_hash[:8]}...",
                f"타입: {pattern_type}, 빈도: +1",
                importance_score=40
            )
            
            return True
            
        except Exception as e:
            logger.error(f"패턴 캐시 저장 실패: {e}")
            self.db.rollback()
            return False
    
    def get_pattern_cache(
        self,
        pattern_type: str = None,
        min_frequency: int = 1,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """패턴 캐시 조회"""
        try:
            query = text("""
                SELECT pattern_hash, pattern_type, pattern_data, frequency, 
                       confidence_score, first_detected, last_detected, memory_ids
                FROM pattern_cache 
                WHERE frequency >= :min_frequency
                AND (:pattern_type IS NULL OR pattern_type = :pattern_type)
                ORDER BY frequency DESC, last_detected DESC
                LIMIT :limit
            """)
            
            results = self.db.execute(query, {
                "pattern_type": pattern_type,
                "min_frequency": min_frequency,
                "limit": limit
            }).fetchall()
            
            patterns = []
            for result in results:
                patterns.append({
                    "pattern_hash": result.pattern_hash,
                    "pattern_type": result.pattern_type,
                    "pattern_data": json.loads(result.pattern_data),
                    "frequency": result.frequency,
                    "confidence_score": float(result.confidence_score or 0),
                    "first_detected": result.first_detected.isoformat(),
                    "last_detected": result.last_detected.isoformat(),
                    "memory_ids": result.memory_ids or []
                })
            
            return patterns
            
        except Exception as e:
            logger.error(f"패턴 캐시 조회 실패: {e}")
            return []
    
    def save_performance_metric(
        self,
        metric_type: str,
        metric_name: str,
        metric_value: float,
        metric_unit: str = "",
        metadata: Dict[str, Any] = None
    ) -> bool:
        """성능 메트릭 저장"""
        try:
            query = text("""
                INSERT INTO performance_metrics 
                (metric_type, metric_name, metric_value, metric_unit, metadata)
                VALUES (:metric_type, :metric_name, :metric_value, :metric_unit, :metadata)
            """)
            
            self.db.execute(query, {
                "metric_type": metric_type,
                "metric_name": metric_name,
                "metric_value": metric_value,
                "metric_unit": metric_unit,
                "metadata": json.dumps(metadata) if metadata else None
            })
            
            self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"성능 메트릭 저장 실패: {e}")
            self.db.rollback()
            return False
    
    def get_performance_metrics(
        self,
        metric_type: str = None,
        hours: int = 24,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """성능 메트릭 조회"""
        try:
            query = text("""
                SELECT metric_timestamp, metric_type, metric_name, metric_value, metric_unit, metadata
                FROM performance_metrics 
                WHERE metric_timestamp >= NOW() - INTERVAL ':hours hours'
                AND (:metric_type IS NULL OR metric_type = :metric_type)
                ORDER BY metric_timestamp DESC
                LIMIT :limit
            """)
            
            results = self.db.execute(query, {
                "metric_type": metric_type,
                "hours": hours,
                "limit": limit
            }).fetchall()
            
            metrics = []
            for result in results:
                metrics.append({
                    "timestamp": result.metric_timestamp.isoformat(),
                    "type": result.metric_type,
                    "name": result.metric_name,
                    "value": float(result.metric_value or 0),
                    "unit": result.metric_unit,
                    "metadata": json.loads(result.metadata) if result.metadata else {}
                })
            
            return metrics
            
        except Exception as e:
            logger.error(f"성능 메트릭 조회 실패: {e}")
            return []
    
    def save_correlation_analysis(
        self,
        correlation_id: str,
        source_type: str,
        target_type: str,
        correlation_strength: float,
        confidence_score: float,
        sample_size: int,
        analysis_window_hours: int,
        correlation_data: Dict[str, Any]
    ) -> bool:
        """상관관계 분석 결과 저장"""
        try:
            query = text("""
                INSERT INTO correlation_analysis 
                (correlation_id, source_type, target_type, correlation_strength, 
                 confidence_score, sample_size, analysis_window_hours, correlation_data)
                VALUES (:correlation_id, :source_type, :target_type, :correlation_strength,
                        :confidence_score, :sample_size, :analysis_window_hours, :correlation_data)
                ON CONFLICT (correlation_id) 
                DO UPDATE SET 
                    correlation_strength = EXCLUDED.correlation_strength,
                    confidence_score = EXCLUDED.confidence_score,
                    sample_size = EXCLUDED.sample_size,
                    correlation_data = EXCLUDED.correlation_data,
                    updated_at = CURRENT_TIMESTAMP
            """)
            
            self.db.execute(query, {
                "correlation_id": correlation_id,
                "source_type": source_type,
                "target_type": target_type,
                "correlation_strength": correlation_strength,
                "confidence_score": confidence_score,
                "sample_size": sample_size,
                "analysis_window_hours": analysis_window_hours,
                "correlation_data": json.dumps(correlation_data)
            })
            
            self.db.commit()
            
            log_important_event(
                f"상관관계 분석 저장: {correlation_id}",
                f"{source_type} ↔ {target_type}, 강도: {correlation_strength:.3f}",
                importance_score=55
            )
            
            return True
            
        except Exception as e:
            logger.error(f"상관관계 분석 저장 실패: {e}")
            self.db.rollback()
            return False
    
    def update_analysis_statistics(
        self,
        analysis_type: str,
        success: bool = True,
        execution_time_ms: int = 0,
        memory_usage_mb: float = 0,
        patterns_found: int = 0,
        correlations_found: int = 0
    ) -> bool:
        """분석 통계 업데이트"""
        try:
            query = text("""
                INSERT INTO analysis_statistics 
                (stat_date, analysis_type, total_analyses, successful_analyses, failed_analyses,
                 avg_execution_time_ms, avg_memory_usage_mb, patterns_found, correlations_found)
                VALUES (CURRENT_DATE, :analysis_type, 1, :success_count, :fail_count,
                        :execution_time_ms, :memory_usage_mb, :patterns_found, :correlations_found)
                ON CONFLICT (stat_date, analysis_type) 
                DO UPDATE SET 
                    total_analyses = analysis_statistics.total_analyses + 1,
                    successful_analyses = analysis_statistics.successful_analyses + :success_count,
                    failed_analyses = analysis_statistics.failed_analyses + :fail_count,
                    avg_execution_time_ms = (analysis_statistics.avg_execution_time_ms * analysis_statistics.total_analyses + :execution_time_ms) / (analysis_statistics.total_analyses + 1),
                    avg_memory_usage_mb = (analysis_statistics.avg_memory_usage_mb * analysis_statistics.total_analyses + :memory_usage_mb) / (analysis_statistics.total_analyses + 1),
                    patterns_found = analysis_statistics.patterns_found + :patterns_found,
                    correlations_found = analysis_statistics.correlations_found + :correlations_found,
                    updated_at = CURRENT_TIMESTAMP
            """)
            
            success_count = 1 if success else 0
            fail_count = 0 if success else 1
            
            self.db.execute(query, {
                "analysis_type": analysis_type,
                "success_count": success_count,
                "fail_count": fail_count,
                "execution_time_ms": execution_time_ms,
                "memory_usage_mb": memory_usage_mb,
                "patterns_found": patterns_found,
                "correlations_found": correlations_found
            })
            
            self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"분석 통계 업데이트 실패: {e}")
            self.db.rollback()
            return False
    
    def get_analysis_statistics(
        self,
        days: int = 7
    ) -> Dict[str, Any]:
        """분석 통계 조회"""
        try:
            query = text("""
                SELECT stat_date, analysis_type, total_analyses, successful_analyses, failed_analyses,
                       avg_execution_time_ms, avg_memory_usage_mb, patterns_found, correlations_found
                FROM analysis_statistics 
                WHERE stat_date >= CURRENT_DATE - INTERVAL ':days days'
                ORDER BY stat_date DESC, analysis_type
            """)
            
            results = self.db.execute(query, {"days": days}).fetchall()
            
            stats = {}
            for result in results:
                date_str = result.stat_date.isoformat()
                if date_str not in stats:
                    stats[date_str] = {}
                
                stats[date_str][result.analysis_type] = {
                    "total_analyses": result.total_analyses,
                    "successful_analyses": result.successful_analyses,
                    "failed_analyses": result.failed_analyses,
                    "avg_execution_time_ms": result.avg_execution_time_ms,
                    "avg_memory_usage_mb": float(result.avg_memory_usage_mb or 0),
                    "patterns_found": result.patterns_found,
                    "correlations_found": result.correlations_found
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"분석 통계 조회 실패: {e}")
            return {}

# 전역 인스턴스
analysis_repository_service = AnalysisRepositoryService() 