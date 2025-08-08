#!/usr/bin/env python3
"""
DuRi Core Node - API Gateway
포트 8080에서 사용자 요청을 받아 Brain과 Evolution 노드로 라우팅
"""
import asyncio
import time
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
import uvicorn
import httpx
from pydantic import BaseModel

# DuRi 로깅 시스템 초기화
from DuRiCore.bootstrap import bootstrap_logging
bootstrap_logging()

import logging
logger = logging.getLogger(__name__)

# 성능 최적화 임포트
from performance_optimizer import PerformanceOptimizer, LoadBalancer
from growth_level_system import growth_level_system
from cognitive_bandwidth_manager import cognitive_bandwidth_manager
from enhanced_emotion_filter import enhanced_emotion_filter

app = FastAPI(title="DuRi Core Node", version="1.0.0")

# 성능 최적화 시스템 초기화
performance_optimizer = PerformanceOptimizer()
load_balancer = LoadBalancer()

# 노드 설정
BRAIN_NODE_URL = "http://localhost:8091"
EVOLUTION_NODE_URL = "http://localhost:8092"

# 요청 모델
class ConversationRequest(BaseModel):
    user_input: str
    duri_response: str
    metadata: Optional[Dict[str, Any]] = {}

class NodeStatus:
    """노드 상태 관리"""
    def __init__(self):
        self.brain_healthy = False
        self.evolution_healthy = False
        self.last_check = None

node_status = NodeStatus()

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "DuRi Core Node - API Gateway",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "nodes": {
            "brain": BRAIN_NODE_URL,
            "evolution": EVOLUTION_NODE_URL
        }
    }

@app.get("/health")
async def health_check():
    """헬스 체크 - 모든 노드 상태 확인"""
    try:
        async with httpx.AsyncClient() as client:
            # Brain 노드 상태 확인
            try:
                brain_response = await client.get(f"{BRAIN_NODE_URL}/health", timeout=2.0)
                node_status.brain_healthy = brain_response.status_code == 200
            except:
                node_status.brain_healthy = False
            
            # Evolution 노드 상태 확인
            try:
                evolution_response = await client.get(f"{EVOLUTION_NODE_URL}/health", timeout=2.0)
                node_status.evolution_healthy = evolution_response.status_code == 200
            except:
                node_status.evolution_healthy = False
        
        node_status.last_check = datetime.now().isoformat()
        
        return {
            "status": "healthy" if (node_status.brain_healthy and node_status.evolution_healthy) else "degraded",
            "timestamp": datetime.now().isoformat(),
            "nodes": {
                "brain": {
                    "url": BRAIN_NODE_URL,
                    "healthy": node_status.brain_healthy
                },
                "evolution": {
                    "url": EVOLUTION_NODE_URL,
                    "healthy": node_status.evolution_healthy
                }
            }
        }
        
    except Exception as e:
        logger.error(f"헬스 체크 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/conversation/process")
