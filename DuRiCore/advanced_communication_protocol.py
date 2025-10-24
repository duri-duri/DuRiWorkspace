#!/usr/bin/env python3
"""
고급 통신 프로토콜 시스템
DuRi Phase 6.2.2.2 - 모듈간 통신 프로토콜 (40% 통신 효율성 향상 목표)

기능:
1. 표준화된 통신 프로토콜
2. 자동 모듈 검증
3. 버전 호환성 관리
4. 실시간 모니터링
5. 자동 복구 시스템
"""

import asyncio
import logging
import queue
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """메시지 타입"""

    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    SYNC = "sync"


class MessagePriority(Enum):
    """메시지 우선순위"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Message:
    """통신 메시지"""

    id: str
    from_module: str
    to_module: str
    message_type: MessageType
    priority: MessagePriority
    data: Any
    timestamp: datetime
    correlation_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.now()


class AdvancedCommunicationProtocol:
    """고급 통신 프로토콜"""

    def __init__(self):
        self.message_queue: queue.PriorityQueue = queue.PriorityQueue()
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.module_connections: Dict[str, Dict[str, Any]] = {}
        self.message_history: List[Message] = []
        self.auto_retry_enabled = True
        self.heartbeat_interval = 30  # 30초
        self.connection_timeout = 60  # 60초

        # 성능 메트릭
        self.performance_metrics = {
            "total_messages": 0,
            "successful_messages": 0,
            "failed_messages": 0,
            "average_response_time": 0.0,
            "message_queue_size": 0,
            "active_connections": 0,
        }

        # 자동화 설정
        self.auto_recovery_enabled = True
        self.auto_sync_enabled = True

        # 모니터링 스레드 시작
        self._start_monitoring()

        logger.info("📡 고급 통신 프로토콜 초기화 완료")

    def _start_monitoring(self):
        """모니터링 스레드 시작"""

        def monitor_connections():
            while True:
                try:
                    current_time = datetime.now()

                    # 연결 상태 확인
                    for module_name, connection in self.module_connections.items():
                        last_heartbeat = connection.get("last_heartbeat")
                        if last_heartbeat and (current_time - last_heartbeat).seconds > self.connection_timeout:
                            logger.warning(f"⚠️  연결 타임아웃: {module_name}")
                            if self.auto_recovery_enabled:
                                self._attempt_recovery(module_name)

                    # 성능 메트릭 업데이트
                    self._update_performance_metrics()

                    time.sleep(10)  # 10초마다 체크
                except Exception as e:
                    logger.error(f"❌ 모니터링 오류: {e}")

        monitor_thread = threading.Thread(target=monitor_connections, daemon=True)
        monitor_thread.start()
        logger.info("🔍 통신 모니터링 시작")

    def register_module(self, module_name: str, module_instance: Any) -> bool:
        """모듈 등록"""
        try:
            self.module_connections[module_name] = {
                "instance": module_instance,
                "status": "active",
                "last_heartbeat": datetime.now(),
                "message_count": 0,
                "error_count": 0,
            }
            logger.info(f"✅ 모듈 등록: {module_name}")
            return True
        except Exception as e:
            logger.error(f"❌ 모듈 등록 실패: {module_name} - {e}")
            return False

    async def send_message(
        self,
        from_module: str,
        to_module: str,
        message_type: MessageType,
        data: Any,
        priority: MessagePriority = MessagePriority.NORMAL,
        correlation_id: Optional[str] = None,
    ) -> str:
        """메시지 전송"""
        try:
            message = Message(
                id=str(uuid.uuid4()),
                from_module=from_module,
                to_module=to_module,
                message_type=message_type,
                priority=priority,
                data=data,
                timestamp=datetime.now(),
                correlation_id=correlation_id,
            )

            # 우선순위 큐에 추가 (우선순위가 높을수록 숫자가 작음)
            priority_value = 5 - message.priority.value
            self.message_queue.put((priority_value, time.time(), message))

            # 메시지 히스토리에 추가
            self.message_history.append(message)

            # 성능 메트릭 업데이트
            self.performance_metrics["total_messages"] += 1
            self.performance_metrics["message_queue_size"] = self.message_queue.qsize()

            logger.info(f"📤 메시지 전송: {from_module} → {to_module} ({message_type.value})")
            return message.id

        except Exception as e:
            logger.error(f"❌ 메시지 전송 실패: {from_module} → {to_module} - {e}")
            self.performance_metrics["failed_messages"] += 1
            raise

    async def process_message_queue(self):
        """메시지 큐 처리"""
        while True:
            try:
                if not self.message_queue.empty():
                    priority, timestamp, message = self.message_queue.get()

                    # 메시지 처리
                    success = await self._process_message(message)

                    if success:
                        self.performance_metrics["successful_messages"] += 1
                    else:
                        self.performance_metrics["failed_messages"] += 1

                        # 재시도 로직
                        if self.auto_retry_enabled and message.retry_count < message.max_retries:
                            message.retry_count += 1
                            self.message_queue.put((priority, time.time(), message))
                            logger.warning(f"🔄 메시지 재시도: {message.id} (시도 {message.retry_count})")

                await asyncio.sleep(0.01)  # 10ms 대기

            except Exception as e:
                logger.error(f"❌ 메시지 큐 처리 오류: {e}")
                await asyncio.sleep(1)

    async def _process_message(self, message: Message) -> bool:
        """개별 메시지 처리"""
        try:
            # 대상 모듈 확인
            if message.to_module not in self.module_connections:
                logger.error(f"❌ 대상 모듈 없음: {message.to_module}")
                return False

            # 연결 상태 확인
            connection = self.module_connections[message.to_module]
            if connection["status"] != "active":
                logger.warning(f"⚠️  비활성 모듈: {message.to_module}")
                return False

            # 메시지 타입별 처리
            if message.message_type == MessageType.REQUEST:
                return await self._handle_request(message)
            elif message.message_type == MessageType.EVENT:
                return await self._handle_event(message)
            elif message.message_type == MessageType.HEARTBEAT:
                return await self._handle_heartbeat(message)
            elif message.message_type == MessageType.SYNC:
                return await self._handle_sync(message)
            else:
                logger.warning(f"⚠️  알 수 없는 메시지 타입: {message.message_type}")
                return False

        except Exception as e:
            logger.error(f"❌ 메시지 처리 실패: {message.id} - {e}")
            return False

    async def _handle_request(self, message: Message) -> bool:
        """요청 메시지 처리"""
        try:
            target_module = self.module_connections[message.to_module]["instance"]

            # 메서드 호출
            if hasattr(target_module, "handle_request"):
                response = await target_module.handle_request(message.data)

                # 응답 전송
                response_message = Message(
                    id=str(uuid.uuid4()),
                    from_module=message.to_module,
                    to_module=message.from_module,
                    message_type=MessageType.RESPONSE,
                    priority=message.priority,
                    data=response,
                    timestamp=datetime.now(),
                    correlation_id=message.id,
                )

                self.message_queue.put((5 - response_message.priority.value, time.time(), response_message))

                # 성능 메트릭 업데이트
                self.module_connections[message.to_module]["message_count"] += 1

                logger.info(f"✅ 요청 처리 완료: {message.id}")
                return True
            else:
                logger.warning(f"⚠️  요청 핸들러 없음: {message.to_module}")
                return False

        except Exception as e:
            logger.error(f"❌ 요청 처리 실패: {message.id} - {e}")
            self.module_connections[message.to_module]["error_count"] += 1
            return False

    async def _handle_event(self, message: Message) -> bool:
        """이벤트 메시지 처리"""
        try:
            # 이벤트 핸들러 호출
            event_type = message.data.get("event_type", "unknown")
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(message.data)
                        else:
                            handler(message.data)
                    except Exception as e:
                        logger.error(f"❌ 이벤트 핸들러 오류: {event_type} - {e}")

            logger.info(f"✅ 이벤트 처리 완료: {message.id}")
            return True

        except Exception as e:
            logger.error(f"❌ 이벤트 처리 실패: {message.id} - {e}")
            return False

    async def _handle_heartbeat(self, message: Message) -> bool:
        """하트비트 메시지 처리"""
        try:
            # 하트비트 응답
            response_message = Message(
                id=str(uuid.uuid4()),
                from_module=message.to_module,
                to_module=message.from_module,
                message_type=MessageType.HEARTBEAT,
                priority=MessagePriority.LOW,
                data={"status": "alive"},
                timestamp=datetime.now(),
                correlation_id=message.id,
            )

            self.message_queue.put((4, time.time(), response_message))

            # 연결 상태 업데이트
            if message.from_module in self.module_connections:
                self.module_connections[message.from_module]["last_heartbeat"] = datetime.now()

            return True

        except Exception as e:
            logger.error(f"❌ 하트비트 처리 실패: {message.id} - {e}")
            return False

    async def _handle_sync(self, message: Message) -> bool:
        """동기화 메시지 처리"""
        try:
            # 모듈 상태 동기화
            sync_data = {
                "module_status": self._get_module_status(),
                "performance_metrics": self.performance_metrics,
                "timestamp": datetime.now().isoformat(),
            }

            response_message = Message(
                id=str(uuid.uuid4()),
                from_module=message.to_module,
                to_module=message.from_module,
                message_type=MessageType.SYNC,
                priority=message.priority,
                data=sync_data,
                timestamp=datetime.now(),
                correlation_id=message.id,
            )

            self.message_queue.put((5 - response_message.priority.value, time.time(), response_message))

            logger.info(f"✅ 동기화 완료: {message.id}")
            return True

        except Exception as e:
            logger.error(f"❌ 동기화 실패: {message.id} - {e}")
            return False

    def register_event_handler(self, event_type: str, handler: Callable):
        """이벤트 핸들러 등록"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []

        self.event_handlers[event_type].append(handler)
        logger.info(f"📝 이벤트 핸들러 등록: {event_type}")

    def _attempt_recovery(self, module_name: str):
        """모듈 복구 시도"""
        try:
            logger.info(f"🔄 모듈 복구 시도: {module_name}")

            # 모듈 재초기화 시도
            if module_name in self.module_connections:
                connection = self.module_connections[module_name]
                module_instance = connection["instance"]

                if hasattr(module_instance, "reinitialize"):
                    module_instance.reinitialize()
                    connection["status"] = "active"
                    connection["last_heartbeat"] = datetime.now()
                    logger.info(f"✅ 모듈 복구 성공: {module_name}")
                else:
                    logger.warning(f"⚠️  복구 메서드 없음: {module_name}")

        except Exception as e:
            logger.error(f"❌ 모듈 복구 실패: {module_name} - {e}")

    def _get_module_status(self) -> Dict[str, Any]:
        """모듈 상태 조회"""
        status = {}
        for module_name, connection in self.module_connections.items():
            status[module_name] = {
                "status": connection["status"],
                "last_heartbeat": connection["last_heartbeat"].isoformat(),
                "message_count": connection["message_count"],
                "error_count": connection["error_count"],
            }
        return status

    def _update_performance_metrics(self):
        """성능 메트릭 업데이트"""
        active_connections = sum(1 for conn in self.module_connections.values() if conn["status"] == "active")

        # 평균 응답 시간 계산
        if self.message_history:
            recent_messages = self.message_history[-100:]  # 최근 100개 메시지
            response_times = []
            for i in range(0, len(recent_messages) - 1, 2):
                if i + 1 < len(recent_messages):
                    msg1 = recent_messages[i]
                    msg2 = recent_messages[i + 1]
                    if msg2.correlation_id == msg1.id:
                        response_time = (msg2.timestamp - msg1.timestamp).total_seconds()
                        response_times.append(response_time)

            avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        else:
            avg_response_time = 0.0

        self.performance_metrics.update(
            {
                "message_queue_size": self.message_queue.qsize(),
                "active_connections": active_connections,
                "average_response_time": avg_response_time,
            }
        )

    def get_performance_report(self) -> Dict[str, Any]:
        """성능 리포트 생성"""
        self._update_performance_metrics()

        success_rate = (
            self.performance_metrics["successful_messages"] / max(self.performance_metrics["total_messages"], 1)
        ) * 100

        return {
            "metrics": self.performance_metrics,
            "success_rate": success_rate,
            "module_status": self._get_module_status(),
            "message_queue_size": self.message_queue.qsize(),
            "active_connections": self.performance_metrics["active_connections"],
            "average_response_time": self.performance_metrics["average_response_time"],
        }


