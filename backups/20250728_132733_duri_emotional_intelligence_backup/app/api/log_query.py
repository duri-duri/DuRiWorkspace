from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime, timedelta

from ..services.log_query_service import log_query_service
from duri_common.logger import get_logger

logger = get_logger("duri_control.api.log_query")

router = APIRouter(prefix="/logs", tags=["log_query"])


@router.get("/search")
async def search_logs(
    query: Optional[str] = Query(None, description="키워드 검색 (메시지, 서비스명, 컨테이너 ID에서 검색)"),
    level: Optional[str] = Query(None, description="로그 레벨 필터 (DEBUG, INFO, WARNING, ERROR)"),
    service: Optional[str] = Query(None, description="서비스명 필터"),
    start_time: Optional[str] = Query(None, description="시작 시간 (ISO 형식: 2025-07-24T04:00:00)"),
    end_time: Optional[str] = Query(None, description="종료 시간 (ISO 형식: 2025-07-24T04:00:00)"),
    limit: int = Query(default=100, ge=1, le=1000, description="결과 제한"),
    offset: int = Query(default=0, ge=0, description="오프셋")
):
    """
    고급 로그 검색 및 필터링
    
    다양한 조건으로 로그를 검색하고 필터링할 수 있습니다.
    
    - **query**: 키워드 검색 (메시지 내용, 서비스명, 컨테이너 ID에서 검색)
    - **level**: 로그 레벨 필터
    - **service**: 특정 서비스 필터
    - **start_time/end_time**: 시간 범위 필터
    - **limit/offset**: 페이지네이션
    
    정규식 검색도 지원합니다: `/pattern/` 형식으로 사용
    """
    try:
        # 시간 파라미터 파싱
        start_dt = None
        end_dt = None
        
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="잘못된 start_time 형식")
        
        if end_time:
            try:
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="잘못된 end_time 형식")
        
        # 로그 검색 실행
        logs, total_count = log_query_service.search_logs(
            query=query,
            level=level,
            service=service,
            start_time=start_dt,
            end_time=end_dt,
            limit=limit,
            offset=offset
        )
        
        return {
            "status": "success",
            "logs": [log.dict() for log in logs],
            "pagination": {
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total_count
            },
            "filters": {
                "query": query,
                "level": level,
                "service": service,
                "start_time": start_time,
                "end_time": end_time
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"로그 검색 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"로그 검색 실패: {str(e)}")


@router.get("/stats")
async def get_advanced_stats():
    """
    고급 로그 통계
    
    상세한 로그 분석 정보를 제공합니다:
    
    - 전체 로그 통계
    - 서비스별 통계
    - 시간별 분포
    - 에러 분석
    - 성능 메트릭
    """
    try:
        stats = log_query_service.get_advanced_statistics()
        
        return {
            "status": "success",
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"고급 통계 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")


@router.get("/errors")
async def get_error_summary(
    hours: int = Query(default=24, ge=1, le=168, description="분석할 시간 범위 (시간)")
):
    """
    에러 요약 정보
    
    지정된 시간 범위 내의 에러 로그를 분석합니다.
    
    - 총 에러 수
    - 시간당 에러율
    - 에러가 발생한 서비스 목록
    - 에러 타임라인
    - 에러 패턴 분석
    """
    try:
        error_summary = log_query_service.get_error_summary(hours=hours)
        
        return {
            "status": "success",
            "error_summary": error_summary,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"에러 요약 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"에러 요약 조회 실패: {str(e)}")


@router.get("/health")
async def get_service_health():
    """
    서비스 건강도 리포트
    
    각 서비스의 건강도를 분석하여 점수와 상태를 제공합니다.
    
    - 서비스별 건강도 점수 (0-100)
    - 상태 분류 (healthy, warning, critical, down)
    - 최근 에러/경고 수
    - 마지막 로그 시간
    """
    try:
        health_report = log_query_service.get_service_health_report()
        
        return {
            "status": "success",
            "health_report": health_report,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"서비스 건강도 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"건강도 조회 실패: {str(e)}")


@router.get("/search/quick")
async def quick_search(
    q: str = Query(..., description="빠른 검색 키워드"),
    limit: int = Query(default=20, ge=1, le=100, description="결과 제한")
):
    """
    빠른 로그 검색
    
    간단한 키워드로 빠르게 로그를 검색합니다.
    메시지, 서비스명, 컨테이너 ID에서 검색합니다.
    """
    try:
        logs, total_count = log_query_service.search_logs(
            query=q,
            limit=limit
        )
        
        return {
            "status": "success",
            "query": q,
            "logs": [log.dict() for log in logs],
            "total_found": total_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"빠른 검색 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"빠른 검색 실패: {str(e)}")


@router.get("/search/errors")
async def search_errors(
    service: Optional[str] = Query(None, description="특정 서비스의 에러만 검색"),
    hours: int = Query(default=24, ge=1, le=168, description="검색할 시간 범위 (시간)"),
    limit: int = Query(default=50, ge=1, le=200, description="결과 제한")
):
    """
    에러 로그 전용 검색
    
    에러 레벨의 로그만 검색합니다.
    서비스별 필터링과 시간 범위 지정이 가능합니다.
    """
    try:
        # 시간 범위 계산
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        logs, total_count = log_query_service.search_logs(
            level="ERROR",
            service=service,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        
        return {
            "status": "success",
            "filters": {
                "level": "ERROR",
                "service": service,
                "hours": hours
            },
            "logs": [log.dict() for log in logs],
            "total_errors": total_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"에러 검색 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"에러 검색 실패: {str(e)}")


@router.get("/search/pattern")
async def search_by_pattern(
    pattern: str = Query(..., description="정규식 패턴 (슬래시 없이)"),
    level: Optional[str] = Query(None, description="로그 레벨 필터"),
    service: Optional[str] = Query(None, description="서비스 필터"),
    limit: int = Query(default=50, ge=1, le=200, description="결과 제한")
):
    """
    정규식 패턴 검색
    
    정규식을 사용하여 로그 메시지를 검색합니다.
    고급 사용자를 위한 기능입니다.
    """
    try:
        # 정규식 패턴 검증
        import re
        try:
            re.compile(pattern)
        except re.error as e:
            raise HTTPException(status_code=400, detail=f"잘못된 정규식 패턴: {str(e)}")
        
        # 패턴을 슬래시로 감싸서 검색
        query = f"/{pattern}/"
        
        logs, total_count = log_query_service.search_logs(
            query=query,
            level=level,
            service=service,
            limit=limit
        )
        
        return {
            "status": "success",
            "pattern": pattern,
            "logs": [log.dict() for log in logs],
            "total_matches": total_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"패턴 검색 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"패턴 검색 실패: {str(e)}") 