"""
DuRi Memory System - Advanced Memory Management API
고급 메모리 관리 API 엔드포인트
"""
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from ..services.advanced_memory_service import advanced_memory_service
from ..services.config_service import get_db_session
from ..decorators.memory_logger import log_api_request

router = APIRouter(prefix="/advanced", tags=["advanced_memory"])

@router.get("/lifecycle/{memory_id}", response_model=Dict[str, Any])
async def manage_lifecycle(
    memory_id: int
):
    """메모리 생명주기 관리"""
    try:
        result = advanced_memory_service.manage_memory_lifecycle(memory_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return {
            "success": True,
            "lifecycle_result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"생명주기 관리 실패: {str(e)}")

@router.post("/optimize/{memory_id}", response_model=Dict[str, Any])
async def optimize_memory(
    memory_id: int
):
    """메모리 저장 최적화"""
    try:
        result = advanced_memory_service.optimize_memory_storage(memory_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return {
            "success": True,
            "optimization_result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메모리 최적화 실패: {str(e)}")

@router.post("/backup", response_model=Dict[str, Any])
async def backup_system():
    """메모리 시스템 백업"""
    try:
        result = advanced_memory_service.backup_memory_system()
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "backup_result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"백업 실패: {str(e)}")

@router.get("/performance", response_model=Dict[str, Any])
async def monitor_performance():
    """성능 모니터링"""
    try:
        result = advanced_memory_service.monitor_performance()
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "performance_metrics": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"성능 모니터링 실패: {str(e)}")

@router.get("/lifecycle/stats", response_model=Dict[str, Any])
async def get_lifecycle_statistics():
    """생명주기 통계 조회"""
    try:
        # 성능 모니터링에서 생명주기 통계 추출
        performance = advanced_memory_service.monitor_performance()
        
        if "error" in performance:
            raise HTTPException(status_code=500, detail=performance["error"])
        
        lifecycle_stats = performance.get("lifecycle_distribution", {})
        
        return {
            "success": True,
            "lifecycle_statistics": lifecycle_stats,
            "total_lifecycles": len(advanced_memory_service.lifecycle_cache)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"생명주기 통계 조회 실패: {str(e)}")

@router.get("/priority/{memory_id}", response_model=Dict[str, Any])
async def get_memory_priority(
    memory_id: int
):
    """메모리 우선순위 조회"""
    try:
        lifecycle = advanced_memory_service.lifecycle_cache.get(memory_id)
        
        if not lifecycle:
            # 생명주기 관리 실행
            result = advanced_memory_service.manage_memory_lifecycle(memory_id)
            if "error" in result:
                raise HTTPException(status_code=404, detail=result["error"])
            return {
                "success": True,
                "priority": result["priority"],
                "evolution_score": result["evolution_score"]
            }
        
        return {
            "success": True,
            "priority": lifecycle.priority.value,
            "evolution_score": lifecycle.evolution_score,
            "access_count": lifecycle.access_count,
            "last_accessed": lifecycle.last_accessed.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"우선순위 조회 실패: {str(e)}")

@router.get("/compression/stats", response_model=Dict[str, Any])
async def get_compression_statistics():
    """압축 통계 조회"""
    try:
        performance = advanced_memory_service.monitor_performance()
        
        if "error" in performance:
            raise HTTPException(status_code=500, detail=performance["error"])
        
        compression_stats = performance.get("compression_efficiency", {})
        
        return {
            "success": True,
            "compression_statistics": compression_stats,
            "total_compressed": len([lc for lc in advanced_memory_service.lifecycle_cache.values() 
                                   if lc.compression_ratio < 1.0])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"압축 통계 조회 실패: {str(e)}")

@router.get("/health/status", response_model=Dict[str, Any])
async def get_system_health():
    """시스템 건강도 조회"""
    try:
        performance = advanced_memory_service.monitor_performance()
        
        if "error" in performance:
            raise HTTPException(status_code=500, detail=performance["error"])
        
        health_status = performance.get("system_health", {})
        
        return {
            "success": True,
            "health_status": health_status,
            "cache_size": len(advanced_memory_service.lifecycle_cache),
            "performance_metrics": performance
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"시스템 건강도 조회 실패: {str(e)}")

@router.post("/batch/optimize", response_model=Dict[str, Any])
async def batch_optimize_memories(
    memory_ids: List[int] = Query(..., description="최적화할 메모리 ID 목록")
):
    """배치 메모리 최적화"""
    try:
        results = []
        success_count = 0
        error_count = 0
        
        for memory_id in memory_ids:
            result = advanced_memory_service.optimize_memory_storage(memory_id)
            
            if "error" in result:
                error_count += 1
                results.append({"memory_id": memory_id, "error": result["error"]})
            else:
                success_count += 1
                results.append({"memory_id": memory_id, "result": result})
        
        return {
            "success": True,
            "batch_optimization": {
                "total_processed": len(memory_ids),
                "success_count": success_count,
                "error_count": error_count,
                "results": results
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"배치 최적화 실패: {str(e)}")

@router.post("/batch/lifecycle", response_model=Dict[str, Any])
async def batch_manage_lifecycles(
    memory_ids: List[int] = Query(..., description="생명주기 관리할 메모리 ID 목록")
):
    """배치 생명주기 관리"""
    try:
        results = []
        success_count = 0
        error_count = 0
        
        for memory_id in memory_ids:
            result = advanced_memory_service.manage_memory_lifecycle(memory_id)
            
            if "error" in result:
                error_count += 1
                results.append({"memory_id": memory_id, "error": result["error"]})
            else:
                success_count += 1
                results.append({"memory_id": memory_id, "result": result})
        
        return {
            "success": True,
            "batch_lifecycle": {
                "total_processed": len(memory_ids),
                "success_count": success_count,
                "error_count": error_count,
                "results": results
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"배치 생명주기 관리 실패: {str(e)}") 