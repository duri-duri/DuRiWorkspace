#!/usr/bin/env python3
"""
DuRi 통합 대화 처리 시스템 테스트 서버
모든 대화 관련 기능을 하나의 시스템으로 통합
"""
import asyncio
import time
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
import uvicorn
from pydantic import BaseModel

# 기존 모듈들 import
import sys
sys.path.append('.')

from duri_modules.unified.unified_conversation_processor import unified_processor
from duri_modules.monitoring.performance_tracker import performance_tracker
from duri_modules.data.conversation_store import conversation_store

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="DuRi 통합 대화 처리 시스템", version="1.0.0")

# 요청 모델 정의
class ConversationRequest(BaseModel):
    user_input: str
    duri_response: str
    metadata: Optional[Dict[str, Any]] = {}

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "DuRi 통합 대화 처리 시스템",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "unified_v1"
    }

@app.post("/conversation/process")
async def process_conversation_unified(request: ConversationRequest):
    """통합 대화 처리: 저장 + 분석 + 평가 + 학습"""
    try:
        user_input = request.user_input
        duri_response = request.duri_response
        metadata = request.metadata or {}
        
        if not user_input or not duri_response:
            raise HTTPException(status_code=400, detail="user_input과 duri_response가 필요합니다")
        
        logger.info(f"🔄 통합 대화 처리 시작: {len(user_input)}자 입력, {len(duri_response)}자 응답")
        
        # 통합 처리 실행
        result = await unified_processor.process_conversation(user_input, duri_response, metadata)
        
        logger.info(f"✅ 통합 대화 처리 완료: 점수 {result.integrated_score:.3f}, 처리시간 {result.processing_time:.3f}초")
        
        # 결과 반환
        return {
            "status": "success",
            "conversation_id": result.conversation_id,
            "integrated_score": result.integrated_score,
            "improvement_suggestions": result.improvement_suggestions,
            "processing_time": result.processing_time,
            "timestamp": result.timestamp,
            "analysis": {
                "meaning": result.meaning_analysis,
                "context": result.context_analysis,
                "emotion": result.emotion_analysis
            },
            "evaluation": {
                "chatgpt_evaluation": result.chatgpt_evaluation,
                "result": result.result_evaluation,
                "self_reflection": result.self_reflection
            },
            "learning": {
                "autonomous": result.learning_result,
                "realtime": result.realtime_learning
            }
        }
        
    except Exception as e:
        logger.error(f"❌ 통합 대화 처리 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/autonomous/learning-cycle")
async def execute_autonomous_learning_cycle(request: ConversationRequest):
    """자율 학습 사이클 실행"""
    try:
        # 대화 컨텍스트 준비
        conversation_context = {
            "conversation": {
                "user_input": request.user_input,
                "duri_response": request.duri_response,
                "metadata": request.metadata
            },
            "evaluation": {},
            "analysis": {}
        }
        
        # 자율 학습 사이클 실행
        cycle_result = await unified_processor.autonomous_core.execute_autonomous_learning_cycle(conversation_context)
        
        if cycle_result:
            return {
                "status": "success",
                "cycle_id": cycle_result.cycle_id,
                "overall_score": cycle_result.overall_score,
                "insights": cycle_result.insights,
                "next_actions": cycle_result.next_actions,
                "start_time": cycle_result.start_time,
                "end_time": cycle_result.end_time,
                "components": {
                    "question_generated": cycle_result.question_generated,
                    "learning_completed": cycle_result.learning_completed,
                    "improvement_applied": cycle_result.improvement_applied
                }
            }
        else:
            return {
                "status": "failed",
                "message": "자율 학습 사이클 실행 실패"
            }
        
    except Exception as e:
        logger.error(f"❌ 자율 학습 사이클 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/autonomous/status")
async def get_autonomous_status():
    """자율 학습 시스템 상태 조회"""
    try:
        status = unified_processor.autonomous_core.get_system_status()
        return {
            "status": "success",
            "autonomous_system": status
        }
        
    except Exception as e:
        logger.error(f"❌ 자율 학습 상태 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation/statistics")
async def get_unified_statistics():
    """통합 처리 통계"""
    try:
        # 통합 처리 통계
        unified_stats = unified_processor.get_processing_statistics()
        
        # 기존 통계들도 포함
        conversation_stats = conversation_store.get_statistics()
        performance_stats = performance_tracker.get_summary()
        
        return {
            "unified_processing": unified_stats,
            "conversation_store": conversation_stats,
            "performance": performance_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"통계 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation/history")
async def get_unified_history(limit: int = 10):
    """통합 처리 히스토리"""
    try:
        history = unified_processor.processing_history[-limit:] if unified_processor.processing_history else []
        
        return {
            "history": [
                {
                    "conversation_id": item.conversation_id,
                    "timestamp": item.timestamp,
                    "integrated_score": item.integrated_score,
                    "user_input_length": len(item.user_input),
                    "duri_response_length": len(item.duri_response),
                    "processing_time": item.processing_time,
                    "improvement_suggestions_count": len(item.improvement_suggestions)
                }
                for item in history
            ],
            "total_count": len(unified_processor.processing_history),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"히스토리 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/conversation/end-session")
