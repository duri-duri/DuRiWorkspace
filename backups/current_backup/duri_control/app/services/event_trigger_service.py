import logging
import time
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from ..database.database import get_db_session
from ..decorators.memory_logger import log_important_event, log_system_event

logger = logging.getLogger(__name__)


class TriggerType(Enum):
    """트리거 타입"""
    COUNT = "count"           # 횟수 기반
    TIME = "time"            # 시간 기반
    PATTERN = "pattern"      # 패턴 기반
    THRESHOLD = "threshold"  # 임계값 기반


@dataclass
class TriggerCondition:
    """트리거 조건"""
    trigger_type: TriggerType
    target_type: str          # 대상 메모리 타입
    condition_value: Any      # 조건값
    action: str              # 실행할 액션
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0


class EventTriggerService:
    """이벤트 트리거 서비스"""
    
    def __init__(self):
        self.triggers: List[TriggerCondition] = []
        self._setup_default_triggers()
    
    def _setup_default_triggers(self):
        """기본 트리거 설정"""
        # 오류 발생 시 중요도 증가
        self.add_trigger(
            trigger_type=TriggerType.COUNT,
            target_type="error",
            condition_value=5,  # 5개 이상 오류 발생 시
            action="increase_importance"
        )
        
        # API 요청 빈도 모니터링
        self.add_trigger(
            trigger_type=TriggerType.TIME,
            target_type="api_request",
            condition_value=300,  # 5분 내
            action="monitor_frequency"
        )
        
        # 중요 이벤트 패턴 감지
        self.add_trigger(
            trigger_type=TriggerType.PATTERN,
            target_type="important_event",
            condition_value="system_restart",
            action="alert_admin"
        )
        
        # 메모리 사용량 임계값
        self.add_trigger(
            trigger_type=TriggerType.THRESHOLD,
            target_type="system_event",
            condition_value=1000,  # 1000개 이상 메모리
            action="cleanup_old_memories"
        )
    
    def add_trigger(self, trigger_type: TriggerType, target_type: str, 
                   condition_value: Any, action: str, enabled: bool = True):
        """새로운 트리거 추가"""
        trigger = TriggerCondition(
            trigger_type=trigger_type,
            target_type=target_type,
            condition_value=condition_value,
            action=action,
            enabled=enabled
        )
        self.triggers.append(trigger)
        logger.info(f"트리거 추가: {trigger_type.value} - {target_type} -> {action}")
    
    def check_triggers(self, memory_type: str, **kwargs):
        """트리거 조건 확인 및 실행"""
        try:
            db = next(get_db_session())
            from .memory_service import MemoryService
            memory_service = MemoryService(db)
            
            for trigger in self.triggers:
                if not trigger.enabled or trigger.target_type != memory_type:
                    continue
                
                if self._should_trigger(trigger, memory_service, **kwargs):
                    self._execute_action(trigger, memory_service, **kwargs)
                    trigger.last_triggered = datetime.now()
                    trigger.trigger_count += 1
            
            db.close()
            
        except Exception as e:
            logger.error(f"트리거 확인 중 오류: {e}")
    
    def _should_trigger(self, trigger: TriggerCondition, memory_service, **kwargs) -> bool:
        """트리거 조건 확인"""
        try:
            if trigger.trigger_type == TriggerType.COUNT:
                # 최근 1시간 내 특정 타입 메모리 개수 확인
                recent_count = memory_service.get_memory_count_by_type(
                    memory_type=trigger.target_type,
                    hours=1
                )
                return recent_count >= trigger.condition_value
            
            elif trigger.trigger_type == TriggerType.TIME:
                # 최근 N초 내 특정 타입 메모리 개수 확인
                recent_count = memory_service.get_memory_count_by_type(
                    memory_type=trigger.target_type,
                    seconds=trigger.condition_value
                )
                return recent_count > 0
            
            elif trigger.trigger_type == TriggerType.PATTERN:
                # 패턴 매칭 확인
                pattern = trigger.condition_value
                recent_memories = memory_service.query_memories(
                    type=trigger.target_type,
                    limit=10
                )
                for memory in recent_memories:
                    if pattern.lower() in memory.content.lower():
                        return True
                return False
            
            elif trigger.trigger_type == TriggerType.THRESHOLD:
                # 전체 메모리 개수 임계값 확인
                total_count = memory_service.get_memory_stats()["total_memories"]
                return total_count >= trigger.condition_value
            
            return False
            
        except Exception as e:
            logger.error(f"트리거 조건 확인 중 오류: {e}")
            return False
    
    def _execute_action(self, trigger: TriggerCondition, memory_service, **kwargs):
        """트리거 액션 실행"""
        try:
            if trigger.action == "increase_importance":
                self._action_increase_importance(memory_service, trigger.target_type)
            
            elif trigger.action == "monitor_frequency":
                self._action_monitor_frequency(memory_service, trigger.target_type)
            
            elif trigger.action == "alert_admin":
                self._action_alert_admin(trigger, **kwargs)
            
            elif trigger.action == "cleanup_old_memories":
                self._action_cleanup_old_memories(memory_service)
            
            else:
                logger.warning(f"알 수 없는 액션: {trigger.action}")
                
        except Exception as e:
            logger.error(f"트리거 액션 실행 중 오류: {e}")
    
    def _action_increase_importance(self, memory_service, memory_type: str):
        """중요도 증가 액션"""
        # 최근 오류 메모리들의 중요도 증가
        recent_errors = memory_service.query_memories(
            type=memory_type,
            limit=10
        )
        
        for memory in recent_errors:
            if memory.importance_score < 90:
                new_importance = min(memory.importance_score + 10, 90)
                memory_service.update_memory(
                    memory_id=memory.id,
                    importance_score=new_importance
                )
        
        log_important_event(
            context="트리거 액션: 중요도 증가",
            content=f"{memory_type} 타입 메모리 {len(recent_errors)}개 중요도 증가",
            importance_score=70
        )
    
    def _action_monitor_frequency(self, memory_service, memory_type: str):
        """빈도 모니터링 액션"""
        # 최근 5분 내 API 요청 통계
        recent_requests = memory_service.query_memories(
            type=memory_type,
            limit=50
        )
        
        if len(recent_requests) > 20:  # 5분 내 20개 이상 요청
            log_system_event(
                context="API 요청 빈도 모니터링",
                content=f"높은 API 요청 빈도 감지: {len(recent_requests)}개/5분",
                importance_score=60
            )
    
    def _action_alert_admin(self, trigger: TriggerCondition, **kwargs):
        """관리자 알림 액션"""
        log_important_event(
            context="관리자 알림",
            content=f"패턴 감지: {trigger.condition_value}",
            importance_score=90
        )
    
    def _action_cleanup_old_memories(self, memory_service):
        """오래된 메모리 정리 액션"""
        # 30일 이상 된 메모리 삭제
        old_memories = memory_service.query_memories(
            days_old=30,
            limit=100
        )
        
        deleted_count = 0
        for memory in old_memories:
            if memory.importance_score < 30:  # 중요도가 낮은 것만 삭제
                memory_service.delete_memory(memory.id)
                deleted_count += 1
        
        if deleted_count > 0:
            log_system_event(
                context="메모리 정리",
                content=f"오래된 메모리 {deleted_count}개 삭제",
                importance_score=40
            )
    
    def get_trigger_stats(self) -> Dict[str, Any]:
        """트리거 통계 조회"""
        return {
            "total_triggers": len(self.triggers),
            "enabled_triggers": len([t for t in self.triggers if t.enabled]),
            "trigger_details": [
                {
                    "type": trigger.trigger_type.value,
                    "target": trigger.target_type,
                    "action": trigger.action,
                    "enabled": trigger.enabled,
                    "trigger_count": trigger.trigger_count,
                    "last_triggered": trigger.last_triggered.isoformat() if trigger.last_triggered else None
                }
                for trigger in self.triggers
            ]
        }


# 전역 인스턴스
event_trigger_service = EventTriggerService() 