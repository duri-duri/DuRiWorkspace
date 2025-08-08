"""
Day 10: 사회적 지능 API
DuRi가 인간과 자연스럽게 소통하고 협력하는 능력 API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from ..database.database import get_db_session
from ..services.social_intelligence_service import SocialIntelligenceService

router = APIRouter(prefix="/social-intelligence", tags=["Social Intelligence"])

@router.post("/conversation", response_model=Dict[str, Any])
async def process_conversation(
    user_input: Dict[str, Any],
    db: Session = Depends(get_db_session)
):
    """대화 처리 및 응답 생성"""
    try:
        si_service = SocialIntelligenceService(db)
        result = si_service.process_conversation(user_input)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "message": "대화 처리 완료",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=Dict[str, Any])
async def get_social_intelligence_stats(db: Session = Depends(get_db_session)):
    """사회적 지능 통계 조회"""
    try:
        si_service = SocialIntelligenceService(db)
        stats = si_service.get_social_intelligence_stats()
        
        return {
            "success": True,
            "message": "사회적 지능 통계 조회 완료",
            "data": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-context", response_model=Dict[str, Any])
async def analyze_conversation_context(
    conversation_data: Dict[str, Any],
    db: Session = Depends(get_db_session)
):
    """대화 맥락 분석"""
    try:
        si_service = SocialIntelligenceService(db)
        
        # 사용자 입력 분석
        input_analysis = si_service._analyze_user_input(conversation_data)
        
        # 맥락 이해
        context_understanding = si_service._understand_context(input_analysis)
        
        # 감정 상태 분석
        emotional_state = si_service._analyze_emotional_state(input_analysis)
        
        return {
            "success": True,
            "message": "대화 맥락 분석 완료",
            "data": {
                "input_analysis": input_analysis,
                "context_understanding": context_understanding,
                "emotional_state": emotional_state
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-response", response_model=Dict[str, Any])
async def generate_appropriate_response(
    conversation_context: Dict[str, Any],
    db: Session = Depends(get_db_session)
):
    """적절한 응답 생성"""
    try:
        si_service = SocialIntelligenceService(db)
        
        # 입력 분석
        input_analysis = si_service._analyze_user_input(conversation_context)
        
        # 맥락 이해
        context_understanding = si_service._understand_context(input_analysis)
        
        # 감정 상태 분석
        emotional_state = si_service._analyze_emotional_state(input_analysis)
        
        # 응답 생성
        response = si_service._generate_appropriate_response(
            input_analysis, context_understanding, emotional_state
        )
        
        return {
            "success": True,
            "message": "적절한 응답 생성 완료",
            "data": {
                "response": response,
                "input_analysis": input_analysis,
                "context_understanding": context_understanding,
                "emotional_state": emotional_state
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-collaboration", response_model=Dict[str, Any])
async def detect_collaboration_opportunity(
    collaboration_data: Dict[str, Any],
    db: Session = Depends(get_db_session)
):
    """협력 기회 탐지"""
    try:
        si_service = SocialIntelligenceService(db)
        
        # 입력 분석
        input_analysis = si_service._analyze_user_input(collaboration_data)
        
        # 맥락 이해
        context_understanding = si_service._understand_context(input_analysis)
        
        # 협력 기회 탐지
        collaboration_opportunity = si_service._detect_collaboration_opportunity(
            input_analysis, context_understanding
        )
        
        return {
            "success": True,
            "message": "협력 기회 탐지 완료",
            "data": {
                "collaboration_opportunity": collaboration_opportunity,
                "input_analysis": input_analysis,
                "context_understanding": context_understanding
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/social-interaction", response_model=Dict[str, Any])
async def process_social_interaction(
    interaction_data: Dict[str, Any],
    db: Session = Depends(get_db_session)
):
    """사회적 상호작용 처리"""
    try:
        si_service = SocialIntelligenceService(db)
        
        # 전체 대화 처리
        result = si_service.process_conversation(interaction_data)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # 사회적 지능 점수 계산
        social_score = result.get("social_intelligence_score", 0)
        
        # 상호작용 품질 평가
        interaction_quality = {
            "excellent": social_score >= 80,
            "good": 60 <= social_score < 80,
            "average": 40 <= social_score < 60,
            "needs_improvement": social_score < 40
        }
        
        return {
            "success": True,
            "message": "사회적 상호작용 처리 완료",
            "data": {
                "result": result,
                "social_intelligence_score": social_score,
                "interaction_quality": interaction_quality,
                "recommendations": _get_interaction_recommendations(social_score)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _get_interaction_recommendations(social_score: float) -> List[str]:
    """상호작용 개선 권장사항"""
    recommendations = []
    
    if social_score < 40:
        recommendations.extend([
            "사회적 규범 이해 강화 필요",
            "감정 인식 능력 향상 필요",
            "맥락 이해 능력 개선 필요"
        ])
    elif social_score < 60:
        recommendations.extend([
            "응답 적절성 향상",
            "협력 능력 강화",
            "공감 능력 개선"
        ])
    elif social_score < 80:
        recommendations.extend([
            "세밀한 맥락 이해 강화",
            "고급 사회적 기술 습득",
            "적응성 향상"
        ])
    else:
        recommendations.extend([
            "현재 수준 유지",
            "지속적 학습",
            "다양한 상황 경험"
        ])
    
    return recommendations 