async def end_conversation_session():
    """대화 세션 종료 및 진화 로그 생성"""
    try:
        result = unified_processor.end_conversation_session()
        return {
            "status": "success",
            "session_end_result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"세션 종료 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/evolution/insights")
async def get_evolution_insights():
    """진화 인사이트 조회"""
    try:
        insights = unified_processor.get_evolution_insights()
        return {
            "status": "success",
            "evolution_insights": insights,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"진화 인사이트 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard")
async def get_unified_dashboard():
    """통합 대시보드"""
    try:
        # 통합 통계
        unified_stats = unified_processor.get_processing_statistics()
        
        # 성능 통계
        performance_stats = performance_tracker.get_summary()
        
        # 대화 저장소 통계
        conversation_stats = conversation_store.get_statistics()
        
        # HTML 대시보드 생성
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>DuRi 통합 대화 처리 시스템</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }}
                .stat-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .stat-title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #333; }}
                .stat-value {{ font-size: 24px; font-weight: bold; color: #667eea; }}
                .stat-detail {{ font-size: 14px; color: #666; margin-top: 5px; }}
                .chart-container {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }}
                .status-indicator {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }}
                .status-active {{ background-color: #4CAF50; }}
                .status-inactive {{ background-color: #f44336; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 DuRi 통합 대화 처리 시스템</h1>
                    <p>모든 대화 관련 기능을 하나의 시스템으로 통합</p>
                    <p>버전: {unified_stats.get('version', 'unified_v1')} | 마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-title">📊 통합 처리 통계</div>
                        <div class="stat-value">{unified_stats.get('total_processed', 0)}</div>
                        <div class="stat-detail">총 처리된 대화 수</div>
                        <div class="stat-detail">평균 점수: {unified_stats.get('average_score', 0.0):.3f}</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-title">💾 대화 저장소</div>
                        <div class="stat-value">{conversation_stats.get('total_conversations', 0)}</div>
                        <div class="stat-detail">저장된 대화 수</div>
                        <div class="stat-detail">학습 가치: {conversation_stats.get('average_learning_value', 0.0):.3f}</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-title">⚡ 성능 통계</div>
                        <div class="stat-value">{performance_stats.get('total_operations', 0)}</div>
                        <div class="stat-detail">총 작업 수</div>
                        <div class="stat-detail">평균 응답 시간: {performance_stats.get('average_response_time', 0.0):.3f}초</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-title">🔄 시스템 상태</div>
                        <div class="stat-value">
                            <span class="status-indicator status-active"></span>활성
                        </div>
                        <div class="stat-detail">통합 처리 시스템 정상 작동 중</div>
                        <div class="stat-detail">마지막 처리: {unified_stats.get('last_processed', 'N/A')}</div>
                    </div>
                </div>
                
                <div class="chart-container">
                    <h3>📈 최근 처리 히스토리</h3>
                    <div style="height: 300px; background: #f9f9f9; border-radius: 5px; padding: 20px; display: flex; align-items: center; justify-content: center; color: #666;">
                        <p>차트 데이터 로딩 중...</p>
                    </div>
                </div>
                
                <div class="chart-container">
                    <h3>🎯 개선 제안</h3>
                    <ul>
                        <li>통합 시스템으로 모든 대화 처리가 단일 경로로 통합됨</li>
                        <li>의미 분석, 평가, 학습이 하나의 흐름으로 연결됨</li>
                        <li>자율학습 루프가 완전히 통합되어 자기 개선 가능</li>
                        <li>중복 제거로 성능 향상 및 유지보수성 개선</li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"대시보드 생성 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/conversation/test")
async def test_unified_system():
    """통합 시스템 테스트"""
    try:
        # 테스트 대화 데이터
        test_conversation = {
            "user_input": "통합 시스템이 잘 작동하는지 테스트해보자",
            "duri_response": "네, 통합 대화 처리 시스템이 정상적으로 작동하고 있습니다. 모든 기능이 하나의 흐름으로 연결되어 있어 효율적인 학습이 가능합니다.",
            "metadata": {
                "test": True,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # 통합 처리 실행
        result = await unified_processor.process_conversation(
            test_conversation["user_input"],
            test_conversation["duri_response"],
            test_conversation["metadata"]
        )
        
        return {
            "status": "success",
            "message": "통합 시스템 테스트 완료",
            "test_result": {
                "conversation_id": result.conversation_id,
                "integrated_score": result.integrated_score,
                "processing_time": result.processing_time,
                "improvement_suggestions_count": len(result.improvement_suggestions)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"테스트 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("🚀 DuRi 통합 대화 처리 시스템 서버 시작")
    uvicorn.run(app, host="0.0.0.0", port=8090) 