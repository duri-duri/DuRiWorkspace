"""
DuRi Memory System - Intelligent Analysis API
지능형 메모리 분석 API 엔드포인트
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from ..services.intelligent_analysis_service import intelligent_analysis_service
from ..services.config_service import get_db_session
from ..decorators.memory_logger import log_api_request

router = APIRouter(prefix="/intelligent", tags=["intelligent_analysis"])


@router.get("/patterns", response_model=Dict[str, Any])
async def analyze_patterns(
    memory_type: Optional[str] = Query(None, description="분석할 메모리 타입"),
    time_window: int = Query(24, description="분석 시간 범위 (시간)"),
    min_frequency: int = Query(3, description="최소 패턴 빈도")
):
    """메모리 패턴 분석"""
    try:
        result = intelligent_analysis_service.analyze_memory_patterns(
            memory_type=memory_type,
            time_window=time_window,
            min_frequency=min_frequency
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "analysis_result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"패턴 분석 실패: {str(e)}")


@router.get("/correlations", response_model=Dict[str, Any])
async def analyze_correlations(
    memory_type: Optional[str] = Query(None, description="분석할 메모리 타입"),
    time_window: int = Query(24, description="분석 시간 범위 (시간)")
):
    """메모리 상관관계 분석"""
    try:
        result = intelligent_analysis_service.analyze_memory_correlations(
            memory_type=memory_type,
            time_window=time_window
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "analysis_result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상관관계 분석 실패: {str(e)}")


@router.get("/recommendations", response_model=Dict[str, Any])
async def get_recommendations(
    user_context: str = Query("", description="사용자 컨텍스트"),
    limit: int = Query(5, description="추천 개수 제한")
):
    """지능형 추천 생성"""
    try:
        result = intelligent_analysis_service.generate_intelligent_recommendations(
            user_context=user_context,
            limit=limit
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "recommendations": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"추천 생성 실패: {str(e)}")


@router.get("/predictions", response_model=Dict[str, Any])
async def predict_trends(
    days_ahead: int = Query(7, description="예측 일수")
):
    """메모리 트렌드 예측"""
    try:
        result = intelligent_analysis_service.predict_memory_trends(
            days_ahead=days_ahead
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "predictions": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"트렌드 예측 실패: {str(e)}")


@router.get("/comprehensive", response_model=Dict[str, Any])
async def comprehensive_analysis(
    memory_type: Optional[str] = Query(None, description="분석할 메모리 타입"),
    time_window: int = Query(24, description="분석 시간 범위 (시간)"),
    include_predictions: bool = Query(True, description="예측 포함 여부")
):
    """종합 지능형 분석"""
    try:
        comprehensive_result = {}
        
        # 1. 패턴 분석
        pattern_result = intelligent_analysis_service.analyze_memory_patterns(
            memory_type=memory_type,
            time_window=time_window
        )
        comprehensive_result["patterns"] = pattern_result
        
        # 2. 상관관계 분석
        correlation_result = intelligent_analysis_service.analyze_memory_correlations(
            memory_type=memory_type,
            time_window=time_window
        )
        comprehensive_result["correlations"] = correlation_result
        
        # 3. 추천 생성
        recommendation_result = intelligent_analysis_service.generate_intelligent_recommendations(
            user_context="",
            limit=10
        )
        comprehensive_result["recommendations"] = recommendation_result
        
        # 4. 예측 (선택적)
        if include_predictions:
            prediction_result = intelligent_analysis_service.predict_memory_trends(
                days_ahead=7
            )
            comprehensive_result["predictions"] = prediction_result
        
        # 종합 분석 결과 로깅
        from ..decorators.memory_logger import log_important_event
        log_important_event(
            context="종합 지능형 분석",
            content="패턴, 상관관계, 추천, 예측 종합 분석 완료",
            importance_score=85
        )
        
        return {
            "success": True,
            "comprehensive_analysis": comprehensive_result,
            "analysis_summary": {
                "patterns_found": len(pattern_result.get("patterns", [])),
                "correlations_found": len(correlation_result.get("correlations", [])),
                "recommendations_generated": len(recommendation_result.get("recommendations", [])),
                "predictions_included": include_predictions
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"종합 분석 실패: {str(e)}")


@router.get("/insights", response_model=Dict[str, Any])
async def get_insights(
    insight_type: str = Query("all", description="인사이트 타입 (all, patterns, correlations, trends)"),
    limit: int = Query(10, description="인사이트 개수 제한")
):
    """지능형 인사이트 조회"""
    try:
        insights = []
        
        if insight_type in ["all", "patterns"]:
            # 패턴 인사이트
            pattern_result = intelligent_analysis_service.analyze_memory_patterns(
                time_window=24,
                min_frequency=2
            )
            if "patterns" in pattern_result:
                for pattern in pattern_result["patterns"][:limit//2]:
                    insights.append({
                        "type": "pattern",
                        "title": f"패턴 발견: {pattern['type']}",
                        "description": pattern["context"],
                        "confidence": pattern["confidence"],
                        "importance": pattern["importance_score"]
                    })
        
        if insight_type in ["all", "correlations"]:
            # 상관관계 인사이트
            correlation_result = intelligent_analysis_service.analyze_memory_correlations(
                time_window=24
            )
            if "correlations" in correlation_result:
                for correlation in correlation_result["correlations"][:limit//2]:
                    insights.append({
                        "type": "correlation",
                        "title": f"상관관계: {correlation['source_type']} ↔ {correlation['target_type']}",
                        "description": f"강도: {correlation['correlation_strength']:.2f}",
                        "confidence": correlation["correlation_strength"],
                        "importance": correlation["correlation_strength"] * 100
                    })
        
        if insight_type in ["all", "trends"]:
            # 트렌드 인사이트
            prediction_result = intelligent_analysis_service.predict_memory_trends(
                days_ahead=7
            )
            if "predictions" in prediction_result:
                for prediction in prediction_result["predictions"]:
                    insights.append({
                        "type": "trend",
                        "title": f"트렌드: {prediction['metric']}",
                        "description": f"예측: {prediction['trend']} (신뢰도: {prediction['confidence']})",
                        "confidence": prediction["confidence"],
                        "importance": prediction["confidence"] * 100
                    })
        
        # 중요도 순으로 정렬
        insights.sort(key=lambda x: x["importance"], reverse=True)
        
        return {
            "success": True,
            "insights": insights[:limit],
            "total_insights": len(insights)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"인사이트 조회 실패: {str(e)}") 