"""
DuRi Memory System - API Endpoints
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from ..services.memory_service import MemoryService
from ..services.config_service import get_db_session
from ..models.memory import MemoryEntry
from ..scheduler import scheduled_cleanup_and_evolve
from ..decorators.memory_logger import log_api_request

router = APIRouter(prefix="/memory", tags=["memory"])

def get_memory_service(db: Session = Depends(get_db_session)) -> MemoryService:
    """MemoryService 의존성 주입"""
    return MemoryService(db)

@router.post("/save", response_model=Dict[str, Any])
@log_api_request(endpoint="/memory/save", method="POST", importance_score=70)
async def save_memory(
    memory_data: Dict[str, Any],
    memory_service: MemoryService = Depends(get_memory_service)
):
    """새로운 기억 저장"""
    try:
        # 필수 필드 검증
        required_fields = ['type', 'context', 'content', 'source']
        for field in required_fields:
            if field not in memory_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # 기본값 설정
        if 'importance_score' not in memory_data:
            memory_data['importance_score'] = 50
        
        if 'tags' not in memory_data:
            memory_data['tags'] = []
        
        # 기억 저장
        memory_entry = memory_service.save_memory(memory_data)
        
        return {
            "success": True,
            "message": "Memory saved successfully",
            "memory": memory_entry.to_dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save memory: {str(e)}")

@router.get("/query", response_model=Dict[str, Any])
@log_api_request(endpoint="/memory/query", method="GET", importance_score=50)
async def query_memories(
    memory_type: Optional[str] = Query(None, description="기억의 종류"),
    source: Optional[str] = Query(None, description="생성 주체"),
    context: Optional[str] = Query(None, description="맥락 검색"),
    tags: Optional[str] = Query(None, description="태그 (쉼표로 구분)"),
    min_importance: Optional[int] = Query(None, description="최소 중요도 점수"),
    memory_level: Optional[str] = Query(None, description="기억 레벨 (short/medium/truth)"),
    limit: int = Query(100, description="조회 개수 제한"),
    offset: int = Query(0, description="조회 시작 위치"),
    memory_service: MemoryService = Depends(get_memory_service)
):
    """기억 조회"""
    try:
        # 태그 파싱
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
        
        # 기억 조회
        memories = memory_service.query_memories(
            memory_type=memory_type,
            source=source,
            context=context,
            tags=tag_list,
            min_importance=min_importance,
            memory_level=memory_level,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "count": len(memories),
            "memories": [memory.to_dict() for memory in memories]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query memories: {str(e)}")

@router.get("/{memory_id}", response_model=Dict[str, Any])
@log_api_request(endpoint="/memory/{memory_id}", method="GET", importance_score=40)
async def get_memory(
    memory_id: int,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """특정 기억 조회"""
    try:
        memory = memory_service.get_memory_by_id(memory_id)
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return {
            "success": True,
            "memory": memory.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get memory: {str(e)}")

@router.put("/{memory_id}", response_model=Dict[str, Any])
async def update_memory(
    memory_id: int,
    update_data: Dict[str, Any],
    memory_service: MemoryService = Depends(get_memory_service)
):
    """기억 업데이트"""
    try:
        memory = memory_service.update_memory(memory_id, update_data)
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return {
            "success": True,
            "message": "Memory updated successfully",
            "memory": memory.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update memory: {str(e)}")

@router.delete("/{memory_id}", response_model=Dict[str, Any])
async def delete_memory(
    memory_id: int,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """기억 삭제"""
    try:
        success = memory_service.delete_memory(memory_id)
        if not success:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return {
            "success": True,
            "message": "Memory deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete memory: {str(e)}")

@router.get("/stats/overview", response_model=Dict[str, Any])
async def get_memory_stats(
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Memory 시스템 통계 조회"""
    try:
        stats = memory_service.get_memory_stats()
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get memory stats: {str(e)}")

