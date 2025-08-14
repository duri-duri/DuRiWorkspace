"""
자동 통합 스케줄링 모듈
ML 통합 과정을 자동으로 스케줄링하고 실행합니다.
"""

import time
import logging
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import schedule
import queue
import traceback

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """작업 상태 열거형"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"

class TaskPriority(Enum):
    """작업 우선순위 열거형"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ScheduledTask:
    """스케줄된 작업 데이터 클래스"""
    task_id: str
    name: str
    description: str
    function: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    schedule_type: str = "interval"  # interval, daily, weekly, custom
    schedule_value: Any = None  # interval: seconds, daily: time, weekly: day, custom: cron
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    run_count: int = 0
    max_retries: int = 3
    retry_count: int = 0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class TaskScheduler:
    """작업 스케줄러"""
    
    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.task_queue = queue.PriorityQueue()
        self.running = False
        self.worker_thread = None
        self.lock = threading.Lock()
        
        # 스케줄 라이브러리 초기화
        self.scheduler = schedule.Scheduler()
    
    def add_task(self, task: ScheduledTask) -> bool:
        """작업 추가"""
        try:
            with self.lock:
                self.tasks[task.task_id] = task
                
                # 스케줄에 작업 등록
                if task.schedule_type == "interval":
                    self.scheduler.every(task.schedule_value).seconds.do(
                        self._execute_task, task.task_id
                    )
                elif task.schedule_type == "daily":
                    self.scheduler.every().day.at(task.schedule_value).do(
                        self._execute_task, task.task_id
                    )
                elif task.schedule_type == "weekly":
                    self.scheduler.every().week.at(task.schedule_value).do(
                        self._execute_task, task.task_id
                    )
                elif task.schedule_type == "custom":
                    # cron 표현식 처리
                    self._add_cron_task(task)
                
                logger.info(f"작업 추가 완료: {task.name} ({task.task_id})")
                return True
        
        except Exception as e:
            logger.error(f"작업 추가 실패: {str(e)}")
            return False
    
    def _add_cron_task(self, task: ScheduledTask):
        """cron 작업 추가"""
        try:
            # cron 표현식 파싱 (예: "0 9 * * 1" = 매주 월요일 오전 9시)
            cron_parts = task.schedule_value.split()
            if len(cron_parts) == 5:
                minute, hour, day, month, weekday = cron_parts
                
                if weekday != "*":
                    # 특정 요일에 실행
                    self.scheduler.every().monday.at(f"{hour}:{minute}").do(
                        self._execute_task, task.task_id
                    )
                else:
                    # 매일 실행
                    self.scheduler.every().day.at(f"{hour}:{minute}").do(
                        self._execute_task, task.task_id
                    )
        
        except Exception as e:
            logger.error(f"cron 작업 추가 실패: {str(e)}")
    
    def remove_task(self, task_id: str) -> bool:
        """작업 제거"""
        try:
            with self.lock:
                if task_id in self.tasks:
                    del self.tasks[task_id]
                    logger.info(f"작업 제거 완료: {task_id}")
                    return True
                return False
        
        except Exception as e:
            logger.error(f"작업 제거 실패: {str(e)}")
            return False
    
    def _execute_task(self, task_id: str):
        """작업 실행"""
        try:
            task = self.tasks.get(task_id)
            if not task:
                logger.warning(f"작업을 찾을 수 없습니다: {task_id}")
                return
            
            # 작업 상태 업데이트
            task.status = TaskStatus.RUNNING
            task.last_run = datetime.now()
            
            logger.info(f"작업 실행 시작: {task.name}")
            
            # 작업 실행
            result = task.function(*task.args, **task.kwargs)
            
            # 성공 처리
            task.status = TaskStatus.COMPLETED
            task.run_count += 1
            task.retry_count = 0
            task.error_message = None
            
            logger.info(f"작업 실행 완료: {task.name}")
            
            # 다음 실행 시간 계산
            self._calculate_next_run(task)
        
        except Exception as e:
            # 실패 처리
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.retry_count += 1
            
            logger.error(f"작업 실행 실패: {task.name} - {str(e)}")
            
            # 재시도 로직
            if task.retry_count < task.max_retries:
                logger.info(f"작업 재시도 예정: {task.name} ({task.retry_count}/{task.max_retries})")
                # 지수 백오프로 재시도 스케줄링
                retry_delay = min(300, 2 ** task.retry_count)  # 최대 5분
                time.sleep(retry_delay)
                self._execute_task(task_id)
            else:
                logger.error(f"작업 최대 재시도 횟수 초과: {task.name}")
    
    def _calculate_next_run(self, task: ScheduledTask):
        """다음 실행 시간 계산"""
        try:
            if task.schedule_type == "interval":
                task.next_run = datetime.now() + timedelta(seconds=task.schedule_value)
            elif task.schedule_type == "daily":
                # 다음 날 같은 시간
                tomorrow = datetime.now() + timedelta(days=1)
                time_parts = task.schedule_value.split(":")
                hour, minute = int(time_parts[0]), int(time_parts[1])
                task.next_run = tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
            elif task.schedule_type == "weekly":
                # 다음 주 같은 요일 같은 시간
                next_week = datetime.now() + timedelta(weeks=1)
                time_parts = task.schedule_value.split(":")
                hour, minute = int(time_parts[0]), int(time_parts[1])
                task.next_run = next_week.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        except Exception as e:
            logger.error(f"다음 실행 시간 계산 실패: {str(e)}")
    
    def start(self):
        """스케줄러 시작"""
        if self.running:
            logger.warning("스케줄러가 이미 실행 중입니다")
            return
        
        self.running = True
        self.worker_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.worker_thread.start()
        logger.info("작업 스케줄러가 시작되었습니다")
    
    def stop(self):
        """스케줄러 중지"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        logger.info("작업 스케줄러가 중지되었습니다")
    
    def _run_scheduler(self):
        """스케줄러 실행 루프"""
        while self.running:
            try:
                self.scheduler.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"스케줄러 실행 중 오류: {str(e)}")
                time.sleep(5)
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """작업 상태 조회"""
        task = self.tasks.get(task_id)
        return task.status if task else None
    
    def get_all_tasks(self) -> List[ScheduledTask]:
        """모든 작업 목록 반환"""
        with self.lock:
            return list(self.tasks.values())
    
    def pause_task(self, task_id: str) -> bool:
        """작업 일시정지"""
        try:
            task = self.tasks.get(task_id)
            if task:
                task.status = TaskStatus.PENDING
                logger.info(f"작업 일시정지: {task.name}")
                return True
            return False
        
        except Exception as e:
            logger.error(f"작업 일시정지 실패: {str(e)}")
            return False
    
    def resume_task(self, task_id: str) -> bool:
        """작업 재개"""
        try:
            task = self.tasks.get(task_id)
            if task and task.status == TaskStatus.PENDING:
                task.status = TaskStatus.PENDING
                logger.info(f"작업 재개: {task.name}")
                return True
            return False
        
        except Exception as e:
            logger.error(f"작업 재개 실패: {str(e)}")
            return False

class AutoIntegrationManager:
    """자동 통합 관리자"""
    
    def __init__(self):
        self.scheduler = TaskScheduler()
        self.integration_tasks: Dict[str, ScheduledTask] = {}
        self.monitoring_enabled = True
        
        # 기본 통합 작업 등록
        self._register_default_tasks()
    
    def _register_default_tasks(self):
        """기본 통합 작업 등록"""
        # Phase 1 자동 실행 (매일 오전 2시)
        phase1_task = ScheduledTask(
            task_id="phase1_auto_run",
            name="Phase 1 자동 실행",
            description="매일 오전 2시에 Phase 1 문제 해결 자동 실행",
            function=self._run_phase1_integration,
            schedule_type="daily",
            schedule_value="02:00",
            priority=TaskPriority.HIGH
        )
        
        # Phase 2 자동 실행 (매일 오전 4시)
        phase2_task = ScheduledTask(
            task_id="phase2_auto_run",
            name="Phase 2 자동 실행",
            description="매일 오전 4시에 Phase 2 딥러닝 통합 자동 실행",
            function=self._run_phase2_integration,
            schedule_type="daily",
            schedule_value="04:00",
            priority=TaskPriority.HIGH
        )
        
        # 성능 모니터링 (30분마다)
        monitoring_task = ScheduledTask(
            task_id="performance_monitoring",
            name="성능 모니터링",
            description="30분마다 시스템 성능 모니터링",
            function=self._monitor_performance,
            schedule_type="interval",
            schedule_value=1800,  # 30분
            priority=TaskPriority.NORMAL
        )
        
        # 백업 자동 실행 (매일 오전 1시)
        backup_task = ScheduledTask(
            task_id="auto_backup",
            name="자동 백업",
            description="매일 오전 1시에 시스템 자동 백업",
            function=self._run_auto_backup,
            schedule_type="daily",
            schedule_value="01:00",
            priority=TaskPriority.MEDIUM
        )
        
        # 작업 등록
        self.add_integration_task(phase1_task)
        self.add_integration_task(phase2_task)
        self.add_integration_task(monitoring_task)
        self.add_integration_task(backup_task)
    
    def add_integration_task(self, task: ScheduledTask) -> bool:
        """통합 작업 추가"""
        try:
            success = self.scheduler.add_task(task)
            if success:
                self.integration_tasks[task.task_id] = task
                logger.info(f"통합 작업 추가: {task.name}")
            return success
        
        except Exception as e:
            logger.error(f"통합 작업 추가 실패: {str(e)}")
            return False
    
    def remove_integration_task(self, task_id: str) -> bool:
        """통합 작업 제거"""
        try:
            success = self.scheduler.remove_task(task_id)
            if success and task_id in self.integration_tasks:
                del self.integration_tasks[task_id]
                logger.info(f"통합 작업 제거: {task_id}")
            return success
        
        except Exception as e:
            logger.error(f"통합 작업 제거 실패: {str(e)}")
            return False
    
    def start_auto_integration(self):
        """자동 통합 시작"""
        try:
            self.scheduler.start()
            logger.info("자동 통합이 시작되었습니다")
            
            # 모니터링 시작
            if self.monitoring_enabled:
                self._start_monitoring()
        
        except Exception as e:
            logger.error(f"자동 통합 시작 실패: {str(e)}")
    
    def stop_auto_integration(self):
        """자동 통합 중지"""
        try:
            self.scheduler.stop()
            logger.info("자동 통합이 중지되었습니다")
        
        except Exception as e:
            logger.error(f"자동 통합 중지 실패: {str(e)}")
    
    def _run_phase1_integration(self):
        """Phase 1 통합 실행"""
        try:
            logger.info("Phase 1 자동 통합 시작")
            
            # Phase 1 문제 해결 실행
            # 여기에 실제 Phase 1 로직 구현
            
            logger.info("Phase 1 자동 통합 완료")
        
        except Exception as e:
            logger.error(f"Phase 1 자동 통합 실패: {str(e)}")
            raise
    
    def _run_phase2_integration(self):
        """Phase 2 통합 실행"""
        try:
            logger.info("Phase 2 자동 통합 시작")
            
            # Phase 2 딥러닝 통합 실행
            # 여기에 실제 Phase 2 로직 구현
            
            logger.info("Phase 2 자동 통합 완료")
        
        except Exception as e:
            logger.error(f"Phase 2 자동 통합 실패: {str(e)}")
            raise
    
    def _monitor_performance(self):
        """성능 모니터링"""
        try:
            logger.info("성능 모니터링 실행")
            
            # 시스템 성능 체크
            # CPU, 메모리, 디스크 사용량 등
            
            logger.info("성능 모니터링 완료")
        
        except Exception as e:
            logger.error(f"성능 모니터링 실패: {str(e)}")
    
    def _run_auto_backup(self):
        """자동 백업 실행"""
        try:
            logger.info("자동 백업 시작")
            
            # 시스템 백업 실행
            # 여기에 실제 백업 로직 구현
            
            logger.info("자동 백업 완료")
        
        except Exception as e:
            logger.error(f"자동 백업 실패: {str(e)}")
    
    def _start_monitoring(self):
        """모니터링 시작"""
        try:
            # 별도 스레드에서 모니터링 실행
            monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            monitoring_thread.start()
            logger.info("모니터링이 시작되었습니다")
        
        except Exception as e:
            logger.error(f"모니터링 시작 실패: {str(e)}")
    
    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.monitoring_enabled:
            try:
                # 작업 상태 확인
                for task_id, task in self.integration_tasks.items():
                    if task.status == TaskStatus.FAILED:
                        logger.warning(f"실패한 작업 발견: {task.name}")
                        
                        # 자동 복구 시도
                        if task.retry_count < task.max_retries:
                            logger.info(f"자동 복구 시도: {task.name}")
                            # 복구 로직 구현
                
                time.sleep(60)  # 1분마다 체크
            
            except Exception as e:
                logger.error(f"모니터링 중 오류: {str(e)}")
                time.sleep(300)  # 오류 시 5분 대기
    
    def get_integration_status(self) -> Dict[str, Any]:
        """통합 상태 반환"""
        try:
            status = {
                "auto_integration_running": self.scheduler.running,
                "total_tasks": len(self.integration_tasks),
                "task_status": {}
            }
            
            for task_id, task in self.integration_tasks.items():
                status["task_status"][task_id] = {
                    "name": task.name,
                    "status": task.status.value,
                    "next_run": task.next_run.isoformat() if task.next_run else None,
                    "last_run": task.last_run.isoformat() if task.last_run else None,
                    "run_count": task.run_count,
                    "error_message": task.error_message
                }
            
            return status
        
        except Exception as e:
            logger.error(f"통합 상태 조회 실패: {str(e)}")
            return {"error": str(e)}
    
    def execute_task_immediately(self, task_id: str) -> bool:
        """작업 즉시 실행"""
        try:
            task = self.integration_tasks.get(task_id)
            if task:
                logger.info(f"작업 즉시 실행: {task.name}")
                self.scheduler._execute_task(task_id)
                return True
            return False
        
        except Exception as e:
            logger.error(f"작업 즉시 실행 실패: {str(e)}")
            return False
    
    def update_task_schedule(self, task_id: str, new_schedule: Dict[str, Any]) -> bool:
        """작업 스케줄 업데이트"""
        try:
            task = self.integration_tasks.get(task_id)
            if not task:
                return False
            
            # 기존 작업 제거
            self.scheduler.remove_task(task_id)
            
            # 스케줄 정보 업데이트
            if 'schedule_type' in new_schedule:
                task.schedule_type = new_schedule['schedule_type']
            if 'schedule_value' in new_schedule:
                task.schedule_value = new_schedule['schedule_value']
            
            # 업데이트된 작업 재등록
            success = self.scheduler.add_task(task)
            if success:
                logger.info(f"작업 스케줄 업데이트 완료: {task.name}")
            
            return success
        
        except Exception as e:
            logger.error(f"작업 스케줄 업데이트 실패: {str(e)}")
            return False

# 사용 예시
if __name__ == "__main__":
    # 자동 통합 관리자 생성
    auto_mgr = AutoIntegrationManager()
    
    # 자동 통합 시작
    auto_mgr.start_auto_integration()
    
    try:
        # 메인 루프
        while True:
            time.sleep(10)
            
            # 상태 출력
            status = auto_mgr.get_integration_status()
            print(f"\n=== 자동 통합 상태 ===")
            print(f"실행 중: {status['auto_integration_running']}")
            print(f"총 작업 수: {status['total_tasks']}")
            
            for task_id, task_info in status['task_status'].items():
                print(f"\n작업: {task_info['name']}")
                print(f"  상태: {task_info['status']}")
                print(f"  다음 실행: {task_info['next_run']}")
                print(f"  마지막 실행: {task_info['last_run']}")
                print(f"  실행 횟수: {task_info['run_count']}")
    
    except KeyboardInterrupt:
        print("\n자동 통합 중지 중...")
        auto_mgr.stop_auto_integration()
        print("자동 통합이 중지되었습니다")
