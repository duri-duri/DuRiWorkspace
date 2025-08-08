#!/usr/bin/env python3
"""
DuRiCore - 헬스체크 API 엔드포인트
전체 시스템 상태 확인
"""

from fastapi import APIRouter
from typing import Dict, Any
import sys
import os

# DuRiCore 모듈 임포트를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from DuRiCore.DuRiCore.modules.emotion_engine import EmotionEngine
from DuRiCore.DuRiCore.modules.learning_engine import LearningEngine
from DuRiCore.DuRiCore.modules.ethical_reasoning import EthicalReasoningEngine
from DuRiCore.DuRiCore.modules.self_evolution import SelfEvolutionEngine

router = APIRouter()

@router.get("/")
async def health_check():
    """전체 시스템 헬스체크"""
    try:
        # 각 엔진 상태 확인
        engines_status = {}
        
        # 감정 엔진 상태 확인
        try:
            emotion_engine = EmotionEngine()
            test_input = {"text": "안녕하세요!", "context": {"type": "greeting"}}
            emotion_result = emotion_engine.analyze_complex_emotion(test_input)
            engines_status["emotion_engine"] = {
                "status": "healthy",
                "test_result": {
                    "primary_emotion": emotion_result.primary_emotion.value,
                    "confidence": emotion_result.confidence
                }
            }
        except Exception as e:
            engines_status["emotion_engine"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # 학습 엔진 상태 확인
        try:
            learning_engine = LearningEngine()
            learning_result = learning_engine.process_learning(
                content="기본 학습 테스트",
                learning_type="text",
                context={"domain": "test"}
            )
            engines_status["learning_engine"] = {
                "status": "healthy",
                "test_result": {
                    "content_type": learning_result.content_type,
                    "learning_score": learning_result.learning_score
                }
            }
        except Exception as e:
            engines_status["learning_engine"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # 윤리 판단 엔진 상태 확인
        try:
            ethical_engine = EthicalReasoningEngine()
            ethical_result = ethical_engine.analyze_ethical_dilemma(
                situation="기본 윤리 테스트",
                context={"complexity": "low"}
            )
            engines_status["ethical_engine"] = {
                "status": "healthy",
                "test_result": {
                    "ethical_score": ethical_result.ethical_score,
                    "confidence": ethical_result.confidence
                }
            }
        except Exception as e:
            engines_status["ethical_engine"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # 자기 진화 엔진 상태 확인
        try:
            evolution_engine = SelfEvolutionEngine()
            evolution_result = evolution_engine.analyze_and_evolve()
            engines_status["evolution_engine"] = {
                "status": "healthy",
                "test_result": {
                    "evolution_score": evolution_result.evolution_score,
                    "improvement_areas_count": len(evolution_result.improvement_areas)
                }
            }
        except Exception as e:
            engines_status["evolution_engine"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # 전체 상태 평가
        healthy_engines = sum(1 for engine in engines_status.values() if engine["status"] == "healthy")
        total_engines = len(engines_status)
        
        overall_status = "healthy" if healthy_engines == total_engines else "degraded"
        
        return {
            "status": overall_status,
            "system": "DuRiCore",
            "version": "1.0.0",
            "engines": engines_status,
            "summary": {
                "total_engines": total_engines,
                "healthy_engines": healthy_engines,
                "unhealthy_engines": total_engines - healthy_engines,
                "health_percentage": (healthy_engines / total_engines) * 100
            },
            "message": f"DuRiCore 시스템 상태: {overall_status}"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "system": "DuRiCore",
            "error": str(e),
            "message": "시스템 헬스체크 중 오류가 발생했습니다."
        }

@router.get("/engines")
async def get_engines_status():
    """각 엔진별 상세 상태"""
    try:
        engines_info = {
            "emotion_engine": {
                "name": "감정 엔진",
                "description": "복합 감정 분석 및 공감적 반응 생성",
                "endpoints": ["/api/v1/emotion/analyze", "/api/v1/emotion/stats", "/api/v1/emotion/batch-analyze"]
            },
            "learning_engine": {
                "name": "학습 엔진", 
                "description": "다양한 콘텐츠 타입별 학습 처리",
                "endpoints": ["/api/v1/learning/process", "/api/v1/learning/stats", "/api/v1/learning/batch-process"]
            },
            "ethical_engine": {
                "name": "윤리 판단 엔진",
                "description": "윤리적 딜레마 분석 및 권장 행동 생성",
                "endpoints": ["/api/v1/ethical/analyze", "/api/v1/ethical/stats", "/api/v1/ethical/batch-analyze"]
            },
            "evolution_engine": {
                "name": "자기 진화 엔진",
                "description": "자기 성능 분석 및 개선 방향 제시",
                "endpoints": ["/api/v1/evolution/analyze", "/api/v1/evolution/stats", "/api/v1/evolution/improve"]
            }
        }
        
        return {
            "success": True,
            "engines": engines_info,
            "message": "엔진 정보를 성공적으로 조회했습니다."
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "엔진 정보 조회 중 오류가 발생했습니다."
        }

@router.get("/version")
async def get_version_info():
    """버전 정보"""
    try:
        return {
            "system": "DuRiCore",
            "version": "1.0.0",
            "phase": "Phase 3 - Interface Separation",
            "completed_modules": [
                "감정 엔진",
                "자기 진화 엔진", 
                "학습 엔진",
                "윤리 판단 엔진"
            ],
            "next_phase": "Phase 4 - Performance Optimization",
            "message": "DuRiCore 버전 정보를 조회했습니다."
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "버전 정보 조회 중 오류가 발생했습니다."
        } 
 
 