class AutoRecoverySystem:
    """자동 복구 시스템"""

    def __init__(self):
        self.recovery_strategies: Dict[str, Callable] = {}
        self.recovery_history: List[Dict[str, Any]] = []
        self.auto_recovery_enabled = True
        logger.info("🔄 자동 복구 시스템 초기화 완료")

    def register_recovery_strategy(self, error_type: str, strategy: Callable):
        """복구 전략 등록"""
        self.recovery_strategies[error_type] = strategy
        logger.info(f"🔄 복구 전략 등록: {error_type}")

    async def attempt_recovery(self, module_name: str, error_type: str, error_details: Any) -> bool:
        """복구 시도"""
        try:
            if error_type in self.recovery_strategies:
                strategy = self.recovery_strategies[error_type]
                success = await strategy(module_name, error_details)

                recovery_record = {
                    "module_name": module_name,
                    "error_type": error_type,
                    "error_details": str(error_details),
                    "success": success,
                    "timestamp": datetime.now().isoformat(),
                }

                self.recovery_history.append(recovery_record)

                if success:
                    logger.info(f"✅ 복구 성공: {module_name} ({error_type})")
                else:
                    logger.warning(f"⚠️  복구 실패: {module_name} ({error_type})")

                return success
            else:
                logger.warning(f"⚠️  복구 전략 없음: {error_type}")
                return False

        except Exception as e:
            logger.error(f"❌ 복구 시도 실패: {module_name} - {e}")
            return False


