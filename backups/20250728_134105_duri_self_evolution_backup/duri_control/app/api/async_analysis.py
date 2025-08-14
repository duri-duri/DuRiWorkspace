"""
DuRi Memory System - Async Analysis API
비동기 분석 API 엔드포인트
"""
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session

from ..services.async_analysis_service import async_analysis_service
from ..services.config_service import get_db_session
from ..decorators.memory_logger import log_api_request

router = APIRouter(prefix="/async", tags=["async_analysis"])

@router.post("/patterns", response_model=Dict[str, Any])
async def schedule_pattern_analysis(
    background_tasks: BackgroundTasks,
    memory_type: Optional[str] = Query(None, description="분석할 메모리 타입"),
    time_window: int = Query(24, description="분석 시간 범위 (시간)"),
    min_frequency: int = Query(3, description="최소 패턴 빈도")
):
    """패턴 분석 스케줄링 (비동기)"""
    try:
        result = await async_analysis_service.schedule_pattern_analysis(
            background_tasks=background_tasks,
            memory_type=memory_type,
            time_window=time_window,
            min_frequency=min_frequency
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "scheduled_analysis": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"패턴 분석 스케줄링 실패: {str(e)}")

@router.post("/correlations", response_model=Dict[str, Any])
async def schedule_correlation_analysis(
    background_tasks: BackgroundTasks,
    memory_type: Optional[str] = Query(None, description="분석할 메모리 타입"),
    time_window: int = Query(24, description="분석 시간 범위 (시간)")
):
    """상관관계 분석 스케줄링 (비동기)"""
    try:
        result = await async_analysis_service.schedule_correlation_analysis(
            background_tasks=background_tasks,
            memory_type=memory_type,
            time_window=time_window
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "scheduled_analysis": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상관관계 분석 스케줄링 실패: {str(e)}")

@router.post("/performance", response_model=Dict[str, Any])
async def schedule_performance_monitoring(
    background_tasks: BackgroundTasks
):
    """성능 모니터링 스케줄링 (비동기)"""
    try:
        result = await async_analysis_service.schedule_performance_monitoring(
            background_tasks=background_tasks
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "scheduled_analysis": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"성능 모니터링 스케줄링 실패: {str(e)}")

@router.post("/comprehensive", response_model=Dict[str, Any])
async def schedule_comprehensive_analysis(
    background_tasks: BackgroundTasks,
    memory_type: Optional[str] = Query(None, description="분석할 메모리 타입"),
    time_window: int = Query(24, description="분석 시간 범위 (시간)")
):
    """종합 분석 스케줄링 (비동기)"""
    try:
        result = await async_analysis_service.schedule_comprehensive_analysis(
            background_tasks=background_tasks,
            memory_type=memory_type,
            time_window=time_window
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "scheduled_analysis": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"종합 분석 스케줄링 실패: {str(e)}")

@router.get("/status/{analysis_id}", response_model=Dict[str, Any])
async def get_analysis_status(
    analysis_id: str
):
    """분석 상태 조회"""
    try:
        result = await async_analysis_service.get_analysis_status(analysis_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return {
            "success": True,
            "analysis_status": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 상태 조회 실패: {str(e)}")

@router.get("/status", response_model=Dict[str, Any])
async def get_all_analysis_status():
    """모든 분석 상태 조회"""
    try:
        result = await async_analysis_service.get_all_analysis_status()
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "all_analysis_status": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"전체 분석 상태 조회 실패: {str(e)}")

@router.post("/batch/patterns", response_model=Dict[str, Any])
async def schedule_batch_pattern_analysis(
    background_tasks: BackgroundTasks,
    memory_types: List[str] = Query(..., description="분석할 메모리 타입 목록"),
    time_window: int = Query(24, description="분석 시간 범위 (시간)")
):
    """배치 패턴 분석 스케줄링"""
    try:
        results = []
        for memory_type in memory_types:
            result = await async_analysis_service.schedule_pattern_analysis(
                background_tasks=background_tasks,
                memory_type=memory_type,
                time_window=time_window
            )
            results.append(result)
        
        return {
            "success": True,
            "batch_scheduled": {
                "total_scheduled": len(results),
                "results": results
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"배치 패턴 분석 스케줄링 실패: {str(e)}")

@router.post("/batch/comprehensive", response_model=Dict[str, Any])
async def schedule_batch_comprehensive_analysis(
    background_tasks: BackgroundTasks,
    memory_types: List[str] = Query(..., description="분석할 메모리 타입 목록"),
    time_window: int = Query(24, description="분석 시간 범위 (시간)")
):
    """배치 종합 분석 스케줄링"""
    try:
        results = []
        for memory_type in memory_types:
            result = await async_analysis_service.schedule_comprehensive_analysis(
                background_tasks=background_tasks,
                memory_type=memory_type,
                time_window=time_window
            )
            results.append(result)
        
        return {
            "success": True,
            "batch_scheduled": {
                "total_scheduled": len(results),
                "results": results
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"배치 종합 분석 스케줄링 실패: {str(e)}")

@router.delete("/cancel/{analysis_id}", response_model=Dict[str, Any])
async def cancel_analysis(
    analysis_id: str
):
    """분석 취소"""
    try:
        # 분석 상태 확인
        status = async_analysis_service.analysis_status.get(analysis_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        if status == "completed":
            raise HTTPException(status_code=400, detail="Cannot cancel completed analysis")
        
        # 분석 취소 (상태를 cancelled로 변경)
        async_analysis_service.analysis_status[analysis_id] = "cancelled"
        
        return {
            "success": True,
            "cancelled_analysis": {
                "analysis_id": analysis_id,
                "status": "cancelled"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 취소 실패: {str(e)}")

@router.get("/queue/status", response_model=Dict[str, Any])
async def get_queue_status():
    """분석 큐 상태 조회"""
    try:
        status = async_analysis_service.analysis_status
        
        queue_stats = {
            "total_analyses": len(status),
            "scheduled": len([s for s in status.values() if s == "scheduled"]),
            "running": len([s for s in status.values() if s == "running"]),
            "completed": len([s for s in status.values() if s == "completed"]),
            "failed": len([s for s in status.values() if s == "failed"]),
            "cancelled": len([s for s in status.values() if s == "cancelled"])
        }
        
        return {
            "success": True,
            "queue_status": queue_stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"큐 상태 조회 실패: {str(e)}") 