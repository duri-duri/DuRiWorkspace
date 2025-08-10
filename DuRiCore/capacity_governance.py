#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 용량 거버넌스 시스템 (Capacity Governance System)
작업량과 품질을 관리하는 시스템

@preserve_identity: 기존 작업 패턴과 품질 기준 보존
@evolution_protection: 진화 과정에서의 안정성 확보
@execution_guarantee: 체계적인 작업 실행 보장
@existence_ai: 지속 가능한 진화와 성장
@final_execution: 효율적이고 안전한 최종 실행
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import math
from pathlib import Path

# DuRi 로깅 시스템 초기화
try:
    from DuRiCore.bootstrap import bootstrap_logging
    bootstrap_logging()
except ImportError:
    # 로컬 디렉토리에서 직접 import
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

class WorkloadLevel(Enum):
    """작업량 수준"""
    VERY_LOW = "very_low"      # 매우 낮음
    LOW = "low"                 # 낮음
    NORMAL = "normal"           # 정상
    HIGH = "high"               # 높음
    VERY_HIGH = "very_high"    # 매우 높음
    CRITICAL = "critical"       # 위험 수준

class PriorityLevel(Enum):
    """우선순위 수준"""
    CRITICAL = "critical"       # 최우선
    HIGH = "high"               # 높음
    MEDIUM = "medium"           # 중간
    LOW = "low"                 # 낮음
    OPTIONAL = "optional"       # 선택적

@dataclass
class WorkItem:
    """작업 항목"""
    id: str
    name: str
    description: str
    priority_level: PriorityLevel
    estimated_workload: int  # 1-10 스케일
    risk_score: int          # 1-10 스케일
    change_impact: int       # 1-10 스케일
    dependencies: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    actual_workload: Optional[int] = None
    status: str = "pending"  # pending, in_progress, completed, blocked
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CapacityMetrics:
    """용량 메트릭"""
    current_wip: int = 0
    max_wip: int = 2
    daily_loc_change: int = 0
    weekly_loc_change: int = 0
    daily_file_change: int = 0
    weekly_file_change: int = 0
    last_reset_date: Optional[datetime] = None
    total_completed_items: int = 0
    average_completion_time: float = 0.0
    capacity_utilization: float = 0.0

@dataclass
class PriorityScore:
    """우선순위 점수"""
    work_item_id: str
    base_score: float
    slo_weight: float
    dependency_weight: float
    final_score: float
    calculated_at: datetime

