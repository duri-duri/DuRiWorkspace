#!/usr/bin/env python3
"""
성능 모니터링이 통합된 DuRi 자가진화 AI 시스템 (인간형 AI 모듈 추가)
"""

import functools
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "duri_modules"))

# 모듈화된 시스템 import
from duri_modules import (
    chatgpt_evaluator,
    context_analyzer,
    conversation_store,
    dashboard_generator,
    duri_chatgpt_discussion,
    duri_self_reflector,
    emotion_analyzer,
    intuitive_judgment,
    meta_loop_system,
    performance_tracker,
)

app = FastAPI(
    title="DuRi Monitored Self-Evolving AI System",
    description="성능 모니터링이 통합된 자가진화 AI 시스템 (인간형 AI 모듈 포함)",
    version="4.0.0",
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
                performance_tracker.track_request(
                    endpoint_name, response_time, success, error_message
                )

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
        "version": "4.0.0",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "evaluation": "✅ loaded",
            "reflection": "✅ loaded",
            "discussion": "✅ loaded",
            "data_store": "✅ loaded",
            "performance_tracker": "✅ loaded",
            "context_analyzer": "✅ loaded",
            "intuitive_judgment": "✅ loaded",
            "emotion_analyzer": "✅ loaded",
        },
        "performance": health_data,
    }


@app.post("/context-analyze")
@track_performance("context_analyze")
async def analyze_context(context_request: Dict[str, Any]):
    """맥락 분석 (인간형 AI 모듈)"""
    try:
        conversation_history = context_request.get("conversation_history", [])

        # 맥락 분석 수행
        context_result = context_analyzer.analyze_conversation_context(
            conversation_history
        )

        return {
            "status": "success",
            "context_analysis": context_result,
            "message": "맥락 분석이 완료되었습니다",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"❌ 맥락 분석 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/intuitive-judgment")
@track_performance("intuitive_judgment")
async def trigger_intuitive_judgment(intuitive_request: Dict[str, Any]):
    """직관적 판단 트리거 (인간형 AI 모듈)"""
    try:
        user_input = intuitive_request.get("user_input", "")
        context = intuitive_request.get("context", {})

        if not user_input:
            raise HTTPException(status_code=400, detail="user_input이 필요합니다")

        # 직관적 판단 트리거
        intuitive_result = intuitive_judgment.trigger_intuitive_response(
            user_input, context
        )

        return {
            "status": "success",
            "intuitive_judgment": intuitive_result,
            "should_trigger": intuitive_judgment.should_trigger_intuition(
                user_input, context
            ),
            "message": "직관적 판단이 완료되었습니다",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"❌ 직관적 판단 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/emotion-analyze")
@track_performance("emotion_analyze")
async def analyze_emotion(emotion_request: Dict[str, Any]):
    """감정 분석 (인간형 AI 모듈)"""
    try:
        text = emotion_request.get("text", "")
        context = emotion_request.get("context", None)

        if not text:
            raise HTTPException(status_code=400, detail="text가 필요합니다")

        # 감정 분석 수행
        emotion_result = emotion_analyzer.analyze_user_emotion(text, context)

        # 감정에 적응한 응답 생성
        adaptive_response = emotion_analyzer.generate_emotion_adaptive_response(
            emotion_result["primary_emotion"], context
        )

        return {
            "status": "success",
            "emotion_analysis": emotion_result,
            "adaptive_response": adaptive_response,
            "message": "감정 분석이 완료되었습니다",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"❌ 감정 분석 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/human-ai-response")