class RealTimeMonitoringSystem:
    """실시간 모니터링 시스템"""

    def __init__(self):
        self.monitoring_data: Dict[str, Any] = {}
        self.alert_thresholds: Dict[str, float] = {}
        self.alert_handlers: Dict[str, List[Callable]] = {}
        self.monitoring_enabled = True
        logger.info("📊 실시간 모니터링 시스템 초기화 완료")

    def set_alert_threshold(self, metric_name: str, threshold: float):
        """알림 임계값 설정"""
        self.alert_thresholds[metric_name] = threshold
        logger.info(f"📊 알림 임계값 설정: {metric_name} = {threshold}")

    def register_alert_handler(self, alert_type: str, handler: Callable):
        """알림 핸들러 등록"""
        if alert_type not in self.alert_handlers:
            self.alert_handlers[alert_type] = []

        self.alert_handlers[alert_type].append(handler)
        logger.info(f"📊 알림 핸들러 등록: {alert_type}")

    def update_metric(self, metric_name: str, value: float):
        """메트릭 업데이트"""
        self.monitoring_data[metric_name] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
        }

        # 알림 확인
        if metric_name in self.alert_thresholds:
            threshold = self.alert_thresholds[metric_name]
            if value > threshold:
                self._trigger_alert(metric_name, value, threshold)

    def _trigger_alert(self, metric_name: str, value: float, threshold: float):
        """알림 트리거"""
        alert_data = {
            "metric_name": metric_name,
            "current_value": value,
            "threshold": threshold,
            "timestamp": datetime.now().isoformat(),
        }

        for handler in self.alert_handlers.get("general", []):
            try:
                handler(alert_data)
            except Exception as e:
                logger.error(f"❌ 알림 핸들러 오류: {e}")

        logger.warning(f"⚠️  알림 트리거: {metric_name} = {value} (임계값: {threshold})")


