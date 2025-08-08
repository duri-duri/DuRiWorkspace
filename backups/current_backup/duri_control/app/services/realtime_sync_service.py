"""
DuRi Memory System - Realtime Sync Service
실시간 메모리 동기화 서비스 (WebSocket 기반)
"""
import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from ..database.database import get_db_session
from ..decorators.memory_logger import log_important_event, log_system_event

logger = logging.getLogger(__name__)

class SyncEventType(Enum):
    """동기화 이벤트 타입"""
    MEMORY_CREATED = "memory_created"
    MEMORY_UPDATED = "memory_updated"
    MEMORY_DELETED = "memory_deleted"
    MEMORY_PROMOTED = "memory_promoted"
    MEMORY_ARCHIVED = "memory_archived"
    ANALYSIS_COMPLETED = "analysis_completed"
    SYSTEM_ALERT = "system_alert"
    HEALTH_UPDATE = "health_update"

@dataclass
class SyncEvent:
    """동기화 이벤트 데이터 클래스"""
    event_type: SyncEventType
    data: Dict[str, Any]
    timestamp: datetime
    source: str
    target_modules: Optional[List[str]] = None

class ConnectionManager:
    """WebSocket 연결 관리자"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str, module_name: str = "unknown"):
        """클라이언트 연결"""
        try:
            await websocket.accept()
            self.active_connections[client_id] = websocket
            self.connection_metadata[client_id] = {
                "module_name": module_name,
                "connected_at": datetime.now(),
                "last_activity": datetime.now(),
                "message_count": 0
            }
            logger.info(f"클라이언트 연결됨: {client_id} ({module_name})")
            
            # 연결 확인 메시지 전송
            await self.send_personal_message(
                client_id,
                {
                    "type": "connection_established",
                    "client_id": client_id,
                    "timestamp": datetime.now().isoformat(),
                    "message": "실시간 동기화 연결이 설정되었습니다"
                }
            )
            
        except Exception as e:
            logger.error(f"클라이언트 연결 실패: {client_id}, 오류: {e}")
    
    def disconnect(self, client_id: str):
        """클라이언트 연결 해제"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            metadata = self.connection_metadata.get(client_id, {})
            logger.info(f"클라이언트 연결 해제: {client_id} ({metadata.get('module_name', 'unknown')})")
            if client_id in self.connection_metadata:
                del self.connection_metadata[client_id]
    
    async def send_personal_message(self, client_id: str, message: Dict[str, Any]):
        """개별 클라이언트에게 메시지 전송"""
        try:
            if client_id in self.active_connections:
                websocket = self.active_connections[client_id]
                await websocket.send_text(json.dumps(message, default=str))
                
                # 메타데이터 업데이트
                if client_id in self.connection_metadata:
                    self.connection_metadata[client_id]["last_activity"] = datetime.now()
                    self.connection_metadata[client_id]["message_count"] += 1
                    
        except Exception as e:
            logger.error(f"개인 메시지 전송 실패: {client_id}, 오류: {e}")
            self.disconnect(client_id)
    
    async def broadcast(self, message: Dict[str, Any], exclude_client: Optional[str] = None):
        """모든 클라이언트에게 브로드캐스트"""
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            if exclude_client and client_id == exclude_client:
                continue
                
            try:
                await websocket.send_text(json.dumps(message, default=str))
                
                # 메타데이터 업데이트
                if client_id in self.connection_metadata:
                    self.connection_metadata[client_id]["last_activity"] = datetime.now()
                    self.connection_metadata[client_id]["message_count"] += 1
                    
            except Exception as e:
                logger.error(f"브로드캐스트 전송 실패: {client_id}, 오류: {e}")
                disconnected_clients.append(client_id)
        
        # 연결이 끊어진 클라이언트 제거
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def broadcast_to_modules(self, message: Dict[str, Any], target_modules: List[str]):
        """특정 모듈들에게만 브로드캐스트"""
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            metadata = self.connection_metadata.get(client_id, {})
            module_name = metadata.get("module_name", "unknown")
            
            if module_name in target_modules:
                try:
                    await websocket.send_text(json.dumps(message, default=str))
                    
                    # 메타데이터 업데이트
                    if client_id in self.connection_metadata:
                        self.connection_metadata[client_id]["last_activity"] = datetime.now()
                        self.connection_metadata[client_id]["message_count"] += 1
                        
                except Exception as e:
                    logger.error(f"모듈 브로드캐스트 전송 실패: {client_id}, 오류: {e}")
                    disconnected_clients.append(client_id)
        
        # 연결이 끊어진 클라이언트 제거
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    def get_connection_info(self) -> Dict[str, Any]:
        """연결 정보 조회"""
        return {
            "total_connections": len(self.active_connections),
            "connections": [
                {
                    "client_id": client_id,
                    "module_name": metadata.get("module_name", "unknown"),
                    "connected_at": metadata.get("connected_at", "").isoformat(),
                    "last_activity": metadata.get("last_activity", "").isoformat(),
                    "message_count": metadata.get("message_count", 0)
                }
                for client_id, metadata in self.connection_metadata.items()
            ]
        }