@router.get("/search/{search_term}", response_model=Dict[str, Any])
async def search_memories(
    search_term: str,
    limit: int = Query(50, description="검색 결과 개수 제한"),
    memory_service: MemoryService = Depends(get_memory_service)
):
    """기억 검색"""
    try:
        memories = memory_service.search_memories(search_term, limit)
        
        return {
            "success": True,
            "search_term": search_term,
            "count": len(memories),
            "memories": [memory.to_dict() for memory in memories]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search memories: {str(e)}")

@router.get("/health/status", response_model=Dict[str, Any])
async def memory_health_check(
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Memory 시스템 상태 확인"""
    try:
        # 간단한 통계 조회로 시스템 상태 확인
        stats = memory_service.get_memory_stats()
        
        return {
            "status": "healthy",
            "service": "DuRi Memory System",
            "total_memories": stats.get('total_memories', 0),
            "recent_24h": stats.get('recent_24h', 0)
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "DuRi Memory System",
            "error": str(e)
        }

@router.get("/level/{memory_level}", response_model=Dict[str, Any])
async def get_memories_by_level(
    memory_level: str,
    limit: int = Query(100, description="조회 개수 제한"),
    memory_service: MemoryService = Depends(get_memory_service)
):
    """특정 레벨의 기억 조회"""
    try:
        if memory_level not in ['short', 'medium', 'truth']:
            raise HTTPException(status_code=400, detail="Invalid memory level. Must be 'short', 'medium', or 'truth'")
        
        memories = memory_service.get_memories_by_level(memory_level, limit)
        
        return {
            "success": True,
            "memory_level": memory_level,
            "count": len(memories),
            "memories": [memory.to_dict() for memory in memories]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get memories by level: {str(e)}")

@router.post("/cleanup/expired", response_model=Dict[str, Any])
async def cleanup_expired_memories(
    memory_service: MemoryService = Depends(get_memory_service)
):
    """만료된 단기 기억 정리"""
    try:
        deleted_count = memory_service.cleanup_expired_memories()
        
        return {
            "success": True,
            "message": f"Cleaned up {deleted_count} expired short-term memories",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup expired memories: {str(e)}")

@router.post("/promote/{memory_id}/medium", response_model=Dict[str, Any])
async def promote_memory_to_medium(
    memory_id: int,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """단기 기억을 중기 기억으로 승격"""
    try:
        result = memory_service.promote_memory_to_medium(memory_id)
        
        if result["success"]:
            return {
                "success": True,
                "message": "Memory promoted to medium level successfully",
                "memory": result["memory"],
                "promotion_score": result["promotion_score"],
                "promotion_reasons": result["promotion_reasons"]
            }
        else:
            return {
                "success": False,
                "message": result["reason"],
                "promotion_score": result.get("promotion_score", 0),
                "promotion_reasons": result.get("promotion_reasons", [])
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to promote memory: {str(e)}")

@router.post("/promote/{memory_id}/truth", response_model=Dict[str, Any])
async def promote_memory_to_truth(
    memory_id: int,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """중기 기억을 장기 기억(Truth)으로 승격"""
    try:
        result = memory_service.promote_memory_to_truth(memory_id)
        
        if result["success"]:
            return {
                "success": True,
                "message": "Memory promoted to truth level successfully",
                "memory": result["memory"],
                "promotion_score": result["promotion_score"],
                "promotion_reasons": result["promotion_reasons"]
            }
        else:
            return {
                "success": False,
                "message": result["reason"],
                "promotion_score": result.get("promotion_score", 0),
                "promotion_reasons": result.get("promotion_reasons", [])
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to promote memory to truth: {str(e)}")

@router.post("/promote/auto", response_model=Dict[str, Any])
async def auto_promote_memories(
    memory_service: MemoryService = Depends(get_memory_service)
):
    """자동 승격 후보 기억들 처리"""
    try:
        result = memory_service.auto_promote_candidates()
        
        return {
            "success": True,
            "message": "Auto promotion completed",
            "results": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to auto promote memories: {str(e)}")

@router.get("/analyze/{memory_id}", response_model=Dict[str, Any])
async def analyze_memory_patterns(
    memory_id: int,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """기억의 패턴 분석"""
    try:
        analysis = memory_service.analyze_memory_patterns(memory_id)
        
        if "error" in analysis:
            raise HTTPException(status_code=404, detail=analysis["error"])
        
        return {
            "success": True,
            "analysis": analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze memory patterns: {str(e)}")

@router.get("/learn/{memory_id}", response_model=Dict[str, Any])
async def analyze_learning_patterns(
    memory_id: int,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """중기 기억의 학습 패턴 분석"""
    try:
        analysis = memory_service.analyze_learning_patterns(memory_id)
        
        if "error" in analysis:
            raise HTTPException(status_code=404, detail=analysis["error"])
        
        return {
            "success": True,
            "analysis": analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze learning patterns: {str(e)}")

@router.get("/compare/{memory_id_1}/{memory_id_2}", response_model=Dict[str, Any])
async def compare_memories(
    memory_id_1: int,
    memory_id_2: int,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """두 기억 비교 분석"""
    try:
        comparison = memory_service.compare_memories(memory_id_1, memory_id_2)
        
        if "error" in comparison:
            raise HTTPException(status_code=404, detail=comparison["error"])
        
        return {
            "success": True,
            "comparison": comparison
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compare memories: {str(e)}")

@router.get("/report/{memory_id}", response_model=Dict[str, Any])
async def generate_learning_report(
    memory_id: int,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """학습 리포트 생성"""
    try:
        report = memory_service.generate_learning_report(memory_id)
        
        if "error" in report:
            raise HTTPException(status_code=404, detail=report["error"])
        
        return {
            "success": True,
            "report": report
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate learning report: {str(e)}")

@router.get("/insights/{memory_level}", response_model=Dict[str, Any])
async def get_learning_insights(
    memory_level: str,
    limit: int = Query(10, description="조회 개수 제한"),
    memory_service: MemoryService = Depends(get_memory_service)
):
    """학습 인사이트 조회"""
    try:
        if memory_level not in ['short', 'medium', 'truth']:
            raise HTTPException(status_code=400, detail="Invalid memory level")
        
        insights = memory_service.get_learning_insights(memory_level, limit)
        
        return {
            "success": True,
            "insights": insights
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get learning insights: {str(e)}")

@router.get("/truth/list", response_model=Dict[str, Any])
async def get_truth_memories(
    context: Optional[str] = Query(None, description="컨텍스트 필터"),
    memory_type: Optional[str] = Query(None, description="메모리 타입 필터"),
    limit: int = Query(50, description="조회 개수 제한"),
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Truth Memory 조회"""
    try:
        truths = memory_service.get_truth_memories(context, memory_type, limit)
        
        return {
            "success": True,
            "truth_memories": [truth.to_dict() for truth in truths],
            "count": len(truths)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get truth memories: {str(e)}")

@router.post("/judge", response_model=Dict[str, Any])
async def make_truth_judgment(
    situation: Dict[str, Any],
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Truth Memory 기반 판단 수행"""
    try:
        judgment_result = memory_service.make_truth_judgment(situation)
        
        return {
            "success": True,
            "judgment": judgment_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to make judgment: {str(e)}")

@router.get("/judgment/history", response_model=Dict[str, Any])
async def get_judgment_history(
    limit: int = Query(20, description="조회 개수 제한"),
    memory_service: MemoryService = Depends(get_memory_service)
):
    """판단 이력 조회"""
    try:
        history = memory_service.get_judgment_history(limit)
        
        return {
            "success": True,
            "judgment_history": history,
            "count": len(history)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get judgment history: {str(e)}")

@router.get("/truth/statistics", response_model=Dict[str, Any])
async def get_truth_statistics(
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Truth Memory 통계"""
    try:
        statistics = memory_service.get_truth_statistics()
        
        return {
            "success": True,
            "statistics": statistics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get truth statistics: {str(e)}") 

@router.post("/auto/cleanup", response_model=Dict[str, Any])
async def auto_cleanup_truth_memories(
    max_age_days: int = Query(30, description="오래된 Truth Memory 삭제 기준(일)"),
    min_success_ratio: float = Query(0.5, description="최소 성공 패턴 비율(미구현)"),
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Truth Memory 자동 정화"""
    try:
        result = memory_service.auto_cleanup_truth_memories(max_age_days, min_success_ratio)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to auto cleanup truth memories: {str(e)}")

@router.post("/auto/evolve", response_model=Dict[str, Any])
async def auto_evolve_truth_memories(
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Truth Memory 자동 진화"""
    try:
        result = memory_service.auto_evolve_truth_memories()
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to auto evolve truth memories: {str(e)}") 

@router.post("/auto/scheduler-test", response_model=Dict[str, Any])
async def scheduler_test():
    """스케줄러 수동 트리거 테스트"""
    try:
        scheduled_cleanup_and_evolve()
        return {"success": True, "message": "스케줄러 작업이 수동으로 실행되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scheduler test failed: {str(e)}") 

@router.get("/meta/report", response_model=Dict[str, Any])
async def get_meta_report(
    memory_service: MemoryService = Depends(get_memory_service)
):
    """DuRi Memory System 메타 리포트"""
    try:
        report = memory_service.meta_report()
        return {"success": True, "report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get meta report: {str(e)}")

@router.get("/meta/insights", response_model=Dict[str, Any])
async def get_meta_insights(
    limit: int = Query(5, description="최대 인사이트 개수"),
    memory_service: MemoryService = Depends(get_memory_service)
):
    """DuRi Memory System 메타 인사이트"""
    try:
        insights = memory_service.meta_insights(limit)
        return {"success": True, "insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get meta insights: {str(e)}") 

@router.get("/triggers/stats", response_model=Dict[str, Any])
@log_api_request(endpoint="/memory/triggers/stats", method="GET", importance_score=30)
async def get_trigger_stats(
    memory_service: MemoryService = Depends(get_memory_service)
):
    """트리거 통계 조회"""
    try:
        trigger_stats = memory_service.get_trigger_stats()
        
        return {
            "success": True,
            "trigger_stats": trigger_stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trigger stats: {str(e)}") 