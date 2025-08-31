import logging
logging.basicConfig(level=logging.INFO)
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .services.config_service import get_db_session
from .services.memory_service import MemoryService

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

def scheduled_cleanup_and_evolve():
    logger.info("[Scheduler] Truth Memory 자동 정화/진화 작업 시작")
    db = next(get_db_session())
    memory_service = MemoryService(db)
    cleanup_result = memory_service.auto_cleanup_truth_memories()
    evolve_result = memory_service.auto_evolve_truth_memories()
    logger.info(f"[Scheduler] Cleanup result: {cleanup_result}")
    logger.info(f"[Scheduler] Evolve result: {evolve_result}")
    db.close()

# 스케줄 등록 함수
def start_scheduler():
    # 매 1분마다 실행 (테스트용)
    trigger = CronTrigger(minute='*')
    scheduler.add_job(scheduled_cleanup_and_evolve, trigger, id="truth_memory_auto_job", replace_existing=True)
    scheduler.start()
    logger.info("[Scheduler] Truth Memory 자동화 스케줄러 시작 (매 1분)") 