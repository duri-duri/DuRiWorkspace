from fastapi import APIRouter, Query, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import datetime

from ..services.log_service import log_service
from ..models.log_entry import LogQueryParams, LogStreamConfig
from duri_common.logger import get_logger

logger = get_logger("duri_control.api.logs")

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/stream")
async def stream_logs(request: Request):
    """
    Server-Sent Events (SSE)를 통한 실시간 로그 스트림
    
    클라이언트가 연결을 유지하면서 새로운 로그를 실시간으로 받을 수 있습니다.
    """
    async def generate():
        try:
            # 로그 수집 시작 (아직 시작되지 않은 경우)
            log_service.start_collection()
            
            # SSE 헤더 전송
            yield "data: {\"type\": \"connected\", \"message\": \"로그 스트림 연결됨\"}\n\n"
            
            # 로그 스트림 시작
            async for sse_data in log_service.stream_logs():
                yield sse_data
                
        except Exception as e:
            logger.error(f"로그 스트림 오류: {e}")
            yield f"data: {{\"type\": \"error\", \"message\": \"스트림 오류: {str(e)}\"}}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )


@router.get("/recent")
async def get_recent_logs(
    limit: int = Query(default=50, ge=1, le=1000, description="조회할 로그 수"),
    service_name: Optional[str] = Query(None, description="특정 서비스 필터"),
    level: Optional[str] = Query(None, description="로그 레벨 필터"),
    since: Optional[str] = Query(None, description="이후 시간부터 조회 (ISO 형식)"),
    until: Optional[str] = Query(None, description="이전 시간까지 조회 (ISO 형식)")
):
    """
    최근 로그 조회
    
    다양한 필터 옵션을 사용하여 로그를 조회할 수 있습니다.
    """
    try:
        # 시간 파라미터 파싱
        since_dt = None
        until_dt = None
        
        if since:
            try:
                since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="잘못된 since 시간 형식")
        
        if until:
            try:
                until_dt = datetime.fromisoformat(until.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="잘못된 until 시간 형식")
        
        # 쿼리 파라미터 생성
        params = LogQueryParams(
            limit=limit,
            service_name=service_name,
            level=level,
            since=since_dt,
            until=until_dt
        )
        
        # 로그 조회
        logs = log_service.get_recent_logs(params)
        
        return {
            "status": "success",
            "logs": [log.dict() for log in logs],
            "count": len(logs),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"로그 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=f"로그 조회 실패: {str(e)}")


@router.get("/statistics")
async def get_log_statistics():
    """
    로그 통계 정보 조회
    
    서비스별, 레벨별 로그 통계와 최근 활동 정보를 제공합니다.
    """
    try:
        stats = log_service.get_log_statistics()
        
        return {
            "status": "success",
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"로그 통계 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=f"로그 통계 조회 실패: {str(e)}")


@router.post("/config")
async def update_log_config(config: LogStreamConfig):
    """
    로그 수집 설정 업데이트
    
    모니터링할 서비스, 로그 레벨, 수집 간격 등을 설정할 수 있습니다.
    """
    try:
        # 기존 서비스 중지
        log_service.stop_collection()
        
        # 새 설정 적용
        log_service.config = config
        
        # 서비스 재시작
        log_service.start_collection()
        
        return {
            "status": "success",
            "message": "로그 수집 설정이 업데이트되었습니다.",
            "config": config.dict(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"로그 설정 업데이트 오류: {e}")
        raise HTTPException(status_code=500, detail=f"설정 업데이트 실패: {str(e)}")


@router.get("/services")
async def get_available_services():
    """
    사용 가능한 서비스 목록 조회
    
    로그 수집이 가능한 서비스들의 목록을 반환합니다.
    """
    try:
        services = list(log_service.container_names.keys())
        
        return {
            "status": "success",
            "services": services,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"서비스 목록 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=f"서비스 목록 조회 실패: {str(e)}")


@router.post("/start")
async def start_log_collection():
    """
    로그 수집 시작
    
    수동으로 로그 수집을 시작할 수 있습니다.
    """
    try:
        log_service.start_collection()
        
        return {
            "status": "success",
            "message": "로그 수집이 시작되었습니다.",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"로그 수집 시작 오류: {e}")
        raise HTTPException(status_code=500, detail=f"로그 수집 시작 실패: {str(e)}")


@router.post("/stop")
async def stop_log_collection():
    """
    로그 수집 중지
    
    수동으로 로그 수집을 중지할 수 있습니다.
    """
    try:
        log_service.stop_collection()
        
        return {
            "status": "success",
            "message": "로그 수집이 중지되었습니다.",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"로그 수집 중지 오류: {e}")
        raise HTTPException(status_code=500, detail=f"로그 수집 중지 실패: {str(e)}") 