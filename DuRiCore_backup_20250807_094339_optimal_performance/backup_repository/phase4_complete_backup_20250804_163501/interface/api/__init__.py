#!/usr/bin/env python3
"""
DuRiCore API Module
FastAPI 라우터 통합
"""

from fastapi import APIRouter

from .emotion import router as emotion_router
from .ethical import router as ethical_router
from .evolution import router as evolution_router
from .health import router as health_router
from .learning import router as learning_router

# 메인 라우터 생성
router = APIRouter(prefix="/api/v1")

# 서브 라우터 등록
router.include_router(emotion_router, prefix="/emotion", tags=["emotion"])
router.include_router(learning_router, prefix="/learning", tags=["learning"])
router.include_router(ethical_router, prefix="/ethical", tags=["ethical"])
router.include_router(evolution_router, prefix="/evolution", tags=["evolution"])
router.include_router(health_router, prefix="/health", tags=["health"])

__all__ = [
    "router",
    "emotion_router",
    "learning_router",
    "ethical_router",
    "evolution_router",
    "health_router",
]