async def process_conversation(request: ConversationRequest):
    """통합 대화 처리 - 성능 최적화 적용"""
    try:
        user_input = request.user_input
        duri_response = request.duri_response
        metadata = request.metadata or {}
        
        if not user_input or not duri_response:
            raise HTTPException(status_code=400, detail="user_input과 duri_response가 필요합니다")
        
        logger.info(f"🔄 최적화된 대화 처리 시작: {len(user_input)}자 입력, {len(duri_response)}자 응답")
        
        # 성장 레벨 시스템을 통한 자극-반응 처리
        growth_result = growth_level_system.process_stimulus(user_input, duri_response)
        
        # 성능 최적화를 통한 처리
        optimized_result = await performance_optimizer.optimize_request(user_input, duri_response, metadata)
        
        logger.info(f"✅ 최적화된 대화 처리 완료: 점수 {optimized_result.get('integrated_score', 0):.3f}")
        
        # 성장 레벨 시스템 결과 추가
        final_result = {
            **optimized_result,
            "growth_system": {
                "current_level": growth_result["current_level"],
                "level_info": growth_result["level_info"],
                "response": growth_result["response"],
                "learning_triggered": growth_result["learning_triggered"],
                "evolution": growth_result["evolution"]
            }
        }
        
        return final_result
        
    except Exception as e:
        logger.error(f"❌ 최적화된 대화 처리 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _call_brain_node(user_input: str, duri_response: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Brain 노드 호출"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BRAIN_NODE_URL}/analyze",
                json={
                    "user_input": user_input,
                    "duri_response": duri_response,
                    "metadata": metadata
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Brain 노드 오류: {response.status_code}")
                return {"error": f"Brain node error: {response.status_code}"}
                
    except Exception as e:
        logger.error(f"Brain 노드 호출 오류: {e}")
        return {"error": str(e)}

async def _call_evolution_node(user_input: str, duri_response: str, brain_result: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Evolution 노드 호출"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{EVOLUTION_NODE_URL}/learn",
                json={
                    "user_input": user_input,
                    "duri_response": duri_response,
                    "brain_analysis": brain_result,
                    "metadata": metadata
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Evolution 노드 오류: {response.status_code}")
                return {"error": f"Evolution node error: {response.status_code}"}
                
    except Exception as e:
        logger.error(f"Evolution 노드 호출 오류: {e}")
        return {"error": str(e)}

def _integrate_results(brain_result: Dict[str, Any], evolution_result: Dict[str, Any]) -> Dict[str, Any]:
    """Brain과 Evolution 결과 통합"""
    try:
        # 통합 점수 계산
        brain_score = brain_result.get("analysis_score", 0.0)
        evolution_score = evolution_result.get("learning_score", 0.0)
        integrated_score = (brain_score + evolution_score) / 2.0
        
        return {
            "status": "success",
            "conversation_id": f"core_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "integrated_score": integrated_score,
            "brain_analysis": brain_result,
            "evolution_learning": evolution_result,
            "timestamp": datetime.now().isoformat(),
            "processing_time": time.time()
        }
        
    except Exception as e:
        logger.error(f"결과 통합 오류: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/dashboard")
async def get_dashboard():
    """대시보드"""
    try:
        # 대시보드 HTML 파일 읽기
        with open("dashboard.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"대시보드 생성 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/performance")
async def get_performance_metrics():
    """성능 메트릭 조회"""
    try:
        # 노드 상태 확인
        await load_balancer.check_node_health()
        
        return {
            "status": "success",
            "performance_metrics": performance_optimizer.get_performance_metrics(),
            "load_balancing": load_balancer.get_load_balancing_stats(),
            "cache_stats": performance_optimizer.get_cache_stats(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"성능 메트릭 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/performance/clear-cache")
async def clear_cache():
    """캐시 클리어"""
    try:
        performance_optimizer.clear_cache()
        return {
            "status": "success",
            "message": "캐시가 성공적으로 클리어되었습니다",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"캐시 클리어 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/growth/status")
async def get_growth_status():
    """성장 상태 조회 (대역폭 정보 포함)"""
    try:
        status = growth_level_system.get_growth_status()
        bandwidth_status = cognitive_bandwidth_manager.get_bandwidth_status()
        
        return {
            "status": "success",
            "growth_status": status,
            "bandwidth_status": bandwidth_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"성장 상태 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bandwidth/status")
async def get_bandwidth_status():
    """인지 대역폭 상태 조회"""
    try:
        # 과부하 복구 확인
        cognitive_bandwidth_manager.check_overload_recovery()
        
        status = cognitive_bandwidth_manager.get_bandwidth_status()
        recommendations = cognitive_bandwidth_manager.get_processing_recommendations()
        
        return {
            "status": "success",
            "bandwidth_status": status,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"대역폭 상태 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bandwidth/update-level")
async def update_bandwidth_level(request: dict):
    """대역폭 레벨 업데이트"""
    try:
        new_level = request.get("level")
        if not new_level or not isinstance(new_level, int):
            raise HTTPException(status_code=400, detail="유효한 레벨이 필요합니다")
        
        cognitive_bandwidth_manager.update_level(new_level)
        
        return {
            "status": "success",
            "message": f"대역폭 레벨이 {new_level}로 업데이트되었습니다",
            "new_level": new_level,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"대역폭 레벨 업데이트 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/emotion/analyze")
async def analyze_emotion(text: str = ""):
    """감정 분석"""
    try:
        if not text:
            raise HTTPException(status_code=400, detail="text 파라미터가 필요합니다")
        
        # 감정 필터 활성화
        enhanced_emotion_filter.set_active(True)
        
        analysis = enhanced_emotion_filter.analyze_emotion(text)
        
        return {
            "status": "success",
            "emotion_analysis": {
                "primary_emotion": analysis.primary_emotion.value,
                "intensity": analysis.intensity.value,
                "confidence": analysis.confidence,
                "secondary_emotions": [emotion.value for emotion in analysis.secondary_emotions],
                "bias_detected": analysis.bias_detected.value,
                "meta_cognition": analysis.meta_cognition,
                "timestamp": analysis.timestamp
            }
        }
        
    except Exception as e:
        logger.error(f"감정 분석 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/emotion/analyze")
async def analyze_emotion_post(request: dict):
    """감정 분석 (POST 방식)"""
    try:
        text = request.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="text 필드가 필요합니다")
        
        # 감정 필터 활성화
        enhanced_emotion_filter.set_active(True)
        
        analysis = enhanced_emotion_filter.analyze_emotion(text)
        
        return {
            "status": "success",
            "emotion_analysis": {
                "primary_emotion": analysis.primary_emotion.value,
                "intensity": analysis.intensity.value,
                "confidence": analysis.confidence,
                "secondary_emotions": [emotion.value for emotion in analysis.secondary_emotions],
                "bias_detected": analysis.bias_detected.value,
                "meta_cognition": analysis.meta_cognition,
                "timestamp": analysis.timestamp
            }
        }
        
    except Exception as e:
        logger.error(f"감정 분석 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/emotion/status")
async def get_emotion_status():
    """감정 필터 상태 조회"""
    try:
        history = enhanced_emotion_filter.get_emotion_history(5)
        recommendations = enhanced_emotion_filter.get_processing_recommendations()
        
        return {
            "status": "success",
            "emotion_filter": {
                "active": enhanced_emotion_filter.active,
                "current_emotion": enhanced_emotion_filter.current_emotion.value if enhanced_emotion_filter.current_emotion else None,
                "emotion_weight": enhanced_emotion_filter.get_emotion_weight(),
                "recommendations": recommendations,
                "recent_history": [
                    {
                        "emotion": analysis.primary_emotion.value,
                        "intensity": analysis.intensity.value,
                        "bias": analysis.bias_detected.value,
                        "timestamp": analysis.timestamp
                    }
                    for analysis in history
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"감정 상태 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/growth/stimulus")
async def process_growth_stimulus(request: ConversationRequest):
    """성장 자극 처리 (대역폭 관리 통합)"""
    try:
        user_input = request.user_input
        duri_response = request.duri_response
        
        if not user_input:
            raise HTTPException(status_code=400, detail="user_input이 필요합니다")
        
        # 성장 레벨 시스템을 통한 자극-반응 처리 (대역폭 관리 포함)
        result = growth_level_system.process_stimulus(user_input, duri_response or "")
        
        # 대역폭 상태 확인
        bandwidth_status = cognitive_bandwidth_manager.get_bandwidth_status()
        
        return {
            "status": "success",
            "growth_result": result,
            "bandwidth_status": bandwidth_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"성장 자극 처리 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("🚀 DuRi Core Node 시작")
    uvicorn.run(app, host="0.0.0.0", port=8090) 