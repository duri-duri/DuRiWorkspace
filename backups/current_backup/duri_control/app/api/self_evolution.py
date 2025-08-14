"""
Day 7: 자기 진화 API
DuRi가 스스로를 분석하고 개선하는 능력 API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..database.database import get_db_session
from ..services.self_evolution_service import SelfEvolutionService

router = APIRouter(prefix="/self-evolution", tags=["Self Evolution"])

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_self_performance(db: Session = Depends(get_db_session)):
    """자기 성능 분석"""
    try:
        se_service = SelfEvolutionService(db)
        result = se_service.analyze_self_performance()
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "message": "자기 성능 분석 완료",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auto-improve", response_model=Dict[str, Any])
async def auto_improve_system(db: Session = Depends(get_db_session)):
    """시스템 자동 개선"""
    try:
        se_service = SelfEvolutionService(db)
        result = se_service.auto_improve_system()
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "message": "시스템 자동 개선 완료",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=Dict[str, Any])
async def get_self_evolution_stats(db: Session = Depends(get_db_session)):
    """자기 진화 통계 조회"""
    try:
        se_service = SelfEvolutionService(db)
        stats = se_service.get_self_evolution_stats()
        
        return {
            "success": True,
            "message": "자기 진화 통계 조회 완료",
            "data": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/improve-specific", response_model=Dict[str, Any])
async def improve_specific_system(
    improvement_request: Dict[str, Any], 
    db: Session = Depends(get_db_session)
):
    """특정 시스템 개선"""
    try:
        se_service = SelfEvolutionService(db)
        
        # 현재 성능 분석
        performance_analysis = se_service.analyze_self_performance()
        
        if "error" in performance_analysis:
            raise HTTPException(status_code=500, detail=performance_analysis["error"])
        
        # 특정 시스템 개선점 찾기
        target_system = improvement_request.get("system", "overall")
        improvement_areas = performance_analysis.get("improvement_areas", [])
        
        target_improvement = None
        for area in improvement_areas:
            if area.get("system") == target_system:
                target_improvement = area
                break
        
        if not target_improvement:
            return {
                "success": True,
                "message": f"{target_system} 시스템은 개선이 필요하지 않습니다",
                "data": {"system": target_system, "status": "no_improvement_needed"}
            }
        
        # 개선 실행
        improvement_result = se_service._execute_improvement(target_improvement)
        
        return {
            "success": True,
            "message": f"{target_system} 시스템 개선 완료",
            "data": {
                "system": target_system,
                "improvement_result": improvement_result,
                "original_analysis": target_improvement
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance-report", response_model=Dict[str, Any])
async def get_detailed_performance_report(db: Session = Depends(get_db_session)):
    """상세 성능 리포트"""
    try:
        se_service = SelfEvolutionService(db)
        
        # 성능 분석
        performance_analysis = se_service.analyze_self_performance()
        
        if "error" in performance_analysis:
            raise HTTPException(status_code=500, detail=performance_analysis["error"])
        
        # 통계 조회
        stats = se_service.get_self_evolution_stats()
        
        # 종합 리포트 생성
        report = {
            "performance_analysis": performance_analysis,
            "evolution_stats": stats,
            "recommendations": [],
            "next_actions": []
        }
        
        # 권장사항 생성
        overall_performance = performance_analysis.get("overall_performance", {})
        overall_score = overall_performance.get("overall_score", 0)
        
        if overall_score < 70:
            report["recommendations"].append("전체 시스템 성능이 낮습니다. 우선순위 개선이 필요합니다.")
        elif overall_score < 80:
            report["recommendations"].append("시스템 성능이 양호하지만 개선 여지가 있습니다.")
        else:
            report["recommendations"].append("시스템 성능이 우수합니다. 유지 관리에 집중하세요.")
        
        # 다음 액션 제안
        improvement_areas = performance_analysis.get("improvement_areas", [])
        for area in improvement_areas:
            if area.get("priority") == "high":
                report["next_actions"].append(f"{area['system']} 시스템 개선 (우선순위: 높음)")
        
        return {
            "success": True,
            "message": "상세 성능 리포트 생성 완료",
            "data": report
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 