class RealtimeSyncService:
    """실시간 동기화 서비스"""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.event_queue: List[SyncEvent] = []
        self.max_queue_size = 1000
        self.sync_enabled = True
    
    async def handle_websocket(self, websocket: WebSocket, client_id: str, module_name: str = "unknown"):
        """WebSocket 연결 처리"""
        await self.connection_manager.connect(websocket, client_id, module_name)
        
        try:
            while True:
                # 클라이언트로부터 메시지 수신
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # 메시지 처리
                await self.handle_client_message(client_id, message)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket 연결 해제: {client_id}")
        except Exception as e:
            logger.error(f"WebSocket 처리 오류: {client_id}, 오류: {e}")
        finally:
            self.connection_manager.disconnect(client_id)
    
    async def handle_client_message(self, client_id: str, message: Dict[str, Any]):
        """클라이언트 메시지 처리"""
        try:
            message_type = message.get("type", "unknown")
            
            if message_type == "ping":
                # 핑 응답
                await self.connection_manager.send_personal_message(
                    client_id,
                    {
                        "type": "pong",
                        "timestamp": datetime.now().isoformat(),
                        "client_id": client_id
                    }
                )
            
            elif message_type == "subscribe":
                # 구독 요청
                event_types = message.get("event_types", [])
                await self.handle_subscription(client_id, event_types)
            
            elif message_type == "unsubscribe":
                # 구독 해제 요청
                event_types = message.get("event_types", [])
                await self.handle_unsubscription(client_id, event_types)
            
            elif message_type == "memory_update":
                # 메모리 업데이트 요청
                memory_data = message.get("data", {})
                await self.handle_memory_update(client_id, memory_data)
            
            else:
                logger.warning(f"알 수 없는 메시지 타입: {message_type} from {client_id}")
                
        except Exception as e:
            logger.error(f"클라이언트 메시지 처리 오류: {client_id}, 오류: {e}")
    
    async def handle_subscription(self, client_id: str, event_types: List[str]):
        """구독 처리"""
        try:
            # 구독 확인 메시지 전송
            await self.connection_manager.send_personal_message(
                client_id,
                {
                    "type": "subscription_confirmed",
                    "event_types": event_types,
                    "timestamp": datetime.now().isoformat(),
                    "message": f"이벤트 타입 {', '.join(event_types)} 구독이 확인되었습니다"
                }
            )
            
            logger.info(f"클라이언트 구독: {client_id} -> {event_types}")
            
        except Exception as e:
            logger.error(f"구독 처리 오류: {client_id}, 오류: {e}")
    
    async def handle_unsubscription(self, client_id: str, event_types: List[str]):
        """구독 해제 처리"""
        try:
            # 구독 해제 확인 메시지 전송
            await self.connection_manager.send_personal_message(
                client_id,
                {
                    "type": "unsubscription_confirmed",
                    "event_types": event_types,
                    "timestamp": datetime.now().isoformat(),
                    "message": f"이벤트 타입 {', '.join(event_types)} 구독이 해제되었습니다"
                }
            )
            
            logger.info(f"클라이언트 구독 해제: {client_id} -> {event_types}")
            
        except Exception as e:
            logger.error(f"구독 해제 처리 오류: {client_id}, 오류: {e}")
    
    async def handle_memory_update(self, client_id: str, memory_data: Dict[str, Any]):
        """메모리 업데이트 처리"""
        try:
            # 메모리 업데이트 처리 (실제 구현에서는 메모리 서비스 호출)
            logger.info(f"메모리 업데이트 요청: {client_id} -> {memory_data.get('id', 'unknown')}")
            
            # 업데이트 확인 메시지 전송
            await self.connection_manager.send_personal_message(
                client_id,
                {
                    "type": "memory_update_confirmed",
                    "memory_id": memory_data.get("id"),
                    "timestamp": datetime.now().isoformat(),
                    "message": "메모리 업데이트가 처리되었습니다"
                }
            )
            
            # 다른 클라이언트들에게 브로드캐스트
            await self.broadcast_memory_event(
                SyncEventType.MEMORY_UPDATED,
                memory_data,
                exclude_client=client_id
            )
            
        except Exception as e:
            logger.error(f"메모리 업데이트 처리 오류: {client_id}, 오류: {e}")
    
    async def broadcast_memory_event(self, event_type: SyncEventType, data: Dict[str, Any], 
                                   exclude_client: Optional[str] = None):
        """메모리 이벤트 브로드캐스트"""
        try:
            event = SyncEvent(
                event_type=event_type,
                data=data,
                timestamp=datetime.now(),
                source="memory_system"
            )
            
            message = {
                "type": "memory_event",
                "event_type": event_type.value,
                "data": data,
                "timestamp": event.timestamp.isoformat(),
                "source": event.source
            }
            
            await self.connection_manager.broadcast(message, exclude_client=exclude_client)
            
            # 이벤트 큐에 추가
            self.add_event_to_queue(event)
            
            logger.info(f"메모리 이벤트 브로드캐스트: {event_type.value}")
            
        except Exception as e:
            logger.error(f"메모리 이벤트 브로드캐스트 오류: {e}")
    
    async def broadcast_system_event(self, event_type: SyncEventType, data: Dict[str, Any],
                                   target_modules: Optional[List[str]] = None):
        """시스템 이벤트 브로드캐스트"""
        try:
            event = SyncEvent(
                event_type=event_type,
                data=data,
                timestamp=datetime.now(),
                source="system",
                target_modules=target_modules
            )
            
            message = {
                "type": "system_event",
                "event_type": event_type.value,
                "data": data,
                "timestamp": event.timestamp.isoformat(),
                "source": event.source
            }
            
            if target_modules:
                await self.connection_manager.broadcast_to_modules(message, target_modules)
            else:
                await self.connection_manager.broadcast(message)
            
            # 이벤트 큐에 추가
            self.add_event_to_queue(event)
            
            logger.info(f"시스템 이벤트 브로드캐스트: {event_type.value}")
            
        except Exception as e:
            logger.error(f"시스템 이벤트 브로드캐스트 오류: {e}")
    
    def add_event_to_queue(self, event: SyncEvent):
        """이벤트를 큐에 추가"""
        self.event_queue.append(event)
        
        # 큐 크기 제한
        if len(self.event_queue) > self.max_queue_size:
            self.event_queue = self.event_queue[-self.max_queue_size:]
    
    def get_event_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """이벤트 히스토리 조회"""
        recent_events = self.event_queue[-limit:] if self.event_queue else []
        return [asdict(event) for event in recent_events]
    
    def get_sync_status(self) -> Dict[str, Any]:
        """동기화 상태 조회"""
        return {
            "sync_enabled": self.sync_enabled,
            "active_connections": self.connection_manager.get_connection_info(),
            "event_queue_size": len(self.event_queue),
            "max_queue_size": self.max_queue_size,
            "last_event_time": self.event_queue[-1].timestamp.isoformat() if self.event_queue else None
        }
    
    async def notify_memory_created(self, memory_data: Dict[str, Any]):
        """메모리 생성 알림"""
        await self.broadcast_memory_event(SyncEventType.MEMORY_CREATED, memory_data)
    
    async def notify_memory_updated(self, memory_data: Dict[str, Any]):
        """메모리 업데이트 알림"""
        await self.broadcast_memory_event(SyncEventType.MEMORY_UPDATED, memory_data)
    
    async def notify_memory_deleted(self, memory_id: int):
        """메모리 삭제 알림"""
        await self.broadcast_memory_event(SyncEventType.MEMORY_DELETED, {"id": memory_id})
    
    async def notify_memory_promoted(self, memory_data: Dict[str, Any]):
        """메모리 승격 알림"""
        await self.broadcast_memory_event(SyncEventType.MEMORY_PROMOTED, memory_data)
    
    async def notify_memory_archived(self, memory_data: Dict[str, Any]):
        """메모리 아카이브 알림"""
        await self.broadcast_memory_event(SyncEventType.MEMORY_ARCHIVED, memory_data)
    
    async def notify_analysis_completed(self, analysis_data: Dict[str, Any]):
        """분석 완료 알림"""
        await self.broadcast_system_event(SyncEventType.ANALYSIS_COMPLETED, analysis_data)
    
    async def notify_system_alert(self, alert_data: Dict[str, Any]):
        """시스템 알림"""
        await self.broadcast_system_event(SyncEventType.SYSTEM_ALERT, alert_data)
    
    async def notify_health_update(self, health_data: Dict[str, Any]):
        """건강도 업데이트 알림"""
        await self.broadcast_system_event(SyncEventType.HEALTH_UPDATE, health_data)

# 전역 인스턴스
realtime_sync_service = RealtimeSyncService() 