"""
DuRi Memory System - Realtime Sync API
실시간 동기화 API 엔드포인트
"""
import logging
import json
import uuid
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from ..services.realtime_sync_service import realtime_sync_service
from ..services.config_service import get_db_session
from ..decorators.memory_logger import log_api_request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sync", tags=["realtime_sync"])

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, module_name: str = "unknown"):
    """WebSocket 실시간 동기화 엔드포인트"""
    try:
        await realtime_sync_service.handle_websocket(websocket, client_id, module_name)
    except Exception as e:
        logger.error(f"WebSocket 처리 오류: {client_id}, 오류: {e}")

@router.get("/status", response_model=Dict[str, Any])
async def get_sync_status():
    """실시간 동기화 상태 조회"""
    try:
        status = realtime_sync_service.get_sync_status()
        
        return {
            "success": True,
            "sync_status": status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"동기화 상태 조회 실패: {str(e)}")

@router.get("/connections", response_model=Dict[str, Any])
async def get_active_connections():
    """활성 연결 목록 조회"""
    try:
        connections = realtime_sync_service.connection_manager.get_connection_info()
        
        return {
            "success": True,
            "active_connections": connections
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"연결 목록 조회 실패: {str(e)}")

@router.get("/events", response_model=Dict[str, Any])
async def get_event_history(
    limit: int = Query(100, description="조회할 이벤트 수")
):
    """이벤트 히스토리 조회"""
    try:
        events = realtime_sync_service.get_event_history(limit=limit)
        
        return {
            "success": True,
            "event_history": {
                "events": events,
                "total_events": len(events),
                "limit": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이벤트 히스토리 조회 실패: {str(e)}")

@router.post("/broadcast/memory", response_model=Dict[str, Any])
async def broadcast_memory_event(
    event_type: str,
    data: Dict[str, Any]
):
    """메모리 이벤트 브로드캐스트"""
    try:
        from ..services.realtime_sync_service import SyncEventType
        
        # 이벤트 타입 검증
        try:
            sync_event_type = SyncEventType(event_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"유효하지 않은 이벤트 타입: {event_type}")
        
        # 이벤트 브로드캐스트
        await realtime_sync_service.broadcast_memory_event(sync_event_type, data)
        
        return {
            "success": True,
            "broadcast_result": {
                "event_type": event_type,
                "message": "이벤트가 성공적으로 브로드캐스트되었습니다",
                "timestamp": data.get("timestamp", "")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이벤트 브로드캐스트 실패: {str(e)}")

@router.post("/broadcast/system", response_model=Dict[str, Any])
async def broadcast_system_event(
    event_type: str,
    data: Dict[str, Any],
    target_modules: Optional[List[str]] = None
):
    """시스템 이벤트 브로드캐스트"""
    try:
        from ..services.realtime_sync_service import SyncEventType
        
        # 이벤트 타입 검증
        try:
            sync_event_type = SyncEventType(event_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"유효하지 않은 이벤트 타입: {event_type}")
        
        # 이벤트 브로드캐스트
        await realtime_sync_service.broadcast_system_event(sync_event_type, data, target_modules)
        
        return {
            "success": True,
            "broadcast_result": {
                "event_type": event_type,
                "target_modules": target_modules,
                "message": "시스템 이벤트가 성공적으로 브로드캐스트되었습니다",
                "timestamp": data.get("timestamp", "")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"시스템 이벤트 브로드캐스트 실패: {str(e)}")

@router.post("/notify/memory-created", response_model=Dict[str, Any])
async def notify_memory_created(memory_data: Dict[str, Any]):
    """메모리 생성 알림"""
    try:
        await realtime_sync_service.notify_memory_created(memory_data)
        
        return {
            "success": True,
            "notification_result": {
                "message": "메모리 생성 알림이 전송되었습니다",
                "memory_id": memory_data.get("id")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메모리 생성 알림 실패: {str(e)}")

@router.post("/notify/memory-updated", response_model=Dict[str, Any])
async def notify_memory_updated(memory_data: Dict[str, Any]):
    """메모리 업데이트 알림"""
    try:
        await realtime_sync_service.notify_memory_updated(memory_data)
        
        return {
            "success": True,
            "notification_result": {
                "message": "메모리 업데이트 알림이 전송되었습니다",
                "memory_id": memory_data.get("id")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메모리 업데이트 알림 실패: {str(e)}")

@router.post("/notify/memory-deleted", response_model=Dict[str, Any])
async def notify_memory_deleted(memory_id: int):
    """메모리 삭제 알림"""
    try:
        await realtime_sync_service.notify_memory_deleted(memory_id)
        
        return {
            "success": True,
            "notification_result": {
                "message": "메모리 삭제 알림이 전송되었습니다",
                "memory_id": memory_id
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메모리 삭제 알림 실패: {str(e)}")

@router.post("/notify/analysis-completed", response_model=Dict[str, Any])
async def notify_analysis_completed(analysis_data: Dict[str, Any]):
    """분석 완료 알림"""
    try:
        await realtime_sync_service.notify_analysis_completed(analysis_data)
        
        return {
            "success": True,
            "notification_result": {
                "message": "분석 완료 알림이 전송되었습니다",
                "analysis_type": analysis_data.get("type")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 완료 알림 실패: {str(e)}")

@router.post("/notify/system-alert", response_model=Dict[str, Any])
async def notify_system_alert(alert_data: Dict[str, Any]):
    """시스템 알림"""
    try:
        await realtime_sync_service.notify_system_alert(alert_data)
        
        return {
            "success": True,
            "notification_result": {
                "message": "시스템 알림이 전송되었습니다",
                "alert_type": alert_data.get("type")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"시스템 알림 실패: {str(e)}")

@router.post("/notify/health-update", response_model=Dict[str, Any])
async def notify_health_update(health_data: Dict[str, Any]):
    """건강도 업데이트 알림"""
    try:
        await realtime_sync_service.notify_health_update(health_data)
        
        return {
            "success": True,
            "notification_result": {
                "message": "건강도 업데이트 알림이 전송되었습니다",
                "health_score": health_data.get("health_score")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"건강도 업데이트 알림 실패: {str(e)}")

@router.post("/test/connection", response_model=Dict[str, Any])
async def test_connection():
    """연결 테스트"""
    try:
        # 테스트 이벤트 생성
        test_data = {
            "test_id": str(uuid.uuid4()),
            "message": "연결 테스트 메시지",
            "timestamp": ""
        }
        
        # 테스트 이벤트 브로드캐스트
        from ..services.realtime_sync_service import SyncEventType
        await realtime_sync_service.broadcast_system_event(
            SyncEventType.SYSTEM_ALERT,
            test_data
        )
        
        return {
            "success": True,
            "test_result": {
                "message": "연결 테스트가 완료되었습니다",
                "test_id": test_data["test_id"],
                "active_connections": realtime_sync_service.connection_manager.get_connection_info()["total_connections"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"연결 테스트 실패: {str(e)}")

@router.delete("/disconnect/{client_id}", response_model=Dict[str, Any])
async def disconnect_client(client_id: str):
    """특정 클라이언트 연결 해제"""
    try:
        realtime_sync_service.connection_manager.disconnect(client_id)
        
        return {
            "success": True,
            "disconnect_result": {
                "message": f"클라이언트 {client_id} 연결이 해제되었습니다",
                "client_id": client_id
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"클라이언트 연결 해제 실패: {str(e)}")

@router.post("/reset", response_model=Dict[str, Any])
async def reset_sync_service():
    """동기화 서비스 초기화"""
    try:
        # 모든 연결 해제
        for client_id in list(realtime_sync_service.connection_manager.active_connections.keys()):
            realtime_sync_service.connection_manager.disconnect(client_id)
        
        # 이벤트 큐 초기화
        realtime_sync_service.event_queue.clear()
        
        return {
            "success": True,
            "reset_result": {
                "message": "동기화 서비스가 초기화되었습니다",
                "active_connections": 0,
                "event_queue_size": 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"동기화 서비스 초기화 실패: {str(e)}") 