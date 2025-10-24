#!/usr/bin/env python3
"""
성능 모니터링이 통합된 DuRi 자가진화 AI 시스템
"""

import functools
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "duri_modules"))

# 모듈화된 시스템 import
from duri_modules import (  # noqa: E402
    chatgpt_evaluator,
    conversation_store,
    dashboard_generator,
    duri_chatgpt_discussion,
    duri_self_reflector,
    meta_loop_system,
    performance_tracker,
)

app = FastAPI(
    title="DuRi Monitored Self-Evolving AI System",
    description="성능 모니터링이 통합된 자가진화 AI 시스템",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def track_performance(endpoint_name: str):
    """성능 추적 데코레이터"""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error_message = None

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_message = str(e)
                raise
            finally:
                response_time = time.time() - start_time
                performance_tracker.track_request(endpoint_name, response_time, success, error_message)

        return wrapper

    return decorator


@app.get("/health")
@track_performance("health_check")
async def health_check():
    """시스템 상태 확인 (성능 모니터링 포함)"""
    health_data = performance_tracker.get_health_check()

    return {
        "status": "healthy",
        "service": "duri-monitored-system",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "evaluation": "✅ loaded",
            "reflection": "✅ loaded",
            "discussion": "✅ loaded",
            "data_store": "✅ loaded",
            "performance_tracker": "✅ loaded",
        },
        "performance": health_data,
    }


