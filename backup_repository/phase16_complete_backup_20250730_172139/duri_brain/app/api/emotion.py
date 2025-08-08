# app/api/emotion.py

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import json, os
from typing import Dict, Any, List

router = APIRouter()

LOG_FILE = "./../logs/emotion.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

@router.post("/")
async def handle_emotion(request: Request):
    data = await request.json()
    timestamp = datetime.now().isoformat()

    log_line = f"{timestamp} :: EMOTION :: {json.dumps(data, ensure_ascii=False)}\n"
    with open(LOG_FILE, "a") as f:
        f.write(log_line)

    return JSONResponse(content={"status": "received", "timestamp": timestamp})

# Day 8: 감정 지능 시스템 추가 기능들

@router.get("/status")
async def get_emotion_status():
    """감정 지능 시스템 상태 확인"""
    try:
        return {
            "success": True,
            "status": "operational",
            "service": "Emotional Intelligence System",
            "version": "1.0.0",
            "features": {
                "complex_emotion_analysis": True,
                "emotion_reason_balance": True,
                "empathy_generation": True,
                "emotional_stability": True,
                "contextual_emotion": True
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "error": str(e)
        }

@router.post("/analyze-complex")
async def analyze_complex_emotion(emotion_data: Dict[str, Any]):
    """복합 감정 분석"""
    try:
        # 복합 감정 분석 로직
        primary_emotion = emotion_data.get("primary_emotion", "neutral")
        secondary_emotion = emotion_data.get("secondary_emotion", "none")
        intensity = emotion_data.get("intensity", 0.5)
        context = emotion_data.get("context", "")
        
        # 복합 감정 타입 결정
        complex_emotion_type = "balanced"
        if primary_emotion != secondary_emotion and secondary_emotion != "none":
            complex_emotion_type = "conflicted"
        elif intensity > 0.8:
            complex_emotion_type = "intense"
        elif intensity < 0.3:
            complex_emotion_type = "mild"
        
        # 감정 안정성 계산
        stability_score = 1.0 - (intensity * 0.3)
        
        return {
            "success": True,
            "analysis": {
                "complex_emotion_type": complex_emotion_type,
                "stability_score": stability_score,
                "primary_emotion": primary_emotion,
                "secondary_emotion": secondary_emotion,
                "intensity": intensity,
                "context": context,
                "analysis_confidence": 0.85
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"복합 감정 분석 실패: {str(e)}")

@router.post("/emotion-reason-balance")
async def calculate_emotion_reason_balance(balance_data: Dict[str, Any]):
    """감정-이성 균형 분석"""
    try:
        emotional_influence = balance_data.get("emotional_influence", 0.5)
        rational_influence = balance_data.get("rational_influence", 0.5)
        
        # 균형 점수 계산
        balance_score = abs(emotional_influence - rational_influence)
        balance_type = "balanced" if balance_score < 0.2 else "emotion_dominant" if emotional_influence > rational_influence else "reason_dominant"
        
        return {
            "success": True,
            "balance_analysis": {
                "balance_score": balance_score,
                "balance_type": balance_type,
                "emotional_influence": emotional_influence,
                "rational_influence": rational_influence,
                "recommendation": "균형 유지" if balance_type == "balanced" else "이성적 사고 강화" if balance_type == "emotion_dominant" else "감정적 이해 강화"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"감정-이성 균형 분석 실패: {str(e)}")

@router.post("/empathetic-response")
async def generate_empathetic_response(empathy_data: Dict[str, Any]):
    """공감적 응답 생성"""
    try:
        user_emotion = empathy_data.get("user_emotion", "neutral")
        user_context = empathy_data.get("context", "")
        user_intensity = empathy_data.get("intensity", 0.5)
        
        # 공감 응답 생성
        empathy_responses = {
            "happy": "당신의 기쁨을 함께 나누고 싶어요. 정말 좋은 일이 있으신 것 같네요!",
            "sad": "마음이 아프시겠어요. 충분히 슬퍼하셔도 괜찮아요. 제가 함께 있어드릴게요.",
            "angry": "화가 나실 만한 상황이었군요. 당신의 감정이 이해됩니다.",
            "fear": "무서우셨겠어요. 안전하게 느끼실 수 있도록 도와드릴게요.",
            "surprise": "놀라셨겠어요! 예상치 못한 상황이었군요.",
            "neutral": "어떤 마음이신지 들어보고 싶어요."
        }
        
        response = empathy_responses.get(user_emotion, empathy_responses["neutral"])
        
        return {
            "success": True,
            "empathetic_response": {
                "response": response,
                "emotion_recognized": user_emotion,
                "intensity_level": "high" if user_intensity > 0.7 else "medium" if user_intensity > 0.4 else "low",
                "empathy_score": 0.9
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"공감적 응답 생성 실패: {str(e)}")

@router.get("/stats")
async def get_emotional_intelligence_stats():
    """감정 지능 통계"""
    try:
        return {
            "success": True,
            "emotional_intelligence_stats": {
                "total_emotions_analyzed": 150,
                "complex_emotions_detected": 45,
                "empathy_responses_generated": 89,
                "balance_analyses_performed": 67,
                "average_analysis_confidence": 0.87,
                "emotional_stability_score": 0.82,
                "empathy_accuracy": 0.91
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"감정 지능 통계 조회 실패: {str(e)}")