@track_performance("human_ai_response")
async def generate_human_ai_response(human_request: Dict[str, Any]):
    """인간형 AI 응답 생성 (통합 모듈)"""
    try:
        user_input = human_request.get("user_input", "")
        conversation_history = human_request.get("conversation_history", [])

        if not user_input:
            raise HTTPException(status_code=400, detail="user_input이 필요합니다")

        # 1. 맥락 분석
        context_result = context_analyzer.analyze_conversation_context(
            conversation_history
        )

        # 2. 감정 분석
        emotion_result = emotion_analyzer.analyze_user_emotion(
            user_input, context_result
        )

        # 3. 직관적 판단 트리거
        intuitive_result = intuitive_judgment.trigger_intuitive_response(
            user_input, context_result
        )

        # 4. 감정에 적응한 응답 생성
        adaptive_response = emotion_analyzer.generate_emotion_adaptive_response(
            emotion_result["primary_emotion"], context_result
        )

        # 5. 통합 응답 생성
        integrated_response = _generate_integrated_response(
            user_input,
            context_result,
            emotion_result,
            intuitive_result,
            adaptive_response,
        )

        return {
            "status": "success",
            "integrated_response": integrated_response,
            "context_analysis": context_result,
            "emotion_analysis": emotion_result,
            "intuitive_judgment": intuitive_result,
            "adaptive_response": adaptive_response,
            "message": "인간형 AI 응답이 생성되었습니다",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"❌ 인간형 AI 응답 생성 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_integrated_response(
    user_input: str,
    context: Dict,
    emotion: Dict,
    intuitive: Optional[Dict],
    adaptive: Dict,
) -> Dict[str, Any]:
    """통합 응답 생성"""

    # 기본 응답 템플릿
    base_response = (
        adaptive["suggested_phrases"][0]
        if adaptive["suggested_phrases"]
        else "알겠습니다. 진행하겠습니다."
    )

    # 직관적 판단이 있을 경우 통합
    if intuitive and intuitive["confidence"] > 0.7:
        integrated_text = f"{intuitive['response']} {base_response}"
    else:
        integrated_text = base_response

    # 맥락 정보 추가
    context_summary = context.get("context_summary", "")

    return {
        "response_text": integrated_text,
        "tone": adaptive["tone"],
        "style": adaptive["style"],
        "context_summary": context_summary,
        "emotion": emotion["primary_emotion"],
        "intensity": emotion["intensity"],
        "confidence": {
            "context": context["confidence"],
            "emotion": emotion["confidence"],
            "intuitive": intuitive["confidence"] if intuitive else 0.0,
        },
        "human_like_indicators": {
            "context_aware": context["confidence"] > 0.7,
            "emotion_adaptive": emotion["confidence"] > 0.6,
            "intuitive_triggered": intuitive is not None,
            "natural_flow": context["conversation_flow"]["flow_type"] != "single",
        },
    }


@app.post("/chatgpt-evaluate")
@track_performance("chatgpt_evaluate")
async def chatgpt_evaluate_response(evaluation_request: Dict[str, Any]):
    """ChatGPT 6차원 평가 (성능 모니터링 포함)"""
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
        raise HTTPException(status_code=500, detail=str(e))


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
        improvement_count = len(
            reflection_result.get("improvement_proposal", {}).get(
                "specific_improvements", []
            )
        )
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
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/capture-conversation")
@track_performance("capture_conversation")
async def capture_conversation_endpoint(conversation_data: Dict[str, Any]):
    """실제 대화 데이터 수집 (성능 모니터링 포함)"""
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

        # 학습 메트릭 추적
        learning_value = conversation_store._calculate_learning_value(
            user_input, duri_response
        )
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
            evaluation_result = chatgpt_evaluator.evaluate_response(
                duri_response, user_input
            )
            print(
                f"   📊 ChatGPT 평가 완료: 총점 {evaluation_result.get('total_score', 0):.3f}"
            )

            # 2단계: DuRi 자기성찰
            reflection_result = duri_self_reflector.reflect_on_chatgpt_feedback(
                evaluation_result, duri_response, user_input
            )
            print(
                f"   🤔 DuRi 자기성찰 완료: {len(reflection_result.get('improvement_proposal', {}).get('specific_improvements', []))}개 개선안"
            )

            # 3단계: DuRi-ChatGPT 논의 (선택적)
            discussion_result = None
            if evaluation_result.get("total_score", 0) < 0.5:  # 낮은 점수일 때만 논의
                discussion_result = duri_chatgpt_discussion.initiate_discussion(
                    reflection_result.get("improvement_proposal", {}), evaluation_result
                )
                print(
                    f"   📥 DuRi-ChatGPT 논의 완료: 합의 수준 {discussion_result.get('agreement_level', 0):.2f}"
                )

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
                        reflection_result.get("improvement_proposal", {}).get(
                            "specific_improvements", []
                        )
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
                        reflection_result.get("improvement_proposal", {}).get(
                            "specific_improvements", []
                        )
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
        raise HTTPException(status_code=500, detail=str(e))


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
        raise HTTPException(status_code=500, detail=str(e))


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
        raise HTTPException(status_code=500, detail=str(e))


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
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard")
async def get_dashboard():
    """실시간 대시보드 생성"""
    try:
        # 필요한 데이터 수집
        performance_summary = performance_tracker.get_performance_summary()
        learning_stats = conversation_store.get_learning_statistics()
        meta_stats = meta_loop_system.get_meta_learning_statistics()

        # 대시보드 생성
        dashboard_path = dashboard_generator.generate_dashboard(
            performance_summary, learning_stats, meta_stats
        )

        return {
            "status": "success",
            "dashboard_path": dashboard_path,
            "dashboard_url": f"file://{dashboard_path}",
            "message": "대시보드가 성공적으로 생성되었습니다",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"❌ 대시보드 생성 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)
