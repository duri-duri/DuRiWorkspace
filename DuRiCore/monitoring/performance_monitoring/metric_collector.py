#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-4: 성능 메트릭 수집 모듈

실시간 성능 메트릭을 수집하고 관리하는 모듈입니다.
- 성능 메트릭 수집
- 메트릭 저장 및 관리
- 메트릭 검증
- 메트릭 통계
"""

import json
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import uuid
import statistics
import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """메트릭 유형"""
    PERFORMANCE = "performance"
    RESOURCE = "resource"
    ERROR = "error"
    CUSTOM = "custom"
    SYSTEM = "system"

class MetricStatus(Enum):
    """메트릭 상태"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    EXPIRED = "expired"

@dataclass
class PerformanceMetric:
    """성능 메트릭"""
    metric_id: str
    metric_type: MetricType
    metric_name: str
    value: float
    unit: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    status: MetricStatus = MetricStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetricCollection:
    """메트릭 수집"""
    collection_id: str
    collection_name: str
    metrics: List[PerformanceMetric] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)

class MetricCollector:
    """성능 메트릭 수집기"""
    
    def __init__(self):
        """초기화"""
        self.metrics: Dict[str, PerformanceMetric] = {}
        self.collections: Dict[str, MetricCollection] = {}
        self.metric_history: List[PerformanceMetric] = []
        
        # 수집 설정
        self.collection_config = {
            "max_metrics": 10000,
            "retention_period": timedelta(hours=24),
            "collection_interval": 1.0,
            "batch_size": 100
        }
        
        # 성능 메트릭
        self.performance_metrics = {
            "total_metrics_collected": 0,
            "active_collections": 0,
            "average_collection_time": 0.0,
            "collection_success_rate": 0.0
        }
        
        # 메트릭 큐
        self.metric_queue = asyncio.Queue()
        
        logger.info("성능 메트릭 수집기 초기화 완료")
    
    async def collect_metric(self, metric_type: MetricType, metric_name: str,
                           value: float, unit: str = "", source: str = "",
                           metadata: Dict[str, Any] = None) -> str:
        """메트릭 수집"""
        try:
            metric_id = f"metric_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            metric = PerformanceMetric(
                metric_id=metric_id,
                metric_type=metric_type,
                metric_name=metric_name,
                value=value,
                unit=unit,
                source=source,
                metadata=metadata or {}
            )
            
            # 메트릭 저장
            self.metrics[metric_id] = metric
            self.metric_history.append(metric)
            
            # 큐에 추가
            await self.metric_queue.put(metric)
            
            # 성능 메트릭 업데이트
            self.performance_metrics["total_metrics_collected"] += 1
            
            logger.info(f"메트릭 수집 완료: {metric_id} ({metric_name}: {value}{unit})")
            return metric_id
            
        except Exception as e:
            logger.error(f"메트릭 수집 실패: {e}")
            return ""
    
    async def start_collection(self, collection_name: str) -> str:
        """메트릭 수집 시작"""
        try:
            collection_id = f"collection_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            collection = MetricCollection(
                collection_id=collection_id,
                collection_name=collection_name
            )
            
            self.collections[collection_id] = collection
            self.performance_metrics["active_collections"] += 1
            
            logger.info(f"메트릭 수집 시작: {collection_id} ({collection_name})")
            return collection_id
            
        except Exception as e:
            logger.error(f"메트릭 수집 시작 실패: {e}")
            return ""
    
    async def stop_collection(self, collection_id: str) -> bool:
        """메트릭 수집 중지"""
        try:
            if collection_id in self.collections:
                collection = self.collections[collection_id]
                collection.end_time = datetime.now()
                collection.status = "completed"
                
                self.performance_metrics["active_collections"] -= 1
                
                logger.info(f"메트릭 수집 중지: {collection_id}")
                return True
            else:
                logger.warning(f"수집을 찾을 수 없음: {collection_id}")
                return False
                
        except Exception as e:
            logger.error(f"메트릭 수집 중지 실패: {e}")
            return False
    
    async def get_metrics_by_type(self, metric_type: MetricType, 
                                time_range: timedelta = None) -> List[PerformanceMetric]:
        """유형별 메트릭 조회"""
        try:
            current_time = datetime.now()
            start_time = current_time - time_range if time_range else datetime.min
            
            metrics = []
            for metric in self.metric_history:
                if (metric.metric_type == metric_type and 
                    metric.timestamp >= start_time and 
                    metric.status == MetricStatus.ACTIVE):
                    metrics.append(metric)
            
            return metrics
            
        except Exception as e:
            logger.error(f"메트릭 조회 실패: {e}")
            return []
    
    async def get_metrics_by_source(self, source: str, 
                                  time_range: timedelta = None) -> List[PerformanceMetric]:
        """소스별 메트릭 조회"""
        try:
            current_time = datetime.now()
            start_time = current_time - time_range if time_range else datetime.min
            
            metrics = []
            for metric in self.metric_history:
                if (metric.source == source and 
                    metric.timestamp >= start_time and 
                    metric.status == MetricStatus.ACTIVE):
                    metrics.append(metric)
            
            return metrics
            
        except Exception as e:
            logger.error(f"메트릭 조회 실패: {e}")
            return []
    
    async def get_metric_statistics(self, metric_name: str, 
                                  time_range: timedelta = None) -> Dict[str, Any]:
        """메트릭 통계 조회"""
        try:
            current_time = datetime.now()
            start_time = current_time - time_range if time_range else datetime.min
            
            values = []
            for metric in self.metric_history:
                if (metric.metric_name == metric_name and 
                    metric.timestamp >= start_time and 
                    metric.status == MetricStatus.ACTIVE):
                    values.append(metric.value)
            
            if not values:
                return {}
            
            statistics_data = {
                "metric_name": metric_name,
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "std": statistics.stdev(values) if len(values) > 1 else 0.0,
                "time_range": time_range.total_seconds() if time_range else None
            }
            
            return statistics_data
            
        except Exception as e:
            logger.error(f"메트릭 통계 조회 실패: {e}")
            return {}
    
    async def cleanup_expired_metrics(self) -> int:
        """만료된 메트릭 정리"""
        try:
            current_time = datetime.now()
            cutoff_time = current_time - self.collection_config["retention_period"]
            
            expired_count = 0
            
            # 만료된 메트릭 찾기
            expired_metrics = []
            for metric in self.metric_history:
                if metric.timestamp < cutoff_time:
                    expired_metrics.append(metric.metric_id)
                    metric.status = MetricStatus.EXPIRED
                    expired_count += 1
            
            # 만료된 메트릭 제거
            for metric_id in expired_metrics:
                if metric_id in self.metrics:
                    del self.metrics[metric_id]
            
            logger.info(f"만료된 메트릭 정리 완료: {expired_count}개")
            return expired_count
            
        except Exception as e:
            logger.error(f"만료된 메트릭 정리 실패: {e}")
            return 0
    
    async def get_collection_report(self, collection_id: str) -> Dict[str, Any]:
        """수집 보고서 생성"""
        try:
            if collection_id not in self.collections:
                return {}
            
            collection = self.collections[collection_id]
            
            # 수집된 메트릭 수 계산
            metrics_count = len([m for m in self.metric_history 
                               if m.timestamp >= collection.start_time and 
                               (collection.end_time is None or m.timestamp <= collection.end_time)])
            
            report = {
                "collection_id": collection_id,
                "collection_name": collection.collection_name,
                "start_time": collection.start_time.isoformat(),
                "end_time": collection.end_time.isoformat() if collection.end_time else None,
                "status": collection.status,
                "metrics_count": metrics_count,
                "duration": (collection.end_time - collection.start_time).total_seconds() if collection.end_time else None
            }
            
            return report
            
        except Exception as e:
            logger.error(f"수집 보고서 생성 실패: {e}")
            return {}
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """성능 요약 조회"""
        try:
            summary = {
                "total_metrics": len(self.metrics),
                "active_collections": self.performance_metrics["active_collections"],
                "total_collected": self.performance_metrics["total_metrics_collected"],
                "collection_success_rate": self.performance_metrics["collection_success_rate"],
                "average_collection_time": self.performance_metrics["average_collection_time"],
                "retention_period": self.collection_config["retention_period"].total_seconds(),
                "max_metrics": self.collection_config["max_metrics"]
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"성능 요약 조회 실패: {e}")
            return {}
