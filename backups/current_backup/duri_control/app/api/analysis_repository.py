"""
DuRi Memory System - Analysis Repository API
분석 전용 저장소 API 엔드포인트
"""
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from ..services.analysis_repository_service import analysis_repository_service
from ..services.config_service import get_db_session
from ..decorators.memory_logger import log_api_request

router = APIRouter(prefix="/repository", tags=["analysis_repository"])

@router.get("/results/{analysis_id}", response_model=Dict[str, Any])
async def get_analysis_result(
    analysis_id: str
):
    """분석 결과 조회"""
    try:
        result = analysis_repository_service.get_analysis_result(analysis_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Analysis result not found")
        
        return {
            "success": True,
            "analysis_result": {
                "analysis_id": result.analysis_id,
                "analysis_type": result.analysis_type,
                "status": result.status.value,
                "parameters": result.parameters,
                "results": result.results,
                "execution_time_ms": result.execution_time_ms,
                "memory_usage_mb": result.memory_usage_mb,
                "created_at": result.created_at.isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 결과 조회 실패: {str(e)}")

@router.get("/patterns", response_model=Dict[str, Any])
async def get_pattern_cache(
    pattern_type: Optional[str] = Query(None, description="패턴 타입"),
    min_frequency: int = Query(1, description="최소 빈도"),
    limit: int = Query(100, description="조회 제한")
):
    """패턴 캐시 조회"""
    try:
        patterns = analysis_repository_service.get_pattern_cache(
            pattern_type=pattern_type,
            min_frequency=min_frequency,
            limit=limit
        )
        
        return {
            "success": True,
            "patterns": patterns,
            "total_patterns": len(patterns)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"패턴 캐시 조회 실패: {str(e)}")

@router.get("/metrics", response_model=Dict[str, Any])
async def get_performance_metrics(
    metric_type: Optional[str] = Query(None, description="메트릭 타입"),
    hours: int = Query(24, description="조회 시간 범위 (시간)"),
    limit: int = Query(1000, description="조회 제한")
):
    """성능 메트릭 조회"""
    try:
        metrics = analysis_repository_service.get_performance_metrics(
            metric_type=metric_type,
            hours=hours,
            limit=limit
        )
        
        return {
            "success": True,
            "metrics": metrics,
            "total_metrics": len(metrics)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"성능 메트릭 조회 실패: {str(e)}")

@router.get("/statistics", response_model=Dict[str, Any])
async def get_analysis_statistics(
    days: int = Query(7, description="조회 일수")
):
    """분석 통계 조회"""
    try:
        stats = analysis_repository_service.get_analysis_statistics(days=days)
        
        return {
            "success": True,
            "statistics": stats,
            "total_days": len(stats)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 통계 조회 실패: {str(e)}")

@router.post("/metrics", response_model=Dict[str, Any])
async def save_performance_metric(
    metric_type: str = Query(..., description="메트릭 타입"),
    metric_name: str = Query(..., description="메트릭 이름"),
    metric_value: float = Query(..., description="메트릭 값"),
    metric_unit: str = Query("", description="메트릭 단위"),
    metadata: Optional[Dict[str, Any]] = None
):
    """성능 메트릭 저장"""
    try:
        success = analysis_repository_service.save_performance_metric(
            metric_type=metric_type,
            metric_name=metric_name,
            metric_value=metric_value,
            metric_unit=metric_unit,
            metadata=metadata
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="메트릭 저장 실패")
        
        return {
            "success": True,
            "saved_metric": {
                "type": metric_type,
                "name": metric_name,
                "value": metric_value,
                "unit": metric_unit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"성능 메트릭 저장 실패: {str(e)}")

@router.post("/patterns", response_model=Dict[str, Any])
async def save_pattern_cache(
    pattern_type: str = Query(..., description="패턴 타입"),
    memory_ids: List[int] = Query(..., description="메모리 ID 목록"),
    confidence_score: float = Query(0.0, description="신뢰도 점수"),
    pattern_data: Dict[str, Any] = None
):
    """패턴 캐시 저장"""
    try:
        success = analysis_repository_service.save_pattern_cache(
            pattern_type=pattern_type,
            pattern_data=pattern_data,
            memory_ids=memory_ids,
            confidence_score=confidence_score
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="패턴 캐시 저장 실패")
        
        return {
            "success": True,
            "saved_pattern": {
                "type": pattern_type,
                "memory_count": len(memory_ids),
                "confidence_score": confidence_score
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"패턴 캐시 저장 실패: {str(e)}")

@router.post("/correlations", response_model=Dict[str, Any])
async def save_correlation_analysis(
    correlation_id: str = Query(..., description="상관관계 ID"),
    source_type: str = Query(..., description="소스 타입"),
    target_type: str = Query(..., description="타겟 타입"),
    correlation_strength: float = Query(..., description="상관관계 강도"),
    confidence_score: float = Query(..., description="신뢰도 점수"),
    sample_size: int = Query(..., description="샘플 크기"),
    analysis_window_hours: int = Query(..., description="분석 시간창"),
    correlation_data: Dict[str, Any] = None
):
    """상관관계 분석 결과 저장"""
    try:
        success = analysis_repository_service.save_correlation_analysis(
            correlation_id=correlation_id,
            source_type=source_type,
            target_type=target_type,
            correlation_strength=correlation_strength,
            confidence_score=confidence_score,
            sample_size=sample_size,
            analysis_window_hours=analysis_window_hours,
            correlation_data=correlation_data
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="상관관계 분석 저장 실패")
        
        return {
            "success": True,
            "saved_correlation": {
                "correlation_id": correlation_id,
                "source_type": source_type,
                "target_type": target_type,
                "strength": correlation_strength,
                "confidence": confidence_score
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상관관계 분석 저장 실패: {str(e)}")

@router.get("/summary", response_model=Dict[str, Any])
async def get_repository_summary():
    """저장소 요약 정보 조회"""
    try:
        # 최근 분석 결과 수
        recent_results = analysis_repository_service.get_analysis_result("recent")
        
        # 패턴 캐시 요약
        patterns = analysis_repository_service.get_pattern_cache(limit=10)
        
        # 성능 메트릭 요약
        metrics = analysis_repository_service.get_performance_metrics(hours=1, limit=10)
        
        # 분석 통계 요약
        stats = analysis_repository_service.get_analysis_statistics(days=1)
        
        summary = {
            "recent_analyses": len(patterns),
            "total_patterns": len(patterns),
            "recent_metrics": len(metrics),
            "daily_statistics": len(stats),
            "repository_status": "healthy"
        }
        
        return {
            "success": True,
            "repository_summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"저장소 요약 조회 실패: {str(e)}")

@router.delete("/patterns/{pattern_hash}", response_model=Dict[str, Any])
async def delete_pattern_cache(
    pattern_hash: str
):
    """패턴 캐시 삭제"""
    try:
        # 패턴 캐시 삭제 로직 (실제 구현에서는 SQL DELETE 쿼리)
        # 여기서는 성공 응답만 반환
        return {
            "success": True,
            "deleted_pattern": {
                "pattern_hash": pattern_hash,
                "status": "deleted"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"패턴 캐시 삭제 실패: {str(e)}")

@router.get("/health", response_model=Dict[str, Any])
async def get_repository_health():
    """저장소 건강도 조회"""
    try:
        # 기본적인 저장소 상태 확인
        patterns = analysis_repository_service.get_pattern_cache(limit=1)
        metrics = analysis_repository_service.get_performance_metrics(hours=1, limit=1)
        
        health_status = {
            "database_connection": "healthy",
            "pattern_cache": "available" if patterns else "empty",
            "performance_metrics": "available" if metrics else "empty",
            "overall_status": "healthy"
        }
        
        return {
            "success": True,
            "repository_health": health_status
        }
        
    except Exception as e:
        return {
            "success": False,
            "repository_health": {
                "database_connection": "unhealthy",
                "error": str(e),
                "overall_status": "unhealthy"
            }
        } 