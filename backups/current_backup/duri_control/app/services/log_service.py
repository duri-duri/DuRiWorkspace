import asyncio
import subprocess
import re
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, AsyncGenerator
from collections import deque
import threading
import time

from ..models.log_entry import LogEntry, LogStreamConfig, LogQueryParams
from duri_common.logger import get_logger

logger = get_logger("duri_control.log_service")


class LogService:
    """로그 수집 및 스트리밍 서비스"""
    
    def __init__(self, config: LogStreamConfig = None):
        self.config = config or LogStreamConfig()
        self.logs: deque = deque(maxlen=self.config.max_entries)
        self.subscribers: List[asyncio.Queue] = []
        self.collection_running = False
        self.collection_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # 서비스별 로그 파일 경로
        self.service_log_paths = {
            "duri_core": "/app/logs/duri_core.log",
            "duri_brain": "/app/logs/duri_brain.log", 
            "duri_evolution": "/app/logs/duri_evolution.log",
            "duri_control": "/app/logs/duri_control.log"
        }
        
        # 컨테이너 이름 매핑
        self.container_names = {
            "duri_core": "duri_core_container",
            "duri_brain": "duri_brain_container",
            "duri_evolution": "duri_evolution_container", 
            "duri_control": "duri_control_container"
        }
    
    def start_collection(self):
        """로그 수집 시작"""
        if not self.collection_running:
            self.collection_running = True
            self.collection_thread = threading.Thread(target=self._collection_worker, daemon=True)
            self.collection_thread.start()
            logger.info("로그 수집 서비스 시작됨")
    
    def stop_collection(self):
        """로그 수집 중지"""
        self.collection_running = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        logger.info("로그 수집 서비스 중지됨")
    
    def _collection_worker(self):
        """로그 수집 워커 스레드"""
        while self.collection_running:
            try:
                # 컨테이너 로그 수집
                self._collect_container_logs()
                
                # 파일 로그 수집 (선택적)
                self._collect_file_logs()
                
                time.sleep(self.config.stream_interval)
                
            except Exception as e:
                logger.error(f"로그 수집 중 오류 발생: {e}")
                time.sleep(5)  # 오류 시 잠시 대기
    
    def _collect_container_logs(self):
        """Docker 컨테이너 로그 수집"""
        for service_name, container_name in self.container_names.items():
            if service_name not in self.config.services and self.config.services:
                continue
                
            try:
                # docker logs 명령으로 최근 로그 조회
                result = subprocess.run(
                    ["docker", "logs", "--tail", "10", "--timestamps", container_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            log_entry = self._parse_container_log_line(line, service_name, container_name)
                            if log_entry:
                                self._add_log_entry(log_entry)
                                
            except Exception as e:
                logger.warning(f"컨테이너 {container_name} 로그 수집 실패: {e}")
    
    def _collect_file_logs(self):
        """파일 기반 로그 수집 (선택적 구현)"""
        # 현재는 컨테이너 로그에 집중하므로 생략
        pass
    
    def _parse_container_log_line(self, line: str, service_name: str, container_name: str) -> Optional[LogEntry]:
        """컨테이너 로그 라인 파싱"""
        try:
            # Docker 로그 형식: "2025-07-24T03:56:31.780482Z message"
            timestamp_match = re.match(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z?)\s+(.+)$', line)
            
            if timestamp_match:
                timestamp_str, message = timestamp_match.groups()
                
                # 타임스탬프 파싱
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except ValueError:
                    timestamp = datetime.now()
                
                # 로그 레벨 추출
                level = self._extract_log_level(message)
                
                # 메시지 정리
                clean_message = self._clean_log_message(message)
                
                return LogEntry(
                    id=str(uuid.uuid4()),
                    timestamp=timestamp,
                    service_name=service_name,
                    level=level,
                    message=clean_message,
                    source="container",
                    container_id=container_name
                )
                
        except Exception as e:
            logger.debug(f"로그 라인 파싱 실패: {line[:100]}... - {e}")
        
        return None
    
    def _extract_log_level(self, message: str) -> str:
        """로그 메시지에서 레벨 추출"""
        message_upper = message.upper()
        
        if any(level in message_upper for level in ["ERROR", "CRITICAL", "FATAL"]):
            return "ERROR"
        elif "WARNING" in message_upper or "WARN" in message_upper:
            return "WARNING"
        elif "DEBUG" in message_upper:
            return "DEBUG"
        else:
            return "INFO"
    
    def _clean_log_message(self, message: str) -> str:
        """로그 메시지 정리"""
        # 불필요한 접두사 제거
        prefixes_to_remove = [
            "INFO:", "WARNING:", "ERROR:", "DEBUG:",
            "INFO -", "WARNING -", "ERROR -", "DEBUG -"
        ]
        
        clean_message = message
        for prefix in prefixes_to_remove:
            if clean_message.startswith(prefix):
                clean_message = clean_message[len(prefix):].strip()
                break
        
        return clean_message
    
    def _add_log_entry(self, log_entry: LogEntry):
        """로그 엔트리 추가"""
        with self._lock:
            self.logs.append(log_entry)
            
            # 구독자들에게 알림
            for queue in self.subscribers[:]:  # 복사본으로 순회
                try:
                    if not queue.full():
                        queue.put_nowait(log_entry)
                except asyncio.QueueFull:
                    # 큐가 가득 찬 경우 구독자 제거
                    self.subscribers.remove(queue)
                except Exception as e:
                    logger.warning(f"구독자 알림 실패: {e}")
                    self.subscribers.remove(queue)
    
    async def subscribe(self) -> asyncio.Queue:
        """로그 스트림 구독"""
        queue = asyncio.Queue(maxsize=100)
        self.subscribers.append(queue)
        return queue
    
    def unsubscribe(self, queue: asyncio.Queue):
        """로그 스트림 구독 해제"""
        if queue in self.subscribers:
            self.subscribers.remove(queue)
    
    def get_recent_logs(self, params: LogQueryParams) -> List[LogEntry]:
        """최근 로그 조회"""
        with self._lock:
            logs = list(self.logs)
        
        # 필터링
        filtered_logs = []
        for log in logs:
            # 서비스 필터
            if params.service_name and log.service_name != params.service_name:
                continue
            
            # 레벨 필터
            if params.level and log.level != params.level:
                continue
            
            # 시간 필터
            if params.since and log.timestamp < params.since:
                continue
            if params.until and log.timestamp > params.until:
                continue
            
            filtered_logs.append(log)
        
        # 최신순 정렬 및 제한
        filtered_logs.sort(key=lambda x: x.timestamp, reverse=True)
        return filtered_logs[:params.limit]
    
    async def stream_logs(self) -> AsyncGenerator[str, None]:
        """SSE 로그 스트림"""
        queue = await self.subscribe()
        
        try:
            while True:
                try:
                    log_entry = await asyncio.wait_for(queue.get(), timeout=30.0)
                    
                    # SSE 형식으로 전송
                    sse_data = f"data: {log_entry.json()}\n\n"
                    yield sse_data
                    
                except asyncio.TimeoutError:
                    # 연결 유지를 위한 heartbeat
                    yield "data: {\"type\": \"heartbeat\", \"timestamp\": \"" + datetime.now().isoformat() + "\"}\n\n"
                    
        except Exception as e:
            logger.error(f"로그 스트림 오류: {e}")
        finally:
            self.unsubscribe(queue)
    
    def get_log_statistics(self) -> Dict:
        """로그 통계 정보"""
        with self._lock:
            logs = list(self.logs)
        
        stats = {
            "total_logs": len(logs),
            "services": {},
            "levels": {},
            "recent_activity": {
                "last_hour": 0,
                "last_24_hours": 0
            }
        }
        
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        one_day_ago = now - timedelta(days=1)
        
        for log in logs:
            # 서비스별 통계
            if log.service_name not in stats["services"]:
                stats["services"][log.service_name] = 0
            stats["services"][log.service_name] += 1
            
            # 레벨별 통계
            if log.level not in stats["levels"]:
                stats["levels"][log.level] = 0
            stats["levels"][log.level] += 1
            
            # 최근 활동
            if log.timestamp >= one_hour_ago:
                stats["recent_activity"]["last_hour"] += 1
            if log.timestamp >= one_day_ago:
                stats["recent_activity"]["last_24_hours"] += 1
        
        return stats


# 전역 로그 서비스 인스턴스
log_service = LogService() 