from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import logging
from datetime import datetime

from .api.health import router as health_router
from .api.control import router as control_router
from .api.monitor import router as monitor_router
from .api.resource import router as resource_router
from .api.logs import router as logs_router
from .api.log_query import router as log_query_router
from .api.config import router as config_router
from .api.backup import router as backup_router
from .api.notify import router as notify_router
from .api.gateway import router as gateway_router
from .api.auth import router as auth_router
from .middleware.auth import add_auth_middleware

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(
        title="DuRi Control API",
        description="DuRi 시스템 중앙 제어 허브 API",
        version="1.0.0"
    )
    
    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 루트 레벨 헬스체크 추가
    @app.get("/health")
    async def health_check():
        return {
            "status": "ok",
            "service": "duri_control",
            "timestamp": datetime.now().isoformat()
        }
    
    @app.get("/")
    async def root():
        return RedirectResponse(url="/docs")
    
    # 백업 서비스 초기화
    from .services.backup_service import init_backup_service
    db_config = {
        'host': 'duri-postgres',
        'port': 5432,
        'database': 'duri',
        'user': 'duri',
        'password': 'duri'
    }
    init_backup_service(db_config)
    
    # 게이트웨이 서비스 초기화
    from .services.gateway_service import init_gateway_service
    init_gateway_service()
    
    # 인증 서비스 초기화
    from .services.auth_service import init_auth_service
    init_auth_service()
    
    # 인증 미들웨어 적용 (gateway, config, backup, auth)
    add_auth_middleware(gateway_router)
    add_auth_middleware(config_router)
    add_auth_middleware(backup_router)
    add_auth_middleware(auth_router)
    
    # 라우터 등록
    app.include_router(health_router, prefix="/health", tags=["health"])
    app.include_router(control_router, prefix="/control", tags=["control"])
    app.include_router(monitor_router, prefix="/monitor", tags=["monitor"])
    app.include_router(resource_router, prefix="/monitor", tags=["resource"])
    app.include_router(logs_router, tags=["logs"])
    app.include_router(log_query_router, tags=["log_query"])
    app.include_router(config_router, prefix="/config", tags=["config"])
    app.include_router(backup_router, prefix="/backup", tags=["backup"])
    app.include_router(notify_router, prefix="/notify", tags=["notify"])
    app.include_router(gateway_router, prefix="/gateway", tags=["gateway"])
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    
    logger.info("DuRi Control FastAPI 앱 초기화 완료")
    
    return app 