# 테스트용 샘플 모듈들
class SampleCommunicationModule:
    """샘플 통신 모듈"""

    def __init__(self, name: str):
        self.name = name
        self.message_count = 0
        self.status = "active"

    async def handle_request(self, data: Any) -> Dict[str, Any]:
        """요청 처리"""
        self.message_count += 1
        await asyncio.sleep(0.01)  # 10ms 시뮬레이션
        return {
            "module": self.name,
            "response": f"처리된 데이터: {data}",
            "message_count": self.message_count,
            "status": "success",
        }

    async def reinitialize(self):
        """재초기화"""
        self.status = "active"
        logger.info(f"🔄 모듈 재초기화: {self.name}")


async def test_advanced_communication_protocol():
    """고급 통신 프로토콜 테스트"""
    logger.info("🧪 고급 통신 프로토콜 테스트 시작")

    # 통신 프로토콜 초기화
    protocol = AdvancedCommunicationProtocol()

    # 샘플 모듈들 생성 및 등록
    module1 = SampleCommunicationModule("module_1")
    module2 = SampleCommunicationModule("module_2")
    module3 = SampleCommunicationModule("module_3")

    protocol.register_module("module_1", module1)
    protocol.register_module("module_2", module2)
    protocol.register_module("module_3", module3)

    # 이벤트 핸들러 등록
    def event_handler(data):
        logger.info(f"📝 이벤트 처리: {data}")

    protocol.register_event_handler("test_event", event_handler)

    # 메시지 전송 테스트
    logger.info("📤 메시지 전송 테스트")

    # 요청 메시지 전송
    request_id = await protocol.send_message(
        "module_1",
        "module_2",
        MessageType.REQUEST,
        {"action": "test", "data": "hello"},
        MessagePriority.HIGH,
    )
    logger.info(f"   요청 메시지 ID: {request_id}")

    # 이벤트 메시지 전송
    event_id = await protocol.send_message(
        "module_1",
        "module_2",
        MessageType.EVENT,
        {"event_type": "test_event", "data": "event_data"},
    )
    logger.info(f"   이벤트 메시지 ID: {event_id}")

    # 하트비트 메시지 전송
    heartbeat_id = await protocol.send_message("module_1", "module_2", MessageType.HEARTBEAT, {"status": "ping"})
    logger.info(f"   하트비트 메시지 ID: {heartbeat_id}")

    # 동기화 메시지 전송
    sync_id = await protocol.send_message("module_1", "module_2", MessageType.SYNC, {"sync_type": "status"})
    logger.info(f"   동기화 메시지 ID: {sync_id}")

    # 메시지 큐 처리 시작
    logger.info("⚡ 메시지 큐 처리 시작")
    queue_task = asyncio.create_task(protocol.process_message_queue())

    # 잠시 대기하여 메시지 처리 완료
    await asyncio.sleep(2)

    # 성능 리포트
    report = protocol.get_performance_report()
    logger.info("📈 성능 리포트:")
    logger.info(f"   총 메시지 수: {report['metrics']['total_messages']}")
    logger.info(f"   성공률: {report['success_rate']:.1f}%")
    logger.info(f"   활성 연결 수: {report['active_connections']}")
    logger.info(f"   평균 응답 시간: {report['average_response_time']:.3f}초")
    logger.info(f"   메시지 큐 크기: {report['message_queue_size']}")

    # 큐 태스크 취소
    queue_task.cancel()

    return report


if __name__ == "__main__":
    asyncio.run(test_advanced_communication_protocol())
