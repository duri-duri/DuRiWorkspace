from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from duri_common.logger import get_logger

logger = get_logger("duri_control.app")

def create_app():
    """FastAPI 앱 팩토리 함수"""
    app = FastAPI(
        title="DuRi Control API",
        description="DuRi Control 모듈 - 시스템 제어 및 모니터링",
        version="1.0.0"
    )
    
    # CORS 미들웨어 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 라우터 등록
    from .api.health import router as health_router
    from .api.control import router as control_router
    from .api.monitor import router as monitor_router
    from .api.resource import router as resource_router
    from .api.logs import router as logs_router
    from .api.log_query import router as log_query_router
    
    app.include_router(health_router, prefix="/health", tags=["health"])
    app.include_router(control_router, prefix="/control", tags=["control"])
    app.include_router(monitor_router, prefix="/monitor", tags=["monitor"])
    app.include_router(resource_router, prefix="/monitor", tags=["resource"])
    app.include_router(logs_router, tags=["logs"])
    app.include_router(log_query_router, tags=["log_query"])
    
    logger.info("DuRi Control FastAPI 앱 초기화 완료")
    return app 