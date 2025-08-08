"""
Day 9: 창의적 사고 API
DuRi가 혁신적이고 독창적인 아이디어를 생성하는 능력 API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from ..database.database import get_db_session
from ..services.creative_thinking_service import CreativeThinkingService

router = APIRouter(prefix="/creative-thinking", tags=["Creative Thinking"])

@router.post("/generate-ideas", response_model=Dict[str, Any])
async def generate_creative_ideas(
    context: Dict[str, Any],
    db: Session = Depends(get_db_session)
):
    """창의적 아이디어 생성"""
    try:
        ct_service = CreativeThinkingService(db)
        result = ct_service.generate_creative_ideas(context)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "message": "창의적 아이디어 생성 완료",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=Dict[str, Any])
async def get_creative_thinking_stats(db: Session = Depends(get_db_session)):
    """창의적 사고 통계 조회"""
    try:
        ct_service = CreativeThinkingService(db)
        stats = ct_service.get_creative_thinking_stats()
        
        return {
            "success": True,
            "message": "창의적 사고 통계 조회 완료",
            "data": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-context", response_model=Dict[str, Any])
async def analyze_creative_context(
    context_data: Dict[str, Any],
    db: Session = Depends(get_db_session)
):
    """창의적 컨텍스트 분석"""
    try:
        ct_service = CreativeThinkingService(db)
        
        # 컨텍스트 분석
        context_analysis = ct_service._analyze_creative_context(context_data)
        
        # 패턴 분석
        pattern_analysis = ct_service._analyze_existing_patterns(context_analysis)
        
        return {
            "success": True,
            "message": "창의적 컨텍스트 분석 완료",
            "data": {
                "context_analysis": context_analysis,
                "pattern_analysis": pattern_analysis
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assess-innovation", response_model=Dict[str, Any])
async def assess_innovation(
    ideas_data: Dict[str, Any],
    db: Session = Depends(get_db_session)
):
    """혁신성 평가"""
    try:
        ct_service = CreativeThinkingService(db)
        
        # 컨텍스트 분석
        context_analysis = ct_service._analyze_creative_context(ideas_data.get("context", {}))
        
        # 패턴 분석
        pattern_analysis = ct_service._analyze_existing_patterns(context_analysis)
        
        # 아이디어 생성
        ideas = ct_service._generate_ideas(context_analysis, pattern_analysis)
        
        # 혁신성 평가
        innovation_assessment = ct_service._assess_innovation(ideas, pattern_analysis)
        
        return {
            "success": True,
            "message": "혁신성 평가 완료",
            "data": {
                "ideas": ideas,
                "innovation_assessment": innovation_assessment
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-feasibility", response_model=Dict[str, Any])
async def analyze_feasibility(
    feasibility_data: Dict[str, Any],
    db: Session = Depends(get_db_session)
):
    """실현 가능성 분석"""
    try:
        ct_service = CreativeThinkingService(db)
        
        # 컨텍스트 분석
        context_analysis = ct_service._analyze_creative_context(feasibility_data.get("context", {}))
        
        # 패턴 분석
        pattern_analysis = ct_service._analyze_existing_patterns(context_analysis)
        
        # 아이디어 생성
        ideas = ct_service._generate_ideas(context_analysis, pattern_analysis)
        
        # 실현 가능성 분석
        feasibility_analysis = ct_service._analyze_feasibility(ideas, context_analysis)
        
        return {
            "success": True,
            "message": "실현 가능성 분석 완료",
            "data": {
                "ideas": ideas,
                "feasibility_analysis": feasibility_analysis
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/creative-synthesis", response_model=Dict[str, Any])
async def creative_synthesis(
    synthesis_data: Dict[str, Any],
    db: Session = Depends(get_db_session)
):
    """창의적 종합 분석"""
    try:
        ct_service = CreativeThinkingService(db)
        
        # 전체 창의적 사고 프로세스 실행
        result = ct_service.generate_creative_ideas(synthesis_data)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # 창의적 사고 점수 계산
        creativity_score = result.get("creativity_score", 0)
        
        # 창의성 수준 평가
        creativity_level = _evaluate_creativity_level(creativity_score)
        
        # 개선 권장사항
        recommendations = _get_creativity_recommendations(creativity_score, result)
        
        return {
            "success": True,
            "message": "창의적 종합 분석 완료",
            "data": {
                "result": result,
                "creativity_score": creativity_score,
                "creativity_level": creativity_level,
                "recommendations": recommendations
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _evaluate_creativity_level(creativity_score: float) -> Dict[str, Any]:
    """창의성 수준 평가"""
    if creativity_score >= 80:
        return {
            "level": "excellent",
            "description": "뛰어난 창의성",
            "characteristics": ["높은 혁신성", "다양한 아이디어", "실현 가능성 우수"]
        }
    elif creativity_score >= 60:
        return {
            "level": "good",
            "description": "양호한 창의성",
            "characteristics": ["적절한 혁신성", "균형잡힌 아이디어", "실현 가능성 보통"]
        }
    elif creativity_score >= 40:
        return {
            "level": "average",
            "description": "평균적인 창의성",
            "characteristics": ["기본적 혁신성", "제한적 아이디어", "실현 가능성 낮음"]
        }
    else:
        return {
            "level": "needs_improvement",
            "description": "개선이 필요한 창의성",
            "characteristics": ["낮은 혁신성", "단조로운 아이디어", "실현 가능성 매우 낮음"]
        }

def _get_creativity_recommendations(creativity_score: float, result: Dict[str, Any]) -> List[str]:
    """창의성 개선 권장사항"""
    recommendations = []
    
    if creativity_score < 40:
        recommendations.extend([
            "패턴 인식 능력 향상 필요",
            "혁신적 사고 방식 개발",
            "아이디어 다양성 확대"
        ])
    elif creativity_score < 60:
        recommendations.extend([
            "혁신성 향상",
            "실현 가능성 개선",
            "아이디어 품질 향상"
        ])
    elif creativity_score < 80:
        recommendations.extend([
            "고급 창의적 기법 습득",
            "혁신적 패턴 연결 강화",
            "실현 가능성 최적화"
        ])
    else:
        recommendations.extend([
            "현재 수준 유지",
            "지속적 창의적 발전",
            "새로운 영역 탐험"
        ])
    
    # 결과 기반 추가 권장사항
    innovation_assessment = result.get("innovation_assessment", {})
    feasibility_analysis = result.get("feasibility_analysis", {})
    
    innovation_score = innovation_assessment.get("overall_innovation_score", 0)
    feasibility_score = feasibility_analysis.get("overall_feasibility", 0)
    
    if innovation_score < 0.5:
        recommendations.append("혁신성 향상이 필요합니다")
    
    if feasibility_score < 0.5:
        recommendations.append("실현 가능성 개선이 필요합니다")
    
    return recommendations 