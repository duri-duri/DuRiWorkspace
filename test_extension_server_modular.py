#!/usr/bin/env python3
"""
모듈화된 DuRi 자가진화 AI 시스템
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "duri_modules"))

# 모듈화된 시스템 import
from duri_modules import (chatgpt_evaluator, conversation_store,
                          duri_chatgpt_discussion, duri_self_reflector)

app = FastAPI(
    title="DuRi Modular Self-Evolving AI System",
    description="모듈화된 자가진화 AI 시스템",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """시스템 상태 확인"""
    return {
        "status": "healthy",
        "service": "duri-modular-system",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "evaluation": "✅ loaded",
            "reflection": "✅ loaded",
            "discussion": "✅ loaded",
        },
    }


@app.post("/chatgpt-evaluate")
async def chatgpt_evaluate_response(evaluation_request: Dict[str, Any]):
    """ChatGPT 6차원 평가 (모듈화된 버전)"""
    try:
        duri_response = evaluation_request.get("duri_response", "")
        user_question = evaluation_request.get("user_question", "")

        if not duri_response or not user_question:
            raise HTTPException(
                status_code=400, detail="duri_response와 user_question이 필요합니다"
            )

        # 모듈화된 평가 시스템 사용
        evaluation_result = chatgpt_evaluator.evaluate_response(
            duri_response, user_question
        )

        return {
            "status": "success",
            "evaluation": evaluation_result,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"❌ ChatGPT 평가 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/duri-self-reflect")
async def duri_self_reflect_endpoint(reflection_request: Dict[str, Any]):
    """DuRi 자기성찰 (모듈화된 버전)"""
    try:
        chatgpt_evaluation = reflection_request.get("chatgpt_evaluation", {})
        original_response = reflection_request.get("original_response", "")
        user_question = reflection_request.get("user_question", "")

        if not chatgpt_evaluation or not original_response:
            raise HTTPException(
                status_code=400,
                detail="chatgpt_evaluation과 original_response가 필요합니다",
            )

        # 모듈화된 자기성찰 시스템 사용
        reflection_result = duri_self_reflector.reflect_on_chatgpt_feedback(
            chatgpt_evaluation, original_response, user_question
        )

        return {
            "status": "success",
            "reflection": reflection_result,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"❌ DuRi 자기성찰 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/duri-chatgpt-discuss")
async def duri_chatgpt_discussion_endpoint(discussion_request: Dict[str, Any]):
    """DuRi-ChatGPT 논의 (모듈화된 버전)"""
    try:
        duri_improvement_proposal = discussion_request.get(
            "duri_improvement_proposal", {}
        )
        chatgpt_evaluation = discussion_request.get("chatgpt_evaluation", {})

        if not duri_improvement_proposal or not chatgpt_evaluation:
            raise HTTPException(
                status_code=400,
                detail="duri_improvement_proposal과 chatgpt_evaluation이 필요합니다",
            )

        # 모듈화된 논의 시스템 사용
        discussion_result = duri_chatgpt_discussion.initiate_discussion(
            duri_improvement_proposal, chatgpt_evaluation
        )

        return {
            "status": "success",
            "discussion": discussion_result,
            "message": f"논의 완료 (합의 수준: {discussion_result['agreement_level']:.2f})",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"❌ DuRi-ChatGPT 논의 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/capture-conversation")
async def capture_conversation_endpoint(conversation_data: Dict[str, Any]):
    """실제 대화 데이터 수집 (ChatGPT 제안 기반)"""
    try:
        user_input = conversation_data.get("user_input", "")
        duri_response = conversation_data.get("duri_response", "")
        metadata = conversation_data.get("metadata", {})

        if not user_input or not duri_response:
            raise HTTPException(
                status_code=400, detail="user_input과 duri_response가 필요합니다"
            )

        # 대화 데이터 저장
        conversation_id = conversation_store.store_conversation(
            user_input, duri_response, metadata
        )

        # 자동 학습 루프 시작 (선택적)
        if conversation_data.get("auto_learn", False):
            # ChatGPT 평가
            evaluation_result = chatgpt_evaluator.evaluate_response(
                duri_response, user_input
            )

            # DuRi 자기성찰
            reflection_result = duri_self_reflector.reflect_on_chatgpt_feedback(
                evaluation_result, duri_response, user_input
            )

            # 학습 결과 저장
            learning_data = {
                "conversation_id": conversation_id,
                "evaluation": evaluation_result,
                "reflection": reflection_result,
                "timestamp": datetime.now().isoformat(),
            }

            return {
                "status": "success",
                "conversation_id": conversation_id,
                "message": "대화 저장 및 자동 학습 완료",
                "learning_data": learning_data,
                "timestamp": datetime.now().isoformat(),
            }

        return {
            "status": "success",
            "conversation_id": conversation_id,
            "message": "대화 저장 완료",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"❌ 대화 저장 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversation-history")
async def get_conversation_history(limit: int = 20):
    """대화 기록 조회"""
    try:
        history = conversation_store.get_conversation_history(limit)
        return {
            "status": "success",
            "conversations": history,
            "total_count": len(history),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"❌ 대화 기록 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/learning-statistics")
async def get_learning_statistics():
    """학습 통계 조회"""
    try:
        stats = conversation_store.get_learning_statistics()
        patterns = conversation_store.extract_learning_patterns()

        return {
            "status": "success",
            "statistics": stats,
            "learning_patterns": patterns,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"❌ 학습 통계 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/module-status")
async def get_module_status():
    """모듈 상태 확인"""
    return {
        "status": "success",
        "modules": {
            "evaluation": {
                "name": "ChatGPT Evaluator",
                "status": "active",
                "description": "6차원 평가 시스템",
            },
            "reflection": {
                "name": "DuRi Self Reflector",
                "status": "active",
                "description": "자기성찰 시스템",
            },
            "discussion": {
                "name": "DuRi-ChatGPT Discussion",
                "status": "active",
                "description": "논의 시스템",
            },
        },
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8087)
