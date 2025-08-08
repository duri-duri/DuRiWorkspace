from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging
from psycopg2.extras import RealDictCursor

from ..services.notify_service import get_notify_service
from ..models.notify_model import (
    NotificationConfig, NotificationRequest, NotificationResponse,
    NotificationStatus, AlertLevel, NotificationType, ResourceType
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/config", response_model=dict, tags=["notify"])
async def update_notification_config(config: NotificationConfig):
    """알림 설정 등록/업데이트"""
    try:
        notify_service = get_notify_service()
        success = notify_service.update_config(config)
        
        if success:
            return {
                "status": "success",
                "message": "알림 설정이 성공적으로 업데이트되었습니다",
                "config": config.dict()
            }
        else:
            raise HTTPException(status_code=500, detail="알림 설정 업데이트 실패")
            
    except Exception as e:
        logger.error(f"알림 설정 업데이트 실패: {e}")
        raise HTTPException(status_code=500, detail=f"알림 설정 업데이트 실패: {str(e)}")


@router.get("/status", response_model=NotificationStatus, tags=["notify"])
async def get_notification_status():
    """현재 알림 활성 상태 조회"""
    try:
        notify_service = get_notify_service()
        return notify_service.get_status()
    except Exception as e:
        logger.error(f"알림 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"알림 상태 조회 실패: {str(e)}")


@router.post("/test", response_model=NotificationResponse, tags=["notify"])
async def send_test_notification(request: NotificationRequest):
    """테스트 알림 전송"""
    try:
        notify_service = get_notify_service()
        return notify_service.send_notification(request)
    except Exception as e:
        logger.error(f"테스트 알림 전송 실패: {e}")
        raise HTTPException(status_code=500, detail=f"테스트 알림 전송 실패: {str(e)}")


@router.post("/alert", response_model=NotificationResponse, tags=["notify"])
async def send_alert(
    level: AlertLevel,
    title: str,
    message: str,
    service_name: Optional[str] = None,
    resource_type: Optional[ResourceType] = None,
    current_value: Optional[float] = None,
    threshold_value: Optional[float] = None
):
    """알림 전송 (간단한 형태)"""
    try:
        notify_service = get_notify_service()
        
        request = NotificationRequest(
            level=level,
            title=title,
            message=message,
            service_name=service_name,
            resource_type=resource_type,
            current_value=current_value,
            threshold_value=threshold_value
        )
        
        return notify_service.send_notification(request)
    except Exception as e:
        logger.error(f"알림 전송 실패: {e}")
        raise HTTPException(status_code=500, detail=f"알림 전송 실패: {str(e)}")


@router.get("/history", response_model=dict, tags=["notify"])
async def get_alert_history(limit: int = 50, level: Optional[AlertLevel] = None, service_name: Optional[str] = None):
    """알림 히스토리 조회"""
    try:
        notify_service = get_notify_service()
        
        # 데이터베이스에서 알림 히스토리 조회
        conn = notify_service._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT id, timestamp, level, title, message, service_name, 
                   resource_type, current_value, threshold_value, metadata,
                   sent_to, failed_to
            FROM alert_history
            WHERE 1=1
        """
        params = []
        
        if level:
            query += " AND level = %s"
            params.append(level.value)
        
        if service_name:
            query += " AND service_name = %s"
            params.append(service_name)
        
        query += " ORDER BY timestamp DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        alerts = []
        for row in results:
            alerts.append({
                "id": row['id'],
                "timestamp": row['timestamp'],
                "level": row['level'],
                "title": row['title'],
                "message": row['message'],
                "service_name": row['service_name'],
                "resource_type": row['resource_type'],
                "current_value": row['current_value'],
                "threshold_value": row['threshold_value'],
                "metadata": row['metadata'],
                "sent_to": row['sent_to'],
                "failed_to": row['failed_to']
            })
        
        return {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "filters": {
                "level": level.value if level else None,
                "service_name": service_name
            }
        }
        
    except Exception as e:
        logger.error(f"알림 히스토리 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"알림 히스토리 조회 실패: {str(e)}")


@router.post("/enable", response_model=dict, tags=["notify"])
async def enable_notifications():
    """알림 활성화"""
    try:
        notify_service = get_notify_service()
        notify_service.config.enabled = True
        notify_service.update_config(notify_service.config)
        
        return {
            "status": "success",
            "message": "알림이 활성화되었습니다"
        }
    except Exception as e:
        logger.error(f"알림 활성화 실패: {e}")
        raise HTTPException(status_code=500, detail=f"알림 활성화 실패: {str(e)}")


@router.post("/disable", response_model=dict, tags=["notify"])
async def disable_notifications():
    """알림 비활성화"""
    try:
        notify_service = get_notify_service()
        notify_service.config.enabled = False
        notify_service.update_config(notify_service.config)
        
        return {
            "status": "success",
            "message": "알림이 비활성화되었습니다"
        }
    except Exception as e:
        logger.error(f"알림 비활성화 실패: {e}")
        raise HTTPException(status_code=500, detail=f"알림 비활성화 실패: {str(e)}")


@router.get("/config", response_model=NotificationConfig, tags=["notify"])
async def get_notification_config():
    """현재 알림 설정 조회"""
    try:
        notify_service = get_notify_service()
        return notify_service.config
    except Exception as e:
        logger.error(f"알림 설정 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"알림 설정 조회 실패: {str(e)}")


@router.delete("/history", response_model=dict, tags=["notify"])
async def clear_alert_history():
    """알림 히스토리 삭제"""
    try:
        notify_service = get_notify_service()
        
        conn = notify_service._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM alert_history")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "알림 히스토리가 삭제되었습니다"
        }
    except Exception as e:
        logger.error(f"알림 히스토리 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=f"알림 히스토리 삭제 실패: {str(e)}") 