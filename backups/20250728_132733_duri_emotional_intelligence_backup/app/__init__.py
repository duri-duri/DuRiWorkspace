from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

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
from .api.memory import router as memory_router
from .api.intelligent_analysis import router as intelligent_analysis_router
from .api.advanced_memory import router as advanced_memory_router
from .api.async_analysis import router as async_analysis_router
from .api.analysis_repository import router as analysis_repository_router
from .api.performance_monitoring import router as performance_monitoring_router
from .api.realtime_sync import router as realtime_sync_router
from .api.dashboard import router as dashboard_router
from .api.evolution import router as evolution_router
from .api.emotional_intelligence import router as emotional_intelligence_router
from .middleware.auth import add_auth_middleware
from .scheduler import start_scheduler

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
    
    # 서비스 매니저를 통한 지연 초기화 설정
    from .services.service_manager import get_service_manager
    service_manager = get_service_manager()
    
    # 서비스 등록
    from .services.backup_service import init_backup_service
    from .services.gateway_service import init_gateway_service
    from .services.auth_service import init_auth_service
    
    def init_backup():
        db_config = {
            'host': 'duri-postgres',
            'port': 5432,
            'database': 'duri',
            'user': 'duri',
            'password': 'duri'
        }
        return init_backup_service(db_config)
    
    service_manager.register_service("BackupService", init_backup)
    service_manager.register_service("GatewayService", init_gateway_service)
    service_manager.register_service("AuthService", init_auth_service)
    
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
    app.include_router(memory_router, tags=["memory"])
    app.include_router(intelligent_analysis_router, tags=["intelligent_analysis"])
    app.include_router(advanced_memory_router, tags=["advanced_memory"])
    app.include_router(async_analysis_router, tags=["async_analysis"])
    app.include_router(analysis_repository_router, tags=["analysis_repository"])
    app.include_router(performance_monitoring_router, tags=["performance_monitoring"])
    app.include_router(realtime_sync_router, tags=["realtime_sync"])
    app.include_router(dashboard_router, tags=["dashboard"])
    app.include_router(evolution_router, tags=["evolution"])
    app.include_router(emotional_intelligence_router, tags=["emotional_intelligence"])
    
    @app.on_event("startup")
    async def startup_event():
        """앱 시작 시 서비스 초기화"""
        logger.info("🚀 DuRi Control 서비스 초기화 시작...")
        
        # 서비스 매니저를 통한 초기화
        from .services.service_manager import get_service_manager
        service_manager = get_service_manager()
        
        if service_manager.initialize_all_services():
            logger.info("✅ 모든 서비스 초기화 완료")
        else:
            logger.error("❌ 서비스 초기화 실패")
            # 여기서는 앱을 중단하지 않고 계속 실행
            # (서비스가 나중에 수동으로 초기화될 수 있음)
        start_scheduler()
        logger.info("[Startup] Truth Memory 자동화 스케줄러가 시작되었습니다.")
    
    logger.info("DuRi Control FastAPI 앱 초기화 완료")
    
    return app 