class CapacityGovernance:
    """DuRi 용량 거버넌스 시스템"""
    
    def __init__(self):
        self.work_items: Dict[str, WorkItem] = {}
        self.metrics = CapacityMetrics()
        self.priority_scores: List[PriorityScore] = []
        self.start_date = datetime.now()
        
        # 용량 제한 설정
        self.daily_loc_limit = 600
        self.weekly_loc_limit = 1500
        self.daily_file_limit = 25
        self.weekly_file_limit = 100
        
        # WIP 제한 설정
        self.normal_wip_limit = 2
        self.temporary_wip_limit = 3
        self.current_wip_limit = self.normal_wip_limit
        
        logger.info("DuRi 용량 거버넌스 시스템 초기화 완료")
    
    def add_work_item(self, work_item: WorkItem) -> str:
        """작업 항목 추가"""
        if work_item.id in self.work_items:
            raise ValueError(f"작업 항목 ID가 이미 존재합니다: {work_item.id}")
        
        self.work_items[work_item.id] = work_item
        
        # 우선순위 점수 계산
        priority_score = self._calculate_priority_score(work_item)
        self.priority_scores.append(priority_score)
        
        logger.info(f"작업 항목 추가: {work_item.name} (ID: {work_item.id})")
        return work_item.id
    
    def remove_work_item(self, work_item_id: str) -> bool:
        """작업 항목 제거"""
        if work_item_id in self.work_items:
            del self.work_items[work_item_id]
            
            # 우선순위 점수에서도 제거
            self.priority_scores = [ps for ps in self.priority_scores if ps.work_item_id != work_item_id]
            
            logger.info(f"작업 항목 제거: {work_item_id}")
            return True
        return False
    
    def start_work_item(self, work_item_id: str) -> bool:
        """작업 항목 시작"""
        if work_item_id not in self.work_items:
            logger.error(f"작업 항목을 찾을 수 없습니다: {work_item_id}")
            return False
        
        work_item = self.work_items[work_item_id]
        
        # WIP 제한 확인
        if self.metrics.current_wip >= self.current_wip_limit:
            logger.warning(f"WIP 제한에 도달했습니다. 현재: {self.metrics.current_wip}, 제한: {self.current_wip_limit}")
            return False
        
        # 의존성 확인
        if not self._check_dependencies(work_item):
            logger.warning(f"의존성이 해결되지 않았습니다: {work_item_id}")
            return False
        
        # 블로커 확인
        if self._check_blockers(work_item):
            logger.warning(f"블로커가 존재합니다: {work_item_id}")
            return False
        
        work_item.status = "in_progress"
        work_item.started_at = datetime.now()
        self.metrics.current_wip += 1
        
        logger.info(f"작업 항목 시작: {work_item.name} (ID: {work_item_id})")
        return True
    
    def complete_work_item(self, work_item_id: str, actual_workload: int, 
                          loc_change: int = 0, file_change: int = 0) -> bool:
        """작업 항목 완료"""
        if work_item_id not in self.work_items:
            logger.error(f"작업 항목을 찾을 수 없습니다: {work_item_id}")
            return False
        
        work_item = self.work_items[work_item_id]
        
        if work_item.status != "in_progress":
            logger.error(f"작업 항목이 진행 중이 아닙니다: {work_item_id}")
            return False
        
        work_item.status = "completed"
        work_item.completed_at = datetime.now()
        work_item.actual_workload = actual_workload
        
        # WIP 감소
        self.metrics.current_wip -= 1
        
        # 메트릭 업데이트
        self._update_metrics(loc_change, file_change)
        
        # 완료 시간 계산
        if work_item.started_at:
            completion_time = (work_item.completed_at - work_item.started_at).total_seconds()
            self._update_average_completion_time(completion_time)
        
        self.metrics.total_completed_items += 1
        
        logger.info(f"작업 항목 완료: {work_item.name} (ID: {work_item_id})")
        return True
    
    def block_work_item(self, work_item_id: str, reason: str) -> bool:
        """작업 항목 차단"""
        if work_item_id not in self.work_items:
            return False
        
        work_item = self.work_items[work_item_id]
        work_item.status = "blocked"
        work_item.metadata["block_reason"] = reason
        
        # WIP에서 제거
        if work_item.status == "in_progress":
            self.metrics.current_wip -= 1
        
        logger.info(f"작업 항목 차단: {work_item.name} (ID: {work_item_id}), 이유: {reason}")
        return True
    
    def _calculate_priority_score(self, work_item: WorkItem) -> PriorityScore:
        """우선순위 점수 계산"""
        # 기본 점수: (리스크 × 변경영향도 / 예상작업량) × w₁ × w₂
        
        # w₁: SLO 근접도 가중치 (0.8-1.2)
        slo_weight = 1.0  # 기본값, 실제로는 SLO 상태에 따라 조정
        
        # w₂: 의존도/차단도 가중치 (0.8-1.3)
        dependency_weight = 1.0
        if work_item.dependencies:
            dependency_weight = 1.1
        if work_item.blockers:
            dependency_weight = 1.3
        
        # 기본 점수 계산
        if work_item.estimated_workload == 0:
            base_score = 0
        else:
            base_score = (work_item.risk_score * work_item.change_impact) / work_item.estimated_workload
        
        # 최종 점수
        final_score = base_score * slo_weight * dependency_weight
        
        priority_score = PriorityScore(
            work_item_id=work_item.id,
            base_score=base_score,
            slo_weight=slo_weight,
            dependency_weight=dependency_weight,
            final_score=final_score,
            calculated_at=datetime.now()
        )
        
        return priority_score
    
    def _check_dependencies(self, work_item: WorkItem) -> bool:
        """의존성 확인"""
        for dep_id in work_item.dependencies:
            if dep_id not in self.work_items:
                return False
            dep_item = self.work_items[dep_id]
            if dep_item.status != "completed":
                return False
        return True
    
    def _check_blockers(self, work_item: WorkItem) -> bool:
        """블로커 확인"""
        for blocker_id in work_item.blockers:
            if blocker_id in self.work_items:
                blocker_item = self.work_items[blocker_id]
                if blocker_item.status in ["in_progress", "blocked"]:
                    return True
        return False
    
    def _update_metrics(self, loc_change: int, file_change: int):
        """메트릭 업데이트"""
        # 일일/주간 리셋 확인
        now = datetime.now()
        if not self.metrics.last_reset_date or now.date() > self.metrics.last_reset_date.date():
            self._reset_daily_metrics()
        
        # LOC 변경량 업데이트
        self.metrics.daily_loc_change += loc_change
        self.metrics.weekly_loc_change += loc_change
        
        # 파일 변경량 업데이트
        self.metrics.daily_file_change += file_change
        self.metrics.weekly_file_change += file_change
        
        # 용량 활용도 계산
        self._calculate_capacity_utilization()
    
    def _reset_daily_metrics(self):
        """일일 메트릭 리셋"""
        self.metrics.daily_loc_change = 0
        self.metrics.daily_file_change = 0
        self.metrics.last_reset_date = datetime.now()
        logger.info("일일 메트릭 리셋 완료")
    
    def _update_average_completion_time(self, completion_time: float):
        """평균 완료 시간 업데이트"""
        if self.metrics.total_completed_items == 1:
            self.metrics.average_completion_time = completion_time
        else:
            # 이동 평균 계산
            alpha = 0.1  # 가중치
            self.metrics.average_completion_time = (
                alpha * completion_time + 
                (1 - alpha) * self.metrics.average_completion_time
            )
    
    def _calculate_capacity_utilization(self):
        """용량 활용도 계산"""
        if self.current_wip_limit > 0:
            self.metrics.capacity_utilization = self.metrics.current_wip / self.current_wip_limit
        else:
            self.metrics.capacity_utilization = 0.0
    
    def get_workload_level(self) -> WorkloadLevel:
        """현재 작업량 수준 반환"""
        wip_ratio = self.metrics.current_wip / self.current_wip_limit
        
        if wip_ratio <= 0.3:
            return WorkloadLevel.VERY_LOW
        elif wip_ratio <= 0.6:
            return WorkloadLevel.LOW
        elif wip_ratio <= 0.8:
            return WorkloadLevel.NORMAL
        elif wip_ratio <= 1.0:
            return WorkloadLevel.HIGH
        elif wip_ratio <= 1.2:
            return WorkloadLevel.VERY_HIGH
        else:
            return WorkloadLevel.CRITICAL
    
    def check_capacity_limits(self) -> Dict[str, bool]:
        """용량 제한 확인"""
        return {
            "daily_loc": self.metrics.daily_loc_change <= self.daily_loc_limit,
            "weekly_loc": self.metrics.weekly_loc_change <= self.weekly_loc_limit,
            "daily_file": self.metrics.daily_file_change <= self.daily_file_limit,
            "weekly_file": self.metrics.weekly_file_change <= self.weekly_file_limit,
            "wip": self.metrics.current_wip <= self.current_wip_limit,
            "can_add_work": self.metrics.current_wip < self.current_wip_limit
        }
    
    def request_wip_increase(self, reason: str) -> bool:
        """WIP 제한 증가 요청"""
        if self.current_wip_limit < self.temporary_wip_limit:
            self.current_wip_limit = self.temporary_wip_limit
            logger.warning(f"WIP 제한 증가 승인: {self.normal_wip_limit} → {self.temporary_wip_limit}, 이유: {reason}")
            return True
        return False
    
    def restore_normal_wip_limit(self):
        """정상 WIP 제한 복원"""
        if self.current_wip_limit > self.normal_wip_limit:
            self.current_wip_limit = self.normal_wip_limit
            logger.info(f"WIP 제한 정상 복원: {self.temporary_wip_limit} → {self.normal_wip_limit}")
    
    def get_priority_queue(self) -> List[Tuple[str, float]]:
        """우선순위 큐 반환"""
        # 최신 우선순위 점수로 정렬
        latest_scores = {}
        for ps in self.priority_scores:
            if ps.work_item_id not in latest_scores or ps.calculated_at > latest_scores[ps.work_item_id].calculated_at:
                latest_scores[ps.work_item_id] = ps
        
        # 대기 중인 작업만 필터링하고 점수순 정렬
        pending_items = [
            (work_item_id, score.final_score)
            for work_item_id, score in latest_scores.items()
            if self.work_items[work_item_id].status == "pending"
        ]
        
        return sorted(pending_items, key=lambda x: x[1], reverse=True)
    
    def get_capacity_report(self) -> Dict[str, Any]:
        """용량 보고서 생성"""
        report = {
            "current_status": {
                "workload_level": self.get_workload_level().value,
                "current_wip": self.metrics.current_wip,
                "wip_limit": self.current_wip_limit,
                "capacity_utilization": self.metrics.capacity_utilization
            },
            "daily_metrics": {
                "loc_change": self.metrics.daily_loc_change,
                "loc_limit": self.daily_loc_limit,
                "file_change": self.metrics.daily_file_change,
                "file_limit": self.daily_file_limit
            },
            "weekly_metrics": {
                "loc_change": self.metrics.weekly_loc_change,
                "loc_limit": self.weekly_loc_limit,
                "file_change": self.metrics.weekly_file_change,
                "file_limit": self.weekly_file_limit
            },
            "capacity_limits": self.check_capacity_limits(),
            "work_items_summary": {
                "total": len(self.work_items),
                "pending": len([w for w in self.work_items.values() if w.status == "pending"]),
                "in_progress": len([w for w in self.work_items.values() if w.status == "in_progress"]),
                "completed": len([w for w in self.work_items.values() if w.status == "completed"]),
                "blocked": len([w for w in self.work_items.values() if w.status == "blocked"])
            },
            "performance_metrics": {
                "total_completed": self.metrics.total_completed_items,
                "average_completion_time": self.metrics.average_completion_time,
                "uptime_days": (datetime.now() - self.start_date).days
            }
        }
        
        # T8: 호환 레이어 - flat alias 추가로 기존 스크립트와의 호환성 보장
        report['current_wip'] = report['current_status']['current_wip']
        report['max_wip'] = report['current_status']['wip_limit']
        report['workload_level'] = report['current_status']['workload_level']
        
        return report
    
    def export_work_items(self) -> List[Dict[str, Any]]:
        """작업 항목 내보내기"""
        return [
            {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "priority_level": item.priority_level.value,
                "status": item.status,
                "estimated_workload": item.estimated_workload,
                "risk_score": item.risk_score,
                "change_impact": item.change_impact,
                "dependencies": item.dependencies,
                "blockers": item.blockers,
                "created_at": item.created_at.isoformat(),
                "started_at": item.started_at.isoformat() if item.started_at else None,
                "completed_at": item.completed_at.isoformat() if item.completed_at else None,
                "actual_workload": item.actual_workload,
                "metadata": item.metadata
            }
            for item in self.work_items.values()
        ]

# 전역 인스턴스
capacity_governance = CapacityGovernance()