@app.post("/chatgpt-evaluate")
@track_performance("chatgpt_evaluate")
async def chatgpt_evaluate_response(evaluation_request: Dict[str, Any]):
    """ChatGPT 6차원 평가 (성능 모니터링 포함)"""
    try:
        duri_response = evaluation_request.get("duri_response", "")
        user_question = evaluation_request.get("user_question", "")

        if not duri_response or not user_question:
            raise HTTPException(status_code=400, detail="duri_response와 user_question이 필요합니다")

        # 모듈화된 평가 시스템 사용
        evaluation_result = chatgpt_evaluator.evaluate_response(duri_response, user_question)

        # 학습 메트릭 추적
        performance_tracker.track_learning_metric(
            "evaluation_score",
            evaluation_result.get("total_score", 0.0),
            {"user_question": user_question[:50]},
        )

        return {
            "status": "success",
            "evaluation": evaluation_result,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"❌ ChatGPT 평가 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))  # noqa: B904


@app.post("/duri-self-reflect")
@track_performance("duri_self_reflect")
async def duri_self_reflect_endpoint(reflection_request: Dict[str, Any]):
    """DuRi 자기성찰 (성능 모니터링 포함)"""
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

        # 학습 메트릭 추적
        improvement_count = len(reflection_result.get("improvement_proposal", {}).get("specific_improvements", []))
        performance_tracker.track_learning_metric(
            "improvement_suggestions",
            improvement_count,
            {"reflection_depth": len(reflection_result.get("accepted_criticisms", []))},
        )

        return {
            "status": "success",
            "reflection": reflection_result,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"❌ DuRi 자기성찰 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))  # noqa: B904


@app.post("/capture-conversation")
@track_performance("capture_conversation")
async def capture_conversation_endpoint(conversation_data: Dict[str, Any]):
    """실제 대화 데이터 수집 (성능 모니터링 포함)"""
    try:
        user_input = conversation_data.get("user_input", "")
        duri_response = conversation_data.get("duri_response", "")
        metadata = conversation_data.get("metadata", {})

        if not user_input or not duri_response:
            raise HTTPException(status_code=400, detail="user_input과 duri_response가 필요합니다")

        # 대화 데이터 저장
        conversation_id = conversation_store.store_conversation(user_input, duri_response, metadata)

        # 학습 메트릭 추적
        learning_value = conversation_store._calculate_learning_value(user_input, duri_response)
        performance_tracker.track_learning_metric(
            "conversation_learning_value",
            learning_value,
            {"conversation_id": conversation_id},
        )

        # 자동 학습 루프 시작 (기본 활성화)
        auto_learn = conversation_data.get("auto_learn", True)  # 기본값을 True로 변경

        if auto_learn:
            print(f"🔄 자동 학습 루프 시작: {conversation_id}")

            # 1단계: ChatGPT 평가
            evaluation_result = chatgpt_evaluator.evaluate_response(duri_response, user_input)
            print(f"   📊 ChatGPT 평가 완료: 총점 {evaluation_result.get('total_score', 0):.3f}")

            # 2단계: DuRi 자기성찰
            reflection_result = duri_self_reflector.reflect_on_chatgpt_feedback(
                evaluation_result, duri_response, user_input
            )
            print(
                f"   🤔 DuRi 자기성찰 완료: {len(reflection_result.get('improvement_proposal', {}).get('specific_improvements', []))}개 개선안"  # noqa: E501
            )

            # 3단계: DuRi-ChatGPT 논의 (선택적)
            discussion_result = None
            if evaluation_result.get("total_score", 0) < 0.5:  # 낮은 점수일 때만 논의
                discussion_result = duri_chatgpt_discussion.initiate_discussion(
                    reflection_result.get("improvement_proposal", {}), evaluation_result
                )
                print(f"   📥 DuRi-ChatGPT 논의 완료: 합의 수준 {discussion_result.get('agreement_level', 0):.2f}")

            # 4단계: 학습 결과 저장 및 메타 루프 준비
            learning_data = {
                "conversation_id": conversation_id,
                "evaluation": evaluation_result,
                "reflection": reflection_result,
                "discussion": discussion_result,
                "auto_learn_enabled": True,
                "learning_cycle_completed": True,
                "timestamp": datetime.now().isoformat(),
            }

            # 메타 학습 메트릭 추적
            performance_tracker.track_learning_metric(
                "learning_cycle_completion",
                1.0,
                {
                    "conversation_id": conversation_id,
                    "evaluation_score": evaluation_result.get("total_score", 0),
                    "improvement_count": len(
                        reflection_result.get("improvement_proposal", {}).get("specific_improvements", [])
                    ),
                },
            )

            return {
                "status": "success",
                "conversation_id": conversation_id,
                "message": "대화 저장 및 자동 학습 루프 완료",
                "learning_data": learning_data,
                "learning_summary": {
                    "evaluation_score": evaluation_result.get("total_score", 0),
                    "improvement_suggestions": len(
                        reflection_result.get("improvement_proposal", {}).get("specific_improvements", [])
                    ),
                    "discussion_held": discussion_result is not None,
                    "cycle_completed": True,
                },
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
        raise HTTPException(status_code=500, detail=str(e))  # noqa: B904


@app.get("/performance-summary")
async def get_performance_summary():
    """성능 요약 조회"""
    try:
        summary = performance_tracker.get_performance_summary()
        return {
            "status": "success",
            "summary": summary,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"❌ 성능 요약 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))  # noqa: B904


@app.get("/system-health")
async def get_system_health():
    """시스템 건강도 확인"""
    try:
        health_data = performance_tracker.get_health_check()
        return {
            "status": "success",
            "health": health_data,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"❌ 시스템 건강도 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))  # noqa: B904


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
        raise HTTPException(status_code=500, detail=str(e))  # noqa: B904


@app.post("/meta-evaluate-improvement")
@track_performance("meta_evaluate_improvement")
async def meta_evaluate_improvement_endpoint(meta_request: Dict[str, Any]):
    """메타 루프: 개선 효과 평가"""
    try:
        original_response = meta_request.get("original_response", "")
        improved_response = meta_request.get("improved_response", "")
        user_question = meta_request.get("user_question", "")
        original_evaluation = meta_request.get("original_evaluation", {})

        if not original_response or not improved_response or not user_question:
            raise HTTPException(
                status_code=400,
                detail="original_response, improved_response, user_question이 필요합니다",
            )

        # 메타 루프 시스템 사용
        meta_result = meta_loop_system.evaluate_improvement_effect(
            original_response, improved_response, user_question, original_evaluation
        )

        # 개선 피드백 생성
        feedback = meta_loop_system.generate_improvement_feedback(meta_result)

        # 학습 메트릭 추적
        improvement_score = meta_result.get("meta_score", 0)
        performance_tracker.track_learning_metric(
            "meta_improvement_score",
            improvement_score,
            {
                "improvement_success": feedback.get("improvement_success", False),
                "overall_improvement": feedback.get("overall_improvement", 0),
            },
        )

        return {
            "status": "success",
            "meta_evaluation": meta_result,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"❌ 메타 평가 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))  # noqa: B904


@app.get("/meta-learning-statistics")
async def get_meta_learning_statistics():
    """메타 학습 통계 조회"""
    try:
        meta_stats = meta_loop_system.get_meta_learning_statistics()

        return {
            "status": "success",
            "meta_learning_statistics": meta_stats,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"❌ 메타 학습 통계 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))  # noqa: B904


@app.get("/dashboard")
async def get_dashboard():
    """실시간 대시보드 생성"""
    try:
        # 필요한 데이터 수집
        performance_summary = performance_tracker.get_performance_summary()
        learning_stats = conversation_store.get_learning_statistics()
        meta_stats = meta_loop_system.get_meta_learning_statistics()

        # 대시보드 생성
        dashboard_path = dashboard_generator.generate_dashboard(performance_summary, learning_stats, meta_stats)

        return {
            "status": "success",
            "dashboard_path": dashboard_path,
            "dashboard_url": f"file://{dashboard_path}",
            "message": "대시보드가 성공적으로 생성되었습니다",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"❌ 대시보드 생성 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))  # noqa: B904


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)
